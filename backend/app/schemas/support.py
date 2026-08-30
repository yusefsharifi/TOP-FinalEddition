"""
Support Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.support import (
    ArticleStatus, CommentAuthorType, KBArticle, KBCategory,
    RequesterType, SLAPolicy, SupportTeam, TicketCategory,
    TicketPriority, TicketStatus,
)

_ro = ConfigDict(from_attributes=True)


# ===========================================================================
# Tickets
# ===========================================================================
class TicketCreate(BaseModel):
    requester_type: RequesterType = RequesterType.CUSTOMER
    requester_name: Optional[str] = None
    requester_email: Optional[str] = None
    requester_phone: Optional[str] = None
    requester_customer_id: Optional[int] = None
    requester_user_id: Optional[int] = None
    category: TicketCategory = TicketCategory.GENERAL
    subcategory: Optional[str] = Field(None, max_length=100)
    priority: TicketPriority = TicketPriority.MEDIUM
    subject: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    attachments: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    related_module: Optional[str] = Field(None, max_length=50)
    related_record_id: Optional[int] = None
    related_record_ref: Optional[str] = Field(None, max_length=100)


class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to_id: Optional[int] = None
    assigned_team_id: Optional[int] = None


class TicketResponse(BaseModel):
    model_config = _ro
    id: int
    ticket_number: str
    subject: str
    description: Optional[str] = None
    category: TicketCategory
    subcategory: Optional[str] = None
    priority: TicketPriority
    status: TicketStatus
    requester_type: RequesterType
    requester_name: Optional[str] = None
    requester_email: Optional[str] = None
    requester_user_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    assigned_team_id: Optional[int] = None
    satisfaction_rating: Optional[int] = None
    resolution_minutes: Optional[int] = None
    sla_resolution_deadline: Optional[datetime] = None
    sla_resolution_breached: bool
    tags: Optional[list] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class TicketCommentResponse(BaseModel):
    model_config = _ro
    id: int
    ticket_id: int
    author_type: CommentAuthorType
    author_name: Optional[str] = None
    content: str
    is_internal: bool
    attachments: Optional[list] = None
    canned_response_id: Optional[int] = None
    created_at: datetime


# ===========================================================================
# Knowledge Base
# ===========================================================================
class KBArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    title_fa: Optional[str] = Field(None, max_length=300)
    slug: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    content_fa: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[list[str]] = None
    is_internal: bool = False


class KBArticleResponse(BaseModel):
    model_config = _ro
    id: int
    title: str
    title_fa: Optional[str] = None
    slug: str
    status: ArticleStatus
    is_internal: bool
    category_id: Optional[int] = None
    tags: Optional[list] = None
    view_count: int
    helpful_count: int
    not_helpful_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class KBCategoryResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    name_fa: Optional[str] = None
    slug: str
    icon: Optional[str] = None
    is_active: bool
    sort_order: int


# ===========================================================================
# Teams & SLA
# ===========================================================================
class SupportTeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    name_fa: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    categories: list[str] = Field(default_factory=list)
    auto_assign: bool = True


class SupportTeamResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    name_fa: Optional[str] = None
    email: Optional[str] = None
    categories: Optional[list] = None
    is_active: bool
    created_at: datetime


class SLAPolicyResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    priority: TicketPriority
    response_minutes: int
    resolution_minutes: int
    business_hours_only: bool
    is_active: bool
