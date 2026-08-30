"""
Support Module — Ticket Service + SLA Engine + KB Service
TOP WorX ERP System

TicketService:    full ticket lifecycle with SLA tracking
SLAEngine:        business-hours-aware deadline calculation + breach detection
KBService:        article management + TF-IDF similarity suggestions
RoutingEngine:    auto-assign tickets based on rules
"""
from __future__ import annotations

import math
import random
import re
import string
from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, Union

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.support import (
    CannedResponse, CommentAuthorType, KBArticle, KBCategory,
    RequesterType, RoutingEngine as RoutingEngineModel,
    SLAPolicy, SupportTeam, SupportTeamMember,
    Ticket, TicketCategory, TicketComment, TicketPriority,
    TicketRoutingRule, TicketStatus, ArticleStatus,
)


class SupportError(Exception):
    pass


JALALI_YEAR = 1403


def _rand(n: int = 5) -> str:
    return "".join(random.choices(string.digits, k=n))


# ===========================================================================
# SLA Engine
# ===========================================================================
class SLAEngine:
    """
    Calculates SLA deadlines accounting for business hours and work days.
    Iranian work week: Saturday–Wednesday (weekday indices 5,6,0,1,2).
    Default business hours: 08:00–17:00 Tehran time.
    """

    DEFAULT_WORK_DAYS = [5, 6, 0, 1, 2]  # Sat, Sun, Mon, Tue, Wed
    DEFAULT_RESPONSE_MINUTES = {
        "low": 240, "medium": 120, "high": 60, "critical": 15, "emergency": 5
    }
    DEFAULT_RESOLUTION_MINUTES = {
        "low": 2880, "medium": 1440, "high": 480, "critical": 240, "emergency": 60
    }

    def _is_business_hours(self, dt: datetime, policy: SLAPolicy) -> bool:
        work_days = policy.work_days or self.DEFAULT_WORK_DAYS
        if dt.weekday() not in work_days:
            return False
        start_h, start_m = map(int, policy.business_hours_start.split(":"))
        end_h, end_m = map(int, policy.business_hours_end.split(":"))
        current_minutes = dt.hour * 60 + dt.minute
        return start_h * 60 + start_m <= current_minutes < end_h * 60 + end_m

    def add_business_minutes(self, start: datetime, minutes: int, policy: SLAPolicy) -> datetime:
        """Add N business minutes to a datetime, skipping non-work hours and days."""
        work_days = policy.work_days or self.DEFAULT_WORK_DAYS
        start_h, start_m = map(int, policy.business_hours_start.split(":"))
        end_h, end_m = map(int, policy.business_hours_end.split(":"))
        business_minutes_per_day = (end_h * 60 + end_m) - (start_h * 60 + start_m)

        current = start
        remaining = minutes

        # If starting outside business hours, advance to next business start
        while not self._is_business_hours(current, policy):
            current += timedelta(minutes=1)
            if current.hour == end_h and current.minute == end_m:
                # Move to next work day start
                current = current.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                current += timedelta(days=1)
                while current.weekday() not in work_days:
                    current += timedelta(days=1)

        while remaining > 0:
            # Minutes left in today's business hours
            current_minutes = current.hour * 60 + current.minute
            end_of_day = end_h * 60 + end_m
            available_today = end_of_day - current_minutes

            if remaining <= available_today:
                current += timedelta(minutes=remaining)
                remaining = 0
            else:
                remaining -= available_today
                # Move to next work day
                current = current.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                current += timedelta(days=1)
                while current.weekday() not in work_days:
                    current += timedelta(days=1)

        return current

    def calculate_deadlines(
        self, ticket: Ticket, policy: SLAPolicy, from_time: Optional[datetime] = None
    ) -> tuple[datetime, datetime]:
        """Returns (response_deadline, resolution_deadline)."""
        start = from_time or ticket.created_at.replace(tzinfo=None) if ticket.created_at else datetime.utcnow()
        priority = ticket.priority.value.lower()
        response_mins = (policy.response_times or self.DEFAULT_RESPONSE_MINUTES).get(priority, 120)
        resolution_mins = (policy.resolution_times or self.DEFAULT_RESOLUTION_MINUTES).get(priority, 1440)
        response_deadline = self.add_business_minutes(start, response_mins, policy)
        resolution_deadline = self.add_business_minutes(start, resolution_mins, policy)
        return response_deadline, resolution_deadline

    def check_breach(self, ticket: Ticket) -> tuple[bool, bool]:
        """Returns (response_breached, resolution_breached) based on current time."""
        now = datetime.utcnow()
        response_breached = (
            ticket.sla_response_deadline is not None
            and now > ticket.sla_response_deadline.replace(tzinfo=None)
            and ticket.first_response_at is None
        )
        resolution_breached = (
            ticket.sla_resolution_deadline is not None
            and now > ticket.sla_resolution_deadline.replace(tzinfo=None)
            and ticket.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED)
        )
        return response_breached, resolution_breached


