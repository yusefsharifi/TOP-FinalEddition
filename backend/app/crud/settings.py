"""
Settings Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import (
    AuditAction, ModuleAuditLog, SettingCategory, SystemNotification,
    SystemSetting,
)
from app.models.auth_enhanced import Role, UserRole


class SettingCRUD:
    async def get(self, db: AsyncSession, key: str) -> Optional[SystemSetting]:
        result = await db.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        category: Optional[SettingCategory] = None,
    ) -> Sequence[SystemSetting]:
        q = select(SystemSetting).order_by(SystemSetting.category, SystemSetting.key)
        if category:
            q = q.where(SystemSetting.category == category)
        return (await db.execute(q)).scalars().all()


class RoleCRUD:
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Role]:
        result = await db.execute(
            select(Role).where(Role.code == code)
        )
        return result.scalar_one_or_none()

    async def list(self, db: AsyncSession) -> Sequence[Role]:
        q = select(Role).order_by(Role.level, Role.name)
        return (await db.execute(q)).scalars().all()

    async def user_count(self, db: AsyncSession, role_id: int) -> int:
        return (await db.execute(
            select(func.count(UserRole.id)).where(UserRole.role_id == role_id)
        )).scalar() or 0


class AuditLogCRUD:
    async def list(
        self,
        db: AsyncSession,
        *,
        action: Optional[AuditAction] = None,
        module: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[ModuleAuditLog]]:
        q = select(ModuleAuditLog).order_by(ModuleAuditLog.created_at.desc())
        if action:
            q = q.where(ModuleAuditLog.action == action)
        if module:
            q = q.where(ModuleAuditLog.module == module)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows


class NotificationCRUD:
    async def list(
        self,
        db: AsyncSession,
        *,
        active_only: bool = True,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[int, Sequence[SystemNotification]]:
        q = select(SystemNotification).order_by(SystemNotification.created_at.desc())
        if active_only:
            q = q.where(SystemNotification.is_active == True)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows


# Singletons
setting_crud = SettingCRUD()
role_crud = RoleCRUD()
audit_log_crud = AuditLogCRUD()
notification_crud = NotificationCRUD()
