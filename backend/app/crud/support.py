"""
Support Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.support import (
    ArticleStatus, KBArticle, KBCategory, SupportTeam, SupportTeamMember,
    Ticket, TicketCategory, TicketComment, TicketPriority, TicketStatus,
)


class TicketCRUD:
    async def get(self, db: AsyncSession, ticket_id: int) -> Optional[Ticket]:
        result = await db.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def list_my(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[int, Sequence[Ticket]]:
        q = (
            select(Ticket)
            .where(or_(Ticket.requester_user_id == user_id, Ticket.assigned_to_id == user_id))
            .order_by(Ticket.created_at.desc())
        )
        if status:
            q = q.where(Ticket.status == status)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def list_all(
        self,
        db: AsyncSession,
        *,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        category: Optional[TicketCategory] = None,
        assigned_to_id: Optional[int] = None,
        team_id: Optional[int] = None,
        search: Optional[str] = None,
        sla_breached: Optional[bool] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[Ticket]]:
        q = select(Ticket).order_by(Ticket.created_at.desc())
        if status:
            q = q.where(Ticket.status == status)
        if priority:
            q = q.where(Ticket.priority == priority)
        if category:
            q = q.where(Ticket.category == category)
        if assigned_to_id is not None:
            q = q.where(Ticket.assigned_to_id == assigned_to_id)
        if team_id:
            q = q.where(Ticket.assigned_team_id == team_id)
        if sla_breached is not None:
            q = q.where(Ticket.sla_resolution_breached == sla_breached)
        if search:
            term = f"%{search}%"
            q = q.where(or_(
                Ticket.subject.ilike(term),
                Ticket.ticket_number.ilike(term),
                Ticket.requester_name.ilike(term),
            ))
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows


class TicketCommentCRUD:
    async def list(
        self,
        db: AsyncSession,
        ticket_id: int,
        *,
        include_internal: bool = False,
    ) -> Sequence[TicketComment]:
        q = (
            select(TicketComment)
            .where(TicketComment.ticket_id == ticket_id)
            .order_by(TicketComment.created_at.asc())
        )
        if not include_internal:
            q = q.where(TicketComment.is_internal.is_(False))
        return (await db.execute(q)).scalars().all()


class KBCategoryCRUD:
    async def list(self, db: AsyncSession) -> Sequence[KBCategory]:
        q = select(KBCategory).where(KBCategory.is_active.is_(True)).order_by(KBCategory.sort_order)
        return (await db.execute(q)).scalars().all()


class SupportTeamCRUD:
    async def list(self, db: AsyncSession) -> Sequence[SupportTeam]:
        q = select(SupportTeam).where(SupportTeam.is_active.is_(True)).order_by(SupportTeam.name)
        return (await db.execute(q)).scalars().all()


# Singletons
ticket_crud = TicketCRUD()
ticket_comment_crud = TicketCommentCRUD()
kb_category_crud = KBCategoryCRUD()
support_team_crud = SupportTeamCRUD()
