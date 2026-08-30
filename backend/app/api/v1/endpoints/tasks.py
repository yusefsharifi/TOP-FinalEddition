"""
Tasks Module — FastAPI Router
TOP WorX ERP System

Task management with assignments, comments, and status tracking.
Uses SQLAlchemy models from app.models.tasks.
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBDep, CurrentUser
from app.core.cache import cache
from app.models.tasks import (
    ProjectTask, TaskComment as TaskCommentModel,
    TaskPriority, TaskStatus,
)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None
    parent_task_id: Optional[int] = None


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None
    created_by_id: int
    parent_task_id: Optional[int] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    task_id: int
    content: str
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── TASKS CRUD ───────────────────────────────────────────────────────────────

@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    db: DBDep,
    current_user: CurrentUser,
    task_status: Optional[TaskStatus] = Query(None, alias="status"),
    priority: Optional[TaskPriority] = None,
    assigned_to_me: bool = False,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[TaskResponse]:
    """List tasks with optional filtering."""
    q = select(ProjectTask).order_by(ProjectTask.created_at.desc())
    if task_status:
        q = q.where(ProjectTask.status == task_status)
    if priority:
        q = q.where(ProjectTask.priority == priority)
    if assigned_to_me:
        q = q.where(ProjectTask.assigned_to_id == current_user.id)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [TaskResponse.model_validate(r) for r in rows]


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> TaskResponse:
    """Create a new task."""
    task = ProjectTask(
        name=data.name,
        description=data.description,
        status=TaskStatus.PENDING,
        priority=data.priority,
        due_date=data.due_date,
        assigned_to_id=data.assigned_to_id,
        parent_task_id=data.parent_task_id,
        created_by_id=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> TaskResponse:
    """Get task details."""
    task = await db.get(ProjectTask, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> TaskResponse:
    """Update task fields."""
    task = await db.get(ProjectTask, task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Track timestamps
    if data.status == TaskStatus.IN_PROGRESS and not task.started_at:
        task.started_at = datetime.utcnow()
    elif data.status == TaskStatus.COMPLETED:
        task.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    """Delete a task (only if PENDING or CANCELLED)."""
    task = await db.get(ProjectTask, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status not in (TaskStatus.PENDING, TaskStatus.CANCELLED):
        raise HTTPException(409, "Cannot delete a task that is in progress or completed")
    await db.delete(task)
    await db.commit()


# ── COMMENTS ─────────────────────────────────────────────────────────────────

@router.get("/{task_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    task_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> list[CommentResponse]:
    """List comments on a task."""
    task = await db.get(ProjectTask, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    q = select(TaskCommentModel).where(TaskCommentModel.task_id == task_id).order_by(TaskCommentModel.created_at.desc())
    rows = (await db.execute(q)).scalars().all()
    return [CommentResponse.model_validate(c) for c in rows]


@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=201)
async def add_comment(
    task_id: int,
    data: CommentCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> CommentResponse:
    """Add a comment to a task."""
    task = await db.get(ProjectTask, task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    comment = TaskCommentModel(
        task_id=task_id,
        content=data.content,
        created_by_id=current_user.id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentResponse.model_validate(comment)


# ── DASHBOARD ────────────────────────────────────────────────────────────────

@router.get("/dashboard/stats")
async def task_stats(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Task dashboard statistics (cached for 2 min)."""
    cache_key = "tasks:dashboard:stats"
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    # Consolidated queries: 2 instead of 12
    total = (await db.execute(select(func.count(ProjectTask.id)))).scalar() or 0
    my_tasks = (await db.execute(
        select(func.count(ProjectTask.id)).where(ProjectTask.assigned_to_id == current_user.id)
    )).scalar() or 0

    # Single GROUP BY query for status counts (was 5 separate queries)
    status_counts = (await db.execute(
        select(ProjectTask.status, func.count(ProjectTask.id).label("cnt"))
        .group_by(ProjectTask.status)
    )).all()
    by_status = {row.status.value: row.cnt for row in status_counts}

    # Single GROUP BY query for priority counts (was 4 separate queries)
    priority_counts = (await db.execute(
        select(ProjectTask.priority, func.count(ProjectTask.id).label("cnt"))
        .group_by(ProjectTask.priority)
    )).all()
    by_priority = {row.priority.value: row.cnt for row in priority_counts}

    result = {
        "total": total,
        "my_tasks": my_tasks,
        "by_status": by_status,
        "by_priority": by_priority,
    }
    await cache.set(cache_key, result, ttl=120)  # 2 min cache
    return result
