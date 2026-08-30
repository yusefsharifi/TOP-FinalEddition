"""
Projects Module — Service Layer
TOP WorX ERP System

Business logic for project management.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import (
    Project, ProjectMilestone, ProjectResource, ProjectRisk,
    ProjectStatus, MilestoneStatus, RiskStatus,
)


class ProjectsError(Exception):
    """Projects business logic error."""
    pass


class ProjectsService:
    async def create_project(
        self,
        db: AsyncSession,
        *,
        code: str,
        name: str,
        description: Optional[str] = None,
        status: ProjectStatus = ProjectStatus.PLANNING,
        priority: str = "medium",
        start_date: date,
        end_date: date,
        budget: Decimal = Decimal("0"),
        manager_id: Optional[int] = None,
        user_id: int,
    ) -> Project:
        """Create a new project with validation."""
        # Check code uniqueness
        existing = await db.execute(select(Project).where(Project.code == code))
        if existing.scalar_one_or_none():
            raise ProjectsError(f"Project code '{code}' already exists")
        
        # Validate dates
        if end_date <= start_date:
            raise ProjectsError("End date must be after start date")
        
        project = Project(
            code=code,
            name=name,
            description=description,
            status=status,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            manager_id=manager_id,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(project)
        await db.flush()
        await db.refresh(project)
        return project

    async def update_project_status(
        self,
        db: AsyncSession,
        project_id: int,
        *,
        new_status: ProjectStatus,
        user_id: int,
    ) -> Project:
        """Update project status with workflow validation."""
        project = await db.get(Project, project_id)
        if not project:
            raise ProjectsError("Project not found")
        
        # Validate status transitions
        valid_transitions = {
            ProjectStatus.PLANNING: [ProjectStatus.ACTIVE, ProjectStatus.CANCELLED],
            ProjectStatus.ACTIVE: [ProjectStatus.ON_HOLD, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED],
            ProjectStatus.ON_HOLD: [ProjectStatus.ACTIVE, ProjectStatus.CANCELLED],
            ProjectStatus.COMPLETED: [],
            ProjectStatus.CANCELLED: [],
        }
        
        if new_status not in valid_transitions.get(project.status, []):
            raise ProjectsError(
                f"Cannot transition from {project.status.value} to {new_status.value}"
            )
        
        # Track actual dates
        if new_status == ProjectStatus.ACTIVE and not project.actual_start_date:
            project.actual_start_date = date.today()
        elif new_status in (ProjectStatus.COMPLETED, ProjectStatus.CANCELLED):
            project.actual_end_date = date.today()
        
        project.status = new_status
        project.updated_by_id = user_id
        await db.flush()
        await db.refresh(project)
        return project

    async def complete_milestone(
        self,
        db: AsyncSession,
        milestone_id: int,
        *,
        user_id: int,
    ) -> ProjectMilestone:
        """Mark a milestone as completed."""
        milestone = await db.get(ProjectMilestone, milestone_id)
        if not milestone:
            raise ProjectsError("Milestone not found")
        
        if milestone.status == MilestoneStatus.COMPLETED:
            raise ProjectsError("Milestone already completed")
        
        milestone.status = MilestoneStatus.COMPLETED
        milestone.completed_at = datetime.utcnow()
        await db.flush()
        await db.refresh(milestone)
        
        # Update project progress
        await self._recalculate_project_progress(db, milestone.project_id)
        
        return milestone

    async def _recalculate_project_progress(
        self,
        db: AsyncSession,
        project_id: int,
    ) -> None:
        """Recalculate project progress based on milestones."""
        project = await db.get(Project, project_id)
        if not project:
            return
        
        # Count milestones
        result = await db.execute(
            select(
                func.count(ProjectMilestone.id).label("total"),
                func.sum(func.cast(
                    ProjectMilestone.status == MilestoneStatus.COMPLETED,
                    type_=Integer
                )).label("completed")
            ).where(ProjectMilestone.project_id == project_id)
        )
        row = result.one()
        
        if row.total and row.total > 0:
            project.progress = Decimal(str(round((row.completed or 0) / row.total * 100, 2)))
        else:
            project.progress = Decimal("0")
        
        await db.flush()

    async def add_risk(
        self,
        db: AsyncSession,
        project_id: int,
        *,
        name: str,
        description: Optional[str] = None,
        probability: Decimal = Decimal("50"),
        impact: Decimal = Decimal("50"),
        mitigation_plan: Optional[str] = None,
        user_id: int,
    ) -> ProjectRisk:
        """Add a risk to a project."""
        project = await db.get(Project, project_id)
        if not project:
            raise ProjectsError("Project not found")
        
        risk = ProjectRisk(
            project_id=project_id,
            name=name,
            description=description,
            probability=probability,
            impact=impact,
            mitigation_plan=mitigation_plan,
            created_by_id=user_id,
        )
        db.add(risk)
        await db.flush()
        await db.refresh(risk)
        return risk

    async def mitigate_risk(
        self,
        db: AsyncSession,
        risk_id: int,
        *,
        user_id: int,
    ) -> ProjectRisk:
        """Mark a risk as mitigated."""
        risk = await db.get(ProjectRisk, risk_id)
        if not risk:
            raise ProjectsError("Risk not found")
        
        if risk.status == RiskStatus.CLOSED:
            raise ProjectsError("Risk already closed")
        
        risk.status = RiskStatus.MITIGATED
        await db.flush()
        await db.refresh(risk)
        return risk


projects_service = ProjectsService()
