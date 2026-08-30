"""
HSE Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.hse import ChecklistStatus, IncidentSeverity, IncidentStatus

_ro = ConfigDict(from_attributes=True)


# ===========================================================================
# Incidents
# ===========================================================================
class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    severity: IncidentSeverity
    location: str = Field(..., min_length=1, max_length=200)
    department: Optional[str] = Field(None, max_length=100)
    injured_persons: int = Field(0, ge=0)
    witnesses: list[str] = Field(default_factory=list)
    immediate_actions: Optional[str] = None


class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    assigned_to_id: Optional[int] = None
    investigation_notes: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_actions: Optional[str] = None


class IncidentResponse(BaseModel):
    model_config = _ro
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


# ===========================================================================
# Checklists
# ===========================================================================
class ChecklistCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    location: str = Field(..., min_length=1, max_length=200)
    items: list[str] = Field(..., min_length=1, description="Checklist items to inspect")


class ChecklistItemResponse(BaseModel):
    model_config = _ro
    id: int
    text: str
    status: ChecklistStatus
    notes: Optional[str] = None
    photo_url: Optional[str] = None


class ChecklistResponse(BaseModel):
    model_config = _ro
    id: int
    title: str
    description: Optional[str] = None
    location: str
    status: ChecklistStatus
    items: list[ChecklistItemResponse] = []
    inspector_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None


class ChecklistItemUpdate(BaseModel):
    status: ChecklistStatus
    notes: Optional[str] = None
    photo_url: Optional[str] = None


# ===========================================================================
# Alerts
# ===========================================================================
class AlertCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    message: str = Field(..., min_length=1)
    severity: IncidentSeverity
    target_department: Optional[str] = Field(None, max_length=100)


class AlertResponse(BaseModel):
    model_config = _ro
    id: int
    title: str
    message: str
    severity: IncidentSeverity
    target_department: Optional[str] = None
    created_by_id: int
    created_at: datetime
