"""
Messages & Internal Communications Module — FastAPI Router
TOP WorX ERP System

Internal messaging with conversations, messages, and notifications.
Uses SQLAlchemy models from app.models.messages.
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBDep, CurrentUser
from app.models.messages import (
    Conversation, ConversationParticipant, Message, MessageReadReceipt,
    Notification, MessagePriority, NotificationSeverity,
)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    participant_ids: list[int] = Field(..., min_length=1)
    is_group: bool = False


class ConversationResponse(BaseModel):
    id: int
    title: Optional[str] = None
    is_group: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    parent_message_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    priority: MessagePriority
    parent_message_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    severity: NotificationSeverity = NotificationSeverity.INFO


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    severity: NotificationSeverity
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── CONVERSATIONS ────────────────────────────────────────────────────────────

@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    db: DBDep,
    current_user: CurrentUser,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[ConversationResponse]:
    """List conversations the current user is part of."""
    participant_ids = select(ConversationParticipant.conversation_id).where(
        ConversationParticipant.user_id == current_user.id
    )
    q = (
        select(Conversation)
        .where(Conversation.id.in_(participant_ids))
        .order_by(Conversation.created_at.desc())
    )
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [ConversationResponse.model_validate(c) for c in rows]


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> ConversationResponse:
    """Create a new conversation (DM or group chat)."""
    conv = Conversation(
        title=data.title,
        is_group=data.is_group,
        created_by_id=current_user.id,
    )
    db.add(conv)
    await db.flush()

    # Add participants (including creator)
    all_participants = list(set(data.participant_ids + [current_user.id]))
    for uid in all_participants:
        participant = ConversationParticipant(
            conversation_id=conv.id,
            user_id=uid,
        )
        db.add(participant)

    await db.commit()
    await db.refresh(conv)
    return ConversationResponse.model_validate(conv)


@router.get("/conversations/{conv_id}", response_model=ConversationResponse)
async def get_conversation(
    conv_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> ConversationResponse:
    """Get conversation details."""
    conv = await db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    # Verify participation — combined with conversation fetch where possible
    is_participant = (await db.execute(
        select(ConversationParticipant.id).where(
            ConversationParticipant.conversation_id == conv_id,
            ConversationParticipant.user_id == current_user.id,
        )
    )).scalar_one_or_none()
    if not is_participant:
        raise HTTPException(403, "You are not a participant in this conversation")
    return ConversationResponse.model_validate(conv)


# ── MESSAGES ─────────────────────────────────────────────────────────────────

@router.get("/conversations/{conv_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conv_id: int,
    db: DBDep,
    current_user: CurrentUser,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[MessageResponse]:
    """List messages in a conversation."""
    conv = await db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    is_participant = (await db.execute(
        select(ConversationParticipant.id).where(
            ConversationParticipant.conversation_id == conv_id,
            ConversationParticipant.user_id == current_user.id,
        )
    )).scalar_one_or_none()
    if not is_participant:
        raise HTTPException(403, "You are not a participant")

    # Use subquery for efficient message listing
    q = select(Message).where(Message.conversation_id == conv_id).order_by(Message.created_at.desc())
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [MessageResponse.model_validate(m) for m in rows]


@router.post("/conversations/{conv_id}/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    conv_id: int,
    data: MessageCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> MessageResponse:
    """Send a message in a conversation."""
    conv = await db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    is_participant = (await db.execute(
        select(ConversationParticipant.id).where(
            ConversationParticipant.conversation_id == conv_id,
            ConversationParticipant.user_id == current_user.id,
        )
    )).scalar_one_or_none()
    if not is_participant:
        raise HTTPException(403, "You are not a participant")

    msg = Message(
        conversation_id=conv_id,
        sender_id=current_user.id,
        content=data.content,
        priority=data.priority,
        parent_message_id=data.parent_message_id,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return MessageResponse.model_validate(msg)


@router.post("/conversations/{conv_id}/read")
async def mark_conversation_read(
    conv_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Mark all messages in a conversation as read."""
    conv = await db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")

    # Update participant last_read_at
    participant = (await db.execute(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conv_id,
            ConversationParticipant.user_id == current_user.id,
        )
    )).scalar_one_or_none()
    if not participant:
        raise HTTPException(403, "You are not a participant")

    participant.last_read_at = datetime.utcnow()
    await db.commit()
    return {"status": "read"}


# ── NOTIFICATIONS ────────────────────────────────────────────────────────────

@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(
    db: DBDep,
    current_user: CurrentUser,
    unread_only: bool = False,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[NotificationResponse]:
    """List notifications for the current user."""
    q = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc())
    if unread_only:
        q = q.where(Notification.is_read == False)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [NotificationResponse.model_validate(n) for n in rows]


@router.post("/notifications", response_model=NotificationResponse, status_code=201)
async def create_notification(
    data: NotificationCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> NotificationResponse:
    """Create a notification for a user."""
    notif = Notification(
        user_id=data.user_id,
        title=data.title,
        message=data.message,
        severity=data.severity,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return NotificationResponse.model_validate(notif)


@router.post("/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Mark a notification as read."""
    notif = await db.get(Notification, notif_id)
    if not notif:
        raise HTTPException(404, "Notification not found")
    if notif.user_id != current_user.id:
        raise HTTPException(403, "Not your notification")
    notif.is_read = True
    notif.read_at = datetime.utcnow()
    await db.commit()
    return {"status": "read"}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Mark all notifications as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    rows = result.scalars().all()
    for notif in rows:
        notif.is_read = True
        notif.read_at = datetime.utcnow()
    await db.commit()
    return {"marked_read": len(rows)}


@router.get("/notifications/unread-count")
async def unread_notification_count(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Get count of unread notifications."""
    count = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )).scalar() or 0
    return {"unread_count": count}
