"""
Settings & Administration Module — FastAPI Router
TOP WorX ERP System

System settings, role management, and audit logging.
Uses SQLAlchemy models from app.models.settings and app.models.auth_enhanced.
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBDep, CurrentUser
from app.core.cache import cached, cache_invalidate, invalidate_settings_cache, cache
from app.models.settings import (
    SystemSetting, ModuleAuditLog, SystemNotification,
    AuditAction, SettingCategory,
)
from app.models.auth_enhanced import Role, Permission, UserRole

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class SettingCreate(BaseModel):
    key: str
    value: str
    value_type: str = "string"
    description: Optional[str] = None
    category: SettingCategory = SettingCategory.GENERAL
    is_sensitive: bool = False
    is_readonly: bool = False


class SettingResponse(BaseModel):
    id: int
    key: str
    value: str
    value_type: str
    description: Optional[str] = None
    category: SettingCategory
    is_sensitive: bool
    is_readonly: bool
    updated_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    permission_codes: list[str] = Field(default_factory=list)


class RoleResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserRoleAssign(BaseModel):
    user_id: int
    role_code: str
    expires_at: Optional[datetime] = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: AuditAction
    module: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    resource_description: Optional[str] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    title: str
    message: str
    severity: str = "info"
    target_roles: Optional[list[str]] = None


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    severity: str
    is_active: bool
    target_roles: Optional[list] = None
    expires_at: Optional[datetime] = None
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _log_audit(
    db: AsyncSession, user_id: int, action: AuditAction,
    module: str, resource_type: str = None, resource_id: int = None,
    resource_description: str = None, old_values: dict = None,
    new_values: dict = None, ip_address: str = None,
):
    entry = ModuleAuditLog(
        user_id=user_id,
        action=action,
        module=module,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_description=resource_description,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
    )
    db.add(entry)


# ── SYSTEM SETTINGS ──────────────────────────────────────────────────────────

@router.get("/system", response_model=list[SettingResponse])
async def list_settings(
    db: DBDep,
    current_user: CurrentUser,
    category: Optional[SettingCategory] = None,
) -> list[SettingResponse]:
    """List all system settings (cached for 5 min)."""
    cache_key = f"settings:list:{category.value if category else 'all'}"
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        return [SettingResponse.model_validate(r) for r in cached_result]

    q = select(SystemSetting)
    if category:
        q = q.where(SystemSetting.category == category)
    q = q.order_by(SystemSetting.category, SystemSetting.key)
    rows = (await db.execute(q)).scalars().all()
    result = [SettingResponse.model_validate(r) for r in rows]
    await cache.set(cache_key, [r.model_dump(mode='json') for r in result], ttl=300)
    return result


@router.get("/system/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    db: DBDep,
    current_user: CurrentUser,
) -> SettingResponse:
    """Get a specific setting by key (cached for 5 min)."""
    cache_key = f"settings:detail:{key}"
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        return SettingResponse.model_validate(cached_result)

    result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(404, f"Setting '{key}' not found")
    resp = SettingResponse.model_validate(setting)
    await cache.set(cache_key, resp.model_dump(mode='json'), ttl=300)
    return resp


@router.post("/system", response_model=SettingResponse, status_code=201)
@cache_invalidate("settings:*")
async def create_setting(
    data: SettingCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> SettingResponse:
    """Create a new system setting (invalidates settings cache)."""
    existing = (await db.execute(
        select(SystemSetting).where(SystemSetting.key == data.key)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(409, f"Setting '{data.key}' already exists")

    setting = SystemSetting(
        key=data.key,
        value=data.value,
        value_type=data.value_type,
        description=data.description,
        category=data.category,
        is_sensitive=data.is_sensitive,
        is_readonly=data.is_readonly,
        updated_by_id=current_user.id,
    )
    db.add(setting)
    await _log_audit(db, current_user.id, AuditAction.CREATE, "settings", "setting", resource_description=data.key, new_values={"key": data.key})
    await db.commit()
    await db.refresh(setting)
    return SettingResponse.model_validate(setting)


@router.put("/system/{key}", response_model=SettingResponse)
@cache_invalidate("settings:*")
async def update_setting(
    key: str,
    data: SettingCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> SettingResponse:
    """Update a system setting (invalidates settings cache)."""
    result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(404, f"Setting '{key}' not found")
    if setting.is_readonly:
        raise HTTPException(409, "This setting is read-only")

    old_value = setting.value
    setting.value = data.value
    setting.description = data.description or setting.description
    setting.category = data.category
    setting.updated_by_id = current_user.id

    await _log_audit(
        db, current_user.id, AuditAction.UPDATE, "settings", "setting",
        resource_description=key,
        old_values={"value": old_value},
        new_values={"value": data.value},
    )
    await db.commit()
    await db.refresh(setting)
    return SettingResponse.model_validate(setting)


# ── ROLES ────────────────────────────────────────────────────────────────────

@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    db: DBDep,
    current_user: CurrentUser,
) -> list[RoleResponse]:
    """List all roles (cached for 5 min)."""
    cache_key = "settings:roles:list"
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        return [RoleResponse.model_validate(r) for r in cached_result]

    q = select(Role).order_by(Role.level, Role.name)
    rows = (await db.execute(q)).scalars().all()
    result = [RoleResponse.model_validate(r) for r in rows]
    await cache.set(cache_key, [r.model_dump(mode='json') for r in result], ttl=300)
    return result


@router.post("/roles", response_model=RoleResponse, status_code=201)
@cache_invalidate("settings:roles:*")
async def create_role(
    data: RoleCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> RoleResponse:
    """Create a new role with permissions (invalidates roles cache)."""
    existing = (await db.execute(
        select(Role).where(Role.code == data.code)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(409, f"Role code '{data.code}' already exists")

    role = Role(
        name=data.name,
        code=data.code,
        description=data.description,
        created_by_id=current_user.id,
    )
    db.add(role)
    await db.flush()

    # Batch fetch all requested permissions in one query (was 1 per permission)
    from app.models.auth_enhanced import RolePermission
    if data.permission_codes:
        perms_result = await db.execute(
            select(Permission).where(Permission.code.in_(data.permission_codes))
        )
        perms_by_code = {p.code: p for p in perms_result.scalars().all()}
        for perm_code in data.permission_codes:
            perm = perms_by_code.get(perm_code)
            if perm:
                rp = RolePermission(role_id=role.id, permission_id=perm.id, granted_by_id=current_user.id)
                db.add(rp)

    await _log_audit(db, current_user.id, AuditAction.CREATE, "settings", "role", resource_description=data.code)
    await db.commit()
    await db.refresh(role)
    return RoleResponse.model_validate(role)


@router.put("/roles/{role_code}", response_model=RoleResponse)
@cache_invalidate("settings:roles:*")
async def update_role(
    role_code: str,
    data: RoleCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> RoleResponse:
    """Update a role's name, description, and permissions (invalidates roles cache)."""
    result = await db.execute(select(Role).where(Role.code == role_code))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, f"Role '{role_code}' not found")

    role.name = data.name
    role.description = data.description

    # Replace permissions — batch fetch all requested permissions in one query
    from app.models.auth_enhanced import RolePermission
    # Delete existing
    existing_rps = await db.execute(
        select(RolePermission).where(RolePermission.role_id == role.id)
    )
    for rp in existing_rps.scalars().all():
        await db.delete(rp)

    # Add new — single query instead of N queries
    if data.permission_codes:
        perms_result = await db.execute(
            select(Permission).where(Permission.code.in_(data.permission_codes))
        )
        perms_by_code = {p.code: p for p in perms_result.scalars().all()}
        for perm_code in data.permission_codes:
            perm = perms_by_code.get(perm_code)
            if perm:
                rp = RolePermission(role_id=role.id, permission_id=perm.id, granted_by_id=current_user.id)
                db.add(rp)

    await _log_audit(db, current_user.id, AuditAction.UPDATE, "settings", "role", resource_description=role_code)
    await db.commit()
    await db.refresh(role)
    return RoleResponse.model_validate(role)


