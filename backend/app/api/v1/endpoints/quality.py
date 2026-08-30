"""
Quality Module — FastAPI Router
TOP WorX ERP System

Manages quality inspections, defect tracking, and compliance.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.deps import DBDep, CurrentUser
from app.core.cache import cache
from app.crud.quality import quality_defect_crud, quality_inspection_crud
from app.models.quality import (
    DefectSeverity, DefectStatus, InspectionStatus,
    QualityDefect, QualityInspection,
)
from app.schemas.quality import (
    QualityDashboardResponse, QualityDefectCreate, QualityDefectResponse,
    QualityDefectUpdate, QualityInspectionCreate, QualityInspectionResponse,
    QualityInspectionUpdate,
)
from app.services.quality_service import quality_service, QualityError

router = APIRouter()


def _err(exc: QualityError) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


# ===========================================================================
# INSPECTIONS
# ===========================================================================

@router.get("/inspections", response_model=list[QualityInspectionResponse])
async def list_inspections(
    db: DBDep,
    current_user: CurrentUser,
    inspection_status: Optional[InspectionStatus] = Query(None, alias="status"),
    inspection_type: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[QualityInspectionResponse]:
    """List quality inspections."""
    _, rows = await quality_inspection_crud.list(
        db,
        status=inspection_status.value if inspection_status else None,
        inspection_type=inspection_type,
        offset=offset,
        limit=limit,
    )
    return [QualityInspectionResponse.model_validate(r) for r in rows]


@router.post("/inspections", response_model=QualityInspectionResponse, status_code=201)
async def create_inspection(
    data: QualityInspectionCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> QualityInspectionResponse:
    """Create a new quality inspection."""
    inspection = await quality_inspection_crud.create(
        db,
        name=data.name,
        description=data.description,
        inspection_type=data.inspection_type,
        item_id=data.item_id,
        batch_number=data.batch_number,
        supplier_id=data.supplier_id,
        quantity_inspected=data.quantity_inspected,
        quantity_passed=data.quantity_passed,
        quantity_failed=data.quantity_failed,
        notes=data.notes,
        inspector_id=current_user.id,
    )
    await db.commit()
    return QualityInspectionResponse.model_validate(inspection)


@router.get("/inspections/{inspection_id}", response_model=QualityInspectionResponse)
async def get_inspection(
    inspection_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> QualityInspectionResponse:
    """Get inspection details."""
    inspection = await quality_inspection_crud.get(db, inspection_id)
    if not inspection:
        raise HTTPException(404, "Inspection not found")
    return QualityInspectionResponse.model_validate(inspection)


@router.patch("/inspections/{inspection_id}", response_model=QualityInspectionResponse)
async def update_inspection(
    inspection_id: int,
    data: QualityInspectionUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> QualityInspectionResponse:
    """Update an inspection."""
    inspection = await quality_inspection_crud.get(db, inspection_id)
    if not inspection:
        raise HTTPException(404, "Inspection not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(inspection, field, value)

    # Recalculate pass rate
    if inspection.quantity_inspected > 0:
        inspection.pass_rate = (
            inspection.quantity_passed / inspection.quantity_inspected * 100
        )

    await db.commit()
    await db.refresh(inspection)
    return QualityInspectionResponse.model_validate(inspection)


@router.post("/inspections/{inspection_id}/complete", response_model=QualityInspectionResponse)
async def complete_inspection(
    inspection_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> QualityInspectionResponse:
    """Mark an inspection as completed."""
    try:
        inspection = await quality_service.complete_inspection(
            db, inspection_id, user_id=current_user.id,
        )
    except QualityError as exc:
        raise _err(exc)
    await db.commit()
    await db.refresh(inspection)
    return QualityInspectionResponse.model_validate(inspection)


# ===========================================================================
# DEFECTS
# ===========================================================================

@router.get("/inspections/{inspection_id}/defects", response_model=list[QualityDefectResponse])
async def list_defects(
    inspection_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> list[QualityDefectResponse]:
    """List defects for an inspection."""
    defects = await quality_defect_crud.list_by_inspection(db, inspection_id)
    return [QualityDefectResponse.model_validate(d) for d in defects]


@router.post("/defects", response_model=QualityDefectResponse, status_code=201)
async def create_defect(
    data: QualityDefectCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> QualityDefectResponse:
    """Log a quality defect."""
    inspection = await quality_inspection_crud.get(db, data.inspection_id)
    if not inspection:
        raise HTTPException(404, "Inspection not found")

    defect = QualityDefect(
        inspection_id=data.inspection_id,
        defect_type=data.defect_type,
        severity=data.severity,
        description=data.description,
        quantity_affected=data.quantity_affected,
        root_cause=data.root_cause,
        corrective_action=data.corrective_action,
    )
    db.add(defect)
    await db.commit()
    await db.refresh(defect)
    return QualityDefectResponse.model_validate(defect)


@router.patch("/defects/{defect_id}", response_model=QualityDefectResponse)
async def update_defect(
    defect_id: int,
    data: QualityDefectUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> QualityDefectResponse:
    """Update a defect."""
    defect = await quality_defect_crud.get(db, defect_id)
    if not defect:
        raise HTTPException(404, "Defect not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(defect, field, value)

    if data.status == "resolved" and not defect.resolved_at:
        defect.resolved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(defect)
    return QualityDefectResponse.model_validate(defect)


@router.post("/defects/{defect_id}/resolve", response_model=QualityDefectResponse)
async def resolve_defect(
    defect_id: int,
    data: QualityDefectUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> QualityDefectResponse:
    """Resolve a quality defect."""
    try:
        defect = await quality_service.resolve_defect(
            db, defect_id,
            root_cause=data.root_cause,
            corrective_action=data.corrective_action,
            user_id=current_user.id,
        )
    except QualityError as exc:
        raise _err(exc)
    await db.commit()
    await db.refresh(defect)
    return QualityDefectResponse.model_validate(defect)


# ===========================================================================
# DASHBOARD
# ===========================================================================

@router.get("/dashboard", response_model=QualityDashboardResponse)
async def quality_dashboard(
    db: DBDep,
    current_user: CurrentUser,
) -> QualityDashboardResponse:
    """Quality module dashboard KPIs (cached for 2 min)."""
    cache_key = "quality:dashboard:kpis"
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        return QualityDashboardResponse(**cached_result)

    stats = await quality_inspection_crud.stats(db)
    # Convert recent_inspections dicts to response models
    recent = [QualityInspectionResponse(**i) for i in stats.pop("recent_inspections", [])]

    result = QualityDashboardResponse(
        total_inspections=stats["total_inspections"],
        pass_rate=stats["pass_rate"],
        total_defects=stats["total_defects"],
        open_defects=stats["open_defects"],
        defects_by_severity=stats["defects_by_severity"],
        recent_inspections=recent,
    )
    await cache.set(cache_key, result.model_dump(mode="json"), ttl=120)
    return result
