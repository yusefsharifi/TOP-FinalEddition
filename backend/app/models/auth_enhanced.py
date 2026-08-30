"""
RBAC Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Enterprise-grade user management with granular permissions:
  User → UserSession (JWT revocation list)
  Role → Permission (M2M via RolePermission)
  User → Role (M2M via UserRole)
  AuditLog (append-only, tamper-evident)

Permission code format: module:action[:scope[:field]]
  Examples:
    inventory:view
    inventory:edit:price        (field-level)
    sales:view:own              (scope-limited)
    sales:view:department
    finance:approve:journal
    admin:user:manage

Data scope hierarchy: OWN < DEPARTMENT < BRANCH < COMPANY < ALL
  A higher scope implies all lower scopes.

Security design notes:
  - Passwords hashed with bcrypt (cost factor 12)
  - MFA secrets encrypted with Fernet (FERNET_KEY env var)
  - Sessions tracked individually for per-device revocation
  - AuditLog is append-only — never delete or update rows
  - Soft-delete on User: deleted_at timestamp, data preserved for audit
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


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class DeviceType(str, enum.Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    API = "api"


class PermissionCategory(str, enum.Enum):
    OPERATIONAL = "operational"
    ADMINISTRATIVE = "administrative"
    SYSTEM = "system"


class RoleType(str, enum.Enum):
    SYSTEM = "system"    # Cannot be deleted or have permissions removed
    CUSTOM = "custom"


class DataScope(str, enum.Enum):
    OWN = "own"              # Only records created by this user
    DEPARTMENT = "department" # Records in user's department
    BRANCH = "branch"
    COMPANY = "company"
    ALL = "all"              # No data scope restriction


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    EXPORT = "export"
    APPROVE = "approve"
    REJECT = "reject"
    SUSPEND = "suspend"
    ACTIVATE = "activate"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"
    SESSION_REVOKE = "session_revoke"
    SYSTEM = "system"


class AuditStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


class Theme(str, enum.Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


# ---------------------------------------------------------------------------
# Permission
# ---------------------------------------------------------------------------
class Permission(Base):
    """
    Granular permission atom.
    code format: module:action[:scope[:field]]
    """
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    category: Mapped[PermissionCategory] = mapped_column(
        Enum(PermissionCategory), nullable=False, default=PermissionCategory.OPERATIONAL
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission"
    )

    __table_args__ = (
        Index("ix_permissions_module", "module"),
        Index("ix_permissions_code", "code"),
    )

    def __repr__(self) -> str:
        return f"<Permission {self.code}>"


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role_type: Mapped[RoleType] = mapped_column(Enum(RoleType), nullable=False, default=RoleType.CUSTOM)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    data_scope: Mapped[DataScope] = mapped_column(
        Enum(DataScope), nullable=False, default=DataScope.OWN
    )
    max_users: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_dashboard: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    allowed_modules: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    parent: Mapped[Optional["Role"]] = relationship("Role", remote_side="Role.id")
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    user_roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="role")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint("level >= 0 AND level <= 10", name="chk_role_level"),
        Index("ix_roles_code", "code"),
    )

    def __repr__(self) -> str:
        return f"<Role {self.code} level={self.level}>"


# ---------------------------------------------------------------------------
# RolePermission  (M2M with conditions)
# ---------------------------------------------------------------------------
class RolePermission(Base):
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Optional conditions: {"max_amount": 50000000, "department_id": [1,2,3]}
    conditions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    granted_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )


# ---------------------------------------------------------------------------
# User (Enhanced)
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Authentication
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)

    # Profile
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name_fa: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name_fa: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # HR link
    employee_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, unique=True
    )

    # Status
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), nullable=False, default=UserStatus.PENDING_VERIFICATION, index=True
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    password_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    force_password_change: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    backup_codes_hashed: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Preferences
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="fa")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="Asia/Tehran")
    theme: Mapped[Theme] = mapped_column(Enum(Theme), nullable=False, default=Theme.SYSTEM)
    notification_preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    password_history: Mapped[list["PasswordHistory"]] = relationship(
        "PasswordHistory", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE and self.deleted_at is None

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_status", "status"),
        Index("ix_users_employee_id", "employee_id"),
    )

    def __repr__(self) -> str:
        return f"<User {self.email} status={self.status}>"


# ---------------------------------------------------------------------------
# UserRole  (M2M with direct permission overrides)
# ---------------------------------------------------------------------------
class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Department context: narrows data_scope even further
    department_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)


# ---------------------------------------------------------------------------
# UserPermissionOverride  (direct grants/denials bypassing roles)
# ---------------------------------------------------------------------------
class UserPermissionOverride(Base):
    """
    Directly grant or deny a permission to a user regardless of their role.
    type=GRANT: adds permission even if role doesn't have it
    type=DENY:  removes permission even if role has it (takes precedence)
    """
    __tablename__ = "user_permission_overrides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False
    )
    override_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "grant" | "deny"
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    granted_by_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", "override_type", name="uq_user_perm_override"),
        CheckConstraint("override_type IN ('grant', 'deny')", name="chk_override_type"),
    )


# ---------------------------------------------------------------------------
# UserSession
# ---------------------------------------------------------------------------
class UserSession(Base):
    """
    Track active sessions for per-device revocation.
    token_jti is the JWT 'jti' claim — checked on every request.
    """
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_jti: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    device_type: Mapped[DeviceType] = mapped_column(Enum(DeviceType), nullable=False, default=DeviceType.DESKTOP)
    device_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoke_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index("ix_user_sessions_jti", "token_jti"),
        Index("ix_user_sessions_user_active", "user_id", "is_active"),
    )


# ---------------------------------------------------------------------------
# PasswordHistory
# ---------------------------------------------------------------------------
class PasswordHistory(Base):
    """Stores hashed history to prevent reuse."""
    __tablename__ = "password_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="password_history")


# ---------------------------------------------------------------------------
# UserInvitation
# ---------------------------------------------------------------------------
class UserInvitation(Base):
    """Pending invitations — time-limited (48 hours)."""
    __tablename__ = "user_invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    invited_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    __table_args__ = (Index("ix_user_invitations_email", "email"),)


# ---------------------------------------------------------------------------
# AuditLog  (append-only, tamper-evident)
# ---------------------------------------------------------------------------
class AuditLog(Base):
    """
    NEVER update or delete rows in this table.
    Indexes are optimised for compliance queries, not writes.
    For high-volume deployments, partition by month on created_at.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Who
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # denorm for history

    # What
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resource_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Details
    changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)   # field-level diff
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Result
    status: Mapped[AuditStatus] = mapped_column(
        Enum(AuditStatus), nullable=False, default=AuditStatus.SUCCESS
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Sensitivity
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_module", "module"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )