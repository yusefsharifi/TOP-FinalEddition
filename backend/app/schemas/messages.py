"""
Messages Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.messages import MessagePriority, NotificationSeverity

_ro = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    participant_ids: list[int] = Field(..., min_length=1)
    is_group: bool = False


class ConversationResponse(BaseModel):
    model_config = _ro
    id: int
    title: Optional[str] = None
    is_group: bool
    created_by_id: Optional[int] = None
    created_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    priority: MessagePriority = MessagePriority.NORMAL
    parent_message_id: Optional[int] = None


class MessageResponse(BaseModel):
    model_config = _ro
    id: int
    conversation_id: int
    sender_id: int
    content: str
    priority: MessagePriority
    parent_message_id: Optional[int] = None
    created_at: datetime


class NotificationCreate(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    severity: NotificationSeverity = NotificationSeverity.INFO


class NotificationResponse(BaseModel):
    model_config = _ro
    id: int
    user_id: int
    title: str
    message: str
    severity: NotificationSeverity
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
