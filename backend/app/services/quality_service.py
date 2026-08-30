"""
Quality Module — Service Layer
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.quality import quality_defect_crud, quality_inspection_crud
from app.models.quality import DefectSeverity, DefectStatus, InspectionStatus


class QualityError(Exception):
    """Quality module business logic error."""
    pass


class QualityService:
    async def complete_inspection(
        self,
        db: AsyncSession,
        inspection_id: int,
        *,
        user_id: int,
    ):
        """Mark an inspection as completed and recalculate pass rate."""
        inspection = await quality_inspection_crud.get(db, inspection_id)
        if not inspection:
            raise QualityError("Inspection not found")
        if inspection.status == InspectionStatus.COMPLETED:
            raise QualityError("Inspection already completed")

        if inspection.quantity_inspected > 0:
            inspection.pass_rate = (
                inspection.quantity_passed / inspection.quantity_inspected * 100
            )
        inspection.status = InspectionStatus.COMPLETED
        inspection.completed_at = datetime.utcnow()
        await db.flush()
        return inspection

    async def resolve_defect(
        self,
        db: AsyncSession,
        defect_id: int,
        *,
        root_cause: Optional[str] = None,
        corrective_action: Optional[str] = None,
        user_id: int,
    ):
        """Resolve a quality defect."""
        defect = await quality_defect_crud.get(db, defect_id)
        if not defect:
            raise QualityError("Defect not found")
        if defect.status == DefectStatus.RESOLVED:
            raise QualityError("Defect already resolved")

        if root_cause:
            defect.root_cause = root_cause
        if corrective_action:
            defect.corrective_action = corrective_action
        defect.status = DefectStatus.RESOLVED
        defect.resolved_at = datetime.utcnow()
        await db.flush()
        return defect


quality_service = QualityService()
