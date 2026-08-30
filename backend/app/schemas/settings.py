"""
Settings Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.settings import AuditAction, SettingCategory

_ro = ConfigDict(from_attributes=True)


class SettingCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str
    value_type: str = Field("string", max_length=20)
    description: Optional[str] = None
    category: SettingCategory = SettingCategory.GENERAL
    is_sensitive: bool = False
    is_readonly: bool = False


class SettingResponse(BaseModel):
    model_config = _ro
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


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    permission_codes: list[str] = Field(default_factory=list)


class RoleResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime


class UserRoleAssign(BaseModel):
    user_id: int
    role_code: str
    expires_at: Optional[datetime] = None


class AuditLogResponse(BaseModel):
    model_config = _ro
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


class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    severity: str = Field("info", max_length=20)
    target_roles: Optional[list[str]] = None


class NotificationResponse(BaseModel):
    model_config = _ro
    id: int
    title: str
    message: str
    severity: str
    is_active: bool
    target_roles: Optional[list] = None
    expires_at: Optional[datetime] = None
    created_by_id: int
    created_at: datetime
