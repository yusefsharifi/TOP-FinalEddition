"""
HSE Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.hse import (
    ChecklistStatus, HSEAlert, HSEChecklist, HSEChecklistItem,
    HSEIncident, IncidentSeverity, IncidentStatus,
)


class IncidentCRUD:
    async def get(self, db: AsyncSession, incident_id: int) -> Optional[HSEIncident]:
        result = await db.execute(
            select(HSEIncident).where(HSEIncident.id == incident_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        severity: Optional[IncidentSeverity] = None,
        status: Optional[IncidentStatus] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[HSEIncident]]:
        q = select(HSEIncident).order_by(HSEIncident.created_at.desc())
        if severity:
            q = q.where(HSEIncident.severity == severity)
        if status:
            q = q.where(HSEIncident.status == status)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def stats(self, db: AsyncSession) -> dict:
        from sqlalchemy import case
        status_counts = (await db.execute(
            select(HSEIncident.status, func.count(HSEIncident.id).label("cnt"))
            .group_by(HSEIncident.status)
        )).all()
        by_status = {row.status.value: row.cnt for row in status_counts}

        severity_counts = (await db.execute(
            select(HSEIncident.severity, func.count(HSEIncident.id).label("cnt"))
            .group_by(HSEIncident.severity)
        )).all()
        by_severity = {row.severity.value: row.cnt for row in severity_counts}

        injured = (await db.execute(
            select(func.coalesce(func.sum(HSEIncident.injured_persons), 0))
        )).scalar() or 0

        return {
            "total": sum(by_status.values()),
            "open": by_status.get("open", 0),
            "under_investigation": by_status.get("under_investigation", 0),
            "resolved": by_status.get("resolved", 0),
            "by_severity": by_severity,
            "total_injured": injured,
        }


class ChecklistCRUD:
    async def get(self, db: AsyncSession, checklist_id: int) -> Optional[HSEChecklist]:
        result = await db.execute(
            select(HSEChecklist)
            .options(selectinload(HSEChecklist.items))
            .where(HSEChecklist.id == checklist_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[HSEChecklist]]:
        q = (
            select(HSEChecklist)
            .options(selectinload(HSEChecklist.items))
            .order_by(HSEChecklist.created_at.desc())
        )
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows


class AlertCRUD:
    async def list(
        self,
        db: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[HSEAlert]]:
        q = select(HSEAlert).order_by(HSEAlert.created_at.desc())
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows


# Singletons
incident_crud = IncidentCRUD()
checklist_crud = ChecklistCRUD()
alert_crud = AlertCRUD()
