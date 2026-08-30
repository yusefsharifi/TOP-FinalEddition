"""CRM module — crm_customer_profiles, crm_customer_tags, crm_tag_assignments,
crm_interactions, crm_social_accounts, crm_sms_providers, crm_sms_templates,
crm_campaigns, crm_workflows, crm_workflow_executions, crm_leads.

Revision ID: 0007_crm_module
Revises: 0006_bi_module
Create Date: 2024-01-01 00:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007_crm_module"
down_revision = "0006_bi_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    def e(values, name):
        return postgresql.ENUM(*values, name=name, create_type=True)

    segment = e(["vip","regular","at_risk","churned","prospect","new"], "customersegment")
    lifecycle = e(["lead","prospect","first_purchase","repeat","loyal","churned"], "lifecyclestage")
    lead_source = e(["advertising","referral","social_media","website","event","cold_call","partner","unknown"], "leadsource")
    contact_method = e(["email","sms","phone","whatsapp","telegram","instagram"], "contactmethod")
    interaction_type = e(["call","email","sms","whatsapp","instagram","telegram","meeting","note","website_visit","cart_abandoned"], "interactiontype")
    direction = e(["inbound","outbound","internal"], "interactiondirection")
    i_status = e(["pending","in_progress","resolved","no_response","scheduled"], "interactionstatus")
    social_platform = e(["instagram","telegram","whatsapp_business","linkedin","twitter"], "socialplatform")
    sms_cat = e(["transactional","marketing","otp","reminder","notification"], "smscategory")
    campaign_type = e(["email","sms","social","multi_channel","push"], "campaigntype")
    campaign_status = e(["draft","scheduled","running","paused","completed","cancelled"], "campaignstatus")
    campaign_goal = e(["awareness","engagement","conversion","retention","reactivation"], "campaigngoal")
    lead_status = e(["new","contacted","qualified","proposal","negotiation","won","lost","nurture"], "leadstatus")
    workflow_trigger = e(["new_lead","first_purchase","abandoned_cart","birthday","no_purchase_30_days","high_value_action","lifecycle_change","tag_added","lead_score_threshold"], "workflowtrigger")
    priority = e(["low","medium","high","urgent"], "priority")

    # crm_customer_profiles
    op.create_table("crm_customer_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("mobile", sa.String(30), nullable=True),
        sa.Column("website", sa.String(200), nullable=True),
        sa.Column("social_media", postgresql.JSON(), nullable=True),
        sa.Column("segment", segment, nullable=False, server_default="prospect"),
        sa.Column("lifecycle_stage", lifecycle, nullable=False, server_default="lead"),
        sa.Column("lead_source", lead_source, nullable=True),
        sa.Column("first_contact_date", sa.Date(), nullable=True),
        sa.Column("first_purchase_date", sa.Date(), nullable=True),
        sa.Column("last_contact_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_purchase_date", sa.Date(), nullable=True),
        sa.Column("total_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_revenue", sa.Numeric(18,4), nullable=False, server_default="0"),
        sa.Column("average_order_value", sa.Numeric(18,4), nullable=False, server_default="0"),
        sa.Column("lifetime_value", sa.Numeric(18,4), nullable=False, server_default="0"),
        sa.Column("engagement_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("churn_risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("preferred_contact_method", contact_method, nullable=False, server_default="sms"),
        sa.Column("preferred_language", sa.String(5), nullable=False, server_default="fa"),
        sa.Column("interests", postgresql.JSON(), nullable=True),
        sa.Column("do_not_contact", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("instagram_id", sa.String(100), nullable=True),
        sa.Column("telegram_id", sa.String(100), nullable=True),
        sa.Column("whatsapp_id", sa.String(50), nullable=True),
        sa.Column("company_name", sa.String(200), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("company_size", sa.String(50), nullable=True),
        sa.Column("decision_maker", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("budget_range", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("engagement_score BETWEEN 0 AND 100"),
        sa.CheckConstraint("churn_risk_score BETWEEN 0 AND 100"),
    )
    op.create_index("ix_crm_profiles_segment", "crm_customer_profiles", ["segment"])
    op.create_index("ix_crm_profiles_lifecycle", "crm_customer_profiles", ["lifecycle_stage"])

    # crm_customer_tags
    op.create_table("crm_customer_tags",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("name_fa", sa.String(50), nullable=True),
        sa.Column("color", sa.String(7), nullable=False, server_default="#1976d2"),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("auto_rules", postgresql.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # crm_tag_assignments
    op.create_table("crm_tag_assignments",
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("crm_customer_profiles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("crm_customer_tags.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("assigned_by_id", sa.Integer(), nullable=True),
    )

    # crm_campaigns (before interactions due to FK)
    op.create_table("crm_campaigns",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("campaign_type", campaign_type, nullable=False),
        sa.Column("target_segment", sa.String(50), nullable=True),
        sa.Column("target_tag_ids", postgresql.JSON(), nullable=True),
        sa.Column("target_customer_ids", postgresql.JSON(), nullable=True),
        sa.Column("target_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("send_time", sa.String(10), nullable=True),
        sa.Column("sms_template_code", sa.String(50), nullable=True),
        sa.Column("social_content", sa.Text(), nullable=True),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("email_body", sa.Text(), nullable=True),
        sa.Column("goal", campaign_goal, nullable=False, server_default="engagement"),
        sa.Column("target_metric", sa.String(100), nullable=True),
        sa.Column("target_value", sa.Numeric(18,4), nullable=True),
        sa.Column("status", campaign_status, nullable=False, server_default="draft"),
        sa.Column("celery_task_id", sa.String(100), nullable=True),
        sa.Column("sent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("delivered_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("opened_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conversion_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revenue_generated", sa.Numeric(18,4), nullable=False, server_default="0"),
        sa.Column("cost", sa.Numeric(18,4), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_crm_campaigns_status", "crm_campaigns", ["status"])

    # crm_interactions
    op.create_table("crm_interactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("crm_customer_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interaction_type", interaction_type, nullable=False),
        sa.Column("direction", direction, nullable=False),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("initiated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("handled_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", i_status, nullable=False, server_default="resolved"),
        sa.Column("outcome", sa.String(500), nullable=True),
        sa.Column("follow_up_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("priority", priority, nullable=False, server_default="medium"),
        sa.Column("external_id", sa.String(200), nullable=True),
        sa.Column("external_platform", sa.String(50), nullable=True),
        sa.Column("delivery_status", sa.String(30), nullable=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("crm_campaigns.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_crm_interactions_customer_type", "crm_interactions", ["customer_id", "interaction_type"])
    op.create_index("ix_crm_interactions_created", "crm_interactions", ["created_at"])
    op.create_index("ix_crm_interactions_external_id", "crm_interactions", ["external_id"])

    # crm_social_accounts
    op.create_table("crm_social_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("platform", social_platform, nullable=False),
        sa.Column("account_name", sa.String(100), nullable=False),
        sa.Column("account_id", sa.String(100), nullable=False),
        sa.Column("access_token_encrypted", sa.Text(), nullable=True),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("webhook_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rate_limit_remaining", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("auto_reply_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("auto_reply_message", sa.Text(), nullable=True),
        sa.Column("working_hours_only", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("platform", "account_id"),
    )

    # crm_sms_providers
    op.create_table("crm_sms_providers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("provider_code", sa.String(30), nullable=False, unique=True),
        sa.Column("api_key_encrypted", sa.Text(), nullable=True),
        sa.Column("api_url", sa.String(300), nullable=False),
        sa.Column("sender_number", sa.String(20), nullable=False),
        sa.Column("daily_limit", sa.Integer(), nullable=False, server_default="10000"),
        sa.Column("monthly_limit", sa.Integer(), nullable=False, server_default="200000"),
        sa.Column("used_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("used_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # crm_sms_templates
    op.create_table("crm_sms_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_fa", sa.Text(), nullable=True),
        sa.Column("category", sms_cat, nullable=False, server_default="transactional"),
        sa.Column("variables", postgresql.JSON(), nullable=True),
        sa.Column("approved_by_provider", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("provider_id", sa.Integer(), sa.ForeignKey("crm_sms_providers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # crm_workflows
    op.create_table("crm_workflows",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("trigger_type", workflow_trigger, nullable=False),
        sa.Column("trigger_conditions", postgresql.JSON(), nullable=True),
        sa.Column("actions", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("execution_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # crm_workflow_executions
    op.create_table("crm_workflow_executions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("crm_workflows.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("error_message", sa.Text(), nullable=True),
    )

    # crm_leads
    op.create_table("crm_leads",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", lead_source, nullable=False, server_default="unknown"),
        sa.Column("source_detail", sa.String(300), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("company_name", sa.String(200), nullable=True),
        sa.Column("budget", sa.String(100), nullable=True),
        sa.Column("timeline", sa.String(100), nullable=True),
        sa.Column("authority", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("need", sa.Text(), nullable=True),
        sa.Column("qualification_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assigned_to_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", lead_status, nullable=False, server_default="new"),
        sa.Column("priority", priority, nullable=False, server_default="medium"),
        sa.Column("tags", postgresql.JSON(), nullable=True),
        sa.Column("converted_to_customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("conversion_date", sa.Date(), nullable=True),
        sa.Column("conversion_value", sa.Numeric(18,4), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_follow_up_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_value", sa.Numeric(18,4), nullable=True),
        sa.Column("probability", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("qualification_score BETWEEN 0 AND 100"),
        sa.CheckConstraint("probability BETWEEN 0 AND 100"),
    )
    op.create_index("ix_crm_leads_status", "crm_leads", ["status"])
    op.create_index("ix_crm_leads_assigned_to", "crm_leads", ["assigned_to_id"])

    # ── Seed SMS templates ─────────────────────────────────────────────────
    op.bulk_insert(
        sa.table("crm_sms_templates",
            sa.column("code", sa.String), sa.column("name", sa.String),
            sa.column("name_fa", sa.String), sa.column("content", sa.Text),
            sa.column("content_fa", sa.Text), sa.column("category", sa.String),
            sa.column("variables", postgresql.JSON), sa.column("is_active", sa.Boolean),
            sa.column("approved_by_provider", sa.Boolean),
        ),
        [
            {"code": "welcome",          "name": "Welcome",          "name_fa": "خوش‌آمد",      "content": "Welcome {customer_name}! Your account is ready.", "content_fa": "سلام {customer_name} عزیز! به خانواده ما خوش آمدید. کد تخفیف شما: {discount_code}", "category": "transactional", "variables": ["customer_name","discount_code"], "is_active": True, "approved_by_provider": False},
            {"code": "order_confirmed",  "name": "Order Confirmed",  "name_fa": "تأیید سفارش",  "content": "Order {order_id} confirmed. Amount: {amount}", "content_fa": "{customer_name} گرامی، سفارش شما به شماره {order_id} ثبت شد. مبلغ: {amount} تومان", "category": "transactional", "variables": ["customer_name","order_id","amount"], "is_active": True, "approved_by_provider": False},
            {"code": "payment_reminder", "name": "Payment Reminder", "name_fa": "یادآوری پرداخت","content": "Reminder: Invoice {invoice_number} of {amount} is due.", "content_fa": "یادآوری: فاکتور {invoice_number} به مبلغ {amount} تومان سررسید شد.", "category": "reminder", "variables": ["invoice_number","amount"], "is_active": True, "approved_by_provider": False},
            {"code": "birthday",         "name": "Birthday Wish",    "name_fa": "تبریک تولد",   "content": "Happy Birthday {customer_name}! Use code {code} for 20% off.", "content_fa": "{customer_name} عزیز، تولدتان مبارک! 🎉 کد تخفیف ۲۰٪: {code}", "category": "marketing", "variables": ["customer_name","code"], "is_active": True, "approved_by_provider": False},
            {"code": "otp",              "name": "OTP",              "name_fa": "رمز یکبار مصرف","content": "Your verification code is {code}. Expires in {expiry_minutes} minutes.", "content_fa": "کد تأیید شما: {code} (معتبر تا {expiry_minutes} دقیقه)", "category": "otp", "variables": ["code","expiry_minutes"], "is_active": True, "approved_by_provider": False},
            {"code": "reactivation",     "name": "Reactivation",     "name_fa": "بازفعال‌سازی", "content": "We miss you! Use code {code} for 15% off your next order.", "content_fa": "دلمون برات تنگ شده! با کد {code} ۱۵٪ تخفیف بگیرید.", "category": "marketing", "variables": ["customer_name","code"], "is_active": True, "approved_by_provider": False},
        ]
    )

    # ── Seed default workflows ─────────────────────────────────────────────
    op.bulk_insert(
        sa.table("crm_workflows",
            sa.column("name", sa.String), sa.column("trigger_type", sa.String),
            sa.column("actions", postgresql.JSON), sa.column("is_active", sa.Boolean),
        ),
        [
            {"name": "Welcome New Lead",     "trigger_type": "new_lead",       "actions": [{"delay_hours": 0, "action": "send_sms", "template": "welcome"}, {"delay_hours": 24, "action": "log_note", "note": "Follow up with new lead"}], "is_active": True},
            {"name": "First Purchase Thanks","trigger_type": "first_purchase",  "actions": [{"delay_hours": 0, "action": "send_sms", "template": "order_confirmed"}, {"delay_hours": 48, "action": "add_tag", "tag_id": 1}], "is_active": False},
            {"name": "Birthday Campaign",    "trigger_type": "birthday",        "actions": [{"delay_hours": 0, "action": "send_sms", "template": "birthday"}], "is_active": False},
            {"name": "Win-back at 30 days",  "trigger_type": "no_purchase_30_days","actions": [{"delay_hours": 0, "action": "send_sms", "template": "reactivation"}], "is_active": False},
        ]
    )


def downgrade() -> None:
    for tbl in ["crm_leads","crm_workflow_executions","crm_workflows",
                "crm_sms_templates","crm_sms_providers","crm_social_accounts",
                "crm_interactions","crm_campaigns","crm_tag_assignments",
                "crm_customer_tags","crm_customer_profiles"]:
        op.drop_table(tbl)
    for e in ["customersegment","lifecyclestage","leadsource","contactmethod",
              "interactiontype","interactiondirection","interactionstatus","socialplatform",
              "smscategory","campaigntype","campaignstatus","campaigngoal","leadstatus",
              "workflowtrigger","priority"]:
        op.execute(f"DROP TYPE IF EXISTS {e}")
