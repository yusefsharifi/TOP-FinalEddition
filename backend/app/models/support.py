"""
Support & Ticketing Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Ticket lifecycle: NEW → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
                                  ↕ PENDING (waiting for customer)
                                  ↕ ESCALATED (SLA breach)
                                  ↕ REOPENED (customer unsatisfied)

Integration points:
  • Ticket.requester_customer_id → sales.customers
  • Ticket.requester_user_id     → users
  • Ticket.assigned_to_id        → users
  • Ticket.related_record_id     → any module (polymorphic)
  • SLAPolicy.work_days          → [5,6,0,1,2] = Thu,Fri skipped for Iranian cal
                                    (0=Mon...6=Sun; Iranian work week Sat-Wed = [5,6,0,1,2])
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, Enum, Float,
    ForeignKey, Index, Integer, JSON, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class RequesterType(str, enum.Enum):
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    SYSTEM = "system"
    ANONYMOUS = "anonymous"


class TicketCategory(str, enum.Enum):
    TECHNICAL = "technical"
    FINANCIAL = "financial"
    SALES = "sales"
    HR = "hr"
    PROCUREMENT = "procurement"
    INVENTORY = "inventory"
    GENERAL = "general"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class TicketStatus(str, enum.Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"           # Waiting for customer/third-party
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
    ESCALATED = "escalated"


class CommentAuthorType(str, enum.Enum):
    AGENT = "agent"
    CUSTOMER = "customer"
    SYSTEM = "system"
    ADMIN = "admin"


class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# ---------------------------------------------------------------------------
# SLAPolicy
# ---------------------------------------------------------------------------
class SLAPolicy(AuditMixin, Base):
    """
    Service Level Agreement policy.
    response_times/resolution_times keys match TicketPriority values (minutes).
    work_days: list of weekday ints; Iranian standard = [5,6,0,1,2] (Sat–Wed).
    """
    __tablename__ = "support_sla_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Minutes per priority
    response_times: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # {"low": 240, "medium": 120, "high": 60, "critical": 15, "emergency": 5}
    resolution_times: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # {"low": 2880, "medium": 1440, "high": 480, "critical": 240, "emergency": 60}

    # Business hours (24h format)
    business_hours_start: Mapped[str] = mapped_column(String(5), nullable=False, default="08:00")
    business_hours_end: Mapped[str] = mapped_column(String(5), nullable=False, default="17:00")
    work_days: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # Iranian: [5,6,0,1,2] = Sat,Sun,Mon,Tue,Wed

    escalation_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    escalation_after_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=120)
    escalation_manager_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="sla_policy")


# ---------------------------------------------------------------------------
# SupportTeam
# ---------------------------------------------------------------------------
class SupportTeam(AuditMixin, Base):
    __tablename__ = "support_teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    categories: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # TicketCategory values
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    round_robin_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    auto_assign: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    members: Mapped[list["SupportTeamMember"]] = relationship(
        "SupportTeamMember", back_populates="team", cascade="all, delete-orphan"
    )
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="assigned_team")


class SupportTeamMember(Base):
    __tablename__ = "support_team_members"
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("support_teams.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    is_lead: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    team: Mapped["SupportTeam"] = relationship("SupportTeam", back_populates="members")


# ---------------------------------------------------------------------------
# TicketRoutingRule
# ---------------------------------------------------------------------------
class TicketRoutingRule(AuditMixin, Base):
    """Auto-routing: match ticket → assign to team/user."""
    __tablename__ = "support_routing_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Matching conditions
    category: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    requester_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    keywords: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Subject/desc keywords

    # Actions
    assign_to_team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("support_teams.id", ondelete="SET NULL"), nullable=True
    )
    assign_to_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    sla_policy_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("support_sla_policies.id", ondelete="SET NULL"), nullable=True
    )
    auto_response_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_response_template: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    __table_args__ = (Index("ix_support_routing_rules_sort", "sort_order"),)


# ---------------------------------------------------------------------------
# CannedResponse
# ---------------------------------------------------------------------------
class CannedResponse(AuditMixin, Base):
    """Pre-written responses for common issues."""
    __tablename__ = "support_canned_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    title_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    shortcut: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_fa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    use_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


# ---------------------------------------------------------------------------
# Ticket
# ---------------------------------------------------------------------------
class Ticket(AuditMixin, Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    # Requester
    requester_type: Mapped[RequesterType] = mapped_column(Enum(RequesterType), nullable=False)
    requester_customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    requester_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Denormalised for external/anonymous requesters
    requester_name: Mapped[str] = mapped_column(String(200), nullable=False)
    requester_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    requester_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Content
    category: Mapped[TicketCategory] = mapped_column(Enum(TicketCategory), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    priority: Mapped[TicketPriority] = mapped_column(Enum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    attachments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Status
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), nullable=False, default=TicketStatus.NEW, index=True)

    # Assignment
    assigned_to_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("support_teams.id", ondelete="SET NULL"), nullable=True
    )
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # SLA
    sla_policy_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("support_sla_policies.id", ondelete="SET NULL"), nullable=True
    )
    sla_response_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_resolution_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_response_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sla_resolution_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timing metrics
    first_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    first_response_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resolution_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Satisfaction
    satisfaction_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    satisfaction_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    satisfaction_submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Related ERP record (polymorphic link)
    related_module: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_record_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    related_record_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g. "INV-001"

    # Timestamps
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_customer_reply_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_agent_reply_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    comments: Mapped[list["TicketComment"]] = relationship(
        "TicketComment", back_populates="ticket", cascade="all, delete-orphan",
        order_by="TicketComment.created_at"
    )
    sla_policy: Mapped[Optional["SLAPolicy"]] = relationship("SLAPolicy", back_populates="tickets")
    assigned_team: Mapped[Optional["SupportTeam"]] = relationship("SupportTeam", back_populates="tickets")

    __table_args__ = (
        CheckConstraint("satisfaction_rating IS NULL OR satisfaction_rating BETWEEN 1 AND 5", name="chk_ticket_rating"),
        Index("ix_support_tickets_status", "status"),
        Index("ix_support_tickets_requester_customer", "requester_customer_id"),
        Index("ix_support_tickets_assigned_to", "assigned_to_id"),
        Index("ix_support_tickets_priority", "priority"),
        Index("ix_support_tickets_sla_resolution", "sla_resolution_deadline"),
        Index("ix_support_tickets_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Ticket {self.ticket_number} {self.status}>"


# ---------------------------------------------------------------------------
# TicketComment
# ---------------------------------------------------------------------------
class TicketComment(AuditMixin, Base):
    __tablename__ = "support_ticket_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True
    )

    author_type: Mapped[CommentAuthorType] = mapped_column(Enum(CommentAuthorType), nullable=False)
    author_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    author_customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    author_name: Mapped[str] = mapped_column(String(200), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attachments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    is_canned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    canned_response_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("support_canned_responses.id", ondelete="SET NULL"), nullable=True
    )

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="comments")

    __table_args__ = (Index("ix_ticket_comments_ticket_id", "ticket_id"),)


# ---------------------------------------------------------------------------
# KnowledgeBase
# ---------------------------------------------------------------------------
class KBCategory(AuditMixin, Base):
    __tablename__ = "support_kb_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("support_kb_categories.id", ondelete="RESTRICT"), nullable=True
    )
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    articles: Mapped[list["KBArticle"]] = relationship("KBArticle", back_populates="category")
    parent: Mapped[Optional["KBCategory"]] = relationship("KBCategory", remote_side="KBCategory.id")


class KBArticle(AuditMixin, Base):
    __tablename__ = "support_kb_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    title_fa: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_fa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("support_kb_categories.id", ondelete="SET NULL"), nullable=True
    )
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    related_article_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    status: Mapped[ArticleStatus] = mapped_column(Enum(ArticleStatus), nullable=False, default=ArticleStatus.DRAFT)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    not_helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Full-text search index (content + title as tsvector in PG)
    search_vector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    category: Mapped[Optional["KBCategory"]] = relationship("KBCategory", back_populates="articles")

    __table_args__ = (
        Index("ix_kb_articles_status", "status"),
        Index("ix_kb_articles_category", "category_id"),
        Index("ix_kb_articles_slug", "slug"),
    )