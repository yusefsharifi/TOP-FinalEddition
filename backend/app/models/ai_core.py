"""
AI Core Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Tables:
  - ai_conversations: Store AI chat threads
  - ai_messages: Store individual AI messages
  - ai_prompts: Store prompt templates
  - ai_usage_logs: Track API usage and costs
  - ai_embeddings: Store vector embeddings for RAG
  - ai_workflows: Store automation workflows
  - ai_insights: Store AI-generated insights
"""
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AIModelType(str, enum.Enum):
    CHAT = "chat"
    EMBEDDING = "embedding"
    COMPLETION = "completion"
    IMAGE = "image"


class WorkflowTriggerType(str, enum.Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    THRESHOLD = "threshold"


class WorkflowActionType(str, enum.Enum):
    CREATE_RECORD = "create_record"
    UPDATE_RECORD = "update_record"
    SEND_NOTIFICATION = "send_notification"
    SEND_EMAIL = "send_email"
    RUN_QUERY = "run_query"
    CALL_WEBHOOK = "call_webhook"
    AI_ANALYSIS = "ai_analysis"


class InsightType(str, enum.Enum):
    TREND = "trend"
    ANOMALY = "anomaly"
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"
    SUMMARY = "summary"


class InsightSeverity(str, enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# AI Conversation
# ---------------------------------------------------------------------------
class AIConversation(Base):
    """Store AI chat threads."""
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    module: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    model: Mapped[str] = mapped_column(String(50), nullable=False, default="gpt-4")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 6), default=Decimal("0"), nullable=False
    )
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    messages: Mapped[list["AIMessage"]] = relationship(
        "AIMessage", back_populates="conversation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_ai_conversations_user_module", "user_id", "module"),
        Index("ix_ai_conversations_created_at", "created_at"),
    )


# ---------------------------------------------------------------------------
# AI Message
# ---------------------------------------------------------------------------
class AIMessage(Base):
    """Store individual AI messages."""
    __tablename__ = "ai_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 6), default=Decimal("0"), nullable=False
    )
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    conversation: Mapped["AIConversation"] = relationship(
        "AIConversation", back_populates="messages"
    )

    __table_args__ = (
        Index("ix_ai_messages_conversation_created", "conversation_id", "created_at"),
    )


# ---------------------------------------------------------------------------
# AI Prompt Template
# ---------------------------------------------------------------------------
class AIPrompt(Base):
    """Store prompt templates."""
    __tablename__ = "ai_prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False, default="gpt-4")
    temperature: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=Decimal("0.7"), nullable=False
    )
    max_tokens: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    module: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_tokens: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


# ---------------------------------------------------------------------------
# AI Usage Log
# ---------------------------------------------------------------------------
class AIUsageLog(Base):
    """Track API usage and costs."""
    __tablename__ = "ai_usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    conversation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ai_conversations.id", ondelete="SET NULL"), nullable=True
    )
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 6), default=Decimal("0"), nullable=False
    )
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_ai_usage_user_date", "user_id", "created_at"),
        Index("ix_ai_usage_model_date", "model", "created_at"),
    )


# ---------------------------------------------------------------------------
# AI Embedding (for RAG)
# ---------------------------------------------------------------------------
class AIEmbedding(Base):
    """Store vector embeddings for RAG."""
    __tablename__ = "ai_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list] = mapped_column(JSON, nullable=False)  # Vector as JSON array
    source_module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_table: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_ai_embeddings_source", "source_module", "source_table", "source_id"),
    )


# ---------------------------------------------------------------------------
# AI Workflow
# ---------------------------------------------------------------------------
class AIWorkflow(Base):
    """Store automation workflows."""
    __tablename__ = "ai_workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger_module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    trigger_event: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_type: Mapped[WorkflowTriggerType] = mapped_column(
        Enum(WorkflowTriggerType), nullable=False, default=WorkflowTriggerType.EVENT
    )
    condition: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    action_type: Mapped[WorkflowActionType] = mapped_column(
        Enum(WorkflowActionType), nullable=False
    )
    action_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    ai_prompt_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ai_prompts.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trigger_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_ai_workflows_trigger", "trigger_module", "trigger_event"),
    )


# ---------------------------------------------------------------------------
# AI Insight
# ---------------------------------------------------------------------------
class AIInsight(Base):
    """Store AI-generated insights."""
    __tablename__ = "ai_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    insight_type: Mapped[InsightType] = mapped_column(Enum(InsightType), nullable=False, index=True)
    severity: Mapped[InsightSeverity] = mapped_column(
        Enum(InsightSeverity), nullable=False, default=InsightSeverity.INFO
    )
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    action_taken: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_ai_insights_module_type", "module", "insight_type"),
        Index("ix_ai_insights_user_unread", "user_id", "is_read"),
    )
