"""Operations modules — HSE, Tasks, Contracts, Messages, Settings

Revision ID: 0010_operations_modules
Revises: 0009_support_module
Create Date: 2024-02-01 00:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0010_operations_modules"
down_revision = "0009_support_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    def e(values, name):
        return postgresql.ENUM(*values, name=name, create_type=True)

    # ── HSE Enums ──────────────────────────────────────────────────────────
    incident_severity = e(["low", "medium", "high", "critical"], "incidentseverity")
    incident_status = e(["open", "under_investigation", "resolved", "closed"], "incidentstatus")
    checklist_status = e(["pending", "in_progress", "passed", "failed"], "checkliststatus")

    # ── Task Enums ─────────────────────────────────────────────────────────
    task_priority = e(["low", "medium", "high", "urgent"], "taskpriority")
    task_status = e(["pending", "in_progress", "completed", "cancelled", "blocked"], "projecttaskstatus")

    # ── Contract Enums ─────────────────────────────────────────────────────
    contract_type = e(["sales", "purchase", "employment", "service", "lease", "nda", "other"], "contracttype")
    contract_status = e(["draft", "pending_approval", "approved", "active", "expired", "terminated", "renewed"], "contractstatus")

    # ── Message Enums ──────────────────────────────────────────────────────
    message_priority = e(["low", "normal", "high", "urgent"], "messagepriority")
    notification_severity = e(["info", "warning", "error", "success"], "notificationseverity")

    # ── Settings Enums ─────────────────────────────────────────────────────
    setting_category = e(["general", "security", "email", "notification", "integration", "ui", "finance", "hr", "inventory"], "settingcategory")
    audit_action = e(["create", "update", "delete", "view", "login", "logout", "login_failed", "export", "import", "approve", "reject"], "moduleauditaction")

    # =========================================================================
    # HSE MODULE
    # =========================================================================

    # ── hse_incidents ──────────────────────────────────────────────────────
    op.create_table("hse_incidents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", incident_severity, nullable=False),
        sa.Column("status", incident_status, nullable=False, server_default="open"),
        sa.Column("location", sa.String(200), nullable=False),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("injured_persons", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("witnesses", postgresql.JSON(), nullable=True),
        sa.Column("immediate_actions", sa.Text(), nullable=True),
        sa.Column("assigned_to_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("investigation_notes", sa.Text(), nullable=True),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("corrective_actions", sa.Text(), nullable=True),
        sa.Column("reported_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_hse_incidents_status_severity", "hse_incidents", ["status", "severity"])
    op.create_index("ix_hse_incidents_created_at", "hse_incidents", ["created_at"])
    op.create_index("ix_hse_incidents_department", "hse_incidents", ["department"])
    op.create_index("ix_hse_incidents_reported_by", "hse_incidents", ["reported_by_id"])
    op.create_index("ix_hse_incidents_assigned_to", "hse_incidents", ["assigned_to_id"])
    op.create_index("ix_hse_incidents_resolved_at", "hse_incidents", ["resolved_at"])
    op.create_index("ix_hse_incidents_dept_status_date", "hse_incidents", ["department", "status", "created_at"])

    # ── hse_checklists ─────────────────────────────────────────────────────
    op.create_table("hse_checklists",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(200), nullable=False),
        sa.Column("status", checklist_status, nullable=False, server_default="pending"),
        sa.Column("inspector_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_hse_checklists_location", "hse_checklists", ["location"])
    op.create_index("ix_hse_checklists_created_at", "hse_checklists", ["created_at"])
    op.create_index("ix_hse_checklists_inspector", "hse_checklists", ["inspector_id"])
    op.create_index("ix_hse_checklists_status_created", "hse_checklists", ["status", "created_at"])

    # ── hse_checklist_items ────────────────────────────────────────────────
    op.create_table("hse_checklist_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("checklist_id", sa.Integer(), sa.ForeignKey("hse_checklists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("status", checklist_status, nullable=False, server_default="pending"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
    )
    op.create_index("ix_hse_checklist_items_checklist_id", "hse_checklist_items", ["checklist_id"])
    op.create_index("ix_hse_checklist_items_status", "hse_checklist_items", ["status"])

    # ── hse_alerts ─────────────────────────────────────────────────────────
    op.create_table("hse_alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", incident_severity, nullable=False),
        sa.Column("target_department", sa.String(100), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_hse_alerts_severity", "hse_alerts", ["severity"])
    op.create_index("ix_hse_alerts_created_at", "hse_alerts", ["created_at"])
    op.create_index("ix_hse_alerts_target_dept", "hse_alerts", ["target_department"])

    # =========================================================================
    # TASKS MODULE
    # =========================================================================

    # ── project_tasks ──────────────────────────────────────────────────────
    op.create_table("project_tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", task_status, nullable=False, server_default="pending"),
        sa.Column("priority", task_priority, nullable=False, server_default="medium"),
        sa.Column("assigned_to_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("parent_task_id", sa.Integer(), sa.ForeignKey("project_tasks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_project_tasks_status_priority", "project_tasks", ["status", "priority"])
    op.create_index("ix_project_tasks_assigned", "project_tasks", ["assigned_to_id", "status"])
    op.create_index("ix_project_tasks_due", "project_tasks", ["due_date"])
    op.create_index("ix_project_tasks_created_by", "project_tasks", ["created_by_id"])
    op.create_index("ix_project_tasks_parent", "project_tasks", ["parent_task_id"])
    op.create_index("ix_project_tasks_created_at", "project_tasks", ["created_at"])
    op.create_index("ix_project_tasks_assigned_due", "project_tasks", ["assigned_to_id", "due_date"])

    # ── task_project_comments ──────────────────────────────────────────────
    op.create_table("task_project_comments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("project_tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_task_project_comments_task_id", "task_project_comments", ["task_id"])
    op.create_index("ix_task_comments_created_by", "task_project_comments", ["created_by_id"])
    op.create_index("ix_task_comments_created_at", "task_project_comments", ["created_at"])

    # =========================================================================
    # CONTRACTS MODULE
    # =========================================================================

    # ── contracts ──────────────────────────────────────────────────────────
    op.create_table("contracts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("contract_type", contract_type, nullable=False),
        sa.Column("status", contract_status, nullable=False, server_default="draft"),
        sa.Column("counterparty_name", sa.String(200), nullable=False),
        sa.Column("counterparty_contact", sa.String(200), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(10), nullable=False, server_default="IRR"),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("renewal_days_notice", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("approved_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_contracts_status_type", "contracts", ["status", "contract_type"])
    op.create_index("ix_contracts_end_date", "contracts", ["end_date"])
    op.create_index("ix_contracts_counterparty", "contracts", ["counterparty_name"])
    op.create_index("ix_contracts_created_by", "contracts", ["created_by_id"])
    op.create_index("ix_contracts_approved_by", "contracts", ["approved_by_id"])
    op.create_index("ix_contracts_start_date", "contracts", ["start_date"])
    op.create_index("ix_contracts_value", "contracts", ["value"])
    op.create_index("ix_contracts_auto_renew_expiry", "contracts", ["auto_renew", "end_date"])
    op.create_index("ix_contracts_status_end_date", "contracts", ["status", "end_date"])

    # ── contract_attachments ───────────────────────────────────────────────
    op.create_table("contract_attachments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("contract_id", sa.Integer(), sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(300), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("uploaded_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_contract_attachments_contract_id", "contract_attachments", ["contract_id"])
    op.create_index("ix_contract_attachments_uploader", "contract_attachments", ["uploaded_by_id"])

    # ── contract_history ───────────────────────────────────────────────────
    op.create_table("contract_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("contract_id", sa.Integer(), sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("old_status", sa.String(30), nullable=True),
        sa.Column("new_status", sa.String(30), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("performed_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("performed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_contract_history_contract_id", "contract_history", ["contract_id"])
    op.create_index("ix_contract_history_action", "contract_history", ["action"])
    op.create_index("ix_contract_history_performed_at", "contract_history", ["performed_at"])
    op.create_index("ix_contract_history_performed_by", "contract_history", ["performed_by_id"])

    # =========================================================================
    # MESSAGES MODULE
    # =========================================================================

    # ── conversations ──────────────────────────────────────────────────────
    op.create_table("conversations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("is_group", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_conversations_created", "conversations", ["created_at"])
    op.create_index("ix_conversations_is_group", "conversations", ["is_group"])
    op.create_index("ix_conversations_created_by", "conversations", ["created_by_id"])

    # ── conversation_participants ──────────────────────────────────────────
    op.create_table("conversation_participants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("last_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_muted", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_index("ix_conversation_participants_conversation_id", "conversation_participants", ["conversation_id"])
    op.create_index("ix_conversation_participants_user_id", "conversation_participants", ["user_id"])
    op.create_unique_constraint("uq_conversation_participant", "conversation_participants", ["conversation_id", "user_id"])
    op.create_index("ix_conv_participants_last_read", "conversation_participants", ["last_read_at"])

    # ── messages ───────────────────────────────────────────────────────────
    op.create_table("messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("priority", message_priority, nullable=False, server_default="normal"),
        sa.Column("parent_message_id", sa.Integer(), sa.ForeignKey("messages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_messages_conversation_created", "messages", ["conversation_id", "created_at"])
    op.create_index("ix_messages_sender", "messages", ["sender_id"])
    op.create_index("ix_messages_priority", "messages", ["priority"])

    # ── message_read_receipts ──────────────────────────────────────────────
    op.create_table("message_read_receipts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("message_id", sa.Integer(), sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_message_read_receipts_message_id", "message_read_receipts", ["message_id"])
    op.create_unique_constraint("uq_message_read_receipt", "message_read_receipts", ["message_id", "user_id"])
    op.create_index("ix_read_receipts_user", "message_read_receipts", ["user_id"])
    op.create_index("ix_read_receipts_read_at", "message_read_receipts", ["read_at"])

    # ── notifications ──────────────────────────────────────────────────────
    op.create_table("notifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", notification_severity, nullable=False, server_default="info"),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_module", sa.String(50), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_notifications_user_unread", "notifications", ["user_id", "is_read"])
    op.create_index("ix_notifications_created", "notifications", ["created_at"])
    op.create_index("ix_notifications_severity", "notifications", ["severity"])
    op.create_index("ix_notifications_source", "notifications", ["source_module", "source_id"])

    # =========================================================================
    # SETTINGS MODULE
    # =========================================================================

    # ── system_settings ────────────────────────────────────────────────────
    op.create_table("system_settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("value_type", sa.String(20), nullable=False, server_default="string"),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("category", setting_category, nullable=False, server_default="general"),
        sa.Column("is_sensitive", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_readonly", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_system_settings_key", "system_settings", ["key"])
    op.create_index("ix_system_settings_category", "system_settings", ["category"])
    op.create_index("ix_system_settings_sensitive", "system_settings", ["is_sensitive"])
    op.create_index("ix_system_settings_value_type", "system_settings", ["value_type"])

    # ── module_audit_logs ──────────────────────────────────────────────────
    op.create_table("module_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("user_email", sa.String(200), nullable=True),
        sa.Column("action", audit_action, nullable=False),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("resource_description", sa.String(500), nullable=True),
        sa.Column("old_values", postgresql.JSON(), nullable=True),
        sa.Column("new_values", postgresql.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_module_audit_user_id", "module_audit_logs", ["user_id"])
    op.create_index("ix_module_audit_action", "module_audit_logs", ["action"])
    op.create_index("ix_module_audit_module", "module_audit_logs", ["module"])
    op.create_index("ix_module_audit_resource", "module_audit_logs", ["resource_type", "resource_id"])
    op.create_index("ix_module_audit_created", "module_audit_logs", ["created_at"])
    op.create_index("ix_module_audit_user_date", "module_audit_logs", ["user_id", "created_at"])

    # ── system_notifications ───────────────────────────────────────────────
    op.create_table("system_notifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("target_roles", postgresql.JSON(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_system_notifications_active", "system_notifications", ["is_active", "created_at"])
    op.create_index("ix_system_notifications_severity", "system_notifications", ["severity"])
    op.create_index("ix_system_notifications_expires", "system_notifications", ["expires_at"])


def downgrade() -> None:
    # Drop tables in reverse order (respect FK dependencies)
    for tbl in [
        "system_notifications", "module_audit_logs", "system_settings",
        "notifications", "message_read_receipts", "messages",
        "conversation_participants", "conversations",
        "contract_history", "contract_attachments", "contracts",
        "task_project_comments", "project_tasks",
        "hse_alerts", "hse_checklist_items", "hse_checklists", "hse_incidents",
    ]:
        op.drop_table(tbl)

    # Drop enums in reverse order
    for enum_name in [
        "moduleauditaction", "settingcategory",
        "notificationseverity", "messagepriority",
        "contractstatus", "contracttype",
        "projecttaskstatus", "taskpriority",
        "checkliststatus", "incidentstatus", "incidentseverity",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
