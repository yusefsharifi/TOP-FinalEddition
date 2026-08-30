"""
CRM Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

_ro = ConfigDict(from_attributes=True)


# ===========================================================================
# Customer Profile
# ===========================================================================
class CustomerProfileResponse(BaseModel):
    model_config = _ro
    id: int
    customer_id: int
    lifecycle_stage: Optional[str] = None
    lead_source: Optional[str] = None
    engagement_score: float
    churn_risk_score: float
    lifetime_value: Decimal
    first_contact_date: Optional[date] = None
    last_interaction_date: Optional[datetime] = None
    segment: Optional[str] = None


# ===========================================================================
# Tags
# ===========================================================================
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    name_fa: Optional[str] = Field(None, max_length=50)
    color: str = Field("#1976d2", max_length=20)
    category: Optional[str] = Field(None, max_length=50)


class TagResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    name_fa: Optional[str] = None
    color: str
    category: Optional[str] = None
    is_active: bool


# ===========================================================================
# Leads
# ===========================================================================
class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    name_fa: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=30)
    company_name: Optional[str] = Field(None, max_length=200)
    source: str = Field("unknown", max_length=50)
    source_detail: Optional[str] = Field(None, max_length=200)
    budget: Optional[str] = None
    timeline: Optional[str] = None
    authority: bool = False
    need: Optional[str] = None
    estimated_value: Optional[Decimal] = Field(None, ge=Decimal("0"))
    probability: int = Field(50, ge=0, le=100)


class LeadResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    name_fa: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    source: str
    status: str
    qualification_score: Optional[int] = None
    probability: int
    estimated_value: Optional[Decimal] = None
    assigned_to_id: Optional[int] = None
    next_follow_up_at: Optional[datetime] = None
    created_at: datetime


# ===========================================================================
# Campaigns
# ===========================================================================
class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    campaign_type: str = Field(..., max_length=50)
    target_segment: Optional[str] = None
    target_tag_ids: Optional[list[int]] = None
    target_customer_ids: Optional[list[int]] = None
    sms_template_code: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, max_length=200)
    goal: str = Field("engagement", max_length=50)


class CampaignResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    description: Optional[str] = None
    campaign_type: str
    status: str
    target_count: int
    sent_count: int
    start_date: Optional[date] = None
    created_at: datetime


# ===========================================================================
# Interactions
# ===========================================================================
class InteractionCreate(BaseModel):
    type: str = Field("note", max_length=50)
    direction: str = Field("outbound", max_length=20)
    content: str = Field("", max_length=5000)
    outcome: Optional[str] = Field(None, max_length=200)
    follow_up_date: Optional[datetime] = None


class InteractionResponse(BaseModel):
    model_config = _ro
    id: int
    type: str
    direction: str
    content: str
    status: str
    delivery_status: Optional[str] = None
    created_at: datetime


# ===========================================================================
# SMS
# ===========================================================================
class SMSSendRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    customer_id: Optional[int] = None
    template_code: Optional[str] = Field(None, max_length=50)
    message: Optional[str] = Field(None, max_length=1000)
    variables: dict = Field(default_factory=dict)


class SMSTemplateCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    name_fa: Optional[str] = Field(None, max_length=100)
    content: str = Field(..., min_length=1)
    content_fa: Optional[str] = None
    category: str = Field("transactional", max_length=50)
    variables: list[str] = Field(default_factory=list)


class SMSTemplateResponse(BaseModel):
    model_config = _ro
    id: int
    code: str
    name: str
    name_fa: Optional[str] = None
    category: str
    variables: Optional[list] = None
    is_active: bool


# ===========================================================================
# Social Media
# ===========================================================================
class SocialAccountCreate(BaseModel):
    platform: str = Field(..., max_length=30)
    account_name: str = Field(..., max_length=100)
    account_id: str = Field(..., max_length=100)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    auto_reply_enabled: bool = False
    auto_reply_message: Optional[str] = None


class SocialAccountResponse(BaseModel):
    model_config = _ro
    id: int
    platform: str
    account_name: str
    last_sync: Optional[datetime] = None
    is_active: bool


# ===========================================================================
# Analytics
# ===========================================================================
class CRMDashboardResponse(BaseModel):
    leads_total: int
    leads_won: int
    leads_lost: int
    win_rate_pct: float
    channel_activity: dict[str, int]


class PipelineForecastResponse(BaseModel):
    stages: list[dict]
    total_weighted: float
