"""
Messages Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.messages import (
    Conversation, ConversationParticipant, Message, Notification,
)


class ConversationCRUD:
    async def get(self, db: AsyncSession, conv_id: int) -> Optional[Conversation]:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conv_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[Conversation]]:
        participant_ids = select(ConversationParticipant.conversation_id).where(
            ConversationParticipant.user_id == user_id
        )
        q = (
            select(Conversation)
            .where(Conversation.id.in_(participant_ids))
            .order_by(Conversation.created_at.desc())
        )
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def is_participant(self, db: AsyncSession, conv_id: int, user_id: int) -> bool:
        result = await db.execute(
            select(ConversationParticipant.id).where(
                ConversationParticipant.conversation_id == conv_id,
                ConversationParticipant.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None


class MessageCRUD:
    async def list_by_conversation(
        self,
        db: AsyncSession,
        conv_id: int,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[Message]]:
        q = (
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at.desc())
        )
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows


class NotificationCRUD:
    async def list_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        unread_only: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[Notification]]:
        q = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        if unread_only:
            q = q.where(Notification.is_read == False)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def unread_count(self, db: AsyncSession, user_id: int) -> int:
        return (await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )).scalar() or 0


# Singletons
conversation_crud = ConversationCRUD()
message_crud = MessageCRUD()
user_notification_crud = NotificationCRUD()
