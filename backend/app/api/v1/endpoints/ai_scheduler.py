"""
AI Scheduler — Periodic Workflow Execution API
TOP WorX ERP System

Endpoints:
  GET  /ai/scheduler/status         — Get scheduler status
  POST /ai/scheduler/start          — Start the scheduler
  POST /ai/scheduler/stop           — Stop the scheduler
  POST /ai/scheduler/pause          — Pause the scheduler
  POST /ai/scheduler/resume         — Resume the scheduler
  GET  /ai/scheduler/jobs           — List all scheduled jobs
  POST /ai/scheduler/jobs           — Add a scheduled job
  PUT  /ai/scheduler/jobs/{handler} — Update a job
  DELETE /ai/scheduler/jobs/{handler} — Remove a job
  POST /ai/scheduler/run/{handler}  — Trigger immediate execution
  POST /ai/scheduler/run-all        — Trigger all handlers now
  GET  /ai/scheduler/history        — Get execution history
  GET  /ai/scheduler/stats          — Get scheduler statistics
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import DBDep, CurrentUser
from app.core.ai.workflow_scheduler import get_scheduler
from app.db.session import AsyncSessionLocal

router = APIRouter()


def _get_scheduler():
    """Get scheduler instance with DB factory."""
    async def db_factory():
        session = AsyncSessionLocal()
        try:
            yield session
        finally:
            await session.close()

    return get_scheduler(db_factory=db_factory)


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class SchedulerStatusResponse(BaseModel):
    running: bool
    total_jobs: int
    enabled_jobs: int
    total_runs: int
    total_triggers: int


class JobCreateRequest(BaseModel):
    handler_name: str = Field(..., description="Workflow handler name")
    interval_minutes: int = Field(default=60, ge=1, le=1440, description="Execution interval in minutes")
    enabled: bool = Field(default=True)
    config: Optional[dict] = Field(None, description="Handler-specific config")


class JobUpdateRequest(BaseModel):
    interval_minutes: Optional[int] = Field(None, ge=1, le=1440)
    enabled: Optional[bool] = None
    config: Optional[dict] = None


class JobResponse(BaseModel):
    handler_name: str
    interval_minutes: int
    enabled: bool
    config: dict
    created_at: str
    last_run: Optional[str]
    next_run: Optional[str]
    run_count: int
    trigger_count: int


class SchedulerActionResponse(BaseModel):
    status: str
    message: Optional[str] = None


class HistoryEntry(BaseModel):
    handler: str
    executed_at: str
    triggered: Optional[bool] = None
    message: Optional[str] = None
    handlers_run: Optional[int] = None
    handlers_triggered: Optional[int] = None


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints — Scheduler Control
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/scheduler/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerStatusResponse:
    """Get the current scheduler status."""
    scheduler = _get_scheduler()
    stats = scheduler.get_stats()
    return SchedulerStatusResponse(
        running=stats["running"],
        total_jobs=stats["total_jobs"],
        enabled_jobs=stats["enabled_jobs"],
        total_runs=stats["total_runs"],
        total_triggers=stats["total_triggers"],
    )


@router.post("/scheduler/start", response_model=SchedulerActionResponse)
async def start_scheduler(
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Start the workflow scheduler."""
    scheduler = _get_scheduler()
    result = scheduler.start()
    return SchedulerActionResponse(
        status=result["status"],
        message=f"Scheduler started with {result.get('jobs', 0)} jobs",
    )


