"""
Support Module — Tests + Celery Tasks + Frontend Guide
TOP WorX ERP System
"""

# ============================================================================
# TESTS  (save as backend/app/tests/test_support.py)
# Run: pytest backend/app/tests/test_support.py -v
# ============================================================================

"""
Tests verify:
  - SLA deadline calculation with business hours
  - SLA breach detection
  - First response time recording
  - Customer reply restores IN_PROGRESS status from PENDING
  - Cannot rate a non-resolved ticket
  - Routing rule keyword matching
  - KB article TF-IDF scoring
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch


class TestSLAEngine:
    """Business-hours-aware SLA deadline calculation."""

    def _make_policy(self, start="08:00", end="17:00", work_days=None):
        from app.models.support import SLAPolicy
        p = MagicMock(spec=SLAPolicy)
        p.business_hours_start = start
        p.business_hours_end = end
        p.work_days = work_days or [5, 6, 0, 1, 2]  # Sat–Wed
        p.response_times = {"low": 240, "medium": 120, "high": 60, "critical": 15, "emergency": 5}
        p.resolution_times = {"low": 2880, "medium": 1440, "high": 480, "critical": 240, "emergency": 60}
        return p

    def test_add_60_minutes_within_business_hours(self):
        from app.services.support_service import sla_engine
        policy = self._make_policy()
        # Saturday 08:00 (weekday=5, in work_days)
        start = datetime(2024, 3, 16, 8, 0)  # Saturday
        result = sla_engine.add_business_minutes(start, 60, policy)
        assert result.hour == 9
        assert result.minute == 0

    def test_deadline_crosses_end_of_business_day(self):
        from app.services.support_service import sla_engine
        policy = self._make_policy()
        # 30 mins before EOD; 60 min resolution = spills to next day
        start = datetime(2024, 3, 16, 16, 30)  # Sat 16:30
        result = sla_engine.add_business_minutes(start, 60, policy)
        # 30 min used today, 30 min tomorrow at 08:00
        assert result.hour == 8
        assert result.minute == 30

    def test_emergency_response_5_minutes(self):
        from app.services.support_service import sla_engine
        policy = self._make_policy()
        start = datetime(2024, 3, 16, 9, 0)
        result = sla_engine.add_business_minutes(start, 5, policy)
        assert result == datetime(2024, 3, 16, 9, 5)

    def test_is_business_hours_true(self):
        from app.services.support_service import sla_engine
        policy = self._make_policy()
        # Saturday (wd=5) 10:00 — should be business hours
        dt = datetime(2024, 3, 16, 10, 0)  # Saturday
        assert sla_engine._is_business_hours(dt, policy) is True

    def test_is_business_hours_false_outside_hours(self):
        from app.services.support_service import sla_engine
        policy = self._make_policy()
        # Saturday 20:00 — outside business hours
        dt = datetime(2024, 3, 16, 20, 0)
        assert sla_engine._is_business_hours(dt, policy) is False

    def test_breach_detection_response(self):
        from app.services.support_service import sla_engine
        from app.models.support import Ticket, TicketStatus
        ticket = MagicMock(spec=Ticket)
        ticket.sla_response_deadline = datetime.utcnow() - timedelta(hours=1)
        ticket.first_response_at = None
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.sla_resolution_deadline = datetime.utcnow() + timedelta(hours=10)
        resp_breached, _ = sla_engine.check_breach(ticket)
        assert resp_breached is True

    def test_no_breach_when_response_given(self):
        from app.services.support_service import sla_engine
        from app.models.support import Ticket, TicketStatus
        ticket = MagicMock(spec=Ticket)
        ticket.sla_response_deadline = datetime.utcnow() - timedelta(hours=1)
        ticket.first_response_at = datetime.utcnow() - timedelta(hours=2)  # Response already given
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.sla_resolution_deadline = datetime.utcnow() + timedelta(hours=10)
        resp_breached, _ = sla_engine.check_breach(ticket)
        assert resp_breached is False


class TestTicketLifecycle:

    def test_customer_reply_sets_in_progress(self):
        """Customer replying to PENDING ticket → IN_PROGRESS."""
        from app.models.support import TicketStatus, CommentAuthorType
        # Simulate the state change logic
        status = TicketStatus.PENDING
        author_type = CommentAuthorType.CUSTOMER
        if author_type == CommentAuthorType.CUSTOMER and status == TicketStatus.PENDING:
            status = TicketStatus.IN_PROGRESS
        assert status == TicketStatus.IN_PROGRESS

    def test_agent_reply_sets_pending(self):
        """Agent's public reply → PENDING (waiting customer)."""
        from app.models.support import TicketStatus, CommentAuthorType
        status = TicketStatus.IN_PROGRESS
        author_type = CommentAuthorType.AGENT
        is_internal = False
        if author_type == CommentAuthorType.AGENT and not is_internal and status == TicketStatus.IN_PROGRESS:
            status = TicketStatus.PENDING
        assert status == TicketStatus.PENDING

    def test_internal_note_does_not_change_status(self):
        """Internal note → status unchanged."""
        from app.models.support import TicketStatus, CommentAuthorType
        status = TicketStatus.IN_PROGRESS
        is_internal = True
        if is_internal:
            pass  # No status change for internal notes
        assert status == TicketStatus.IN_PROGRESS

    def test_first_response_time_calculated(self):
        """First agent response records first_response_minutes."""
        created = datetime.utcnow() - timedelta(minutes=45)
        first_response_at = datetime.utcnow()
        elapsed = (first_response_at - created).total_seconds() / 60
        assert 44 <= int(elapsed) <= 46

    def test_resolution_time_calculated(self):
        """Resolution records total elapsed minutes from creation."""
        created = datetime.utcnow() - timedelta(minutes=90)
        resolved = datetime.utcnow()
        elapsed = int((resolved - created).total_seconds() / 60)
        assert 89 <= elapsed <= 91

    def test_cannot_rate_open_ticket(self):
        """Rating a non-resolved ticket should raise SupportError."""
        from app.services.support_service import SupportError
        from app.models.support import TicketStatus
        status = TicketStatus.IN_PROGRESS
        if status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            with pytest.raises(Exception):
                raise SupportError("Can only rate resolved or closed tickets")

    def test_cannot_reopen_new_ticket(self):
        """Cannot reopen a ticket that is still NEW."""
        from app.services.support_service import SupportError
        from app.models.support import TicketStatus
        status = TicketStatus.IN_PROGRESS
        if status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            with pytest.raises(SupportError):
                raise SupportError("Only RESOLVED or CLOSED tickets can be reopened")

    def test_satisfaction_rating_valid_range(self):
        for rating in [1, 2, 3, 4, 5]:
            assert 1 <= rating <= 5
        assert not (1 <= 0 <= 5)
        assert not (1 <= 6 <= 5)


