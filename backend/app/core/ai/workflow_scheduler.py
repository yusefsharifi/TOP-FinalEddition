"""
AI Workflow Scheduler — Periodic Execution Service
TOP WorX ERP System

Provides:
  - Background scheduler thread for periodic workflow execution
  - Configurable intervals per handler (minutes, hours, daily, weekly)
  - Execution history tracking
  - Start/stop/pause controls
  - Integration with B3 workflow handlers

Usage:
  scheduler = WorkflowScheduler(db_factory)
  scheduler.start()
  scheduler.add_job("low_stock_auto_po", interval_minutes=60)
  scheduler.add_job("invoice_due_reminder", interval_minutes=360)
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class WorkflowScheduler:
    """
    Background scheduler for periodic workflow execution.
    
    Runs workflow handlers on configurable schedules using a daemon thread.
    Thread-safe with lock-protected state.
    """

    def __init__(self, db_factory: Callable):
        """
        Args:
            db_factory: Async callable that returns an AsyncSession.
                        e.g., async def get_db(): yield AsyncSession(...)
        """
        self._db_factory = db_factory
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._jobs: dict[str, SchedulerJob] = {}
        self._history: list[dict] = []
        self._max_history = 200

    # ── Control ──────────────────────────────────────────────────────────

    def start(self) -> dict:
        """Start the scheduler background thread."""
        with self._lock:
            if self._running:
                return {"status": "already_running", "jobs": len(self._jobs)}

            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            logger.info(f"Workflow scheduler started with {len(self._jobs)} jobs")
            return {"status": "started", "jobs": len(self._jobs)}

    def stop(self) -> dict:
        """Stop the scheduler background thread."""
        with self._lock:
            if not self._running:
                return {"status": "already_stopped"}

            self._running = False
            if self._thread:
                self._thread.join(timeout=5)
            logger.info("Workflow scheduler stopped")
            return {"status": "stopped"}

    def pause(self) -> dict:
        """Pause the scheduler (stop executing but keep jobs)."""
        with self._lock:
            self._running = False
            return {"status": "paused", "jobs": len(self._jobs)}

    def resume(self) -> dict:
        """Resume a paused scheduler."""
        with self._lock:
            if self._running:
                return {"status": "already_running"}
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            return {"status": "resumed"}

    @property
    def is_running(self) -> bool:
        return self._running

    # ── Job Management ───────────────────────────────────────────────────

    def add_job(
        self,
        handler_name: str,
        interval_minutes: int = 60,
        enabled: bool = True,
        config: Optional[dict] = None,
    ) -> dict:
        """Add or update a scheduled job."""
        with self._lock:
            self._jobs[handler_name] = SchedulerJob(
                handler_name=handler_name,
                interval_minutes=interval_minutes,
                enabled=enabled,
                config=config or {},
            )
            logger.info(f"Job added: {handler_name} (every {interval_minutes}min)")
            return self._jobs[handler_name].to_dict()

    def remove_job(self, handler_name: str) -> dict:
        """Remove a scheduled job."""
        with self._lock:
            if handler_name in self._jobs:
                del self._jobs[handler_name]
                return {"status": "removed", "handler": handler_name}
            return {"status": "not_found", "handler": handler_name}

    def enable_job(self, handler_name: str) -> dict:
        """Enable a scheduled job."""
        with self._lock:
            if handler_name in self._jobs:
                self._jobs[handler_name].enabled = True
                return {"status": "enabled", "handler": handler_name}
            return {"status": "not_found"}

    def disable_job(self, handler_name: str) -> dict:
        """Disable a scheduled job."""
        with self._lock:
            if handler_name in self._jobs:
                self._jobs[handler_name].enabled = False
                return {"status": "disabled", "handler": handler_name}
            return {"status": "not_found"}

    def get_job(self, handler_name: str) -> Optional[dict]:
        """Get a specific job's details."""
        job = self._jobs.get(handler_name)
        return job.to_dict() if job else None

    def list_jobs(self) -> list[dict]:
        """List all scheduled jobs."""
        return [job.to_dict() for job in self._jobs.values()]

    # ── Execution ────────────────────────────────────────────────────────

    def run_now(self, handler_name: Optional[str] = None) -> dict:
        """
        Trigger immediate execution of a handler or all handlers.
        Runs in a background thread to avoid blocking.
        """
        if handler_name:
            thread = threading.Thread(
                target=self._execute_handler,
                args=(handler_name,),
                daemon=True,
            )
            thread.start()
            return {"status": "triggered", "handler": handler_name}
        else:
            thread = threading.Thread(
                target=self._execute_all,
                daemon=True,
            )
            thread.start()
            return {"status": "triggered", "handler": "all"}

    def _execute_handler(self, handler_name: str) -> dict:
        """Execute a single handler (sync wrapper for async)."""
        import asyncio
        from app.core.ai.workflow_handlers import run_handler

        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def _run():
                async for db in self._db_factory():
                    return await run_handler(handler_name, db)

            result = loop.run_until_complete(_run())
            loop.close()

            # Record in history
            entry = {
                "handler": handler_name,
                "executed_at": datetime.utcnow().isoformat(),
                "triggered": result.get("triggered", False),
                "message": result.get("message", ""),
            }
            self._history.append(entry)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

            # Update job stats
            if handler_name in self._jobs:
                self._jobs[handler_name].last_run = datetime.utcnow()
                self._jobs[handler_name].run_count += 1
                if result.get("triggered"):
                    self._jobs[handler_name].trigger_count += 1

            logger.info(f"Handler '{handler_name}' executed: triggered={result.get('triggered')}")
            return result

        except Exception as e:
            logger.error(f"Handler '{handler_name}' failed: {e}")
            return {"handler": handler_name, "error": str(e)}

    def _execute_all(self) -> dict:
        """Execute all enabled handlers."""
        import asyncio
        from app.core.ai.workflow_handlers import run_all_handlers

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def _run():
                async for db in self._db_factory():
                    return await run_all_handlers(db)

            result = loop.run_until_complete(_run())
            loop.close()

            entry = {
                "handler": "all",
                "executed_at": result.get("executed_at", datetime.utcnow().isoformat()),
                "handlers_run": result.get("handlers_run", 0),
                "handlers_triggered": result.get("handlers_triggered", 0),
            }
            self._history.append(entry)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

            logger.info(
                f"All handlers executed: {result.get('handlers_triggered', 0)} triggered"
            )
            return result

        except Exception as e:
            logger.error(f"Execute all failed: {e}")
            return {"error": str(e)}

    # ── Scheduler Loop ───────────────────────────────────────────────────

    def _run_loop(self):
        """Main scheduler loop — checks jobs every 60 seconds."""
        logger.info("Scheduler loop started")
        while self._running:
            try:
                now = datetime.utcnow()
                with self._lock:
                    jobs_to_run = []
                    for name, job in self._jobs.items():
                        if not job.enabled:
                            continue
                        if job.next_run and job.next_run <= now:
                            jobs_to_run.append(name)

                for name in jobs_to_run:
                    logger.info(f"Running scheduled job: {name}")
                    self._execute_handler(name)
                    # Update next run time
                    with self._lock:
                        if name in self._jobs:
                            self._jobs[name].next_run = (
                                datetime.utcnow()
                                + timedelta(minutes=self._jobs[name].interval_minutes)
                            )

            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")

            time.sleep(60)  # Check every minute

    # ── History ──────────────────────────────────────────────────────────

    def get_history(self, limit: int = 20) -> list[dict]:
        """Get recent execution history."""
        return list(reversed(self._history[-limit:]))

    def get_stats(self) -> dict:
        """Get scheduler statistics."""
        enabled = sum(1 for j in self._jobs.values() if j.enabled)
        return {
            "running": self._running,
            "total_jobs": len(self._jobs),
            "enabled_jobs": enabled,
            "total_runs": sum(j.run_count for j in self._jobs.values()),
            "total_triggers": sum(j.trigger_count for j in self._jobs.values()),
            "history_count": len(self._history),
        }

    def clear_history(self):
        """Clear execution history."""
        self._history.clear()
        return {"status": "cleared"}


