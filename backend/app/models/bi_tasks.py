"""
BI Module — Celery Tasks
TOP WorX ERP System

Schedule (celery beat):
  Every 15 min: run_incremental_etl + evaluate_alerts + snapshot_kpis
  Every night 01:00: run_full_etl
  Every Monday 08:00: send_weekly_report

Setup:
    pip install celery redis
    celery -A app.tasks.bi_tasks worker --loglevel=info
    celery -A app.tasks.bi_tasks beat --loglevel=info

DECISION POINT ⚙️: Replace `get_sync_db_session` with your actual
sync DB session factory, or use celery-sqlalchemy with async support.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    from celery.schedules import crontab

    # INTEGRATION POINT: Update broker URL from config
    app = Celery(
        "bi_tasks",
        broker="redis://localhost:6379/0",
        backend="redis://localhost:6379/0",
    )

    app.conf.beat_schedule = {
        # Every 15 minutes: incremental ETL + alert evaluation
        "bi-incremental-etl": {
            "task": "app.tasks.bi_tasks.run_incremental_etl",
            "schedule": 900.0,   # 15 minutes
        },
        # Every 15 minutes: snapshot current KPIs
        "bi-kpi-snapshot": {
            "task": "app.tasks.bi_tasks.snapshot_kpis",
            "schedule": 900.0,
        },
        # Every night at 01:00
        "bi-full-etl-nightly": {
            "task": "app.tasks.bi_tasks.run_full_etl",
            "schedule": crontab(hour=1, minute=0),
        },
        # Every Monday at 08:00
        "bi-weekly-report": {
            "task": "app.tasks.bi_tasks.send_weekly_executive_report",
            "schedule": crontab(day_of_week="monday", hour=8, minute=0),
        },
    }

    app.conf.timezone = "Asia/Tehran"

    @app.task(bind=True, max_retries=3, default_retry_delay=60)
    def run_incremental_etl(self):
        """Incremental ETL: sync new JE lines to fact_transaction."""
        try:
            asyncio.run(_async_incremental_etl())
            logger.info("Incremental ETL completed")
        except Exception as exc:
            logger.error("Incremental ETL failed: %s", exc)
            raise self.retry(exc=exc)

    @app.task(bind=True, max_retries=1)
    def run_full_etl(self):
        """Full ETL: refresh all dimensions + full fact reload."""
        try:
            asyncio.run(_async_full_etl())
            logger.info("Full ETL completed")
        except Exception as exc:
            logger.error("Full ETL failed: %s", exc)
            raise self.retry(exc=exc)

    @app.task(bind=True, max_retries=3, default_retry_delay=30)
    def snapshot_kpis(self):
        """Save KPI snapshot and evaluate alert rules."""
        try:
            asyncio.run(_async_snapshot_kpis())
            logger.info("KPI snapshot + alert evaluation completed")
        except Exception as exc:
            logger.error("KPI snapshot failed: %s", exc)
            raise self.retry(exc=exc)

    @app.task
    def send_weekly_executive_report():
        """Generate and email weekly executive summary."""
        try:
            asyncio.run(_async_weekly_report())
        except Exception as exc:
            logger.error("Weekly report failed: %s", exc)

    @app.task
    def send_scheduled_report(template_id: int):
        """Send a scheduled user report."""
        asyncio.run(_async_scheduled_report(template_id))

except ImportError:
    logger.warning("Celery not installed — scheduled tasks disabled. pip install celery redis")

    # Stub classes for when Celery is not available
    class app:
        @staticmethod
        def task(*args, **kwargs):
            def decorator(fn):
                return fn
            return decorator


# ---------------------------------------------------------------------------
# Async implementations (called by tasks)
# ---------------------------------------------------------------------------
async def _get_db():
    """Get async DB session. INTEGRATION POINT: use your real session factory."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    import os
    from app.core.config import settings
    db_url = settings.DATABASE_URL
    engine = create_async_engine(db_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    return factory()


async def _async_incremental_etl():
    from app.services.etl_service import etl_service
    async with await _get_db() as db:
        run = await etl_service.run_incremental(db)
        await db.commit()
        logger.info("ETL run: %s rows, %.1fs", run.rows_inserted, run.duration_seconds)


async def _async_full_etl():
    from app.services.etl_service import etl_service
    async with await _get_db() as db:
        count = await etl_service.populate_dim_date(db)
        dims = await etl_service.sync_dimensions(db)
        await db.commit()
        logger.info("Full ETL: %d date rows, dims: %s", count, dims)


async def _async_snapshot_kpis():
    """Take KPI snapshot and fire alerts."""
    from app.services.kpi_service import kpi_service
    from app.services.dashboard_service import alert_service
    now = datetime.utcnow()
    year = 1403   # DECISION POINT ⚙️: compute from current date using jdatetime
    month = now.month

    async with await _get_db() as db:
        kpis = await kpi_service.get_all_kpis(db, year, month)
        period_label = f"{year}-{month:02d}"
        await kpi_service.save_snapshot(db, kpis, period_label)
        await alert_service.evaluate_all(db, year, month)
        await db.commit()


async def _async_weekly_report():
    """Generate weekly executive summary and email to recipients."""
    from app.services.dashboard_service import dashboard_service
    now = datetime.utcnow()
    year, month = 1403, now.month

    async with await _get_db() as db:
        data = await dashboard_service.ceo_dashboard(db, year, month)
        # TODO: format as HTML email and send via SMTP
        logger.info("Weekly executive report generated: %d KPIs", len(data.get("kpis", {})))


async def _async_scheduled_report(template_id: int):
    """Run a saved report template and email results."""
    from sqlalchemy import select
    from app.models.bi import ReportTemplate, ReportSchedule
    from app.services.dashboard_service import report_builder

    async with await _get_db() as db:
        schedule_r = await db.execute(
            select(ReportSchedule).where(ReportSchedule.template_id == template_id, ReportSchedule.is_active.is_(True))
        )
        schedules = schedule_r.scalars().all()
        for sched in schedules:
            tmpl = await db.get(ReportTemplate, template_id)
            if not tmpl:
                continue
            result = await report_builder.build_report(db, **tmpl.config)
            # TODO: format as Excel/PDF and email to sched.recipients
            sched.last_sent = datetime.utcnow()
            tmpl.last_run_at = datetime.utcnow()
            tmpl.run_count += 1
        await db.commit()