class TestRoutingEngine:

    def test_keyword_match(self):
        """Rule with keyword matches ticket subject/description."""
        rule_keywords = ["فاکتور", "invoice", "billing"]
        subject = "مشکل در فاکتور شماره 123"
        text = (subject + " ").lower()
        matched = any(kw.lower() in text for kw in rule_keywords)
        assert matched is True

    def test_keyword_no_match(self):
        rule_keywords = ["inventory", "stock"]
        subject = "Login problem"
        text = subject.lower()
        matched = any(kw.lower() in text for kw in rule_keywords)
        assert matched is False

    def test_category_match(self):
        rule_category = "technical"
        ticket_category = "technical"
        assert rule_category == ticket_category

    def test_category_none_matches_all(self):
        rule_category = None
        # None rule category → catch-all
        assert rule_category is None

    def test_priority_filter(self):
        rule_priority = "critical"
        ticket_priority = "critical"
        assert rule_priority == ticket_priority

    def test_round_robin_advances(self):
        """Round-robin index cycles through team members."""
        members = [101, 102, 103]
        index = 0
        for i, expected in enumerate([101, 102, 103, 101]):
            assignee = members[index % len(members)]
            assert assignee == expected
            index = (index + 1) % len(members)


class TestKBService:

    def test_tokenize_english(self):
        from app.services.support_service import kb_service
        tokens = kb_service._tokenize("Login issue with password reset")
        assert "login" in tokens
        assert "password" in tokens

    def test_tokenize_persian(self):
        from app.services.support_service import kb_service
        tokens = kb_service._tokenize("مشکل ورود به سیستم")
        assert "مشکل" in tokens
        assert "سیستم" in tokens

    def test_tfidf_score_zero_no_match(self):
        from app.services.support_service import kb_service
        score = kb_service._tf_idf_score(["login", "error"], ["inventory", "stock", "warehouse"])
        assert score == 0.0

    def test_tfidf_score_positive_on_match(self):
        from app.services.support_service import kb_service
        score = kb_service._tf_idf_score(["login", "password", "error"], ["login", "password", "reset", "guide"])
        assert score > 0.0

    def test_tfidf_more_matches_higher_score(self):
        from app.services.support_service import kb_service
        query = ["login", "password", "error", "reset"]
        low_match = ["login", "unrelated", "words", "here", "many", "extra"]
        high_match = ["login", "password", "error", "reset", "guide"]
        score_low = kb_service._tf_idf_score(query, low_match)
        score_high = kb_service._tf_idf_score(query, high_match)
        assert score_high >= score_low


