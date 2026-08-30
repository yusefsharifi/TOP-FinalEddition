"""
Projects Module — FastAPI Router
TOP WorX ERP System

INTEGRATION POINT: Register in api.py:
    from app.api.v1.endpoints.projects import router as projects_router
    api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.deps import DBDep, CurrentUser
from app.core.cache import cache
from app.models.projects import (
    Project, ProjectMilestone, ProjectResource, ProjectRisk,
    ProjectStatus, ProjectPriority, MilestoneStatus, RiskStatus, ResourceType,
)
from app.schemas.projects import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    ResourceCreate, ResourceUpdate, ResourceResponse,
    RiskCreate, RiskUpdate, RiskResponse,
    ProjectDashboardResponse,
)

router = APIRouter()


# ── PROJECTS CRUD ────────────────────────────────────────────────────────────

@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    db: DBDep,
    current_user: CurrentUser,
    project_status: Optional[ProjectStatus] = Query(None, alias="status"),
    priority: Optional[ProjectPriority] = None,
    manager_id: Optional[int] = None,
    search: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[ProjectResponse]:
    """List projects with optional filtering."""
    q = select(Project).order_by(Project.created_at.desc())
    if project_status:
        q = q.where(Project.status == project_status)
    if priority:
        q = q.where(Project.priority == priority)
    if manager_id:
        q = q.where(Project.manager_id == manager_id)
    if search:
        term = f"%{search}%"
        q = q.where(
            (Project.name.ilike(term)) | (Project.code.ilike(term))
        )
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [ProjectResponse.model_validate(r) for r in rows]


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> ProjectResponse:
    """Create a new project."""
    # Check code uniqueness
    existing = await db.execute(select(Project).where(Project.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(409, f"Project code '{data.code}' already exists")
    
    project = Project(
        **data.model_dump(),
        created_by_id=current_user.id,
        updated_by_id=current_user.id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> ProjectResponse:
    """Get project details."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> ProjectResponse:
    """Update project fields."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    project.updated_by_id = current_user.id
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    """Delete a project (only if PLANNING or CANCELLED)."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if project.status not in (ProjectStatus.PLANNING, ProjectStatus.CANCELLED):
        raise HTTPException(409, "Cannot delete a project that is active or completed")
    await db.delete(project)
    await db.commit()


# ── MILESTONES ───────────────────────────────────────────────────────────────

@router.get("/{project_id}/milestones", response_model=list[MilestoneResponse])
async def list_milestones(
    project_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> list[MilestoneResponse]:
    """List milestones for a project."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    q = select(ProjectMilestone).where(
        ProjectMilestone.project_id == project_id
    ).order_by(ProjectMilestone.due_date)
    rows = (await db.execute(q)).scalars().all()
    return [MilestoneResponse.model_validate(r) for r in rows]


@router.post("/{project_id}/milestones", response_model=MilestoneResponse, status_code=201)
async def create_milestone(
    project_id: int,
    data: MilestoneCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> MilestoneResponse:
    """Create a milestone for a project."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    milestone = ProjectMilestone(
        project_id=project_id,
        **data.model_dump(),
        created_by_id=current_user.id,
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)
    return MilestoneResponse.model_validate(milestone)


