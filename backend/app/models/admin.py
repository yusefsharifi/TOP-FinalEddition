"""
RBAC Module — Admin Router + Audit Middleware
TOP WorX ERP System

Admin router: /admin/users, /admin/roles, /admin/permissions, /admin/audit
My account: /me
Middleware: auto-audit logging for all state-changing requests
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, select


from app.models.auth_enhanced import (
    AuditAction, AuditLog, AuditStatus, Permission, Role,
    RolePermission, User, UserInvitation, UserRole, UserSession, UserStatus,
)
from app.services.permission_engine import audit_service, permission_engine
from app.services.user_management_service import (
    UserManagementError, user_management_service,
)

# ---------------------------------------------------------------------------
# Real dependencies from centralized deps module
# ---------------------------------------------------------------------------
from app.api.deps import DBDep, CurrentUser

# Alias for backward compatibility — endpoints use `cu: CU`
CU = CurrentUser

router = APIRouter()


def _err(exc: Exception) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


# ===========================================================================
# MY ACCOUNT  /me
# ===========================================================================
@router.get("/me")
async def my_profile(db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == cu.id))
    user = user_r.scalar_one_or_none()
    if not user:
        return {"id": cu.id, "email": cu.email, "name": f"{cu.first_name} {cu.last_name}"}
    return {
        "id": user.id, "email": user.email,
        "first_name": user.first_name, "last_name": user.last_name,
        "first_name_fa": user.first_name_fa, "last_name_fa": user.last_name_fa,
        "phone": user.phone, "avatar_url": user.avatar_url,
        "status": user.status.value,
        "email_verified": user.email_verified,
        "mfa_enabled": user.mfa_enabled,
        "language": user.language, "timezone": user.timezone, "theme": user.theme.value,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "password_expires_at": user.password_expires_at.isoformat() if user.password_expires_at else None,
    }


@router.put("/me")
async def update_my_profile(data: dict, db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == cu.id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    allowed = ["first_name", "last_name", "first_name_fa", "last_name_fa", "phone", "avatar_url"]
    for field in allowed:
        if field in data:
            setattr(user, field, data[field])
    await db.commit()
    return {"status": "updated"}


@router.put("/me/password")
async def change_my_password(data: dict, db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == cu.id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    try:
        await user_management_service.change_password(
            db, user, data["new_password"],
            require_old=True, old_password=data.get("old_password"),
        )
    except UserManagementError as exc:
        raise _err(exc)
    await db.commit()
    return {"status": "password changed"}


@router.put("/me/preferences")
async def update_preferences(data: dict, db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == cu.id))
    user = user_r.scalar_one_or_none()
    if user:
        for field in ["language", "timezone", "theme", "notification_preferences"]:
            if field in data:
                setattr(user, field, data[field])
    await db.commit()
    return {"status": "preferences updated"}


@router.get("/me/sessions")
async def my_sessions(db: DBDep, cu: CU) -> list[dict]:
    sessions_r = await db.execute(
        select(UserSession)
        .where(UserSession.user_id == cu.id, UserSession.is_active.is_(True))
        .order_by(UserSession.last_activity_at.desc())
    )
    return [{"id": s.id, "device_type": s.device_type.value, "device_name": s.device_name,
             "ip_address": s.ip_address, "created_at": s.created_at.isoformat(),
             "last_activity_at": s.last_activity_at.isoformat()}
            for s in sessions_r.scalars().all()]


@router.delete("/me/sessions/{session_id}", status_code=204)
async def revoke_my_session(session_id: int, db: DBDep, cu: CU) -> None:
    session_r = await db.execute(
        select(UserSession).where(UserSession.id == session_id, UserSession.user_id == cu.id)
    )
    session = session_r.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    await user_management_service.revoke_session(db, session, "Manual logout")
    await db.commit()


@router.get("/me/permissions")
async def my_permissions(db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == cu.id))
    user = user_r.scalar_one_or_none()
    if not user:
        return {"permissions": [], "modules": []}
    perms = await permission_engine.get_user_permissions(db, user)
    modules = await permission_engine.get_accessible_modules(db, user)
    return {
        "permissions": list(perms.keys()),
        "modules": modules,
        "permission_details": perms,
    }


@router.get("/me/audit")
async def my_audit(
    db: DBDep, cu: CU,
    offset: int = 0, limit: int = 50,
) -> list[dict]:
    logs = await audit_service.get_trail(db, user_id=cu.id, offset=offset, limit=limit)
    return [_format_log(log) for log in logs]


# ===========================================================================
# ADMIN — USERS
# ===========================================================================
@router.get("/admin/users")
async def list_users(
    db: DBDep, cu: CU,
    status: Optional[UserStatus] = None,
    role_code: Optional[str] = None,
    search: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    # TODO: require_permission(cu, "admin:user:view")
    q = select(User).where(User.deleted_at.is_(None)).order_by(User.created_at.desc())
    if status:
        q = q.where(User.status == status)
    if search:
        from sqlalchemy import or_
        term = f"%{search}%"
        q = q.where(or_(User.email.ilike(term), User.first_name.ilike(term), User.last_name.ilike(term)))
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [_format_user(u) for u in rows]


@router.post("/admin/users", status_code=201)
async def create_user(data: dict, db: DBDep, cu: CU) -> dict:
    # TODO: require_permission(cu, "admin:user:manage")
    try:
        user, temp_password = await user_management_service.create_user(
            db,
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            role_id=data["role_id"],
            created_by=cu,
            first_name_fa=data.get("first_name_fa"),
            last_name_fa=data.get("last_name_fa"),
            phone=data.get("phone"),
        )
    except UserManagementError as exc:
        raise _err(exc)
    await db.commit()
    return {**_format_user(user), "temp_password": temp_password}


@router.get("/admin/users/{user_id}")
async def get_user(user_id: int, db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == user_id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    # Load roles
    roles_r = await db.execute(
        select(Role).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
    )
    roles = roles_r.scalars().all()

    return {
        **_format_user(user),
        "roles": [{"id": r.id, "code": r.code, "name": r.name, "level": r.level} for r in roles],
    }


@router.put("/admin/users/{user_id}")
async def update_user(user_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == user_id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    allowed = ["first_name", "last_name", "first_name_fa", "last_name_fa", "phone", "avatar_url", "language"]
    for field in allowed:
        if field in data:
            setattr(user, field, data[field])
    await db.commit()
    return _format_user(user)


@router.delete("/admin/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: DBDep, cu: CU) -> None:
    user_r = await db.execute(select(User).where(User.id == user_id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    try:
        await user_management_service.soft_delete(db, user_id, cu)
    except UserManagementError as exc:
        raise _err(exc)
    await db.commit()


@router.post("/admin/users/{user_id}/suspend")
async def suspend_user(user_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    try:
        user = await user_management_service.suspend_user(db, user_id, data.get("reason", ""), cu)
    except UserManagementError as exc:
        raise _err(exc)
    await db.commit()
    return {"status": "suspended", "user_id": user.id}


@router.post("/admin/users/{user_id}/activate")
async def activate_user(user_id: int, db: DBDep, cu: CU) -> dict:
    try:
        user = await user_management_service.activate_user(db, user_id, cu)
    except UserManagementError as exc:
        raise _err(exc)
    await db.commit()
    return {"status": "active", "user_id": user.id}


@router.post("/admin/users/{user_id}/reset-password")
async def reset_password(user_id: int, db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == user_id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    temp_password = user_management_service._generate_temp_password()
    try:
        await user_management_service.change_password(db, user, temp_password, changed_by=cu)
    except UserManagementError as exc:
        raise _err(exc)
    user.force_password_change = True
    await db.commit()
    return {"temp_password": temp_password, "force_change": True}


@router.post("/admin/users/{user_id}/change-role")
async def change_user_role(user_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    try:
        await user_management_service.change_role(db, user_id, data["role_id"], cu)
    except UserManagementError as exc:
        raise _err(exc)
    await db.commit()
    return {"status": "role changed"}


@router.get("/admin/users/{user_id}/sessions")
async def user_sessions(user_id: int, db: DBDep, cu: CU) -> list[dict]:
    sessions_r = await db.execute(
        select(UserSession).where(UserSession.user_id == user_id).order_by(UserSession.created_at.desc()).limit(20)
    )
    return [{"id": s.id, "is_active": s.is_active, "device_type": s.device_type.value,
             "ip_address": s.ip_address, "created_at": s.created_at.isoformat(),
             "revoke_reason": s.revoke_reason} for s in sessions_r.scalars().all()]


@router.delete("/admin/users/{user_id}/sessions/all")
async def revoke_all_user_sessions(user_id: int, db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == user_id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    count = await user_management_service.revoke_all_sessions(db, user, "Admin force logout", cu)
    await db.commit()
    return {"revoked": count}


@router.get("/admin/users/{user_id}/audit")
async def user_audit(user_id: int, db: DBDep, cu: CU, offset: int = 0, limit: int = 50) -> list[dict]:
    logs = await audit_service.get_trail(db, user_id=user_id, offset=offset, limit=limit)
    return [_format_log(log) for log in logs]


@router.get("/admin/users/{user_id}/permissions")
async def user_effective_permissions(user_id: int, db: DBDep, cu: CU) -> dict:
    user_r = await db.execute(select(User).where(User.id == user_id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    perms = await permission_engine.get_user_permissions(db, user)
    return {"user_id": user_id, "permissions": list(perms.keys()), "details": perms}


# ===========================================================================
# ADMIN — INVITATIONS
# ===========================================================================
@router.post("/admin/users/invite", status_code=201)
async def invite_user(data: dict, db: DBDep, cu: CU) -> dict:
    try:
        inv = await user_management_service.invite_user(
            db, email=data["email"], role_id=data["role_id"],
            invited_by=cu, department_id=data.get("department_id"),
            first_name=data.get("first_name"), last_name=data.get("last_name"),
        )
    except UserManagementError as exc:
        raise _err(exc)
    await db.commit()
    return {"invitation_id": inv.id, "email": inv.email, "expires_at": inv.expires_at.isoformat()}


# ===========================================================================
# ADMIN — ROLES
# ===========================================================================
@router.get("/admin/roles")
async def list_roles(db: DBDep, cu: CU) -> list[dict]:
    rows = (await db.execute(select(Role).where(Role.is_active.is_(True)).order_by(Role.level))).scalars().all()
    return [{"id": r.id, "code": r.code, "name": r.name, "level": r.level,
             "data_scope": r.data_scope.value, "role_type": r.role_type.value} for r in rows]


@router.post("/admin/roles", status_code=201)
async def create_role(data: dict, db: DBDep, cu: CU) -> dict:
    # TODO: require_role(cu, "super_admin")
    role = Role(
        code=data["code"], name=data["name"], name_fa=data.get("name_fa"),
        description=data.get("description"),
        level=data.get("level", 5),
        data_scope=data.get("data_scope", "own"),
        default_dashboard=data.get("default_dashboard"),
        created_by_id=cu.id,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return {"id": role.id, "code": role.code}


@router.put("/admin/roles/{role_id}/permissions")
async def update_role_permissions(role_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    """Replace all permissions for a role."""
    role_r = await db.execute(select(Role).where(Role.id == role_id))
    role = role_r.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Role not found")
    if role.role_type.value == "system" and not await _is_super_admin(db, cu):
        raise HTTPException(403, "Cannot modify system role permissions")

    # Remove existing
    existing_r = await db.execute(select(RolePermission).where(RolePermission.role_id == role_id))
    for rp in existing_r.scalars().all():
        await db.delete(rp)
    await db.flush()

    # Add new
    permission_ids = data.get("permission_ids", [])
    for perm_id in permission_ids:
        rp = RolePermission(role_id=role_id, permission_id=perm_id, granted_by_id=cu.id)
        db.add(rp)

    await db.commit()
    return {"role_id": role_id, "permissions_set": len(permission_ids)}


@router.post("/admin/roles/{role_id}/clone", status_code=201)
async def clone_role(role_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    role_r = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    original = role_r.scalar_one_or_none()
    if not original:
        raise HTTPException(404, "Role not found")

    new_role = Role(
        code=data["code"],
        name=data.get("name", f"Copy of {original.name}"),
        description=original.description,
        level=original.level,
        data_scope=original.data_scope,
        role_type="custom",
        created_by_id=cu.id,
    )
    db.add(new_role)
    await db.flush()

    perms_r = await db.execute(select(RolePermission).where(RolePermission.role_id == role_id))
    for rp in perms_r.scalars().all():
        db.add(RolePermission(role_id=new_role.id, permission_id=rp.permission_id, granted_by_id=cu.id))

    await db.commit()
    return {"id": new_role.id, "code": new_role.code, "cloned_from": role_id}


@router.get("/admin/roles/{role_id}/users")
async def role_users(role_id: int, db: DBDep, cu: CU) -> list[dict]:
    rows = (await db.execute(
        select(User).join(UserRole, UserRole.user_id == User.id)
        .where(UserRole.role_id == role_id, User.deleted_at.is_(None))
    )).scalars().all()
    return [_format_user(u) for u in rows]


# ===========================================================================
# ADMIN — PERMISSIONS
# ===========================================================================
@router.get("/admin/permissions")
async def list_permissions(db: DBDep, cu: CU, module: Optional[str] = None) -> list[dict]:
    q = select(Permission).where(Permission.is_active.is_(True)).order_by(Permission.code)
    if module:
        q = q.where(Permission.module == module)
    rows = (await db.execute(q)).scalars().all()
    return [{"id": p.id, "code": p.code, "name": p.name, "module": p.module,
             "action": p.action, "scope": p.scope, "category": p.category.value} for p in rows]


@router.get("/admin/permissions/modules")
async def permissions_by_module(db: DBDep, cu: CU) -> dict:
    """Grouped by module for Role Matrix UI."""
    rows = (await db.execute(select(Permission).where(Permission.is_active.is_(True)).order_by(Permission.code))).scalars().all()
    grouped: dict[str, list] = {}
    for p in rows:
        grouped.setdefault(p.module, []).append({
            "id": p.id, "code": p.code, "name": p.name,
            "action": p.action, "scope": p.scope,
        })
    return grouped


# ===========================================================================
# ADMIN — AUDIT
# ===========================================================================
@router.get("/admin/audit")
async def global_audit(
    db: DBDep, cu: CU,
    module: Optional[str] = None,
    action: Optional[AuditAction] = None,
    user_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[AuditStatus] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    # TODO: require_permission(cu, "admin:audit:view")
    logs = await audit_service.get_trail(
        db, module=module, action=action, user_id=user_id,
        date_from=date_from, date_to=date_to, status=status,
        offset=offset, limit=limit,
    )
    return [_format_log(log) for log in logs]


@router.get("/admin/audit/stats")
async def audit_stats(db: DBDep, cu: CU, days: int = Query(30, ge=1, le=365)) -> dict:
    return await audit_service.stats(db, days=days)


@router.get("/admin/audit/compliance-report")
async def compliance_report(
    db: DBDep, cu: CU,
    user_id: Optional[int] = None,
    module: Optional[str] = None,
) -> dict:
    return await audit_service.compliance_report(db, user_id=user_id, module=module)


@router.get("/admin/security/failed-logins")
async def failed_logins(db: DBDep, cu: CU, hours: int = 24) -> list[dict]:
    from datetime import timedelta
    since = datetime.utcnow() - timedelta(hours=hours)
    logs = await audit_service.get_trail(
        db, action=AuditAction.LOGIN_FAILED, date_from=since, limit=200
    )
    return [_format_log(log) for log in logs]


# ===========================================================================
# Helpers
# ===========================================================================
def _format_user(user: User) -> dict:
    return {
        "id": user.id, "email": user.email,
        "first_name": user.first_name, "last_name": user.last_name,
        "first_name_fa": getattr(user, "first_name_fa", None),
        "last_name_fa": getattr(user, "last_name_fa", None),
        "phone": getattr(user, "phone", None),
        "status": user.status.value if hasattr(user.status, "value") else str(user.status),
        "email_verified": getattr(user, "email_verified", False),
        "mfa_enabled": getattr(user, "mfa_enabled", False),
        "created_at": user.created_at.isoformat() if getattr(user, "created_at", None) else None,
        "last_login_at": user.last_login_at.isoformat() if getattr(user, "last_login_at", None) else None,
    }


def _format_log(log: AuditLog) -> dict:
    return {
        "id": log.id,
        "user_email": log.user_email,
        "action": log.action.value,
        "module": log.module,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "resource_description": log.resource_description,
        "status": log.status.value,
        "ip_address": log.ip_address,
        "created_at": log.created_at.isoformat(),
        "changes": log.changes if not log.is_sensitive else None,
    }


async def _is_super_admin(db: AsyncSession, cu) -> bool:
    r = await db.execute(
        select(Role).join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == cu.id, Role.code == "super_admin")
    )
    return r.scalar_one_or_none() is not None


# ===========================================================================
# Audit Middleware
# ===========================================================================
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Auto-audit all state-changing requests (POST, PUT, PATCH, DELETE).
    Adds request_id header to every response.
    Does NOT log GET requests (too noisy; log explicitly in handlers).

    INTEGRATION POINT: Add to app:
        app.add_middleware(AuditMiddleware)
    """

    SKIP_PATHS = {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}
    LOG_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: StarletteRequest, call_next) -> StarletteResponse:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        # Log state-changing requests
        if (request.method in self.LOG_METHODS and
                request.url.path not in self.SKIP_PATHS and
                response.status_code < 500):

            # Extract user info from request state (set by auth middleware)
            user_id = getattr(request.state, "user_id", None)
            user_email = getattr(request.state, "user_email", None)

            # Determine action from method
            action_map = {
                "POST": AuditAction.CREATE,
                "PUT": AuditAction.UPDATE,
                "PATCH": AuditAction.UPDATE,
                "DELETE": AuditAction.DELETE,
            }
            action = action_map.get(request.method, AuditAction.SYSTEM)

            # Extract module from path: /api/v1/finance/... → "finance"
            parts = request.url.path.strip("/").split("/")
            module = parts[2] if len(parts) > 2 else "unknown"

            audit_status = AuditStatus.SUCCESS if response.status_code < 400 else (
                AuditStatus.DENIED if response.status_code == 403 else AuditStatus.FAILURE
            )

            # Fire-and-forget audit log (don't block response)
            # In production use a queue/task for this
            import asyncio
            asyncio.create_task(self._log_request(
                user_id=user_id, user_email=user_email,
                action=action, module=module,
                path=request.url.path, method=request.method,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                request_id=request_id,
                status=audit_status,
                status_code=response.status_code,
            ))

        return response

    async def _log_request(self, **kwargs) -> None:
        """Log to DB asynchronously — separate session."""
        try:
            async with _SessionLocal() as db:
                entry = AuditLog(
                    user_id=kwargs.get("user_id"),
                    user_email=kwargs.get("user_email"),
                    action=kwargs["action"],
                    module=kwargs["module"],
                    resource_description=f"{kwargs['method']} {kwargs['path']}",
                    ip_address=kwargs.get("ip_address"),
                    user_agent=kwargs.get("user_agent"),
                    request_id=kwargs.get("request_id"),
                    status=kwargs["status"],
                )
                db.add(entry)
                await db.commit()
        except Exception:
            pass  # Never crash the request pipeline