sla_engine = SLAEngine()


# ===========================================================================
# Routing Engine
# ===========================================================================
class RoutingService:

    async def find_matching_rule(
        self,
        db: AsyncSession,
        ticket_category: str,
        ticket_priority: str,
        requester_type: str,
        subject: str,
        description: str,
    ) -> Optional[TicketRoutingRule]:
        """Find first matching routing rule (ordered by sort_order)."""
        rules_r = await db.execute(
            select(TicketRoutingRule)
            .where(TicketRoutingRule.is_active.is_(True))
            .order_by(TicketRoutingRule.sort_order.asc())
        )
        rules = rules_r.scalars().all()
        text = (subject + " " + description).lower()

        for rule in rules:
            if rule.category and rule.category != ticket_category:
                continue
            if rule.priority and rule.priority != ticket_priority:
                continue
            if rule.requester_type and rule.requester_type != requester_type:
                continue
            if rule.keywords:
                if not any(kw.lower() in text for kw in rule.keywords):
                    continue
            return rule
        return None

    async def get_next_assignee(self, db: AsyncSession, team: SupportTeam) -> Optional[int]:
        """Round-robin assignment within team."""
        members_r = await db.execute(
            select(SupportTeamMember.user_id)
            .where(SupportTeamMember.team_id == team.id)
            .order_by(SupportTeamMember.joined_at)
        )
        member_ids = [r.user_id for r in members_r.all()]
        if not member_ids:
            return None

        idx = team.round_robin_index % len(member_ids)
        assignee_id = member_ids[idx]
        team.round_robin_index = (team.round_robin_index + 1) % len(member_ids)
        await db.flush()
        return assignee_id


routing_service = RoutingService()