# ═══════════════════════════════════════════════════════════════════════════════
# Scheduler Job
# ═══════════════════════════════════════════════════════════════════════════════

class SchedulerJob:
    """Represents a single scheduled job."""

    def __init__(
        self,
        handler_name: str,
        interval_minutes: int = 60,
        enabled: bool = True,
        config: Optional[dict] = None,
    ):
        self.handler_name = handler_name
        self.interval_minutes = interval_minutes
        self.enabled = enabled
        self.config = config or {}
        self.created_at = datetime.utcnow()
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = datetime.utcnow() + timedelta(minutes=interval_minutes)
        self.run_count = 0
        self.trigger_count = 0

    def to_dict(self) -> dict:
        return {
            "handler_name": self.handler_name,
            "interval_minutes": self.interval_minutes,
            "enabled": self.enabled,
            "config": self.config,
            "created_at": self.created_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "trigger_count": self.trigger_count,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_scheduler: Optional[WorkflowScheduler] = None


def get_scheduler(db_factory: Optional[Callable] = None) -> WorkflowScheduler:
    """Get or create the singleton scheduler instance."""
    global _scheduler
    if _scheduler is None:
        if db_factory is None:
            raise ValueError("db_factory required for first initialization")
        _scheduler = WorkflowScheduler(db_factory)
    return _scheduler
