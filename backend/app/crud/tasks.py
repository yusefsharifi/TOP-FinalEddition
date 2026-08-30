"""
Tasks Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tasks import (
    ProjectTask, TaskComment, TaskPriority, TaskStatus,
)


class TaskCRUD:
    async def get(self, db: AsyncSession, task_id: int) -> Optional[ProjectTask]:
        result = await db.execute(
            select(ProjectTask).where(ProjectTask.id == task_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assigned_to_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[ProjectTask]]:
        q = select(ProjectTask).order_by(ProjectTask.created_at.desc())
        if status:
            q = q.where(ProjectTask.status == status)
        if priority:
            q = q.where(ProjectTask.priority == priority)
        if assigned_to_id:
            q = q.where(ProjectTask.assigned_to_id == assigned_to_id)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def stats(self, db: AsyncSession, user_id: Optional[int] = None) -> dict:
        total = (await db.execute(select(func.count(ProjectTask.id)))).scalar() or 0
        my_tasks = 0
        if user_id:
            my_tasks = (await db.execute(
                select(func.count(ProjectTask.id)).where(ProjectTask.assigned_to_id == user_id)
            )).scalar() or 0

        status_counts = (await db.execute(
            select(ProjectTask.status, func.count(ProjectTask.id).label("cnt"))
            .group_by(ProjectTask.status)
        )).all()
        by_status = {row.status.value: row.cnt for row in status_counts}

        priority_counts = (await db.execute(
            select(ProjectTask.priority, func.count(ProjectTask.id).label("cnt"))
            .group_by(ProjectTask.priority)
        )).all()
        by_priority = {row.priority.value: row.cnt for row in priority_counts}

        return {
            "total": total,
            "my_tasks": my_tasks,
            "by_status": by_status,
            "by_priority": by_priority,
        }


class TaskCommentCRUD:
    async def list(
        self,
        db: AsyncSession,
        task_id: int,
    ) -> Sequence[TaskComment]:
        q = (
            select(TaskComment)
            .where(TaskComment.task_id == task_id)
            .order_by(TaskComment.created_at.desc())
        )
        return (await db.execute(q)).scalars().all()


# Singletons
task_crud = TaskCRUD()
task_comment_crud = TaskCommentCRUD()
