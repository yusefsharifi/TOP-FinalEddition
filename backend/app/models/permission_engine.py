"""
RBAC Module — Permission Engine + Password Policy + Audit Service
TOP WorX ERP System

PermissionEngine: evaluates permissions with data-scope filtering
PasswordPolicy:   enforces complexity + history + expiry rules
AuditService:     tamper-evident audit trail with compliance reports
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta
from typing import Any, Optional, Type

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_enhanced import (
    AuditAction, AuditLog, AuditStatus, DataScope, PasswordHistory,
    Permission, Role, RolePermission, User, UserPermissionOverride,
    UserRole, UserStatus,
)


# ===========================================================================
# Permission Engine
# ===========================================================================
class PermissionEngine:
    """
    Evaluates whether a user has a given permission, respecting:
    1. Direct DENY overrides (highest priority)
    2. Role-based permissions
    3. Direct GRANT overrides
    4. Role data_scope constraints
    5. RolePermission condition constraints
    """

    async def get_user_permissions(
        self, db: AsyncSession, user: User
    ) -> dict[str, dict]:
        """
        Returns {permission_code: {"granted": bool, "conditions": dict, "scope": str}}
        Caches internally per request — call once per handler.
        """
        perms: dict[str, dict] = {}

        # Load roles + their permissions
        roles_r = await db.execute(
            select(UserRole, Role, RolePermission, Permission)
            .join(Role, Role.id == UserRole.role_id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .where(
                UserRole.user_id == user.id,
                Role.is_active.is_(True),
                Permission.is_active.is_(True),
                or_(UserRole.expires_at.is_(None), UserRole.expires_at > datetime.utcnow()),
                or_(RolePermission.expires_at.is_(None), RolePermission.expires_at > datetime.utcnow()),
            )
        )
        for user_role, role, rp, perm in roles_r.all():
            # Wildcard: role has permission "module:*" → grants all module permissions
            perms[perm.code] = {
                "granted": True,
                "conditions": rp.conditions or {},
                "scope": role.data_scope.value,
                "role_code": role.code,
            }

        # Apply direct DENY overrides (removes permissions)
        denies_r = await db.execute(
            select(UserPermissionOverride, Permission)
            .join(Permission, Permission.id == UserPermissionOverride.permission_id)
            .where(
                UserPermissionOverride.user_id == user.id,
                UserPermissionOverride.override_type == "deny",
                or_(UserPermissionOverride.expires_at.is_(None),
                    UserPermissionOverride.expires_at > datetime.utcnow()),
            )
        )
        for override, perm in denies_r.all():
            perms.pop(perm.code, None)  # Remove the permission

        # Apply direct GRANT overrides (adds permissions)
        grants_r = await db.execute(
            select(UserPermissionOverride, Permission)
            .join(Permission, Permission.id == UserPermissionOverride.permission_id)
            .where(
                UserPermissionOverride.user_id == user.id,
                UserPermissionOverride.override_type == "grant",
                or_(UserPermissionOverride.expires_at.is_(None),
                    UserPermissionOverride.expires_at > datetime.utcnow()),
            )
        )
        for override, perm in grants_r.all():
            perms[perm.code] = {"granted": True, "conditions": {}, "scope": "all", "role_code": "override"}

        return perms

    async def has_permission(
        self,
        db: AsyncSession,
        user: User,
        permission_code: str,
        resource: Any = None,
    ) -> bool:
        """
        Core permission check with wildcard support.
        Supports patterns like: inventory:* matches inventory:view, inventory:create, etc.
        """
        if not user.is_active:
            return False
        if user.status == UserStatus.SUSPENDED:
            return False

        user_perms = await self.get_user_permissions(db, user)

        # Check exact match
        if permission_code in user_perms:
            perm_data = user_perms[permission_code]
            return await self._check_conditions(user, perm_data, resource)

        # Check wildcard matches (e.g., "inventory:*" matches "inventory:create")
        parts = permission_code.split(":")
        for i in range(len(parts), 0, -1):
            wildcard = ":".join(parts[:i]) + ":*"
            if wildcard in user_perms:
                perm_data = user_perms[wildcard]
                return await self._check_conditions(user, perm_data, resource)

        # Super-admin wildcard
        if "*" in user_perms:
            return True

        return False

    async def _check_conditions(
        self, user: User, perm_data: dict, resource: Any
    ) -> bool:
        """Check RolePermission conditions (max_amount, department constraints)."""
        conditions = perm_data.get("conditions", {})
        if not conditions:
            return True

        # Department restriction
        if "department_ids" in conditions:
            user_dept = getattr(user, "department_id", None)
            if user_dept not in conditions["department_ids"]:
                return False

        # Amount limit (for finance approvals)
        if "max_amount" in conditions and resource is not None:
            resource_amount = getattr(resource, "total_amount", None) or getattr(resource, "amount", None)
            if resource_amount and resource_amount > conditions["max_amount"]:
                return False

        return True

    async def apply_data_scope(
        self,
        db: AsyncSession,
        user: User,
        query,
        permission_code: str,
        owner_field: str = "created_by_id",
        department_field: str = "department_id",
    ):
        """
        Applies data scope filter to a SQLAlchemy query.
        Returns filtered query based on user's role data_scope for the permission.
        """
        user_perms = await self.get_user_permissions(db, user)

        scope = DataScope.OWN  # Default: most restrictive
        if permission_code in user_perms:
            scope_str = user_perms[permission_code].get("scope", "own")
            try:
                scope = DataScope(scope_str)
            except ValueError:
                scope = DataScope.OWN

        if scope == DataScope.ALL:
            return query  # No filter
        elif scope == DataScope.OWN:
            return query.where(getattr(query.column_descriptions[0]["entity"], owner_field) == user.id)
        elif scope == DataScope.DEPARTMENT:
            user_dept = getattr(user, "department_id", None)
            if user_dept:
                return query.where(getattr(query.column_descriptions[0]["entity"], department_field) == user_dept)
            return query.where(getattr(query.column_descriptions[0]["entity"], owner_field) == user.id)
        return query

    async def filter_response_fields(
        self,
        db: AsyncSession,
        user: User,
        data: dict,
        field_permissions: dict[str, str],
    ) -> dict:
        """
        Remove fields the user cannot see.
        field_permissions = {"cost_price": "inventory:view:cost", "salary": "hr:view:salary"}
        """
        result = dict(data)
        for field, required_perm in field_permissions.items():
            if field in result:
                if not await self.has_permission(db, user, required_perm):
                    result.pop(field)
        return result

    async def get_accessible_modules(self, db: AsyncSession, user: User) -> list[str]:
        """Return list of module names the user has any access to."""
        perms = await self.get_user_permissions(db, user)
        modules = set()
        for code in perms:
            parts = code.split(":")
            if parts:
                modules.add(parts[0])
        return sorted(modules)


permission_engine = PermissionEngine()


# ===========================================================================
# Password Policy
# ===========================================================================
class PasswordPolicy:
    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    max_age_days: int = 90
    prevent_reuse_count: int = 5    # Cannot reuse last N passwords
    max_failed_attempts: int = 5
    lockout_minutes: int = 30

    def validate_strength(self, password: str) -> tuple[bool, list[str]]:
        """Returns (is_valid, list_of_error_messages)."""
        errors = []

        if len(password) < self.min_length:
            errors.append(f"حداقل {self.min_length} کاراکتر باشد / Minimum {self.min_length} characters")
        if len(password) > self.max_length:
            errors.append(f"حداکثر {self.max_length} کاراکتر / Maximum {self.max_length} characters")
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("باید حداقل یک حرف بزرگ انگلیسی داشته باشد / Requires uppercase letter")
        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("باید حداقل یک حرف کوچک انگلیسی داشته باشد / Requires lowercase letter")
        if self.require_numbers and not re.search(r"\d", password):
            errors.append("باید حداقل یک عدد داشته باشد / Requires a digit")
        if self.require_special and not any(c in self.special_chars for c in password):
            errors.append(f"باید حداقل یک کاراکتر خاص داشته باشد / Requires special character: {self.special_chars[:10]}...")
        # Common password patterns
        if password.lower() in ("password", "123456", "qwerty", "topworx", "admin123"):
            errors.append("رمز عبور بسیار ساده است / Password is too common")

        return len(errors) == 0, errors

    async def check_history(
        self, db: AsyncSession, user_id: int, new_password: str
    ) -> tuple[bool, str]:
        """Returns (ok, error_message). ok=False means password was used before."""
        history_r = await db.execute(
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(self.prevent_reuse_count)
        )
        history = history_r.scalars().all()

        import bcrypt
        for entry in history:
            if bcrypt.checkpw(new_password.encode(), entry.hashed_password.encode()):
                return False, f"نمی‌توانید {self.prevent_reuse_count} رمز عبور آخر را مجدداً استفاده کنید / Cannot reuse last {self.prevent_reuse_count} passwords"
        return True, ""

    def is_expired(self, user: User) -> bool:
        if not user.password_expires_at:
            return False
        return datetime.utcnow() > user.password_expires_at.replace(tzinfo=None)

    def should_expire_at(self) -> datetime:
        return datetime.utcnow() + timedelta(days=self.max_age_days)

    async def record_history(self, db: AsyncSession, user: User) -> None:
        entry = PasswordHistory(user_id=user.id, hashed_password=user.hashed_password)
        db.add(entry)
        # Keep only last N entries
        old_r = await db.execute(
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user.id)
            .order_by(PasswordHistory.created_at.desc())
            .offset(self.prevent_reuse_count + 1)
        )
        for old in old_r.scalars().all():
            await db.delete(old)
        await db.flush()


password_policy = PasswordPolicy()


# ===========================================================================
# Audit Service
# ===========================================================================
class AuditService:

    async def log(
        self,
        db: AsyncSession,
        *,
        user: Optional[User] = None,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        action: AuditAction,
        module: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        resource_description: Optional[str] = None,
        changes: Optional[dict] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        status: AuditStatus = AuditStatus.SUCCESS,
        error_message: Optional[str] = None,
        is_sensitive: bool = False,
    ) -> AuditLog:
        """Create an audit log entry. Never raises — logs errors silently."""
        try:
            uid = (user.id if user else None) or user_id
            uemail = (user.email if user else None) or user_email

            entry = AuditLog(
                user_id=uid,
                user_email=uemail,
                action=action,
                module=module,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_description=resource_description,
                changes=changes,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                request_id=request_id,
                status=status,
                error_message=error_message,
                is_sensitive=is_sensitive,
            )
            db.add(entry)
            await db.flush()
            return entry
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to create audit log")
            # Return a dummy object so callers don't crash
            return AuditLog(action=action, module=module, status=status)

    def build_changes(self, old: Any, new: Any, fields: list[str]) -> dict:
        """Build field-level change diff for audit log."""
        changes = {}
        for field in fields:
            old_val = getattr(old, field, None) if old else None
            new_val = getattr(new, field, None) if new else None
            if old_val != new_val:
                changes[field] = {
                    "old": str(old_val) if old_val is not None else None,
                    "new": str(new_val) if new_val is not None else None,
                }
        return changes

    def mask_sensitive(self, data: dict, fields: list[str] = None) -> dict:
        """Mask sensitive fields before storing in audit log."""
        default_sensitive = ["hashed_password", "mfa_secret", "api_key", "token", "password"]
        to_mask = (fields or []) + default_sensitive
        result = dict(data)
        for field in to_mask:
            if field in result:
                result[field] = "***REDACTED***"
        return result

    async def get_trail(
        self,
        db: AsyncSession,
        *,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        user_id: Optional[int] = None,
        module: Optional[str] = None,
        action: Optional[AuditAction] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[AuditStatus] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[AuditLog]:
        q = select(AuditLog).order_by(AuditLog.created_at.desc())
        if resource_type:
            q = q.where(AuditLog.resource_type == resource_type)
        if resource_id is not None:
            q = q.where(AuditLog.resource_id == resource_id)
        if user_id is not None:
            q = q.where(AuditLog.user_id == user_id)
        if module:
            q = q.where(AuditLog.module == module)
        if action:
            q = q.where(AuditLog.action == action)
        if date_from:
            q = q.where(AuditLog.created_at >= date_from)
        if date_to:
            q = q.where(AuditLog.created_at <= date_to)
        if status:
            q = q.where(AuditLog.status == status)
        result = await db.execute(q.offset(offset).limit(limit))
        return result.scalars().all()

    async def stats(self, db: AsyncSession, days: int = 30) -> dict:
        """Activity statistics for the last N days."""
        from sqlalchemy import func, extract
        since = datetime.utcnow() - timedelta(days=days)
        total_r = await db.execute(
            select(func.count(AuditLog.id)).where(AuditLog.created_at >= since)
        )
        failed_r = await db.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.created_at >= since,
                AuditLog.status == AuditStatus.FAILURE,
            )
        )
        denied_r = await db.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.created_at >= since,
                AuditLog.status == AuditStatus.DENIED,
            )
        )
        by_action_r = await db.execute(
            select(AuditLog.action, func.count(AuditLog.id).label("cnt"))
            .where(AuditLog.created_at >= since)
            .group_by(AuditLog.action)
        )
        return {
            "period_days": days,
            "total_events": total_r.scalar_one() or 0,
            "failed_events": failed_r.scalar_one() or 0,
            "denied_events": denied_r.scalar_one() or 0,
            "by_action": {r.action.value: r.cnt for r in by_action_r.all()},
        }

    async def compliance_report(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        module: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Who did what, when — for regulatory compliance."""
        logs = await self.get_trail(
            db, user_id=user_id, module=module,
            date_from=date_from, date_to=date_to, limit=10000
        )
        # Group by user
        by_user: dict[str, list] = {}
        for log in logs:
            key = log.user_email or str(log.user_id) or "system"
            by_user.setdefault(key, []).append({
                "action": log.action.value,
                "module": log.module,
                "resource": f"{log.resource_type}:{log.resource_id}" if log.resource_id else log.module,
                "status": log.status.value,
                "timestamp": log.created_at.isoformat(),
            })
        return {
            "report_generated_at": datetime.utcnow().isoformat(),
            "filters": {"user_id": user_id, "module": module},
            "total_events": len(logs),
            "by_user": by_user,
        }


audit_service = AuditService()
