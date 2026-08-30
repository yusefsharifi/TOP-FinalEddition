"""Support & Ticketing — SLA policies, teams, routing rules, tickets,
comments, KB categories, KB articles, canned responses.

Revision ID: 0009_support_module
Revises: 0008_rbac_module
Create Date: 2024-01-01 00:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009_support_module"
down_revision = "0008_rbac_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    def e(values, name):
        return postgresql.ENUM(*values, name=name, create_type=True)

    requester_type = e(["customer","employee","system","anonymous"], "requestertype")
    ticket_cat = e(["technical","financial","sales","hr","procurement","inventory","general"], "ticketcategory")
    ticket_pri = e(["low","medium","high","critical","emergency"], "ticketpriority")
    ticket_status = e(["new","assigned","in_progress","pending","resolved","closed","reopened","escalated"], "ticketstatus")
    comment_author = e(["agent","customer","system","admin"], "commentauthortype")
    article_status = e(["draft","published","archived"], "articlestatus")

    # ── support_sla_policies ──────────────────────────────────────────────
    op.create_table("support_sla_policies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("response_times", postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column("resolution_times", postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column("business_hours_start", sa.String(5), nullable=False, server_default="08:00"),
        sa.Column("business_hours_end", sa.String(5), nullable=False, server_default="17:00"),
        sa.Column("work_days", postgresql.JSON(), nullable=False, server_default='[5,6,0,1,2]'),
        sa.Column("escalation_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("escalation_after_minutes", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("escalation_manager_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── support_teams ─────────────────────────────────────────────────────
    op.create_table("support_teams",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("categories", postgresql.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("round_robin_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("auto_assign", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── support_team_members ──────────────────────────────────────────────
    op.create_table("support_team_members",
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("support_teams.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("is_lead", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── support_routing_rules ─────────────────────────────────────────────
    op.create_table("support_routing_rules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("category", sa.String(30), nullable=True),
        sa.Column("priority", sa.String(20), nullable=True),
        sa.Column("requester_type", sa.String(20), nullable=True),
        sa.Column("keywords", postgresql.JSON(), nullable=True),
        sa.Column("assign_to_team_id", sa.Integer(), sa.ForeignKey("support_teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assign_to_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sla_policy_id", sa.Integer(), sa.ForeignKey("support_sla_policies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("auto_response_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("auto_response_template", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_support_routing_rules_sort", "support_routing_rules", ["sort_order"])

    # ── support_canned_responses ──────────────────────────────────────────
    op.create_table("support_canned_responses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("title_fa", sa.String(200), nullable=True),
        sa.Column("shortcut", sa.String(30), nullable=True, unique=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_fa", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── support_tickets ───────────────────────────────────────────────────
    op.create_table("support_tickets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ticket_number", sa.String(30), nullable=False, unique=True),
        sa.Column("requester_type", requester_type, nullable=False),
        sa.Column("requester_customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("requester_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("requester_name", sa.String(200), nullable=False),
        sa.Column("requester_email", sa.String(200), nullable=True),
        sa.Column("requester_phone", sa.String(30), nullable=True),
        sa.Column("category", ticket_cat, nullable=False),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("priority", ticket_pri, nullable=False, server_default="medium"),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("attachments", postgresql.JSON(), nullable=True),
        sa.Column("tags", postgresql.JSON(), nullable=True),
        sa.Column("status", ticket_status, nullable=False, server_default="new"),
        sa.Column("assigned_to_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_team_id", sa.Integer(), sa.ForeignKey("support_teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sla_policy_id", sa.Integer(), sa.ForeignKey("support_sla_policies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sla_response_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sla_resolution_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sla_response_breached", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sla_resolution_breached", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("first_response_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_response_minutes", sa.Integer(), nullable=True),
        sa.Column("resolution_minutes", sa.Integer(), nullable=True),
        sa.Column("satisfaction_rating", sa.Integer(), nullable=True),
        sa.Column("satisfaction_comment", sa.Text(), nullable=True),
        sa.Column("satisfaction_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("related_module", sa.String(50), nullable=True),
        sa.Column("related_record_id", sa.Integer(), nullable=True),
        sa.Column("related_record_ref", sa.String(100), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_customer_reply_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_agent_reply_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("satisfaction_rating IS NULL OR satisfaction_rating BETWEEN 1 AND 5", name="chk_ticket_rating"),
    )
    for idx in [["status"], ["priority"], ["assigned_to_id"], ["requester_customer_id"],
                ["sla_resolution_deadline"], ["created_at"]]:
        op.create_index(f"ix_support_tickets_{'_'.join(idx)}", "support_tickets", idx)

    # ── support_ticket_comments ───────────────────────────────────────────
    op.create_table("support_ticket_comments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_type", comment_author, nullable=False),
        sa.Column("author_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("author_customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("author_name", sa.String(200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_internal", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("attachments", postgresql.JSON(), nullable=True),
        sa.Column("is_canned", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("canned_response_id", sa.Integer(), sa.ForeignKey("support_canned_responses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_ticket_comments_ticket_id", "support_ticket_comments", ["ticket_id"])

    # ── KB categories ─────────────────────────────────────────────────────
    op.create_table("support_kb_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("support_kb_categories.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── KB articles ───────────────────────────────────────────────────────
    op.create_table("support_kb_articles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("title_fa", sa.String(500), nullable=True),
        sa.Column("slug", sa.String(200), nullable=False, unique=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_fa", sa.Text(), nullable=True),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("support_kb_categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tags", postgresql.JSON(), nullable=True),
        sa.Column("related_article_ids", postgresql.JSON(), nullable=True),
        sa.Column("status", article_status, nullable=False, server_default="draft"),
        sa.Column("is_internal", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("helpful_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("not_helpful_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("search_vector", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_kb_articles_status", "support_kb_articles", ["status"])
    op.create_index("ix_kb_articles_category", "support_kb_articles", ["category_id"])

    # ── PostgreSQL full-text search trigger for KB articles ───────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION support_kb_search_update()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('simple',
                coalesce(NEW.title, '') || ' ' ||
                coalesce(NEW.title_fa, '') || ' ' ||
                coalesce(NEW.excerpt, '') || ' ' ||
                left(coalesce(NEW.content, ''), 2000)
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER support_kb_search_trigger
        BEFORE INSERT OR UPDATE ON support_kb_articles
        FOR EACH ROW EXECUTE FUNCTION support_kb_search_update();
    """)
    op.execute("""
        CREATE INDEX ix_kb_articles_search_vector
        ON support_kb_articles USING GIN(to_tsvector('simple', 
            coalesce(title,'') || ' ' || coalesce(title_fa,'') || ' ' ||
            coalesce(excerpt,'') || ' ' || left(coalesce(content,''),2000)
        ));
    """)

    # ── Seed: default SLA policy ──────────────────────────────────────────
    op.bulk_insert(
        sa.table("support_sla_policies",
            sa.column("name", sa.String), sa.column("name_fa", sa.String),
            sa.column("is_default", sa.Boolean), sa.column("is_active", sa.Boolean),
            sa.column("response_times", postgresql.JSON),
            sa.column("resolution_times", postgresql.JSON),
            sa.column("business_hours_start", sa.String),
            sa.column("business_hours_end", sa.String),
            sa.column("work_days", postgresql.JSON),
            sa.column("escalation_enabled", sa.Boolean),
            sa.column("escalation_after_minutes", sa.Integer),
        ),
        [
            {
                "name": "Standard SLA", "name_fa": "SLA استاندارد",
                "is_default": True, "is_active": True,
                "response_times": {"low": 240, "medium": 120, "high": 60, "critical": 15, "emergency": 5},
                "resolution_times": {"low": 2880, "medium": 1440, "high": 480, "critical": 240, "emergency": 60},
                "business_hours_start": "08:00", "business_hours_end": "17:00",
                "work_days": [5, 6, 0, 1, 2],
                "escalation_enabled": True, "escalation_after_minutes": 120,
            },
            {
                "name": "VIP SLA", "name_fa": "SLA ویژه",
                "is_default": False, "is_active": True,
                "response_times": {"low": 120, "medium": 60, "high": 30, "critical": 10, "emergency": 5},
                "resolution_times": {"low": 1440, "medium": 720, "high": 240, "critical": 120, "emergency": 30},
                "business_hours_start": "07:00", "business_hours_end": "20:00",
                "work_days": [5, 6, 0, 1, 2, 3],
                "escalation_enabled": True, "escalation_after_minutes": 60,
            },
        ]
    )

    # ── Seed: support teams ───────────────────────────────────────────────
    op.bulk_insert(
        sa.table("support_teams",
            sa.column("name", sa.String), sa.column("name_fa", sa.String),
            sa.column("categories", postgresql.JSON),
            sa.column("is_active", sa.Boolean), sa.column("auto_assign", sa.Boolean),
        ),
        [
            {"name": "Technical Support", "name_fa": "پشتیبانی فنی", "categories": ["technical"], "is_active": True, "auto_assign": True},
            {"name": "Financial Support", "name_fa": "پشتیبانی مالی", "categories": ["financial"], "is_active": True, "auto_assign": True},
            {"name": "General Support",   "name_fa": "پشتیبانی عمومی", "categories": ["general","sales","hr"], "is_active": True, "auto_assign": True},
        ]
    )

    # ── Seed: routing rules ───────────────────────────────────────────────
    op.bulk_insert(
        sa.table("support_routing_rules",
            sa.column("name", sa.String), sa.column("category", sa.String),
            sa.column("sort_order", sa.Integer), sa.column("is_active", sa.Boolean),
            sa.column("auto_response_enabled", sa.Boolean),
            sa.column("auto_response_template", sa.String),
        ),
        [
            {"name": "Route Technical", "category": "technical", "sort_order": 1, "is_active": True, "auto_response_enabled": True, "auto_response_template": "technical"},
            {"name": "Route Financial", "category": "financial", "sort_order": 2, "is_active": True, "auto_response_enabled": True, "auto_response_template": "general"},
            {"name": "Route General",   "category": None,        "sort_order": 99,"is_active": True, "auto_response_enabled": True, "auto_response_template": "general"},
        ]
    )

    # ── Seed: KB categories ───────────────────────────────────────────────
    op.bulk_insert(
        sa.table("support_kb_categories",
            sa.column("name", sa.String), sa.column("name_fa", sa.String),
            sa.column("slug", sa.String), sa.column("sort_order", sa.Integer),
            sa.column("is_active", sa.Boolean), sa.column("icon", sa.String),
        ),
        [
            {"name": "Getting Started", "name_fa": "شروع به کار",   "slug": "getting-started", "sort_order": 1, "is_active": True, "icon": "🚀"},
            {"name": "Finance & Billing","name_fa": "مالی و فاکتور", "slug": "finance-billing", "sort_order": 2, "is_active": True, "icon": "💰"},
            {"name": "Inventory",       "name_fa": "انبارداری",     "slug": "inventory",        "sort_order": 3, "is_active": True, "icon": "📦"},
            {"name": "HR & Payroll",    "name_fa": "منابع انسانی",   "slug": "hr-payroll",       "sort_order": 4, "is_active": True, "icon": "👥"},
            {"name": "Technical",       "name_fa": "فنی",           "slug": "technical",        "sort_order": 5, "is_active": True, "icon": "🔧"},
        ]
    )

    # ── Seed: canned responses ────────────────────────────────────────────
    op.bulk_insert(
        sa.table("support_canned_responses",
            sa.column("title", sa.String), sa.column("title_fa", sa.String),
            sa.column("shortcut", sa.String), sa.column("content", sa.Text),
            sa.column("content_fa", sa.Text), sa.column("category", sa.String),
            sa.column("is_active", sa.Boolean),
        ),
        [
            {
                "title": "Greeting", "title_fa": "سلام",
                "shortcut": "/hi",
                "content": "Hello! Thank you for contacting TOP WorX support. How can I help you today?",
                "content_fa": "سلام! از تماس شما با پشتیبانی TOP WorX متشکریم. چطور می‌توانم کمک کنم؟",
                "category": "general", "is_active": True,
            },
            {
                "title": "Asking for more info", "title_fa": "درخواست اطلاعات بیشتر",
                "shortcut": "/info",
                "content": "Could you please provide more details about the issue? Screenshots or error messages would help us resolve this faster.",
                "content_fa": "لطفاً جزئیات بیشتری درباره مشکل ارائه دهید. تصویر از صفحه یا پیام خطا به ما کمک می‌کند سریع‌تر حل کنیم.",
                "category": "general", "is_active": True,
            },
            {
                "title": "Resolved", "title_fa": "رفع مشکل",
                "shortcut": "/resolved",
                "content": "Your issue has been resolved. Please let us know if you have any further questions.",
                "content_fa": "مشکل شما رفع شد. اگر سوال دیگری دارید خوشحال می‌شویم کمک کنیم.",
                "category": "general", "is_active": True,
            },
            {
                "title": "Invoice clarification", "title_fa": "توضیح فاکتور",
                "shortcut": "/inv",
                "content": "Please refer to your invoice in the Finance module under Sales → Invoices.",
                "content_fa": "لطفاً به فاکتور خود در ماژول مالی زیر فروش ← فاکتورها مراجعه کنید.",
                "category": "financial", "is_active": True,
            },
        ]
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS support_kb_search_trigger ON support_kb_articles")
    op.execute("DROP FUNCTION IF EXISTS support_kb_search_update()")
    for tbl in ["support_kb_articles", "support_kb_categories",
                "support_ticket_comments", "support_tickets",
                "support_canned_responses", "support_routing_rules",
                "support_team_members", "support_teams", "support_sla_policies"]:
        op.drop_table(tbl)
    for e in ["requestertype","ticketcategory","ticketpriority",
              "ticketstatus","commentauthortype","articlestatus"]:
        op.execute(f"DROP TYPE IF EXISTS {e}")
