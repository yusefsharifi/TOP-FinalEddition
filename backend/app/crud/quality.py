"""
Quality Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

import random
import string
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quality import QualityDefect, QualityInspection


def _rand(n: int = 5) -> str:
    return "".join(random.choices(string.digits, k=n))


class QualityInspectionCRUD:
    async def get(self, db: AsyncSession, inspection_id: int) -> Optional[QualityInspection]:
        result = await db.execute(
            select(QualityInspection).where(QualityInspection.id == inspection_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        status: Optional[str] = None,
        inspection_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[QualityInspection]]:
        q = select(QualityInspection).order_by(QualityInspection.created_at.desc())
        if status:
            q = q.where(QualityInspection.status == status)
        if inspection_type:
            q = q.where(QualityInspection.inspection_type == inspection_type)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self,
        db: AsyncSession,
        *,
        name: str,
        description: Optional[str] = None,
        inspection_type: str = "incoming",
        item_id: Optional[int] = None,
        batch_number: Optional[str] = None,
        supplier_id: Optional[int] = None,
        quantity_inspected: int = 0,
        quantity_passed: int = 0,
        quantity_failed: int = 0,
        notes: Optional[str] = None,
        inspector_id: int,
    ) -> QualityInspection:
        year = 1403
        inspection_number = f"QC-{year}-{_rand(5)}"
        pass_rate = (quantity_passed / quantity_inspected * 100) if quantity_inspected > 0 else 0.0

        obj = QualityInspection(
            inspection_number=inspection_number,
            name=name,
            description=description,
            inspection_type=inspection_type,
            status="in_progress" if quantity_inspected == 0 else "completed",
            item_id=item_id,
            batch_number=batch_number,
            supplier_id=supplier_id,
            quantity_inspected=quantity_inspected,
            quantity_passed=quantity_passed,
            quantity_failed=quantity_failed,
            pass_rate=pass_rate,
            inspector_id=inspector_id,
            notes=notes,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def stats(self, db: AsyncSession) -> dict:
        total = (await db.execute(
            select(func.count(QualityInspection.id))
        )).scalar() or 0

        avg_pass_rate = (await db.execute(
            select(func.coalesce(func.avg(QualityInspection.pass_rate), 0))
            .where(QualityInspection.status == "completed")
        )).scalar() or 0

        defect_total = (await db.execute(
            select(func.count(QualityDefect.id))
        )).scalar() or 0

        open_defects = (await db.execute(
            select(func.count(QualityDefect.id))
            .where(QualityDefect.status != "resolved")
        )).scalar() or 0

        severity_counts = (await db.execute(
            select(QualityDefect.severity, func.count(QualityDefect.id).label("cnt"))
            .group_by(QualityDefect.severity)
        )).all()
        by_severity = {row.severity: row.cnt for row in severity_counts}

        recent = (await db.execute(
            select(QualityInspection)
            .order_by(QualityInspection.created_at.desc())
            .limit(5)
        )).scalars().all()

        return {
            "total_inspections": total,
            "pass_rate": round(float(avg_pass_rate), 1),
            "total_defects": defect_total,
            "open_defects": open_defects,
            "defects_by_severity": by_severity,
            "recent_inspections": [i.__dict__ for i in recent],
        }


class QualityDefectCRUD:
    async def get(self, db: AsyncSession, defect_id: int) -> Optional[QualityDefect]:
        result = await db.execute(
            select(QualityDefect).where(QualityDefect.id == defect_id)
        )
        return result.scalar_one_or_none()

    async def list_by_inspection(
        self,
        db: AsyncSession,
        inspection_id: int,
    ) -> Sequence[QualityDefect]:
        q = (
            select(QualityDefect)
            .where(QualityDefect.inspection_id == inspection_id)
            .order_by(QualityDefect.created_at.desc())
        )
        return (await db.execute(q)).scalars().all()


# Singletons
quality_inspection_crud = QualityInspectionCRUD()
quality_defect_crud = QualityDefectCRUD()