# ===========================================================================
# Ticket Service
# ===========================================================================
class TicketService:

    async def _get_default_sla(self, db: AsyncSession) -> Optional[SLAPolicy]:
        r = await db.execute(
            select(SLAPolicy).where(SLAPolicy.is_default.is_(True), SLAPolicy.is_active.is_(True))
        )
        return r.scalar_one_or_none()

    async def create_ticket(
        self,
        db: AsyncSession,
        *,
        requester_type: RequesterType,
        requester_name: str,
        requester_email: Optional[str] = None,
        requester_phone: Optional[str] = None,
        requester_customer_id: Optional[int] = None,
        requester_user_id: Optional[int] = None,
        category: TicketCategory,
        subcategory: Optional[str] = None,
        priority: TicketPriority = TicketPriority.MEDIUM,
        subject: str = "",
        description: str = "",
        attachments: Optional[list] = None,
        tags: Optional[list] = None,
        related_module: Optional[str] = None,
        related_record_id: Optional[int] = None,
        related_record_ref: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Ticket:
        """Full ticket creation with auto-routing and SLA assignment."""
        ticket_number = f"TKT-{JALALI_YEAR}-{_rand(5)}"

        ticket = Ticket(
            ticket_number=ticket_number,
            requester_type=requester_type,
            requester_customer_id=requester_customer_id,
            requester_user_id=requester_user_id,
            requester_name=requester_name,
            requester_email=requester_email,
            requester_phone=requester_phone,
            category=category,
            subcategory=subcategory,
            priority=priority,
            subject=subject,
            description=description,
            attachments=attachments,
            tags=tags,
            related_module=related_module,
            related_record_id=related_record_id,
            related_record_ref=related_record_ref,
            status=TicketStatus.NEW,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(ticket)
        await db.flush()

        # Auto-routing
        rule = await routing_service.find_matching_rule(
            db, category.value, priority.value, requester_type.value, subject, description
        )

        if rule:
            if rule.sla_policy_id:
                ticket.sla_policy_id = rule.sla_policy_id
            if rule.assign_to_team_id:
                ticket.assigned_team_id = rule.assign_to_team_id
                if rule.assign_to_user_id:
                    ticket.assigned_to_id = rule.assign_to_user_id
                    ticket.assigned_at = datetime.utcnow()
                    ticket.status = TicketStatus.ASSIGNED
                elif rule.assign_to_team_id:
                    # Round-robin within team
                    team_r = await db.execute(select(SupportTeam).where(SupportTeam.id == rule.assign_to_team_id))
                    team = team_r.scalar_one_or_none()
                    if team and team.auto_assign:
                        assignee_id = await routing_service.get_next_assignee(db, team)
                        if assignee_id:
                            ticket.assigned_to_id = assignee_id
                            ticket.assigned_at = datetime.utcnow()
                            ticket.status = TicketStatus.ASSIGNED

            # Auto-response
            if rule.auto_response_enabled:
                auto_comment = TicketComment(
                    ticket_id=ticket.id,
                    author_type=CommentAuthorType.SYSTEM,
                    author_name="پشتیبانی TOP WorX / Support",
                    content=self._get_auto_response(rule.auto_response_template, ticket),
                    is_internal=False,
                    created_by_id=None,
                )
                db.add(auto_comment)

        # Calculate SLA deadlines
        sla_policy = None
        if ticket.sla_policy_id:
            sla_r = await db.execute(select(SLAPolicy).where(SLAPolicy.id == ticket.sla_policy_id))
            sla_policy = sla_r.scalar_one_or_none()
        if not sla_policy:
            sla_policy = await self._get_default_sla(db)
        if sla_policy:
            ticket.sla_policy_id = sla_policy.id
            resp_dl, res_dl = sla_engine.calculate_deadlines(ticket, sla_policy)
            ticket.sla_response_deadline = resp_dl
            ticket.sla_resolution_deadline = res_dl

        await db.flush()
        return ticket

    def _get_auto_response(self, template_name: Optional[str], ticket: Ticket) -> str:
        templates = {
            "general": (
                f"با سلام {ticket.requester_name} عزیز،\n\n"
                f"تیکت شما با شماره {ticket.ticket_number} دریافت شد. "
                f"تیم پشتیبانی ما در اسرع وقت با شما تماس خواهد گرفت.\n\n"
                f"با احترام — پشتیبانی TOP WorX"
            ),
            "technical": (
                f"Dear {ticket.requester_name},\n\n"
                f"Your technical support ticket {ticket.ticket_number} has been received. "
                f"Our technical team will respond within the SLA timeframe.\n\nThank you."
            ),
        }
        return templates.get(template_name or "general", templates["general"])

    async def assign_ticket(
        self,
        db: AsyncSession,
        ticket: Ticket,
        assignee_id: int,
        assigned_by_id: int,
    ) -> Ticket:
        was_unassigned = ticket.assigned_to_id is None
        ticket.assigned_to_id = assignee_id
        ticket.assigned_at = datetime.utcnow()
        ticket.status = TicketStatus.ASSIGNED
        ticket.updated_by_id = assigned_by_id

        # Add system comment
        db.add(TicketComment(
            ticket_id=ticket.id,
            author_type=CommentAuthorType.SYSTEM,
            author_name="System",
            content=f"تیکت به کاربر {assignee_id} تخصیص داده شد.",
            is_internal=True,
            created_by_id=assigned_by_id,
        ))
        await db.flush()
        return ticket

    async def add_comment(
        self,
        db: AsyncSession,
        ticket: Ticket,
        content: str,
        author_type: CommentAuthorType,
        author_name: str,
        author_user_id: Optional[int] = None,
        author_customer_id: Optional[int] = None,
        is_internal: bool = False,
        attachments: Optional[list] = None,
        canned_response_id: Optional[int] = None,
    ) -> TicketComment:
        comment = TicketComment(
            ticket_id=ticket.id,
            author_type=author_type,
            author_user_id=author_user_id,
            author_customer_id=author_customer_id,
            author_name=author_name,
            content=content,
            is_internal=is_internal,
            attachments=attachments,
            is_canned=canned_response_id is not None,
            canned_response_id=canned_response_id,
            created_by_id=author_user_id,
        )
        db.add(comment)

        now = datetime.utcnow()

        if author_type == CommentAuthorType.CUSTOMER:
            ticket.last_customer_reply_at = now
            # Customer replied → set back to In Progress if Pending
            if ticket.status == TicketStatus.PENDING:
                ticket.status = TicketStatus.IN_PROGRESS

        elif author_type in (CommentAuthorType.AGENT, CommentAuthorType.ADMIN):
            ticket.last_agent_reply_at = now
            if not is_internal:
                # Set status to PENDING (waiting for customer)
                if ticket.status == TicketStatus.IN_PROGRESS:
                    ticket.status = TicketStatus.PENDING
                # Record first response time
                if not ticket.first_response_at:
                    ticket.first_response_at = now
                    if ticket.created_at:
                        elapsed = (now - ticket.created_at.replace(tzinfo=None)).total_seconds() / 60
                        ticket.first_response_minutes = int(elapsed)
                    # Check SLA response breach
                    if ticket.sla_response_deadline and now > ticket.sla_response_deadline.replace(tzinfo=None):
                        ticket.sla_response_breached = True

            # Update canned response use count
            if canned_response_id:
                cr_r = await db.execute(select(CannedResponse).where(CannedResponse.id == canned_response_id))
                cr = cr_r.scalar_one_or_none()
                if cr:
                    cr.use_count += 1

        ticket.status = TicketStatus.IN_PROGRESS if ticket.status == TicketStatus.ASSIGNED else ticket.status
        await db.flush()
        return comment

    async def resolve_ticket(
        self,
        db: AsyncSession,
        ticket: Ticket,
        resolution_note: str,
        resolved_by_id: int,
    ) -> Ticket:
        if ticket.status in (TicketStatus.CLOSED, TicketStatus.RESOLVED):
            raise SupportError(f"Ticket {ticket.ticket_number} is already {ticket.status.value}")

        now = datetime.utcnow()
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = now
        ticket.updated_by_id = resolved_by_id

        # Calculate resolution time
        if ticket.created_at:
            elapsed = (now - ticket.created_at.replace(tzinfo=None)).total_seconds() / 60
            ticket.resolution_minutes = int(elapsed)

        # Check SLA resolution breach
        if ticket.sla_resolution_deadline and now > ticket.sla_resolution_deadline.replace(tzinfo=None):
            ticket.sla_resolution_breached = True

        # Resolution comment
        db.add(TicketComment(
            ticket_id=ticket.id,
            author_type=CommentAuthorType.AGENT,
            author_user_id=resolved_by_id,
            author_name="Agent",
            content=resolution_note,
            is_internal=False,
            created_by_id=resolved_by_id,
        ))

        await db.flush()
        # TODO: send satisfaction survey email
        return ticket

    async def close_ticket(self, db: AsyncSession, ticket: Ticket, closed_by_id: int) -> Ticket:
        if ticket.status not in (TicketStatus.RESOLVED, TicketStatus.PENDING):
            raise SupportError("Only RESOLVED or PENDING tickets can be closed")
        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = datetime.utcnow()
        ticket.updated_by_id = closed_by_id
        await db.flush()
        return ticket

    async def reopen_ticket(
        self, db: AsyncSession, ticket: Ticket, reason: str, requester_id: int, is_customer: bool = False
    ) -> Ticket:
        if ticket.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            raise SupportError("Only RESOLVED or CLOSED tickets can be reopened")
        ticket.status = TicketStatus.REOPENED
        ticket.resolved_at = None
        ticket.updated_by_id = requester_id if not is_customer else None
        db.add(TicketComment(
            ticket_id=ticket.id,
            author_type=CommentAuthorType.CUSTOMER if is_customer else CommentAuthorType.AGENT,
            author_user_id=None if is_customer else requester_id,
            author_customer_id=requester_id if is_customer else None,
            author_name="Customer" if is_customer else "Agent",
            content=f"Ticket reopened: {reason}",
            is_internal=False,
        ))
        await db.flush()
        return ticket

    async def submit_satisfaction(
        self,
        db: AsyncSession,
        ticket: Ticket,
        rating: int,
        comment: Optional[str] = None,
    ) -> Ticket:
        if ticket.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            raise SupportError("Can only rate resolved or closed tickets")
        if not 1 <= rating <= 5:
            raise SupportError("Rating must be 1–5")
        ticket.satisfaction_rating = rating
        ticket.satisfaction_comment = comment
        ticket.satisfaction_submitted_at = datetime.utcnow()
        await db.flush()
        return ticket

    async def check_sla_breaches(self, db: AsyncSession) -> dict:
        """
        Cron job: scan open tickets for SLA violations.
        Called by Celery beat every 5 minutes.
        """
        now = datetime.utcnow()
        open_statuses = [TicketStatus.NEW, TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS,
                        TicketStatus.PENDING, TicketStatus.REOPENED, TicketStatus.ESCALATED]

        # Response breaches
        response_breached_r = await db.execute(
            select(Ticket).where(
                Ticket.status.in_(open_statuses),
                Ticket.first_response_at.is_(None),
                Ticket.sla_response_deadline < now,
                Ticket.sla_response_breached.is_(False),
            )
        )
        response_breached = response_breached_r.scalars().all()
        for t in response_breached:
            t.sla_response_breached = True

        # Resolution breaches
        resolution_breached_r = await db.execute(
            select(Ticket).where(
                Ticket.status.in_(open_statuses),
                Ticket.sla_resolution_deadline < now,
                Ticket.sla_resolution_breached.is_(False),
            )
        )
        resolution_breached = resolution_breached_r.scalars().all()
        for t in resolution_breached:
            t.sla_resolution_breached = True
            # Escalate
            if t.sla_policy_id:
                sla_r = await db.execute(select(SLAPolicy).where(SLAPolicy.id == t.sla_policy_id))
                sla = sla_r.scalar_one_or_none()
                if sla and sla.escalation_enabled and t.status != TicketStatus.ESCALATED:
                    t.status = TicketStatus.ESCALATED
                    # TODO: notify sla.escalation_manager_id

        await db.flush()
        return {
            "response_breaches": len(response_breached),
            "resolution_breaches": len(resolution_breached),
        }

    async def get_performance_metrics(
        self,
        db: AsyncSession,
        team_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """SLA compliance, resolution times, CSAT scores."""
        q = select(Ticket)
        if team_id:
            q = q.where(Ticket.assigned_team_id == team_id)
        if date_from:
            q = q.where(Ticket.created_at >= date_from)
        if date_to:
            q = q.where(Ticket.created_at <= date_to)

        total_r = await db.execute(select(func.count(Ticket.id)).select_from(q.subquery()))
        total = total_r.scalar_one() or 0

        resolved_r = await db.execute(
            select(func.count(Ticket.id), func.avg(Ticket.resolution_minutes),
                   func.avg(Ticket.first_response_minutes))
            .select_from(q.subquery())
            .where(Ticket.resolution_minutes.isnot(None))
        )
        resolved_row = resolved_r.one()

        sla_ok_r = await db.execute(
            select(func.count(Ticket.id))
            .select_from(q.subquery())
            .where(Ticket.sla_resolution_breached.is_(False), Ticket.resolution_minutes.isnot(None))
        )
        sla_ok = sla_ok_r.scalar_one() or 0

        csat_r = await db.execute(
            select(func.avg(Ticket.satisfaction_rating), func.count(Ticket.satisfaction_rating))
            .select_from(q.subquery())
            .where(Ticket.satisfaction_rating.isnot(None))
        )
        csat_row = csat_r.one()

        resolved_count = resolved_row[0] or 0
        avg_resolution = float(resolved_row[1] or 0)
        avg_first_response = float(resolved_row[2] or 0)

        return {
            "total_tickets": total,
            "resolved_tickets": resolved_count,
            "resolution_rate_pct": round(resolved_count / total * 100, 1) if total else 0,
            "avg_resolution_minutes": round(avg_resolution, 1),
            "avg_first_response_minutes": round(avg_first_response, 1),
            "sla_compliance_pct": round(sla_ok / resolved_count * 100, 1) if resolved_count else 0,
            "avg_csat_score": round(float(csat_row[0] or 0), 2),
            "csat_responses": csat_row[1] or 0,
        }


ticket_service = TicketService()


# ===========================================================================
# Knowledge Base Service
# ===========================================================================
class KBService:

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenizer: lowercase words + Persian word splitting."""
        return re.findall(r"[\w\u0600-\u06FF]+", text.lower())

    def _tf_idf_score(self, query_tokens: list[str], article_tokens: list[str]) -> float:
        """Simple TF-IDF-like relevance score."""
        if not article_tokens or not query_tokens:
            return 0.0
        query_set = set(query_tokens)
        matches = sum(1 for t in article_tokens if t in query_set)
        # Normalise by article length
        return matches / (1 + math.log(1 + len(article_tokens)))

    async def suggest_for_ticket(
        self,
        db: AsyncSession,
        subject: str,
        description: str,
        max_results: int = 5,
        is_internal: bool = False,
    ) -> list[dict]:
        """
        Suggest KB articles relevant to a ticket or search query.
        Uses TF-IDF word overlap. For production replace with
        PostgreSQL full-text search or an embedding model.
        DECISION POINT ⚙️: Replace with pg_trgm or pgvector for better accuracy.
        """
        query_text = f"{subject} {description}"
        query_tokens = self._tokenize(query_text)

        q = select(KBArticle).where(KBArticle.status == ArticleStatus.PUBLISHED)
        if not is_internal:
            q = q.where(KBArticle.is_internal.is_(False))

        articles = (await db.execute(q)).scalars().all()

        scored = []
        for article in articles:
            article_text = f"{article.title} {article.title_fa or ''} {article.excerpt or ''} {article.content[:500]}"
            article_tokens = self._tokenize(article_text)
            score = self._tf_idf_score(query_tokens, article_tokens)
            if score > 0:
                scored.append((score, article))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": a.id, "title": a.title, "title_fa": a.title_fa,
                "slug": a.slug, "excerpt": a.excerpt, "score": round(s, 4),
            }
            for s, a in scored[:max_results]
        ]

    async def get_article(self, db: AsyncSession, slug: str, increment_view: bool = True) -> Optional[KBArticle]:
        r = await db.execute(select(KBArticle).where(KBArticle.slug == slug))
        article = r.scalar_one_or_none()
        if article and increment_view:
            article.view_count += 1
            await db.flush()
        return article

    async def rate_article(self, db: AsyncSession, article_id: int, helpful: bool) -> None:
        r = await db.execute(select(KBArticle).where(KBArticle.id == article_id))
        article = r.scalar_one_or_none()
        if article:
            if helpful:
                article.helpful_count += 1
            else:
                article.not_helpful_count += 1
            await db.flush()

    async def search(
        self,
        db: AsyncSession,
        query: str,
        category_id: Optional[int] = None,
        is_internal: bool = False,
        limit: int = 20,
    ) -> list[KBArticle]:
        """Search articles by text (simple ILIKE; upgrade to pg_trgm for production)."""
        term = f"%{query}%"
        from sqlalchemy import or_
        q = select(KBArticle).where(
            KBArticle.status == ArticleStatus.PUBLISHED,
            or_(
                KBArticle.title.ilike(term),
                KBArticle.title_fa.ilike(term),
                KBArticle.content.ilike(term),
            )
        )
        if not is_internal:
            q = q.where(KBArticle.is_internal.is_(False))
        if category_id:
            q = q.where(KBArticle.category_id == category_id)
        q = q.order_by(KBArticle.view_count.desc()).limit(limit)
        return (await db.execute(q)).scalars().all()


kb_service = KBService()
