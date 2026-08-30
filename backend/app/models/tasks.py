"""
Tasks Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Task management with assignments, comments, and status tracking.
Extends the existing workflow.py Task model with richer fields.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime, Enum, ForeignKey,
    Index, Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


# ── Enums ────────────────────────────────────────────────────────────────────

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


# ── Models ───────────────────────────────────────────────────────────────────

class ProjectTask(Base):
    """
    Standalone task (not tied to a workflow).
    For workflow-related tasks, use the Task model in workflow.py.
    """
    __tablename__ = "project_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM, index=True)

    # Assignment
    assigned_to_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Hierarchy
    parent_task_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("project_tasks.id", ondelete="SET NULL"), nullable=True
    )

    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    assignee = relationship("User", foreign_keys=[assigned_to_id])
    creator = relationship("User", foreign_keys=[created_by_id])
    parent_task = relationship("ProjectTask", remote_side="ProjectTask.id", backref="subtasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_project_tasks_status_priority", "status", "priority"),
        Index("ix_project_tasks_assigned", "assigned_to_id", "status"),
        Index("ix_project_tasks_due", "due_date"),
        Index("ix_project_tasks_created_by", "created_by_id"),
        Index("ix_project_tasks_parent", "parent_task_id"),
        Index("ix_project_tasks_created_at", "created_at"),
        Index("ix_project_tasks_assigned_due", "assigned_to_id", "due_date"),
    )


class TaskComment(Base):
    """Comment on a task."""
    __tablename__ = "task_project_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    task: Mapped["ProjectTask"] = relationship("ProjectTask", back_populates="comments")
    creator = relationship("User")

    __table_args__ = (
        Index("ix_task_comments_created_by", "created_by_id"),
        Index("ix_task_comments_created_at", "created_at"),
    )
