"""
CRM Module — FastAPI Router
TOP WorX ERP System

INTEGRATION POINT: Register in api.py:
    from app.api.api_v1.endpoints.crm import router as crm_router
    api_router.include_router(crm_router, prefix="/crm", tags=["crm"])
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select

from app.models.crm import (
    AutomationWorkflow, CustomerInteraction, CustomerProfile, CustomerTag,
    InteractionDirection, InteractionType, Lead, LeadStatus,
    MarketingCampaign, CampaignStatus, SMSProvider, SMSTemplate,
    SocialMediaAccount, SocialPlatform, WorkflowTrigger,
)
from app.services.crm_service import CRMError, campaign_service, crm_service, lead_scoring_engine, workflow_engine
from app.services.sms_service import SMSProviderError, sms_service
from app.services.social_services import instagram_service, telegram_service, whatsapp_service

# ---------------------------------------------------------------------------
# Real dependencies from centralized deps module
# ---------------------------------------------------------------------------
from app.api.deps import DBDep, get_current_active_user as get_current_user

# CU = CurrentUser alias — typed dependency for this module
from typing import Annotated
from app.models.auth_enhanced import User
CU = Annotated[User, Depends(get_current_user)]

router = APIRouter()


def _crm_err(exc: Exception) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


# ===========================================================================
# CUSTOMERS — 360° VIEW
# ===========================================================================
@router.get("/customers/360/{customer_id}")
async def customer_360(customer_id: int, db: DBDep, cu: CU) -> dict:
    """Full 360° customer profile: profile, interactions, invoices, tags."""
    try:
        return await crm_service.get_customer_360(db, customer_id)
    except CRMError as exc:
        raise _crm_err(exc)


@router.get("/customers/segments")
async def list_segments(db: DBDep, cu: CU) -> list[dict]:
    """Count of customers per segment."""
    rows = (await db.execute(
        select(CustomerProfile.segment, func.count(CustomerProfile.id).label("count"))
        .group_by(CustomerProfile.segment)
    )).all()
    return [{"segment": r.segment.value, "count": r.count} for r in rows]


@router.post("/customers/{customer_id}/tags/{tag_id}", status_code=201)
async def add_customer_tag(customer_id: int, tag_id: int, db: DBDep, cu: CU) -> dict:
    profile = await crm_service.get_or_create_profile(db, customer_id)
    await crm_service.add_tag(db, profile.id, tag_id, user_id=cu.id)
    await db.commit()
    return {"status": "tagged"}


@router.delete("/customers/{customer_id}/tags/{tag_id}", status_code=204)
async def remove_customer_tag(customer_id: int, tag_id: int, db: DBDep, cu: CU) -> None:
    profile = await crm_service.get_or_create_profile(db, customer_id)
    await crm_service.remove_tag(db, profile.id, tag_id)
    await db.commit()


@router.get("/customers/{customer_id}/interactions")
async def get_interactions(
    customer_id: int, db: DBDep, cu: CU,
    interaction_type: Optional[str] = None,
    offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    """Full interaction history across all channels."""
    profile = await crm_service.get_or_create_profile(db, customer_id)
    q = select(CustomerInteraction).where(CustomerInteraction.customer_id == profile.id).order_by(CustomerInteraction.created_at.desc())
    if interaction_type:
        q = q.where(CustomerInteraction.interaction_type == interaction_type)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [{"id": r.id, "type": r.interaction_type.value, "direction": r.direction.value,
             "content": (r.content or "")[:200], "status": r.status.value,
             "delivery_status": r.delivery_status, "created_at": r.created_at.isoformat()}
            for r in rows]


@router.post("/customers/{customer_id}/interactions", status_code=201)
async def log_interaction(customer_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    """Log a manual interaction (call, meeting, note, etc.)."""
    profile = await crm_service.get_or_create_profile(db, customer_id)
    from app.models.crm import InteractionDirection as D
    interaction = await crm_service.log_interaction(
        db, profile.id,
        interaction_type=data.get("type", "note"),
        direction=D(data.get("direction", "outbound")),
        content=data.get("content", ""),
        user_id=cu.id,
        outcome=data.get("outcome"),
        follow_up_date=datetime.fromisoformat(data["follow_up_date"]) if data.get("follow_up_date") else None,
    )
    await db.commit()
    return {"id": interaction.id, "status": "logged"}


@router.post("/customers/{customer_id}/refresh-scores")
async def refresh_scores(customer_id: int, db: DBDep, cu: CU) -> dict:
    profile = await crm_service.get_or_create_profile(db, customer_id)
    profile = await crm_service.refresh_scores(db, profile.id)
    await db.commit()
    return {"engagement_score": profile.engagement_score, "churn_risk_score": profile.churn_risk_score}


# ===========================================================================
# TAGS
# ===========================================================================
@router.get("/tags")
async def list_tags(db: DBDep, cu: CU) -> list[dict]:
    rows = (await db.execute(select(CustomerTag).where(CustomerTag.is_active.is_(True)).order_by(CustomerTag.name))).scalars().all()
    return [{"id": t.id, "name": t.name, "name_fa": t.name_fa, "color": t.color, "category": t.category} for t in rows]


@router.post("/tags", status_code=201)
async def create_tag(data: dict, db: DBDep, cu: CU) -> dict:
    tag = CustomerTag(name=data["name"], name_fa=data.get("name_fa"), color=data.get("color", "#1976d2"),
                      category=data.get("category"), created_by_id=cu.id)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return {"id": tag.id, "name": tag.name}


# ===========================================================================
# SOCIAL MEDIA
# ===========================================================================
@router.get("/social/accounts")
async def list_social_accounts(db: DBDep, cu: CU) -> list[dict]:
    rows = (await db.execute(select(SocialMediaAccount).where(SocialMediaAccount.is_active.is_(True)))).scalars().all()
    return [{"id": r.id, "platform": r.platform.value, "account_name": r.account_name,
             "last_sync": r.last_sync.isoformat() if r.last_sync else None} for r in rows]


@router.post("/social/accounts", status_code=201)
async def connect_social_account(data: dict, db: DBDep, cu: CU) -> dict:
    from app.services.sms_service import _encrypt
    account = SocialMediaAccount(
        platform=SocialPlatform(data["platform"]),
        account_name=data["account_name"],
        account_id=data["account_id"],
        access_token_encrypted=_encrypt(data.get("access_token", "")),
        refresh_token_encrypted=_encrypt(data.get("refresh_token", "")) if data.get("refresh_token") else None,
        auto_reply_enabled=data.get("auto_reply_enabled", False),
        auto_reply_message=data.get("auto_reply_message"),
        created_by_id=cu.id,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return {"id": account.id, "platform": account.platform.value, "status": "connected"}


@router.get("/social/messages")
async def unified_inbox(
    db: DBDep, cu: CU,
    platform: Optional[str] = None,
    status: Optional[str] = "pending",
    offset: int = 0, limit: int = 50,
) -> list[dict]:
    """Unified inbox: all inbound social/SMS interactions."""
    q = (
        select(CustomerInteraction)
        .where(
            CustomerInteraction.direction == InteractionDirection.INBOUND,
            CustomerInteraction.interaction_type.in_([
                InteractionType.INSTAGRAM, InteractionType.TELEGRAM,
                InteractionType.WHATSAPP, InteractionType.SMS,
            ]),
        )
        .order_by(CustomerInteraction.created_at.desc())
    )
    if platform:
        q = q.where(CustomerInteraction.external_platform == platform)
    if status:
        q = q.where(CustomerInteraction.status == status)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [{"id": r.id, "platform": r.external_platform, "type": r.interaction_type.value,
             "content": (r.content or "")[:200], "status": r.status.value,
             "customer_id": r.customer_id, "created_at": r.created_at.isoformat()} for r in rows]


@router.post("/social/messages/{interaction_id}/reply")
async def reply_to_message(interaction_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    """Reply to a social/SMS message via the appropriate channel."""
    interaction_r = await db.execute(select(CustomerInteraction).where(CustomerInteraction.id == interaction_id))
    interaction = interaction_r.scalar_one_or_none()
    if not interaction:
        raise HTTPException(404, "Interaction not found")

    reply_text = data.get("message", "")
    platform = interaction.external_platform

    if platform == "telegram":
        accounts_r = await db.execute(select(SocialMediaAccount).where(
            SocialMediaAccount.platform == SocialPlatform.TELEGRAM, SocialMediaAccount.is_active.is_(True)))
        account = accounts_r.scalars().first()
        if account:
            await telegram_service.send_message(db, account.id, interaction.customer_id, reply_text)

    elif platform in ("sms", None):
        profile_r = await db.execute(select(CustomerProfile).where(CustomerProfile.id == interaction.customer_id))
        profile = profile_r.scalar_one_or_none()
        if profile:
            from app.models.sales import Customer
            customer_r = await db.execute(select(Customer).where(Customer.id == profile.customer_id))
            customer = customer_r.scalar_one_or_none()
            if customer and customer.phone:
                await sms_service.send_single(db, phone=customer.phone, customer_id=customer.id, custom_message=reply_text, user_id=cu.id)

    # Mark original as resolved
    interaction.status = "resolved"
    await db.commit()
    return {"status": "replied"}


# Telegram webhook endpoint
@router.post("/social/telegram/webhook/{account_id}", include_in_schema=False)
async def telegram_webhook(account_id: int, request: Request, db: DBDep) -> dict:
    """Receive Telegram webhook updates."""
    update = await request.json()
    result = await telegram_service.handle_incoming_message(db, account_id, update)
    await db.commit()
    return result


# WhatsApp webhook
@router.get("/social/whatsapp/webhook/{account_id}", include_in_schema=False)
async def whatsapp_webhook_verify(account_id: int, request: Request) -> str:
    """WhatsApp webhook verification challenge."""
    import os
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "topworx_verify")
    params = dict(request.query_params)
    if params.get("hub.verify_token") == verify_token:
        return params.get("hub.challenge", "")
    raise HTTPException(403, "Invalid verify token")


@router.post("/social/whatsapp/webhook/{account_id}", include_in_schema=False)
async def whatsapp_webhook_receive(account_id: int, request: Request, db: DBDep) -> dict:
    payload = await request.json()
    result = await whatsapp_service.receive_webhook(db, payload)
    await db.commit()
    return result


# ===========================================================================
# SMS
# ===========================================================================
@router.post("/sms/send")
async def send_sms(data: dict, db: DBDep, cu: CU) -> dict:
    """Send single SMS to a customer."""
    try:
        result = await sms_service.send_single(
            db,
            phone=data["phone"],
            customer_id=data.get("customer_id"),
            template_code=data.get("template_code"),
            custom_message=data.get("message"),
            variables=data.get("variables", {}),
            user_id=cu.id,
        )
    except SMSProviderError as exc:
        raise _crm_err(exc)
    await db.commit()
    return result


@router.post("/sms/bulk")
async def send_bulk_sms(data: dict, db: DBDep, cu: CU, background_tasks: BackgroundTasks) -> dict:
    """Queue bulk SMS campaign. Processed by Celery in background."""
    campaign_id = data.get("campaign_id")
    template_code = data.get("template_code")
    customer_ids = data.get("customer_ids", [])

    # Build phone list
    from app.models.sales import Customer
    rows = (await db.execute(
        select(Customer.id, Customer.phone).where(
            Customer.id.in_(customer_ids), Customer.phone.isnot(None)
        )
    )).all()
    pairs = [(r.phone, r.id) for r in rows]

    # Queue in background (Celery in production)
    background_tasks.add_task(
        sms_service.send_bulk, db,
        phone_customer_pairs=pairs,
        template_code=template_code,
        campaign_id=campaign_id,
        user_id=cu.id,
    )
    return {"queued": len(pairs), "status": "processing"}


@router.get("/sms/templates")
async def list_sms_templates(db: DBDep, cu: CU) -> list[dict]:
    rows = (await db.execute(select(SMSTemplate).where(SMSTemplate.is_active.is_(True)).order_by(SMSTemplate.code))).scalars().all()
    return [{"id": t.id, "code": t.code, "name": t.name, "name_fa": t.name_fa,
             "category": t.category.value, "variables": t.variables} for t in rows]


@router.post("/sms/templates", status_code=201)
async def create_sms_template(data: dict, db: DBDep, cu: CU) -> dict:
    tmpl = SMSTemplate(
        code=data["code"], name=data["name"], name_fa=data.get("name_fa"),
        content=data["content"], content_fa=data.get("content_fa"),
        category=data.get("category", "transactional"),
        variables=data.get("variables", []),
        created_by_id=cu.id,
    )
    db.add(tmpl)
    await db.commit()
    await db.refresh(tmpl)
    return {"id": tmpl.id, "code": tmpl.code}


@router.post("/sms/webhook/{provider}")
async def sms_inbound_webhook(provider: str, request: Request, db: DBDep) -> dict:
    """Receive incoming SMS from provider webhook."""
    payload = await request.json()
    # Kavenegar format
    if provider == "kavenegar":
        phone = payload.get("from", "")
        message_text = payload.get("message", "")
        external_id = payload.get("messageid", "")
    # MeliPayamak format
    elif provider == "melipayamak":
        phone = payload.get("from", "")
        message_text = payload.get("text", "")
        external_id = payload.get("id", "")
    else:
        phone = payload.get("from", "")
        message_text = payload.get("message", payload.get("text", ""))
        external_id = payload.get("id", "")

    result = await sms_service.handle_inbound(db, phone, message_text, provider, external_id)
    await db.commit()
    return result


# ===========================================================================
# CAMPAIGNS
# ===========================================================================
@router.get("/campaigns")
async def list_campaigns(
    db: DBDep, cu: CU,
    status: Optional[CampaignStatus] = None,
    offset: int = 0, limit: int = 50,
) -> list[dict]:
    q = select(MarketingCampaign).order_by(MarketingCampaign.id.desc())
    if status:
        q = q.where(MarketingCampaign.status == status)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [{"id": c.id, "name": c.name, "type": c.campaign_type.value, "status": c.status.value,
             "target_count": c.target_count, "sent_count": c.sent_count, "start_date": str(c.start_date) if c.start_date else None}
            for c in rows]


@router.post("/campaigns", status_code=201)
async def create_campaign(data: dict, db: DBDep, cu: CU) -> dict:
    campaign = MarketingCampaign(
        name=data["name"], description=data.get("description"),
        campaign_type=data["campaign_type"],
        target_segment=data.get("target_segment"),
        target_tag_ids=data.get("target_tag_ids"),
        target_customer_ids=data.get("target_customer_ids"),
        sms_template_code=data.get("sms_template_code"),
        subject=data.get("subject"),
        goal=data.get("goal", "engagement"),
        created_by_id=cu.id,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return {"id": campaign.id, "name": campaign.name, "status": campaign.status.value}


@router.post("/campaigns/{campaign_id}/launch")
async def launch_campaign(campaign_id: int, db: DBDep, cu: CU) -> dict:
    campaign_r = await db.execute(select(MarketingCampaign).where(MarketingCampaign.id == campaign_id))
    campaign = campaign_r.scalar_one_or_none()
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    try:
        result = await campaign_service.launch_campaign(db, campaign, user_id=cu.id)
    except CRMError as exc:
        raise _crm_err(exc)
    await db.commit()
    return result


@router.get("/campaigns/{campaign_id}/performance")
async def campaign_performance(campaign_id: int, db: DBDep, cu: CU) -> dict:
    try:
        return await campaign_service.get_performance(db, campaign_id)
    except CRMError as exc:
        raise _crm_err(exc)


# ===========================================================================
# LEADS
# ===========================================================================
@router.get("/leads")
async def list_leads(
    db: DBDep, cu: CU,
    status: Optional[LeadStatus] = None,
    assigned_to_me: bool = False,
    offset: int = 0, limit: int = 50,
) -> list[dict]:
    q = select(Lead).order_by(Lead.id.desc())
    if status:
        q = q.where(Lead.status == status)
    if assigned_to_me:
        q = q.where(Lead.assigned_to_id == cu.id)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [{"id": r.id, "name": r.name, "phone": r.phone, "status": r.status.value,
             "score": r.qualification_score, "probability": r.probability,
             "estimated_value": float(r.estimated_value or 0),
             "assigned_to_id": r.assigned_to_id,
             "next_follow_up": r.next_follow_up_at.isoformat() if r.next_follow_up_at else None}
            for r in rows]


@router.get("/leads/pipeline")
async def lead_pipeline(db: DBDep, cu: CU) -> dict:
    """Kanban board data: leads grouped by status with totals."""
    rows = (await db.execute(
        select(Lead.status, func.count(Lead.id).label("count"),
               func.coalesce(func.sum(Lead.estimated_value), Decimal("0")).label("value"))
        .group_by(Lead.status)
    )).all()
    pipeline = {}
    for r in rows:
        pipeline[r.status.value] = {"count": r.count, "total_value": float(r.value or 0)}
    return pipeline


@router.post("/leads", status_code=201)
async def create_lead(data: dict, db: DBDep, cu: CU) -> dict:
    lead = Lead(
        name=data["name"], name_fa=data.get("name_fa"),
        email=data.get("email"), phone=data.get("phone"),
        company_name=data.get("company_name"),
        source=data.get("source", "unknown"),
        source_detail=data.get("source_detail"),
        budget=data.get("budget"), timeline=data.get("timeline"),
        authority=data.get("authority", False), need=data.get("need"),
        estimated_value=Decimal(str(data["estimated_value"])) if data.get("estimated_value") else None,
        probability=data.get("probability", 50),
        created_by_id=cu.id,
    )
    db.add(lead)
    await db.flush()
    score, action = await lead_scoring_engine.score_and_auto_qualify(db, lead)
    # Trigger new lead workflow
    await workflow_engine.trigger(db, WorkflowTrigger.NEW_LEAD, lead_id=lead.id)
    await db.commit()
    return {"id": lead.id, "score": score, "status": lead.status.value, "action": action}


@router.post("/leads/{lead_id}/assign")
async def assign_lead(lead_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    lead.assigned_to_id = data["user_id"]
    lead.assigned_at = datetime.utcnow()
    await db.commit()
    return {"status": "assigned", "user_id": data["user_id"]}


@router.post("/leads/{lead_id}/convert")
async def convert_lead_to_customer(lead_id: int, db: DBDep, cu: CU) -> dict:
    """Convert a qualified lead to a Sales Customer."""
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")

    from app.models.sales import Customer
    import random, string
    code = "LEAD-" + "".join(random.choices(string.digits, k=5))
    customer = Customer(
        code=code, name=lead.name, name_fa=lead.name_fa,
        phone=lead.phone, email=lead.email,
        is_active=True, payment_terms=30,
        created_by_id=cu.id,
    )
    db.add(customer)
    await db.flush()

    # Create CRM profile
    profile = CustomerProfile(
        customer_id=customer.id,
        lifecycle_stage="first_purchase",
        lead_source=lead.source,
        first_contact_date=lead.created_at.date(),
    )
    db.add(profile)
    await db.flush()

    lead.status = LeadStatus.WON
    lead.converted_to_customer_id = customer.id
    lead.conversion_date = datetime.utcnow().date()
    lead.conversion_value = lead.estimated_value

    await workflow_engine.trigger(db, WorkflowTrigger.FIRST_PURCHASE, customer_id=customer.id)
    await db.commit()
    return {"customer_id": customer.id, "status": "converted"}


@router.post("/leads/{lead_id}/score")
async def rescore_lead(lead_id: int, db: DBDep, cu: CU) -> dict:
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    score, action = await lead_scoring_engine.score_and_auto_qualify(db, lead)
    await db.commit()
    return {"score": score, "status": lead.status.value, "action": action}


@router.get("/leads/forecast")
async def pipeline_forecast(db: DBDep, cu: CU) -> dict:
    """Weighted pipeline value: sum(estimated_value × probability)."""
    rows = (await db.execute(
        select(Lead.status,
               func.count(Lead.id).label("count"),
               func.sum(Lead.estimated_value).label("total"),
               func.sum(Lead.estimated_value * Lead.probability / 100).label("weighted"))
        .where(Lead.status.notin_([LeadStatus.WON, LeadStatus.LOST]))
        .group_by(Lead.status)
    )).all()
    return {
        "stages": [{"status": r.status.value, "count": r.count,
                    "total_value": float(r.total or 0), "weighted_value": float(r.weighted or 0)}
                   for r in rows],
        "total_weighted": sum(float(r.weighted or 0) for r in rows),
    }


# ===========================================================================
# ANALYTICS
# ===========================================================================
@router.get("/analytics/dashboard")
async def crm_analytics(db: DBDep, cu: CU) -> dict:
    """CRM KPIs: conversion rates, channel performance, lead metrics."""
    total_leads = (await db.execute(select(func.count(Lead.id)))).scalar_one() or 0
    won = (await db.execute(select(func.count(Lead.id)).where(Lead.status == LeadStatus.WON))).scalar_one() or 0
    lost = (await db.execute(select(func.count(Lead.id)).where(Lead.status == LeadStatus.LOST))).scalar_one() or 0

    channel_rows = (await db.execute(
        select(CustomerInteraction.interaction_type, func.count(CustomerInteraction.id).label("cnt"))
        .group_by(CustomerInteraction.interaction_type)
    )).all()

    return {
        "leads_total": total_leads,
        "leads_won": won,
        "leads_lost": lost,
        "win_rate_pct": round(won / (won + lost) * 100, 1) if (won + lost) > 0 else 0,
        "channel_activity": {r.interaction_type.value: r.cnt for r in channel_rows},
    }
