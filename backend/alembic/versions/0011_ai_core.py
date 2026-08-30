"""AI Core Module Tables

Revision ID: 0011
Revises: 0010
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # AI Enums
    message_role_enum = sa.Enum("user", "assistant", "system", name="message_role_enum")
    message_role_enum.create(op.get_bind(), checkfirst=True)

    workflow_trigger_enum = sa.Enum("manual", "scheduled", "event", "threshold", name="workflow_trigger_enum")
    workflow_trigger_enum.create(op.get_bind(), checkfirst=True)

    workflow_action_enum = sa.Enum("create_record", "update_record", "send_notification", "send_email", "run_query", "call_webhook", "ai_analysis", name="workflow_action_enum")
    workflow_action_enum.create(op.get_bind(), checkfirst=True)

    insight_type_enum = sa.Enum("trend", "anomaly", "prediction", "recommendation", "alert", "summary", name="insight_type_enum")
    insight_type_enum.create(op.get_bind(), checkfirst=True)

    insight_severity_enum = sa.Enum("info", "low", "medium", "high", "critical", name="insight_severity_enum")
    insight_severity_enum.create(op.get_bind(), checkfirst=True)

    # AI Conversations
    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("module", sa.String(50), nullable=True),
        sa.Column("model", sa.String(50), nullable=False, server_default="gpt-4"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_cost", sa.Numeric(10, 6), nullable=False, server_default=sa.text("0")),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_conversations_user_id", "ai_conversations", ["user_id"])
    op.create_index("ix_ai_conversations_module", "ai_conversations", ["module"])
    op.create_index("ix_ai_conversations_user_module", "ai_conversations", ["user_id", "module"])
    op.create_index("ix_ai_conversations_created_at", "ai_conversations", ["created_at"])

    # AI Messages
    op.create_table(
        "ai_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", message_role_enum, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model", sa.String(50), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("cost", sa.Numeric(10, 6), nullable=False, server_default=sa.text("0")),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_messages_conversation_id", "ai_messages", ["conversation_id"])
    op.create_index("ix_ai_messages_conversation_created", "ai_messages", ["conversation_id", "created_at"])

    # AI Prompts
    op.create_table(
        "ai_prompts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("user_prompt_template", sa.Text(), nullable=False),
        sa.Column("model", sa.String(50), nullable=False, server_default="gpt-4"),
        sa.Column("temperature", sa.Numeric(3, 2), nullable=False, server_default=sa.text("0.7")),
        sa.Column("max_tokens", sa.Integer(), nullable=False, server_default=sa.text("2000")),
        sa.Column("module", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("avg_tokens", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_prompts_module", "ai_prompts", ["module"])

    # AI Usage Logs
    op.create_table(
        "ai_usage_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("ai_conversations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("endpoint", sa.String(100), nullable=False),
        sa.Column("model", sa.String(50), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("cost", sa.Numeric(10, 6), nullable=False, server_default=sa.text("0")),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_usage_logs_user_id", "ai_usage_logs", ["user_id"])
    op.create_index("ix_ai_usage_logs_endpoint", "ai_usage_logs", ["endpoint"])
    op.create_index("ix_ai_usage_logs_model", "ai_usage_logs", ["model"])
    op.create_index("ix_ai_usage_logs_created_at", "ai_usage_logs", ["created_at"])
    op.create_index("ix_ai_usage_user_date", "ai_usage_logs", ["user_id", "created_at"])
    op.create_index("ix_ai_usage_model_date", "ai_usage_logs", ["model", "created_at"])

    # AI Embeddings
    op.create_table(
        "ai_embeddings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=False),
        sa.Column("source_module", sa.String(50), nullable=False),
        sa.Column("source_table", sa.String(100), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_embeddings_source_module", "ai_embeddings", ["source_module"])
    op.create_index("ix_ai_embeddings_source", "ai_embeddings", ["source_module", "source_table", "source_id"])

    # AI Workflows
    op.create_table(
        "ai_workflows",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("trigger_module", sa.String(50), nullable=False),
        sa.Column("trigger_event", sa.String(50), nullable=False),
        sa.Column("trigger_type", workflow_trigger_enum, nullable=False, server_default="event"),
        sa.Column("condition", sa.JSON(), nullable=True),
        sa.Column("action_type", workflow_action_enum, nullable=False),
        sa.Column("action_config", sa.JSON(), nullable=False),
        sa.Column("ai_prompt_id", sa.Integer(), sa.ForeignKey("ai_prompts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trigger_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_workflows_trigger_module", "ai_workflows", ["trigger_module"])
    op.create_index("ix_ai_workflows_trigger", "ai_workflows", ["trigger_module", "trigger_event"])

    # AI Insights
    op.create_table(
        "ai_insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("insight_type", insight_type_enum, nullable=False),
        sa.Column("severity", insight_severity_enum, nullable=False, server_default="info"),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_dismissed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("action_taken", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_insights_user_id", "ai_insights", ["user_id"])
    op.create_index("ix_ai_insights_insight_type", "ai_insights", ["insight_type"])
    op.create_index("ix_ai_insights_module", "ai_insights", ["module"])
    op.create_index("ix_ai_insights_created_at", "ai_insights", ["created_at"])
    op.create_index("ix_ai_insights_module_type", "ai_insights", ["module", "insight_type"])
    op.create_index("ix_ai_insights_user_unread", "ai_insights", ["user_id", "is_read"])


def downgrade() -> None:
    op.drop_table("ai_insights")
    op.drop_table("ai_workflows")
    op.drop_table("ai_embeddings")
    op.drop_table("ai_usage_logs")
    op.drop_table("ai_prompts")
    op.drop_table("ai_messages")
    op.drop_table("ai_conversations")

    sa.Enum(name="insight_severity_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="insight_type_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="workflow_action_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="workflow_trigger_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="message_role_enum").drop(op.get_bind(), checkfirst=True)
