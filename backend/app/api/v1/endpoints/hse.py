"""
HSE Module — Health, Safety & Environment
TOP WorX ERP System

Manages safety incidents, inspections, checklists, and alerts.
Uses SQLAlchemy models from app.models.hse.
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import DBDep, CurrentUser
from app.core.cache import cache, invalidate_pattern
from app.models.hse import (
    HSEAlert, HSEChecklist, HSEChecklistItem, HSEIncident,
    ChecklistStatus, IncidentSeverity, IncidentStatus,
)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: IncidentSeverity
    location: str
    department: Optional[str] = None
    injured_persons: int = 0
    witnesses: list[str] = Field(default_factory=list)
    immediate_actions: Optional[str] = None


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    location: str
    department: Optional[str] = None
    injured_persons: int
    witnesses: Optional[list] = None
    immediate_actions: Optional[str] = None
    reported_by_id: int
    assigned_to_id: Optional[int] = None
    investigation_notes: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_actions: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    assigned_to_id: Optional[int] = None
    investigation_notes: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_actions: Optional[str] = None


class ChecklistCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    items: list[str] = Field(..., min_length=1, description="Checklist items to inspect")


class ChecklistItemResponse(BaseModel):
    id: int
    text: str
    status: ChecklistStatus
    notes: Optional[str] = None
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class ChecklistResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    location: str
    status: ChecklistStatus
    items: list[ChecklistItemResponse]
    inspector_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChecklistItemUpdate(BaseModel):
    status: ChecklistStatus
    notes: Optional[str] = None
    photo_url: Optional[str] = None


class AlertCreate(BaseModel):
    title: str
    message: str
    severity: IncidentSeverity
    target_department: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    severity: IncidentSeverity
    target_department: Optional[str] = None
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── INCIDENTS ────────────────────────────────────────────────────────────────

@router.get("/incidents", response_model=list[IncidentResponse])
async def list_incidents(
    db: DBDep,
    current_user: CurrentUser,
    severity: Optional[IncidentSeverity] = None,
    incident_status: Optional[IncidentStatus] = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[IncidentResponse]:
    """List all safety incidents with optional filtering."""
    q = select(HSEIncident).order_by(HSEIncident.created_at.desc())
    if severity:
        q = q.where(HSEIncident.severity == severity)
    if incident_status:
        q = q.where(HSEIncident.status == incident_status)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [IncidentResponse.model_validate(r) for r in rows]


@router.post("/incidents", response_model=IncidentResponse, status_code=201)
async def create_incident(
    data: IncidentCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> IncidentResponse:
    """Report a new safety incident."""
    incident = HSEIncident(
        title=data.title,
        description=data.description,
        severity=data.severity,
        status=IncidentStatus.OPEN,
        location=data.location,
        department=data.department,
        injured_persons=data.injured_persons,
        witnesses=data.witnesses,
        immediate_actions=data.immediate_actions,
        reported_by_id=current_user.id,
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return IncidentResponse.model_validate(incident)


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> IncidentResponse:
    """Get incident details."""
    incident = await db.get(HSEIncident, incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")
    return IncidentResponse.model_validate(incident)


@router.patch("/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> IncidentResponse:
    """Update an incident (status, assignment, investigation notes)."""
    incident = await db.get(HSEIncident, incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)

    if data.status == IncidentStatus.RESOLVED:
        incident.resolved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(incident)
    return IncidentResponse.model_validate(incident)


@router.get("/incidents/stats/summary")
async def incident_stats(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Incident statistics summary."""
    # Consolidated single query with GROUP BY for status counts
    from sqlalchemy import case
    status_counts = (await db.execute(
        select(
            HSEIncident.status,
            func.count(HSEIncident.id).label("cnt"),
        )
        .group_by(HSEIncident.status)
    )).all()
    by_status = {row.status.value: row.cnt for row in status_counts}

    # Consolidated single query for severity counts
    severity_counts = (await db.execute(
        select(
            HSEIncident.severity,
            func.count(HSEIncident.id).label("cnt"),
        )
        .group_by(HSEIncident.severity)
    )).all()
    by_severity = {row.severity.value: row.cnt for row in severity_counts}

    injured = (await db.execute(select(func.coalesce(func.sum(HSEIncident.injured_persons), 0)))).scalar() or 0

    return {
        "total": sum(by_status.values()),
        "open": by_status.get("open", 0),
        "under_investigation": by_status.get("under_investigation", 0),
        "resolved": by_status.get("resolved", 0),
        "by_severity": by_severity,
        "total_injured": injured,
    }


# ── SAFETY CHECKLISTS ────────────────────────────────────────────────────────