@router.delete("/roles/{role_code}", status_code=204)
@cache_invalidate("settings:roles:*")
async def delete_role(
    role_code: str,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    """Delete a role (only if no users assigned, invalidates roles cache)."""
    result = await db.execute(select(Role).where(Role.code == role_code))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, f"Role '{role_code}' not found")

    # Check for assigned users
    user_count = (await db.execute(
        select(func.count(UserRole.id)).where(UserRole.role_id == role.id)
    )).scalar() or 0
    if user_count > 0:
        raise HTTPException(409, "Cannot delete a role that is assigned to users")

    await db.delete(role)
    await _log_audit(db, current_user.id, AuditAction.DELETE, "settings", "role", resource_description=role_code)
    await db.commit()


# ── SYSTEM NOTIFICATIONS ─────────────────────────────────────────────────────

@router.get("/notifications", response_model=list[NotificationResponse])
async def list_system_notifications(
    db: DBDep,
    current_user: CurrentUser,
    active_only: bool = True,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[NotificationResponse]:
    """List system-wide notifications/announcements."""
    q = select(SystemNotification).order_by(SystemNotification.created_at.desc())
    if active_only:
        q = q.where(SystemNotification.is_active == True)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [NotificationResponse.model_validate(n) for n in rows]


@router.post("/notifications", response_model=NotificationResponse, status_code=201)
async def create_system_notification(
    data: NotificationCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> NotificationResponse:
    """Create a system-wide notification/announcement."""
    notif = SystemNotification(
        title=data.title,
        message=data.message,
        severity=data.severity,
        target_roles=data.target_roles,
        created_by_id=current_user.id,
    )
    db.add(notif)
    await _log_audit(db, current_user.id, AuditAction.CREATE, "settings", "notification", resource_description=data.title)
    await db.commit()
    await db.refresh(notif)
    return NotificationResponse.model_validate(notif)


# ── AUDIT LOG ────────────────────────────────────────────────────────────────

@router.get("/audit-log", response_model=list[AuditLogResponse])
async def list_audit_log(
    db: DBDep,
    current_user: CurrentUser,
    action: Optional[AuditAction] = None,
    module: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[AuditLogResponse]:
    """List audit log entries."""
    q = select(ModuleAuditLog).order_by(ModuleAuditLog.created_at.desc())
    if action:
        q = q.where(ModuleAuditLog.action == action)
    if module:
        q = q.where(ModuleAuditLog.module == module)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [AuditLogResponse.model_validate(r) for r in rows]
