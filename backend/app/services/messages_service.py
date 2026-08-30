"""
Messages Module — Service Layer
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.messages import conversation_crud, message_crud
from app.models.messages import (
    Conversation, ConversationParticipant, Message, MessagePriority,
)


class MessagesError(Exception):
    """Messages business logic error."""
    pass


class MessagesService:
    async def create_conversation(
        self,
        db: AsyncSession,
        *,
        title: Optional[str] = None,
        participant_ids: list[int],
        is_group: bool = False,
        created_by_id: int,
    ) -> Conversation:
        conv = Conversation(
            title=title,
            is_group=is_group,
            created_by_id=created_by_id,
        )
        db.add(conv)
        await db.flush()

        all_participants = list(set(participant_ids + [created_by_id]))
        for uid in all_participants:
            participant = ConversationParticipant(
                conversation_id=conv.id,
                user_id=uid,
            )
            db.add(participant)

        await db.flush()
        await db.refresh(conv)
        return conv

    async def send_message(
        self,
        db: AsyncSession,
        conv_id: int,
        *,
        sender_id: int,
        content: str,
        priority: MessagePriority = MessagePriority.NORMAL,
        parent_message_id: Optional[int] = None,
    ) -> Message:
        conv = await conversation_crud.get(db, conv_id)
        if not conv:
            raise MessagesError("Conversation not found")

        is_participant = await conversation_crud.is_participant(db, conv_id, sender_id)
        if not is_participant:
            raise MessagesError("You are not a participant in this conversation")

        msg = Message(
            conversation_id=conv_id,
            sender_id=sender_id,
            content=content,
            priority=priority,
            parent_message_id=parent_message_id,
        )
        db.add(msg)
        await db.flush()
        await db.refresh(msg)
        return msg

    async def mark_read(
        self,
        db: AsyncSession,
        conv_id: int,
        user_id: int,
    ):
        conv = await conversation_crud.get(db, conv_id)
        if not conv:
            raise MessagesError("Conversation not found")

        from sqlalchemy import select
        participant = (await db.execute(
            select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == conv_id,
                ConversationParticipant.user_id == user_id,
            )
        )).scalar_one_or_none()

        if not participant:
            raise MessagesError("You are not a participant")

        participant.last_read_at = datetime.utcnow()
        await db.flush()
        return {"status": "read"}


messages_service = MessagesService()