@router.post("/scheduler/stop", response_model=SchedulerActionResponse)
async def stop_scheduler(
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Stop the workflow scheduler."""
    scheduler = _get_scheduler()
    result = scheduler.stop()
    return SchedulerActionResponse(status=result["status"])


@router.post("/scheduler/pause", response_model=SchedulerActionResponse)
async def pause_scheduler(
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Pause the scheduler (stops execution but keeps jobs)."""
    scheduler = _get_scheduler()
    result = scheduler.pause()
    return SchedulerActionResponse(status=result["status"])


@router.post("/scheduler/resume", response_model=SchedulerActionResponse)
async def resume_scheduler(
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Resume a paused scheduler."""
    scheduler = _get_scheduler()
    result = scheduler.resume()
    return SchedulerActionResponse(status=result["status"])


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints — Job Management
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/scheduler/jobs", response_model=list[JobResponse])
async def list_scheduled_jobs(
    db: DBDep,
    current_user: CurrentUser,
) -> list[JobResponse]:
    """List all scheduled workflow jobs."""
    scheduler = _get_scheduler()
    jobs = scheduler.list_jobs()
    return [JobResponse(**j) for j in jobs]


@router.post("/scheduler/jobs", response_model=JobResponse, status_code=201)
async def create_scheduled_job(
    data: JobCreateRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> JobResponse:
    """Add or update a scheduled job."""
    # Validate handler exists
    from app.core.ai.workflow_handlers import WORKFLOW_HANDLERS
    if data.handler_name not in WORKFLOW_HANDLERS:
        raise HTTPException(
            status_code=400,
            detail=f"Handler '{data.handler_name}' not found. Available: {list(WORKFLOW_HANDLERS.keys())}",
        )

    scheduler = _get_scheduler()
    result = scheduler.add_job(
        handler_name=data.handler_name,
        interval_minutes=data.interval_minutes,
        enabled=data.enabled,
        config=data.config,
    )
    return JobResponse(**result)


@router.put("/scheduler/jobs/{handler_name}", response_model=JobResponse)
async def update_scheduled_job(
    handler_name: str,
    data: JobUpdateRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> JobResponse:
    """Update a scheduled job's configuration."""
    scheduler = _get_scheduler()
    job = scheduler.get_job(handler_name)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{handler_name}' not found")

    # Update fields
    if data.interval_minutes is not None:
        job["interval_minutes"] = data.interval_minutes
    if data.enabled is not None:
        job["enabled"] = data.enabled
    if data.config is not None:
        job["config"] = data.config

    scheduler.add_job(
        handler_name=handler_name,
        interval_minutes=job["interval_minutes"],
        enabled=job["enabled"],
        config=job["config"],
    )
    return JobResponse(**job)


@router.delete("/scheduler/jobs/{handler_name}", response_model=SchedulerActionResponse)
async def delete_scheduled_job(
    handler_name: str,
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Remove a scheduled job."""
    scheduler = _get_scheduler()
    result = scheduler.remove_job(handler_name)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail=f"Job '{handler_name}' not found")
    return SchedulerActionResponse(status=result["status"])


@router.post("/scheduler/jobs/{handler_name}/enable", response_model=SchedulerActionResponse)
async def enable_scheduled_job(
    handler_name: str,
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Enable a scheduled job."""
    scheduler = _get_scheduler()
    result = scheduler.enable_job(handler_name)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail=f"Job '{handler_name}' not found")
    return SchedulerActionResponse(status=result["status"])


@router.post("/scheduler/jobs/{handler_name}/disable", response_model=SchedulerActionResponse)
async def disable_scheduled_job(
    handler_name: str,
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Disable a scheduled job."""
    scheduler = _get_scheduler()
    result = scheduler.disable_job(handler_name)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail=f"Job '{handler_name}' not found")
    return SchedulerActionResponse(status=result["status"])


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints — Manual Execution
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/scheduler/run/{handler_name}", response_model=SchedulerActionResponse)
async def run_handler_now(
    handler_name: str,
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Trigger immediate execution of a specific handler."""
    from app.core.ai.workflow_handlers import WORKFLOW_HANDLERS
    if handler_name not in WORKFLOW_HANDLERS:
        raise HTTPException(
            status_code=404,
            detail=f"Handler '{handler_name}' not found",
        )

    scheduler = _get_scheduler()
    result = scheduler.run_now(handler_name)
    return SchedulerActionResponse(
        status=result["status"],
        message=f"Handler '{handler_name}' triggered",
    )


@router.post("/scheduler/run-all", response_model=SchedulerActionResponse)
async def run_all_now(
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Trigger immediate execution of all handlers."""
    scheduler = _get_scheduler()
    result = scheduler.run_now()
    return SchedulerActionResponse(
        status=result["status"],
        message="All handlers triggered",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints — History & Stats
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/scheduler/history", response_model=list[HistoryEntry])
async def get_execution_history(
    db: DBDep,
    current_user: CurrentUser,
    limit: int = 20,
) -> list[HistoryEntry]:
    """Get recent execution history."""
    scheduler = _get_scheduler()
    history = scheduler.get_history(limit=limit)
    return [HistoryEntry(**h) for h in history]


@router.get("/scheduler/stats")
async def get_scheduler_stats(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Get scheduler statistics."""
    scheduler = _get_scheduler()
    return scheduler.get_stats()


@router.post("/scheduler/clear-history", response_model=SchedulerActionResponse)
async def clear_history(
    db: DBDep,
    current_user: CurrentUser,
) -> SchedulerActionResponse:
    """Clear execution history."""
    scheduler = _get_scheduler()
    scheduler.clear_history()
    return SchedulerActionResponse(status="cleared")


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints — Preset Schedules
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/scheduler/presets/default", response_model=list[JobResponse])
async def setup_default_schedule(
    db: DBDep,
    current_user: CurrentUser,
) -> list[JobResponse]:
    """
    Set up a default schedule for all B3 workflow handlers.
    
    Default intervals:
      - low_stock_auto_po: Every hour
      - invoice_due_reminder: Every 6 hours
      - lead_high_score_assign: Daily
      - expense_anomaly_alert: Daily
      - employee_anniversary_review: Daily
      - project_delay_escalation: Every 4 hours
      - quality_issue_quarantine: Every 4 hours
      - customer_churn_retention: Daily
    """
    from app.core.ai.workflow_handlers import WORKFLOW_HANDLERS

    preset_intervals = {
        "low_stock_auto_po": 60,           # Every hour
        "invoice_due_reminder": 360,        # Every 6 hours
        "lead_high_score_assign": 1440,     # Daily
        "expense_anomaly_alert": 1440,      # Daily
        "employee_anniversary_review": 1440, # Daily
        "project_delay_escalation": 240,    # Every 4 hours
        "quality_issue_quarantine": 240,    # Every 4 hours
        "customer_churn_retention": 1440,   # Daily
    }

    scheduler = _get_scheduler()
    jobs = []

    for handler_name, interval in preset_intervals.items():
        if handler_name in WORKFLOW_HANDLERS:
            result = scheduler.add_job(
                handler_name=handler_name,
                interval_minutes=interval,
                enabled=True,
            )
            jobs.append(JobResponse(**result))

    return jobs
