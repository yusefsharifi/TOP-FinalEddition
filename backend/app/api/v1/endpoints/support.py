"""
Support & Ticketing Module — FastAPI Router
TOP WorX ERP System

Customer portal: /support/tickets, /support/kb
Agent interface: /support/tickets/all, /support/dashboard, /support/reports
Admin:           /support/teams, /support/sla, /support/routing

INTEGRATION POINT: Register in api.py:
    from app.api.api_v1.endpoints.support import router as support_router
    api_router.include_router(support_router, prefix="/support", tags=["support"])
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, or_, select


from app.models.support import (
    ArticleStatus, CannedResponse, CommentAuthorType, KBArticle,
    KBCategory, RequesterType, SLAPolicy, SupportTeam,
    SupportTeamMember, Ticket, TicketCategory, TicketComment,
    TicketPriority, TicketRoutingRule, TicketStatus,
)
from app.services.support_service import (
    SupportError, kb_service, sla_engine, ticket_service,
)

# ---------------------------------------------------------------------------
# Real dependencies from centralized deps module
# ---------------------------------------------------------------------------
from app.api.deps import DBDep, CurrentUser

# Alias for backward compatibility — endpoints use `cu: CU`
CU = CurrentUser

router = APIRouter()


def _not_found(msg: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail=msg)


def _bad(msg: str) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


# ===========================================================================
# CUSTOMER PORTAL — /support/tickets
# ===========================================================================

@router.post("/tickets", status_code=201)
async def create_ticket(data: dict, db: DBDep, cu: CU) -> dict:
    """
    Create ticket from customer or internal user.
    Pass requester_type: "customer" | "employee"
    """
    try:
        ticket = await ticket_service.create_ticket(
            db,
            requester_type=RequesterType(data.get("requester_type", "customer")),
            requester_name=data.get("requester_name", f"{cu.first_name} {cu.last_name}"),
            requester_email=data.get("requester_email", cu.email),
            requester_phone=data.get("requester_phone"),
            requester_customer_id=data.get("requester_customer_id"),
            requester_user_id=data.get("requester_user_id", cu.id),
            category=TicketCategory(data.get("category", "general")),
            subcategory=data.get("subcategory"),
            priority=TicketPriority(data.get("priority", "medium")),
            subject=data["subject"],
            description=data["description"],
            attachments=data.get("attachments"),
            tags=data.get("tags"),
            related_module=data.get("related_module"),
            related_record_id=data.get("related_record_id"),
            related_record_ref=data.get("related_record_ref"),
            user_id=cu.id,
        )
    except SupportError as exc:
        raise _bad(str(exc))
    await db.commit()
    return _fmt_ticket(ticket)


@router.get("/tickets")
async def my_tickets(
    db: DBDep, cu: CU,
    status_filter: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[dict]:
    """Customer: see only own tickets. Agent: see all (use /tickets/all)."""
    q = (
        select(Ticket)
        .where(
            or_(
                Ticket.requester_user_id == cu.id,
                Ticket.assigned_to_id == cu.id,
            )
        )
        .order_by(Ticket.created_at.desc())
    )
    if status_filter:
        q = q.where(Ticket.status == status_filter)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [_fmt_ticket(t) for t in rows]


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int, db: DBDep, cu: CU) -> dict:
    """Ticket detail with full comment thread."""
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")

    comments_r = await db.execute(
        select(TicketComment)
        .where(
            TicketComment.ticket_id == ticket_id,
            TicketComment.is_internal.is_(False),  # customers don't see internal notes
        )
        .order_by(TicketComment.created_at.asc())
    )
    comments = comments_r.scalars().all()

    return {
        **_fmt_ticket(ticket),
        "comments": [_fmt_comment(c) for c in comments],
    }


@router.post("/tickets/{ticket_id}/reply", status_code=201)
async def customer_reply(ticket_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    """Customer adds a reply to their ticket."""
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")

    # Only the requester can reply (or an agent)
    try:
        comment = await ticket_service.add_comment(
            db, ticket,
            content=data["content"],
            author_type=CommentAuthorType.CUSTOMER,
            author_name=cu.first_name + " " + cu.last_name,
            author_user_id=cu.id,
            is_internal=False,
            attachments=data.get("attachments"),
        )
    except SupportError as exc:
        raise _bad(str(exc))
    await db.commit()
    return _fmt_comment(comment)


@router.post("/tickets/{ticket_id}/close")
async def customer_close_ticket(ticket_id: int, db: DBDep, cu: CU) -> dict:
    """Customer marks resolved ticket as closed."""
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")
    try:
        ticket = await ticket_service.close_ticket(db, ticket, closed_by_id=cu.id)
    except SupportError as exc:
        raise _bad(str(exc))
    await db.commit()
    return {"status": "closed", "ticket_number": ticket.ticket_number}


@router.post("/tickets/{ticket_id}/rate")
async def rate_ticket(ticket_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    """Submit CSAT rating (1–5) after resolution."""
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")
    try:
        ticket = await ticket_service.submit_satisfaction(
            db, ticket,
            rating=int(data["rating"]),
            comment=data.get("comment"),
        )
    except SupportError as exc:
        raise _bad(str(exc))
    await db.commit()
    return {"status": "rated", "rating": ticket.satisfaction_rating}


# ===========================================================================
# KNOWLEDGE BASE — Customer & Agent
# ===========================================================================

@router.get("/kb")
async def list_kb_articles(
    db: DBDep, cu: CU,
    category_id: Optional[int] = None,
    offset: int = 0,
    limit: int = 20,
) -> list[dict]:
    q = (
        select(KBArticle)
        .where(KBArticle.status == ArticleStatus.PUBLISHED, KBArticle.is_internal.is_(False))
        .order_by(KBArticle.view_count.desc())
    )
    if category_id:
        q = q.where(KBArticle.category_id == category_id)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [_fmt_article(a) for a in rows]


@router.get("/kb/search")
async def search_kb(
    db: DBDep, cu: CU,
    q: str = Query(..., min_length=2),
    category_id: Optional[int] = None,
) -> list[dict]:
    results = await kb_service.search(db, q, category_id=category_id, is_internal=False)
    return [_fmt_article(a) for a in results]


@router.get("/kb/suggest")
async def suggest_kb(
    db: DBDep, cu: CU,
    subject: str = Query(""),
    description: str = Query(""),
) -> list[dict]:
    """KB suggestions before submitting ticket (pre-deflection)."""
    return await kb_service.suggest_for_ticket(db, subject, description, max_results=5)


@router.get("/kb/categories")
async def list_kb_categories(db: DBDep, cu: CU) -> list[dict]:
    rows = (await db.execute(
        select(KBCategory).where(KBCategory.is_active.is_(True)).order_by(KBCategory.sort_order)
    )).scalars().all()
    return [{"id": c.id, "name": c.name, "name_fa": c.name_fa, "slug": c.slug, "icon": c.icon} for c in rows]


@router.get("/kb/{slug}")
async def get_kb_article(slug: str, db: DBDep, cu: CU) -> dict:
    article = await kb_service.get_article(db, slug, increment_view=True)
    if not article:
        raise _not_found("Article not found")
    return {**_fmt_article(article), "content": article.content, "content_fa": article.content_fa}


@router.post("/kb/{article_id}/helpful")
async def rate_kb_article(article_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    await kb_service.rate_article(db, article_id, helpful=data.get("helpful", True))
    await db.commit()
    return {"status": "recorded"}


# ===========================================================================
# AGENT INTERFACE — /support/dashboard
# ===========================================================================

@router.get("/dashboard")
async def agent_dashboard(db: DBDep, cu: CU) -> dict:
    """Agent's ticket queue stats + their open tickets."""
    # My open tickets
    my_tickets_r = await db.execute(
        select(Ticket)
        .where(
            Ticket.assigned_to_id == cu.id,
            Ticket.status.in_([TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS,
                                TicketStatus.PENDING, TicketStatus.ESCALATED]),
        )
        .order_by(Ticket.sla_resolution_deadline.asc().nullslast())
        .limit(20)
    )
    my_tickets = my_tickets_r.scalars().all()

    # Queue stats
    stats_r = await db.execute(
        select(Ticket.status, func.count(Ticket.id).label("cnt"))
        .group_by(Ticket.status)
    )
    status_counts = {r.status.value: r.cnt for r in stats_r.all()}

    # SLA at risk (deadline within 1 hour)
    from datetime import timedelta
    soon = datetime.utcnow() + timedelta(hours=1)
    at_risk_r = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.sla_resolution_deadline <= soon,
            Ticket.status.in_([TicketStatus.NEW, TicketStatus.ASSIGNED,
                                TicketStatus.IN_PROGRESS, TicketStatus.PENDING]),
            Ticket.sla_resolution_breached.is_(False),
        )
    )
    at_risk = at_risk_r.scalar_one() or 0

    # Unassigned count
    unassigned_r = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.status == TicketStatus.NEW,
            Ticket.assigned_to_id.is_(None),
        )
    )
    unassigned = unassigned_r.scalar_one() or 0

    return {
        "my_open_tickets": [_fmt_ticket(t) for t in my_tickets],
        "queue": status_counts,
        "unassigned": unassigned,
        "sla_at_risk": at_risk,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/tickets/all")
async def list_all_tickets(
    db: DBDep, cu: CU,
    status_filter: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    category: Optional[TicketCategory] = None,
    assigned_to_id: Optional[int] = None,
    team_id: Optional[int] = None,
    search: Optional[str] = None,
    sla_breached: Optional[bool] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    """Agent/admin: full ticket list with filters."""
    # TODO: require_permission("support:view:all")
    q = select(Ticket).order_by(Ticket.created_at.desc())
    if status_filter:
        q = q.where(Ticket.status == status_filter)
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
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [_fmt_ticket(t) for t in rows]


@router.get("/tickets/{ticket_id}/full")
async def get_ticket_full(ticket_id: int, db: DBDep, cu: CU) -> dict:
    """Agent view: all comments including internal notes."""
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")
    comments_r = await db.execute(
        select(TicketComment)
        .where(TicketComment.ticket_id == ticket_id)
        .order_by(TicketComment.created_at.asc())
    )
    comments = comments_r.scalars().all()
    suggestions = await kb_service.suggest_for_ticket(
        db, ticket.subject, ticket.description[:500], max_results=3, is_internal=True
    )
    return {
        **_fmt_ticket(ticket),
        "comments": [_fmt_comment(c) for c in comments],
        "kb_suggestions": suggestions,
    }


@router.post("/tickets/{ticket_id}/assign")
async def assign_ticket(ticket_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")
    assignee_id = data.get("user_id", cu.id)
    ticket = await ticket_service.assign_ticket(db, ticket, assignee_id=assignee_id, assigned_by_id=cu.id)
    await db.commit()
    return {"status": "assigned", "assigned_to_id": ticket.assigned_to_id}


@router.post("/tickets/{ticket_id}/comment", status_code=201)
async def agent_comment(ticket_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    """Agent adds public reply or internal note."""
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")
    is_internal = data.get("is_internal", False)
    author_type = CommentAuthorType.AGENT
    canned_id = data.get("canned_response_id")
    content = data["content"]

    # If using canned response, get its content
    if canned_id:
        cr_r = await db.execute(select(CannedResponse).where(CannedResponse.id == canned_id))
        cr = cr_r.scalar_one_or_none()
        if cr:
            content = cr.content_fa or cr.content

    try:
        comment = await ticket_service.add_comment(
            db, ticket,
            content=content,
            author_type=author_type,
            author_name=f"{cu.first_name} {cu.last_name}",
            author_user_id=cu.id,
            is_internal=is_internal,
            attachments=data.get("attachments"),
            canned_response_id=canned_id,
        )
    except SupportError as exc:
        raise _bad(str(exc))
    await db.commit()
    return _fmt_comment(comment)


@router.post("/tickets/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")
    try:
        ticket = await ticket_service.resolve_ticket(
            db, ticket,
            resolution_note=data.get("resolution", "Resolved by agent."),
            resolved_by_id=cu.id,
        )
    except SupportError as exc:
        raise _bad(str(exc))
    await db.commit()
    return {"status": "resolved", "resolution_minutes": ticket.resolution_minutes}


@router.post("/tickets/{ticket_id}/escalate")
async def escalate_ticket(ticket_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")
    ticket.status = TicketStatus.ESCALATED
    ticket.updated_by_id = cu.id
    from app.models.support import CommentAuthorType as CAT
    from app.models.support import TicketComment as TC
    db.add(TC(
        ticket_id=ticket.id,
        author_type=CAT.SYSTEM,
        author_name="System",
        content=f"Escalated by {cu.first_name}: {data.get('reason', '')}",
        is_internal=True,
        created_by_id=cu.id,
    ))
    await db.commit()
    return {"status": "escalated"}


@router.post("/tickets/{ticket_id}/reopen")
async def reopen_ticket(ticket_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise _not_found("Ticket not found")
    try:
        ticket = await ticket_service.reopen_ticket(
            db, ticket,
            reason=data.get("reason", "Reopened"),
            requester_id=cu.id,
            is_customer=data.get("is_customer", False),
        )
    except SupportError as exc:
        raise _bad(str(exc))
    await db.commit()
    return {"status": "reopened"}


# ===========================================================================
# TEAMS
# ===========================================================================

@router.get("/teams")
async def list_teams(db: DBDep, cu: CU) -> list[dict]:
    rows = (await db.execute(
        select(SupportTeam).where(SupportTeam.is_active.is_(True)).order_by(SupportTeam.name)
    )).scalars().all()
    return [{"id": t.id, "name": t.name, "name_fa": t.name_fa,
             "email": t.email, "categories": t.categories} for t in rows]


@router.post("/teams", status_code=201)
async def create_team(data: dict, db: DBDep, cu: CU) -> dict:
    team = SupportTeam(
        name=data["name"], name_fa=data.get("name_fa"),
        email=data.get("email"),
        categories=data.get("categories", []),
        auto_assign=data.get("auto_assign", True),
        created_by_id=cu.id,
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return {"id": team.id, "name": team.name}


@router.post("/teams/{team_id}/members", status_code=201)
async def add_team_member(team_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    existing = await db.execute(
        select(SupportTeamMember).where(
            SupportTeamMember.team_id == team_id,
            SupportTeamMember.user_id == data["user_id"],
        )
    )
    if existing.scalar_one_or_none():
        return {"status": "already member"}
    member = SupportTeamMember(
        team_id=team_id, user_id=data["user_id"],
        is_lead=data.get("is_lead", False),
    )
    db.add(member)
    await db.commit()
    return {"status": "added", "user_id": data["user_id"]}


# ===========================================================================
# SLA POLICIES
# ===========================================================================

@router.get("/sla")
async def list_sla_policies(db: DBDep, cu: CU) -> list[dict]:
    rows = (await db.execute(select(SLAPolicy).where(SLAPolicy.is_active.is_(True)))).scalars().all()
    return [{"id": s.id, "name": s.name, "is_default": s.is_default,
             "response_times": s.response_times, "resolution_times": s.resolution_times} for s in rows]


@router.post("/sla", status_code=201)
async def create_sla_policy(data: dict, db: DBDep, cu: CU) -> dict:
    sla = SLAPolicy(
        name=data["name"], name_fa=data.get("name_fa"),
        is_default=data.get("is_default", False),
        response_times=data.get("response_times", {"low": 240, "medium": 120, "high": 60, "critical": 15, "emergency": 5}),
        resolution_times=data.get("resolution_times", {"low": 2880, "medium": 1440, "high": 480, "critical": 240, "emergency": 60}),
        business_hours_start=data.get("business_hours_start", "08:00"),
        business_hours_end=data.get("business_hours_end", "17:00"),
        work_days=data.get("work_days", [5, 6, 0, 1, 2]),
        escalation_enabled=data.get("escalation_enabled", True),
        escalation_after_minutes=data.get("escalation_after_minutes", 120),
        created_by_id=cu.id,
    )
    db.add(sla)
    await db.commit()
    await db.refresh(sla)
    return {"id": sla.id, "name": sla.name}


# ===========================================================================
# CANNED RESPONSES
# ===========================================================================

@router.get("/canned-responses")
async def list_canned_responses(
    db: DBDep, cu: CU, category: Optional[str] = None, search: Optional[str] = None
) -> list[dict]:
    q = select(CannedResponse).where(CannedResponse.is_active.is_(True)).order_by(CannedResponse.use_count.desc())
    if category:
        q = q.where(CannedResponse.category == category)
    if search:
        q = q.where(or_(CannedResponse.title.ilike(f"%{search}%"), CannedResponse.shortcut.ilike(f"%{search}%")))
    rows = (await db.execute(q)).scalars().all()
    return [{"id": r.id, "title": r.title, "title_fa": r.title_fa, "shortcut": r.shortcut,
             "content": r.content, "content_fa": r.content_fa, "use_count": r.use_count} for r in rows]


@router.post("/canned-responses", status_code=201)
async def create_canned_response(data: dict, db: DBDep, cu: CU) -> dict:
    cr = CannedResponse(
        title=data["title"], title_fa=data.get("title_fa"),
        shortcut=data.get("shortcut"), content=data["content"],
        content_fa=data.get("content_fa"), category=data.get("category"),
        created_by_id=cu.id,
    )
    db.add(cr)
    await db.commit()
    await db.refresh(cr)
    return {"id": cr.id, "title": cr.title}


# ===========================================================================
# ROUTING RULES
# ===========================================================================

@router.get("/routing-rules")
async def list_routing_rules(db: DBDep, cu: CU) -> list[dict]:
    rows = (await db.execute(
        select(TicketRoutingRule).where(TicketRoutingRule.is_active.is_(True)).order_by(TicketRoutingRule.sort_order)
    )).scalars().all()
    return [{"id": r.id, "name": r.name, "category": r.category, "priority": r.priority,
             "keywords": r.keywords, "assign_to_team_id": r.assign_to_team_id,
             "sort_order": r.sort_order} for r in rows]


@router.post("/routing-rules", status_code=201)
async def create_routing_rule(data: dict, db: DBDep, cu: CU) -> dict:
    rule = TicketRoutingRule(
        name=data["name"],
        category=data.get("category"),
        priority=data.get("priority"),
        requester_type=data.get("requester_type"),
        keywords=data.get("keywords"),
        assign_to_team_id=data.get("assign_to_team_id"),
        assign_to_user_id=data.get("assign_to_user_id"),
        sla_policy_id=data.get("sla_policy_id"),
        auto_response_enabled=data.get("auto_response_enabled", False),
        auto_response_template=data.get("auto_response_template"),
        sort_order=data.get("sort_order", 0),
        created_by_id=cu.id,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return {"id": rule.id, "name": rule.name}


# ===========================================================================
# KNOWLEDGE BASE — Admin management
# ===========================================================================

@router.post("/kb/articles", status_code=201)
async def create_kb_article(data: dict, db: DBDep, cu: CU) -> dict:
    import re as _re
    slug = data.get("slug") or _re.sub(r"[^a-z0-9-]", "-", data["title"].lower())[:100]
    article = KBArticle(
        title=data["title"], title_fa=data.get("title_fa"), slug=slug,
        content=data["content"], content_fa=data.get("content_fa"),
        excerpt=data.get("excerpt"),
        category_id=data.get("category_id"),
        tags=data.get("tags"),
        status=ArticleStatus(data.get("status", "draft")),
        is_internal=data.get("is_internal", False),
        created_by_id=cu.id,
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return _fmt_article(article)


@router.put("/kb/articles/{article_id}")
async def update_kb_article(article_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    article = await db.get(KBArticle, article_id)
    if not article:
        raise _not_found("Article not found")
    for field in ["title", "title_fa", "content", "content_fa", "excerpt", "tags", "status", "is_internal"]:
        if field in data:
            val = data[field]
            if field == "status":
                val = ArticleStatus(val)
            setattr(article, field, val)
    article.updated_by_id = cu.id
    article.version += 1
    await db.commit()
    return _fmt_article(article)


# ===========================================================================
# REPORTS
# ===========================================================================

@router.get("/reports/performance")
async def performance_report(
    db: DBDep, cu: CU,
    team_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> dict:
    return await ticket_service.get_performance_metrics(db, team_id=team_id, date_from=date_from, date_to=date_to)


@router.get("/reports/satisfaction")
async def satisfaction_report(
    db: DBDep, cu: CU,
    team_id: Optional[int] = None,
) -> dict:
    """CSAT breakdown: score distribution + comments."""
    q = select(
        Ticket.satisfaction_rating, func.count(Ticket.id).label("cnt")
    ).where(Ticket.satisfaction_rating.isnot(None))
    if team_id:
        q = q.where(Ticket.assigned_team_id == team_id)
    q = q.group_by(Ticket.satisfaction_rating).order_by(Ticket.satisfaction_rating)

    rows = (await db.execute(q)).all()
    distribution = {str(r.satisfaction_rating): r.cnt for r in rows}
    total = sum(v for v in distribution.values())
    weighted = sum(int(k) * v for k, v in distribution.items())
    avg = round(weighted / total, 2) if total else 0

    # Recent comments
    comments_r = await db.execute(
        select(Ticket.ticket_number, Ticket.satisfaction_rating, Ticket.satisfaction_comment)
        .where(Ticket.satisfaction_comment.isnot(None))
        .order_by(Ticket.satisfaction_submitted_at.desc())
        .limit(10)
    )
    comments = [{"ticket": r.ticket_number, "rating": r.satisfaction_rating,
                 "comment": r.satisfaction_comment} for r in comments_r.all()]

    return {
        "avg_csat": avg, "total_responses": total,
        "distribution": distribution, "recent_comments": comments,
    }


@router.post("/internal/check-sla")
async def run_sla_check(db: DBDep, cu: CU) -> dict:
    """Manual trigger for SLA breach check (also runs via Celery)."""
    result = await ticket_service.check_sla_breaches(db)
    await db.commit()
    return result


# ===========================================================================
# Formatters
# ===========================================================================

def _fmt_ticket(t: Ticket) -> dict:
    return {
        "id": t.id,
        "ticket_number": t.ticket_number,
        "subject": t.subject,
        "category": t.category.value,
        "subcategory": t.subcategory,
        "priority": t.priority.value,
        "status": t.status.value,
        "requester_name": t.requester_name,
        "requester_email": t.requester_email,
        "assigned_to_id": t.assigned_to_id,
        "assigned_team_id": t.assigned_team_id,
        "sla_response_deadline": t.sla_response_deadline.isoformat() if t.sla_response_deadline else None,
        "sla_resolution_deadline": t.sla_resolution_deadline.isoformat() if t.sla_resolution_deadline else None,
        "sla_response_breached": t.sla_response_breached,
        "sla_resolution_breached": t.sla_resolution_breached,
        "first_response_minutes": t.first_response_minutes,
        "resolution_minutes": t.resolution_minutes,
        "satisfaction_rating": t.satisfaction_rating,
        "related_module": t.related_module,
        "related_record_ref": t.related_record_ref,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None,
        "closed_at": t.closed_at.isoformat() if t.closed_at else None,
    }


def _fmt_comment(c: TicketComment) -> dict:
    return {
        "id": c.id,
        "author_type": c.author_type.value,
        "author_name": c.author_name,
        "content": c.content,
        "is_internal": c.is_internal,
        "is_canned": c.is_canned,
        "attachments": c.attachments,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def _fmt_article(a: KBArticle) -> dict:
    return {
        "id": a.id, "title": a.title, "title_fa": a.title_fa,
        "slug": a.slug, "excerpt": a.excerpt,
        "category_id": a.category_id, "tags": a.tags,
        "status": a.status.value, "is_internal": a.is_internal,
        "view_count": a.view_count,
        "helpful_count": a.helpful_count,
        "not_helpful_count": a.not_helpful_count,
        "version": a.version,
    }