@router.get("/checklists", response_model=list[ChecklistResponse])
async def list_checklists(
    db: DBDep,
    current_user: CurrentUser,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[ChecklistResponse]:
    """List safety checklists."""
    q = (
        select(HSEChecklist)
        .options(selectinload(HSEChecklist.items))
        .order_by(HSEChecklist.created_at.desc())
    )
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [ChecklistResponse.model_validate(c) for c in rows]


@router.post("/checklists", response_model=ChecklistResponse, status_code=201)
async def create_checklist(
    data: ChecklistCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> ChecklistResponse:
    """Create a new safety inspection checklist."""
    checklist = HSEChecklist(
        title=data.title,
        description=data.description,
        location=data.location,
        status=ChecklistStatus.PENDING,
        inspector_id=current_user.id,
    )
    db.add(checklist)
    await db.flush()  # get the ID

    items = []
    for idx, item_text in enumerate(data.items):
        item = HSEChecklistItem(
            checklist_id=checklist.id,
            text=item_text,
            status=ChecklistStatus.PENDING,
        )
        db.add(item)
        items.append(item)

    await db.commit()
    await db.refresh(checklist)

    resp = ChecklistResponse.model_validate(checklist)
    resp.items = [ChecklistItemResponse.model_validate(i) for i in items]
    return resp


@router.get("/checklists/{checklist_id}", response_model=ChecklistResponse)
async def get_checklist(
    checklist_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> ChecklistResponse:
    """Get checklist details with items."""
    result = await db.execute(
        select(HSEChecklist)
        .options(selectinload(HSEChecklist.items))
        .where(HSEChecklist.id == checklist_id)
    )
    checklist = result.scalar_one_or_none()
    if not checklist:
        raise HTTPException(404, "Checklist not found")
    return ChecklistResponse.model_validate(checklist)


@router.put("/checklists/{checklist_id}/items/{item_id}")
async def update_checklist_item(
    checklist_id: int,
    item_id: int,
    data: ChecklistItemUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Update a single checklist item (mark pass/fail with notes)."""
    item = await db.get(HSEChecklistItem, item_id)
    if not item or item.checklist_id != checklist_id:
        raise HTTPException(404, "Item not found in checklist")

    item.status = data.status
    item.notes = data.notes
    item.photo_url = data.photo_url

    # Recalculate overall checklist status using relationship
    checklist = await db.get(HSEChecklist, checklist_id)
    result = await db.execute(
        select(HSEChecklist)
        .options(selectinload(HSEChecklist.items))
        .where(HSEChecklist.id == checklist_id)
    )
    checklist = result.scalar_one()
    statuses = [i.status for i in checklist.items]

    if all(s == ChecklistStatus.PASSED for s in statuses):
        checklist.status = ChecklistStatus.PASSED
        checklist.completed_at = datetime.utcnow()
    elif any(s == ChecklistStatus.FAILED for s in statuses):
        checklist.status = ChecklistStatus.FAILED
        checklist.completed_at = datetime.utcnow()
    else:
        checklist.status = ChecklistStatus.IN_PROGRESS

    await db.commit()
    return {"status": "updated", "item_id": item_id}


# ── ALERTS ───────────────────────────────────────────────────────────────────

@router.get("/alerts", response_model=list[AlertResponse])
async def list_alerts(
    db: DBDep,
    current_user: CurrentUser,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[AlertResponse]:
    """List safety alerts."""
    q = select(HSEAlert).order_by(HSEAlert.created_at.desc())
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [AlertResponse.model_validate(r) for r in rows]


@router.post("/alerts", response_model=AlertResponse, status_code=201)
async def create_alert(
    data: AlertCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> AlertResponse:
    """Create a safety alert."""
    alert = HSEAlert(
        title=data.title,
        message=data.message,
        severity=data.severity,
        target_department=data.target_department,
        created_by_id=current_user.id,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)


@router.get("/dashboard")
async def hse_dashboard(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """HSE dashboard KPIs (cached for 2 min)."""
    cache_key = "hse:dashboard:kpis"
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    open_incidents = (await db.execute(
        select(func.count(HSEIncident.id)).where(HSEIncident.status == IncidentStatus.OPEN)
    )).scalar() or 0
    pending_checklists = (await db.execute(
        select(func.count(HSEChecklist.id)).where(HSEChecklist.status == ChecklistStatus.PENDING)
    )).scalar() or 0
    failed_checklists = (await db.execute(
        select(func.count(HSEChecklist.id)).where(HSEChecklist.status == ChecklistStatus.FAILED)
    )).scalar() or 0
    alert_count = (await db.execute(select(func.count(HSEAlert.id)))).scalar() or 0

    result = {
        "open_incidents": open_incidents,
        "pending_checklists": pending_checklists,
        "failed_checklists": failed_checklists,
        "active_alerts": alert_count,
    }
    await cache.set(cache_key, result, ttl=120)  # 2 min cache
    return result
