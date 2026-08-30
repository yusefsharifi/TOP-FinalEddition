"""
HSE Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Models for safety incidents, inspection checklists, and safety alerts.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Enum, ForeignKey,
    Index, Integer, JSON, String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


# ── Enums ────────────────────────────────────────────────────────────────────

class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ChecklistStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"


# ── Models ───────────────────────────────────────────────────────────────────

class HSEIncident(Base):
    """Safety incident report."""
    __tablename__ = "hse_incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(Enum(IncidentSeverity), nullable=False, index=True)
    status: Mapped[IncidentStatus] = mapped_column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.OPEN, index=True)

    # Location
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # People involved
    injured_persons: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    witnesses: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # list of names

    # Immediate response
    immediate_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Investigation
    assigned_to_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    investigation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrective_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    reported_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reported_by_id])
    assignee = relationship("User", foreign_keys=[assigned_to_id])

    __table_args__ = (
        Index("ix_hse_incidents_status_severity", "status", "severity"),
        Index("ix_hse_incidents_created_at", "created_at"),
        Index("ix_hse_incidents_department", "department"),
        Index("ix_hse_incidents_reported_by", "reported_by_id"),
        Index("ix_hse_incidents_assigned_to", "assigned_to_id"),
        Index("ix_hse_incidents_resolved_at", "resolved_at"),
        Index("ix_hse_incidents_dept_status_date", "department", "status", "created_at"),
    )


class HSEChecklist(Base):
    """Safety inspection checklist."""
    __tablename__ = "hse_checklists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[ChecklistStatus] = mapped_column(
        Enum(ChecklistStatus), nullable=False, default=ChecklistStatus.PENDING, index=True
    )

    # Inspector
    inspector_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    inspector = relationship("User")
    items = relationship("HSEChecklistItem", back_populates="checklist", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_hse_checklists_location", "location"),
        Index("ix_hse_checklists_created_at", "created_at"),
        Index("ix_hse_checklists_inspector", "inspector_id"),
        Index("ix_hse_checklists_status_created", "status", "created_at"),
    )


class HSEChecklistItem(Base):
    """Individual item within a safety checklist."""
    __tablename__ = "hse_checklist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    checklist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("hse_checklists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ChecklistStatus] = mapped_column(
        Enum(ChecklistStatus), nullable=False, default=ChecklistStatus.PENDING
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    checklist: Mapped["HSEChecklist"] = relationship("HSEChecklist", back_populates="items")

    __table_args__ = (
        Index("ix_hse_checklist_items_status", "status"),
    )


class HSEAlert(Base):
    """Safety alert (hazard warning, chemical spill, equipment issue)."""
    __tablename__ = "hse_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(Enum(IncidentSeverity), nullable=False, index=True)
    target_department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    creator = relationship("User")

    __table_args__ = (
        Index("ix_hse_alerts_created_at", "created_at"),
        Index("ix_hse_alerts_target_dept", "target_department"),
    )