@router.patch("/{project_id}/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    project_id: int,
    milestone_id: int,
    data: MilestoneUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> MilestoneResponse:
    """Update a milestone."""
    milestone = await db.get(ProjectMilestone, milestone_id)
    if not milestone or milestone.project_id != project_id:
        raise HTTPException(404, "Milestone not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(milestone, field, value)
    
    if data.status == MilestoneStatus.COMPLETED and not milestone.completed_at:
        milestone.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(milestone)
    return MilestoneResponse.model_validate(milestone)


# ── RESOURCES ────────────────────────────────────────────────────────────────

@router.get("/{project_id}/resources", response_model=list[ResourceResponse])
async def list_resources(
    project_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> list[ResourceResponse]:
    """List resources for a project."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    q = select(ProjectResource).where(
        ProjectResource.project_id == project_id
    ).order_by(ProjectResource.name)
    rows = (await db.execute(q)).scalars().all()
    return [ResourceResponse.model_validate(r) for r in rows]


@router.post("/{project_id}/resources", response_model=ResourceResponse, status_code=201)
async def create_resource(
    project_id: int,
    data: ResourceCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> ResourceResponse:
    """Add a resource to a project."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    resource = ProjectResource(
        project_id=project_id,
        **data.model_dump(),
        created_by_id=current_user.id,
    )
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return ResourceResponse.model_validate(resource)


@router.patch("/{project_id}/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    project_id: int,
    resource_id: int,
    data: ResourceUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> ResourceResponse:
    """Update a resource."""
    resource = await db.get(ProjectResource, resource_id)
    if not resource or resource.project_id != project_id:
        raise HTTPException(404, "Resource not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    
    await db.commit()
    await db.refresh(resource)
    return ResourceResponse.model_validate(resource)


@router.delete("/{project_id}/resources/{resource_id}", status_code=204)
async def delete_resource(
    project_id: int,
    resource_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    """Delete a resource."""
    resource = await db.get(ProjectResource, resource_id)
    if not resource or resource.project_id != project_id:
        raise HTTPException(404, "Resource not found")
    await db.delete(resource)
    await db.commit()


# ── RISKS ────────────────────────────────────────────────────────────────────

@router.get("/{project_id}/risks", response_model=list[RiskResponse])
async def list_risks(
    project_id: int,
    db: DBDep,
    current_user: CurrentUser,
    risk_status: Optional[RiskStatus] = Query(None, alias="status"),
) -> list[RiskResponse]:
    """List risks for a project."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    q = select(ProjectRisk).where(ProjectRisk.project_id == project_id)
    if risk_status:
        q = q.where(ProjectRisk.status == risk_status)
    q = q.order_by(ProjectRisk.created_at.desc())
    rows = (await db.execute(q)).scalars().all()
    return [RiskResponse.model_validate(r) for r in rows]


@router.post("/{project_id}/risks", response_model=RiskResponse, status_code=201)
async def create_risk(
    project_id: int,
    data: RiskCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> RiskResponse:
    """Add a risk to a project."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    risk = ProjectRisk(
        project_id=project_id,
        **data.model_dump(),
        created_by_id=current_user.id,
    )
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    return RiskResponse.model_validate(risk)


@router.patch("/{project_id}/risks/{risk_id}", response_model=RiskResponse)
async def update_risk(
    project_id: int,
    risk_id: int,
    data: RiskUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> RiskResponse:
    """Update a risk."""
    risk = await db.get(ProjectRisk, risk_id)
    if not risk or risk.project_id != project_id:
        raise HTTPException(404, "Risk not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(risk, field, value)
    
    await db.commit()
    await db.refresh(risk)
    return RiskResponse.model_validate(risk)


# ── DASHBOARD ────────────────────────────────────────────────────────────────

@router.get("/dashboard/stats")
async def project_stats(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Project dashboard statistics (cached for 2 min)."""
    cache_key = "projects:dashboard:stats"
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Consolidated queries
    total = (await db.execute(select(func.count(Project.id)))).scalar() or 0
    
    # Status counts
    status_counts = (await db.execute(
        select(Project.status, func.count(Project.id).label("cnt"))
        .group_by(Project.status)
    )).all()
    by_status = {row.status.value: row.cnt for row in status_counts}
    
    # Priority counts
    priority_counts = (await db.execute(
        select(Project.priority, func.count(Project.id).label("cnt"))
        .group_by(Project.priority)
    )).all()
    by_priority = {row.priority.value: row.cnt for row in priority_counts}
    
    # Budget totals
    budget_totals = (await db.execute(
        select(
            func.coalesce(func.sum(Project.budget), Decimal("0")).label("total_budget"),
            func.coalesce(func.sum(Project.actual_cost), Decimal("0")).label("total_actual"),
        )
    )).one()
    
    # Recent projects
    recent_q = select(Project).order_by(Project.created_at.desc()).limit(5)
    recent_rows = (await db.execute(recent_q)).scalars().all()
    
    result = {
        "total_projects": total,
        "active_projects": by_status.get("active", 0),
        "completed_projects": by_status.get("completed", 0),
        "total_budget": float(budget_totals.total_budget),
        "total_actual_cost": float(budget_totals.total_actual),
        "projects_by_status": by_status,
        "projects_by_priority": by_priority,
        "recent_projects": [ProjectResponse.model_validate(p).model_dump() for p in recent_rows],
    }
    await cache.set(cache_key, result, ttl=120)  # 2 min cache
    return result
