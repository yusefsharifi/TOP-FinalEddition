"""
Projects Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Project management with tasks, milestones, resources, and risks.
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, Enum,
    ForeignKey, Index, Integer, Numeric, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


# ── Enums ────────────────────────────────────────────────────────────────────

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MilestoneStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"


class RiskStatus(str, enum.Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    CLOSED = "closed"


class ResourceType(str, enum.Enum):
    HUMAN = "human"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    FINANCIAL = "financial"


# ── Models ───────────────────────────────────────────────────────────────────

class Project(Base):
    """Main project model."""
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNING, index=True
    )
    priority: Mapped[ProjectPriority] = mapped_column(
        Enum(ProjectPriority), nullable=False, default=ProjectPriority.MEDIUM, index=True
    )
    
    # Dates
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Budget
    budget: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    actual_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    
    # Progress
    progress: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    
    # Manager
    manager_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    milestones: Mapped[list["ProjectMilestone"]] = relationship("ProjectMilestone", back_populates="project", cascade="all, delete-orphan")
    resources: Mapped[list["ProjectResource"]] = relationship("ProjectResource", back_populates="project", cascade="all, delete-orphan")
    risks: Mapped[list["ProjectRisk"]] = relationship("ProjectRisk", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_projects_status_priority", "status", "priority"),
        Index("ix_projects_manager", "manager_id"),
        Index("ix_projects_dates", "start_date", "end_date"),
    )

    def __repr__(self) -> str:
        return f"<Project {self.code} — {self.name}>"


class ProjectMilestone(Base):
    """Project milestone."""
    __tablename__ = "project_milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[MilestoneStatus] = mapped_column(
        Enum(MilestoneStatus), nullable=False, default=MilestoneStatus.PENDING, index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    project: Mapped["Project"] = relationship("Project", back_populates="milestones")
    
    __table_args__ = (
        Index("ix_project_milestones_project", "project_id"),
        Index("ix_project_milestones_status", "status"),
        Index("ix_project_milestones_due", "due_date"),
    )


class ProjectResource(Base):
    """Project resource allocation."""
    __tablename__ = "project_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[ResourceType] = mapped_column(Enum(ResourceType), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("1"))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    availability: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("100"))
    
    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    project: Mapped["Project"] = relationship("Project", back_populates="resources")
    
    __table_args__ = (
        Index("ix_project_resources_project", "project_id"),
        Index("ix_project_resources_type", "type"),
    )


class ProjectRisk(Base):
    """Project risk."""
    __tablename__ = "project_risks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    probability: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("50"))
    impact: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("50"))
    mitigation_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[RiskStatus] = mapped_column(
        Enum(RiskStatus), nullable=False, default=RiskStatus.OPEN, index=True
    )
    
    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    project: Mapped["Project"] = relationship("Project", back_populates="risks")
    
    __table_args__ = (
        Index("ix_project_risks_project", "project_id"),
        Index("ix_project_risks_status", "status"),
    )
