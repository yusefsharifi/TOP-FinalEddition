"""
Settings & Administration — SQLAlchemy 2.0 Models
TOP WorX ERP System

System settings, audit logging, and configuration management.
Note: Roles and Permissions are in auth_enhanced.py — this module adds
system-wide settings and extended audit capabilities.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey,
    Index, Integer, JSON, String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


# ── Enums ────────────────────────────────────────────────────────────────────

class SettingCategory(str, enum.Enum):
    GENERAL = "general"
    SECURITY = "security"
    EMAIL = "email"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"
    UI = "ui"
    FINANCE = "finance"
    HR = "hr"
    INVENTORY = "inventory"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"


# ── Models ───────────────────────────────────────────────────────────────────

class SystemSetting(Base):
    """
    Key-value system settings with categories.
    Settings are loaded at startup and cached.
    """
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    value_type: Mapped[str] = mapped_column(String(20), nullable=False, default="string")  # string, int, bool, json
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    category: Mapped[SettingCategory] = mapped_column(
        Enum(SettingCategory), nullable=False, default=SettingCategory.GENERAL, index=True
    )
    is_sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # hides value in UI
    is_readonly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Audit
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_system_settings_category", "category"),
        Index("ix_system_settings_sensitive", "is_sensitive"),
        Index("ix_system_settings_value_type", "value_type"),
    )


class ModuleAuditLog(Base):
    """
    Module-level audit log for tracking user actions across the ERP.
    Complements the AuditLog in auth_enhanced.py with more business-level detail.
    """
    __tablename__ = "module_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Who
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True
    )
    user_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # denormalized for history

    # What
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resource_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Changes
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index("ix_module_audit_module_action", "module", "action"),
        Index("ix_module_audit_resource", "resource_type", "resource_id"),
        Index("ix_module_audit_created", "created_at"),
        Index("ix_module_audit_user_date", "user_id", "created_at"),
    )


class SystemNotification(Base):
    """
    System-wide announcements and notifications (not user-specific).
    Displayed on dashboard or admin panel.
    """
    __tablename__ = "system_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")  # info, warning, error
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    target_roles: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # list of role codes, null = all
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_system_notifications_active", "is_active", "created_at"),
        Index("ix_system_notifications_severity", "severity"),
        Index("ix_system_notifications_expires", "expires_at"),
    )
