"""
Tasks Module — Service Layer
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.tasks import task_crud
from app.models.tasks import ProjectTask, TaskStatus


class TasksError(Exception):
    """Tasks business logic error."""
    pass


class TasksService:
    async def update_task_status(
        self,
        db: AsyncSession,
        task_id: int,
        *,
        new_status: TaskStatus,
        user_id: int,
    ) -> ProjectTask:
        task = await task_crud.get(db, task_id)
        if not task:
            raise TasksError("Task not found")

        old_status = task.status
        task.status = new_status

        if new_status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()
        elif new_status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()

        await db.flush()
        await db.refresh(task)
        return task


tasks_service = TasksService()
