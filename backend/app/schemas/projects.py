"""
Projects Module — Pydantic Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.projects import ProjectStatus, ProjectPriority, MilestoneStatus, RiskStatus, ResourceType


# ── Project Schemas ──────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=300)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    priority: ProjectPriority = ProjectPriority.MEDIUM
    start_date: date
    end_date: date
    budget: Decimal = Decimal("0")
    manager_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    progress: Optional[Decimal] = None
    manager_id: Optional[int] = None


class ProjectResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    status: ProjectStatus
    priority: ProjectPriority
    start_date: date
    end_date: date
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    budget: Decimal
    actual_cost: Decimal
    progress: Decimal
    manager_id: Optional[int] = None
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Milestone Schemas ────────────────────────────────────────────────────────

class MilestoneCreate(BaseModel):
    name: str = Field(..., max_length=300)
    description: Optional[str] = None
    due_date: date


class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[MilestoneStatus] = None


class MilestoneResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    due_date: date
    status: MilestoneStatus
    completed_at: Optional[datetime] = None
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Resource Schemas ─────────────────────────────────────────────────────────

class ResourceCreate(BaseModel):
    name: str = Field(..., max_length=200)
    type: ResourceType
    quantity: Decimal = Decimal("1")
    unit_cost: Decimal = Decimal("0")
    total_cost: Decimal = Decimal("0")
    availability: Decimal = Decimal("100")


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ResourceType] = None
    quantity: Optional[Decimal] = None
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    availability: Optional[Decimal] = None


class ResourceResponse(BaseModel):
    id: int
    project_id: int
    name: str
    type: ResourceType
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    availability: Decimal
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Risk Schemas ─────────────────────────────────────────────────────────────

class RiskCreate(BaseModel):
    name: str = Field(..., max_length=300)
    description: Optional[str] = None
    probability: Decimal = Decimal("50")
    impact: Decimal = Decimal("50")
    mitigation_plan: Optional[str] = None


class RiskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    probability: Optional[Decimal] = None
    impact: Optional[Decimal] = None
    mitigation_plan: Optional[str] = None
    status: Optional[RiskStatus] = None


class RiskResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    probability: Decimal
    impact: Decimal
    mitigation_plan: Optional[str] = None
    status: RiskStatus
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard ────────────────────────────────────────────────────────────────

class ProjectDashboardResponse(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    total_budget: Decimal
    total_actual_cost: Decimal
    projects_by_status: dict
    projects_by_priority: dict
    recent_projects: list[ProjectResponse]