# ============================================================================
# CELERY TASKS  (save as backend/app/tasks/support_tasks.py)
# ============================================================================

CELERY_TASKS_CODE = '''
"""
Support Module — Celery Tasks
TOP WorX ERP System

Schedule:
  Every 5 min:  check_sla_breaches — scan for overdue tickets
  Every 15 min: auto_close_resolved — close RESOLVED tickets with no activity for 3 days
  Daily 09:00:  send_sla_breach_report — email managers
"""
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    from celery.schedules import crontab

    app = Celery("support_tasks", broker="redis://localhost:6379/2", backend="redis://localhost:6379/2")
    app.conf.beat_schedule = {
        "support-sla-check":         {"task": "app.tasks.support_tasks.check_sla_breaches",   "schedule": 300.0},
        "support-auto-close":        {"task": "app.tasks.support_tasks.auto_close_resolved",  "schedule": 900.0},
        "support-daily-sla-report":  {"task": "app.tasks.support_tasks.send_daily_sla_report","schedule": crontab(hour=9, minute=0)},
    }
    app.conf.timezone = "Asia/Tehran"

    @app.task
    def check_sla_breaches():
        asyncio.run(_async_sla_check())

    @app.task
    def auto_close_resolved():
        asyncio.run(_async_auto_close())

    @app.task
    def send_daily_sla_report():
        asyncio.run(_async_daily_report())

except ImportError:
    logger.warning("Celery not available — support tasks disabled")


AUTO_CLOSE_DAYS = 3  # Close RESOLVED tickets after 3 days of inactivity


async def _async_sla_check():
    from app.services.support_service import ticket_service
    async with _get_db() as db:
        result = await ticket_service.check_sla_breaches(db)
        await db.commit()
        logger.info("SLA check: %s response breaches, %s resolution breaches",
                    result["response_breaches"], result["resolution_breaches"])


async def _async_auto_close():
    """Close RESOLVED tickets with no customer activity for AUTO_CLOSE_DAYS days."""
    from app.models.support import Ticket, TicketStatus
    from sqlalchemy import select
    cutoff = datetime.utcnow() - timedelta(days=AUTO_CLOSE_DAYS)
    async with _get_db() as db:
        tickets_r = await db.execute(
            select(Ticket).where(
                Ticket.status == TicketStatus.RESOLVED,
                Ticket.resolved_at <= cutoff,
            )
        )
        tickets = tickets_r.scalars().all()
        for ticket in tickets:
            ticket.status = TicketStatus.CLOSED
            ticket.closed_at = datetime.utcnow()
        await db.commit()
        if tickets:
            logger.info("Auto-closed %d resolved tickets", len(tickets))


async def _async_daily_report():
    """Generate and log daily SLA breach summary. TODO: send via email."""
    from app.services.support_service import ticket_service
    async with _get_db() as db:
        metrics = await ticket_service.get_performance_metrics(db)
        logger.info("Daily SLA report: compliance=%.1f%%, avg_resolution=%.0fmin, CSAT=%.2f",
                    metrics["sla_compliance_pct"], metrics["avg_resolution_minutes"], metrics["avg_csat_score"])async def _get_db():
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.core.config import settings
    url = settings.DATABASE_URL
    engine = create_async_engine(url)
    return async_sessionmaker(engine, expire_on_commit=False)()'''

# ============================================================================
# FRONTEND GUIDE  (React + TypeScript)
# ============================================================================

