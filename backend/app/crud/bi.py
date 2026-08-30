"""
BI Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bi import (
    AlertEvent, AlertRule, KPISnapshot, ReportTemplate,
)


class KPISnapshotCRUD:
    async def list_history(
        self,
        db: AsyncSession,
        kpi_name: str,
        *,
        days: int = 90,
    ) -> Sequence[KPISnapshot]:
        since = datetime.utcnow().replace(hour=0, minute=0, second=0) - timedelta(days=days)
        q = (
            select(KPISnapshot)
            .where(KPISnapshot.kpi_name == kpi_name, KPISnapshot.snapshot_at >= since)
            .order_by(KPISnapshot.snapshot_at.asc())
        )
        return (await db.execute(q)).scalars().all()


class AlertRuleCRUD:
    async def get(self, db: AsyncSession, rule_id: int) -> Optional[AlertRule]:
        result = await db.execute(
            select(AlertRule).where(AlertRule.id == rule_id)
        )
        return result.scalar_one_or_none()


class AlertEventCRUD:
    async def list(
        self,
        db: AsyncSession,
        *,
        unacknowledged_only: bool = False,
    ) -> Sequence[AlertEvent]:
        q = select(AlertEvent).order_by(AlertEvent.triggered_at.desc()).limit(100)
        if unacknowledged_only:
            q = q.where(AlertEvent.acknowledged.is_(False))
        return (await db.execute(q)).scalars().all()


class ReportTemplateCRUD:
    async def list_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Sequence[ReportTemplate]:
        q = (
            select(ReportTemplate)
            .where((ReportTemplate.is_public.is_(True)) | (ReportTemplate.created_by_id == user_id))
            .order_by(ReportTemplate.run_count.desc())
        )
        return (await db.execute(q)).scalars().all()


# Singletons
kpi_snapshot_crud = KPISnapshotCRUD()
alert_rule_crud = AlertRuleCRUD()
alert_event_crud = AlertEventCRUD()
report_template_crud = ReportTemplateCRUD()