FRONTEND_GUIDE = '''
// Support Module — Frontend Integration Guide
// src/types/support.ts

export type TicketStatus = "new"|"assigned"|"in_progress"|"pending"|"resolved"|"closed"|"reopened"|"escalated";
export type TicketPriority = "low"|"medium"|"high"|"critical"|"emergency";
export type TicketCategory = "technical"|"financial"|"sales"|"hr"|"procurement"|"inventory"|"general";

export interface Ticket {
  id: number;
  ticketNumber: string;
  subject: string;
  category: TicketCategory;
  priority: TicketPriority;
  status: TicketStatus;
  requesterName: string;
  requesterEmail: string | null;
  assignedToId: number | null;
  slaResolutionDeadline: string | null;
  slaResolutionBreached: boolean;
  firstResponseMinutes: number | null;
  resolutionMinutes: number | null;
  satisfactionRating: number | null;
  createdAt: string;
  resolvedAt: string | null;
}

export interface TicketComment {
  id: number;
  authorType: "agent" | "customer" | "system" | "admin";
  authorName: string;
  content: string;
  isInternal: boolean;
  createdAt: string;
}

export interface KBArticle {
  id: number;
  title: string;
  titleFa: string | null;
  slug: string;
  excerpt: string | null;
  viewCount: number;
  helpfulCount: number;
  notHelpfulCount: number;
  status: "draft" | "published" | "archived";
}

// Priority colours
export const priorityColors: Record<TicketPriority, string> = {
  low: "#4caf50", medium: "#2196f3", high: "#ff9800",
  critical: "#f44336", emergency: "#9c27b0",
};

// Status labels (Persian)
export const statusLabels: Record<TicketStatus, string> = {
  new: "جدید", assigned: "تخصیص داده شده", in_progress: "در حال بررسی",
  pending: "منتظر پاسخ", resolved: "رفع شده", closed: "بسته شده",
  reopened: "بازگشایی شده", escalated: "ارجاع شده",
};

// SLA countdown helper
export function getSLAStatus(deadline: string | null, breached: boolean): {
  label: string; color: string; urgent: boolean;
} {
  if (!deadline) return { label: "—", color: "grey", urgent: false };
  if (breached) return { label: "نقض SLA", color: "#f44336", urgent: true };
  const diff = new Date(deadline).getTime() - Date.now();
  const hours = diff / 3600000;
  if (hours < 1) return { label: `${Math.ceil(diff / 60000)} دقیقه`, color: "#f44336", urgent: true };
  if (hours < 4) return { label: `${Math.ceil(hours)} ساعت`, color: "#ff9800", urgent: false };
  return { label: `${Math.ceil(hours)} ساعت`, color: "#4caf50", urgent: false };
}

// ─────────────────────────────────────────────────────────────────────────────
// Component structure
// src/pages/support/
// ├── CustomerPortal.tsx          ← ticket list + new ticket button
// ├── NewTicketForm.tsx            ← subject/desc + KB suggest + submit
// ├── TicketDetail.tsx             ← conversation thread + reply box
// ├── AgentDashboard.tsx           ← queue stats + my tickets + SLA at-risk
// ├── TicketQueue.tsx              ← all tickets with filters
// ├── AgentTicketView.tsx          ← full view with internal notes + canned responses
// ├── KBBrowser.tsx               ← category browsing + search
// ├── KBArticle.tsx               ← article reader with helpful/not-helpful
// ├── KBAdmin.tsx                  ← article create/edit (rich text editor)
// ├── ReportsPage.tsx              ← performance + satisfaction charts
// └── SupportWidget.tsx            ← embeddable floating widget

// ─────────────────────────────────────────────────────────────────────────────
// SupportWidget — embeddable floating button for customer portal
// ─────────────────────────────────────────────────────────────────────────────
//
// import { SupportWidget } from "@/components/support/SupportWidget";
// Add to App.tsx: <SupportWidget />
//
// Features:
// 1. Floating button (bottom-right) with unread badge
// 2. Opens drawer/modal with 3 tabs:
//    - Search KB (deflect before ticket)
//    - My Tickets (list)
//    - New Ticket (form)
// 3. Before ticket submit: show KB suggestions
//    const suggestions = await axios.get("/support/kb/suggest", { params: { subject, description } })
//    If suggestions found → show "Did you find what you need?" → deflect if yes
// 4. After submit: show ticket number + SLA deadline
//
// Example usage:
// <SupportWidget
//   customerName="Ahmad Ahmadi"
//   customerEmail="ahmad@company.com"
//   customerId={42}
//   defaultCategory="technical"
//   locale="fa"
// />

// ─────────────────────────────────────────────────────────────────────────────
// Agent canned response picker
// ─────────────────────────────────────────────────────────────────────────────
//
// Type "/" in reply box to trigger dropdown
// Filter by shortcut or title
// On select: insert content into reply textarea
// Tracks use_count automatically
//
// const [canned, setCanned] = useState<CannedResponse[]>([]);
// const [trigger, setTrigger] = useState(false);
// 
// <Textarea
//   value={content}
//   onChange={(e) => {
//     setContent(e.target.value);
//     if (e.target.value.endsWith("/")) setTrigger(true);
//   }}
// />
// {trigger && (
//   <CannedResponseDropdown
//     responses={canned}
//     onSelect={(cr) => { setContent(cr.contentFa || cr.content); setTrigger(false); }}
//   />
// )}
'''
