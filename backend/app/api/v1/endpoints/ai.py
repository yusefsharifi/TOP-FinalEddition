"""
AI Module — FastAPI Router (Full Implementation)
TOP WorX ERP System

Endpoints:
  - POST /ai/chat — Chat with AI assistant
  - POST /ai/conversations — Create conversation
  - GET /ai/conversations — List conversations
  - GET /ai/conversations/{id} — Get conversation with messages
  - DELETE /ai/conversations/{id} — Delete conversation
  - POST /ai/prompts — Create prompt template
  - GET /ai/prompts — List prompt templates
  - GET /ai/insights — Get AI insights
  - POST /ai/insights/{id}/read — Mark insight as read
  - GET /ai/usage — Usage statistics
  - POST /ai/workflows — Create automation workflow
  - GET /ai/workflows — List workflows
  - GET /ai/dashboard — AI dashboard overview
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.deps import DBDep, CurrentUser
from app.core.ai.engine import AIEngine, get_ai_engine
from app.core.config import settings
from app.crud.ai import (
    ai_conversation_crud,
    ai_message_crud,
    ai_prompt_crud,
    ai_workflow_crud,
    ai_insight_crud,
    ai_usage_crud,
)
from app.models.ai_core import MessageRole, InsightType, InsightSeverity

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    module: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None


class ChatResponse(BaseModel):
    reply: str
    model: str
    tokens_used: int
    cost: float
    duration_ms: int
    conversation_id: int


class ConversationCreate(BaseModel):
    title: str
    module: Optional[str] = None
    model: Optional[str] = None


class ConversationResponse(BaseModel):
    id: int
    title: str
    module: Optional[str]
    model: str
    total_tokens: int
    total_cost: float
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    model: Optional[str]
    tokens_used: int
    cost: float
    duration_ms: Optional[int]
    created_at: datetime


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse]


class PromptCreate(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    user_prompt_template: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000
    module: Optional[str] = None


class PromptResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    system_prompt: str
    user_prompt_template: str
    model: str
    temperature: float
    max_tokens: int
    module: Optional[str]
    is_active: bool
    usage_count: int
    created_at: datetime


class InsightResponse(BaseModel):
    id: int
    insight_type: str
    severity: str
    module: str
    title: str
    description: str
    data: Optional[dict]
    confidence: Optional[float]
    is_read: bool
    created_at: datetime


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_module: str
    trigger_event: str
    action_type: str
    action_config: dict
    condition: Optional[dict] = None


class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    trigger_module: str
    trigger_event: str
    action_type: str
    is_active: bool
    trigger_count: int
    success_count: int
    failure_count: int
    created_at: datetime


class UsageStatsResponse(BaseModel):
    period_days: int
    total_requests: int
    total_tokens: int
    total_cost: float
    avg_duration_ms: float


# ── Chat Endpoint ────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    data: ChatRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> ChatResponse:
    """Chat with AI assistant."""
    engine = get_ai_engine(db)

    # Get or create conversation
    conversation_id = data.conversation_id
    if not conversation_id:
        conv = await ai_conversation_crud.create(
            db,
            user_id=current_user.id,
            title=data.message[:100],
            module=data.module,
            model=data.model,
        )
        conversation_id = conv.id
    else:
        conv = await ai_conversation_crud.get(db, conversation_id)
        if not conv or conv.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    await ai_message_crud.create(
        db,
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=data.message,
    )

    # Build messages for LLM
    history = await ai_message_crud.list_by_conversation(db, conversation_id, limit=20)
    messages = [{"role": m.role.value, "content": m.content} for m in history]

    # Call AI
    try:
        response = await engine.chat(
            messages=messages,
            model=data.model,
            temperature=data.temperature,
            system_prompt=data.system_prompt,
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

    # Save assistant message
    await ai_message_crud.create(
        db,
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content=response["content"],
        model=response["model"],
        tokens_used=response["input_tokens"] + response["output_tokens"],
        cost=Decimal(str(response["cost"])),
        duration_ms=response["duration_ms"],
    )

    return ChatResponse(
        reply=response["content"],
        model=response["model"],
        tokens_used=response["input_tokens"] + response["output_tokens"],
        cost=response["cost"],
        duration_ms=response["duration_ms"],
        conversation_id=conversation_id,
    )


# ── Conversation Endpoints ──────────────────────────────────────────────────

@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> ConversationResponse:
    """Create a new AI conversation."""
    conv = await ai_conversation_crud.create(
        db,
        user_id=current_user.id,
        title=data.title,
        module=data.module,
        model=data.model,
    )
    return ConversationResponse.model_validate(conv)


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    db: DBDep,
    current_user: CurrentUser,
    module: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[ConversationResponse]:
    """List user's conversations."""
    convs = await ai_conversation_crud.list_by_user(
        db, current_user.id, module=module, offset=offset, limit=limit
    )
    return [ConversationResponse.model_validate(c) for c in convs]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> ConversationDetailResponse:
    """Get conversation with messages."""
    conv = await ai_conversation_crud.get(db, conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await ai_message_crud.list_by_conversation(db, conversation_id)

    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        module=conv.module,
        model=conv.model,
        total_tokens=conv.total_tokens,
        total_cost=float(conv.total_cost),
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageResponse.model_validate(m) for m in messages],
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Soft-delete a conversation."""
    conv = await ai_conversation_crud.get(db, conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await ai_conversation_crud.soft_delete(db, conversation_id)
    return {"status": "deleted"}


# ── Prompt Endpoints ─────────────────────────────────────────────────────────

@router.post("/prompts", response_model=PromptResponse, status_code=201)
async def create_prompt(
    data: PromptCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> PromptResponse:
    """Create a prompt template."""
    existing = await ai_prompt_crud.get_by_name(db, data.name)
    if existing:
        raise HTTPException(status_code=409, detail="Prompt name already exists")

    prompt = await ai_prompt_crud.create(
        db,
        name=data.name,
        description=data.description,
        system_prompt=data.system_prompt,
        user_prompt_template=data.user_prompt_template,
        model=data.model,
        temperature=Decimal(str(data.temperature)),
        max_tokens=data.max_tokens,
        module=data.module,
        created_by_id=current_user.id,
    )
    return PromptResponse.model_validate(prompt)


@router.get("/prompts", response_model=list[PromptResponse])
async def list_prompts(
    db: DBDep,
    current_user: CurrentUser,
    module: Optional[str] = None,
) -> list[PromptResponse]:
    """List active prompt templates."""
    prompts = await ai_prompt_crud.list_active(db, module=module)
    return [PromptResponse.model_validate(p) for p in prompts]


# ── Insight Endpoints ────────────────────────────────────────────────────────

@router.get("/insights", response_model=list[InsightResponse])
async def list_insights(
    db: DBDep,
    current_user: CurrentUser,
    module: Optional[str] = None,
    unread_only: bool = False,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[InsightResponse]:
    """Get AI insights for current user."""
    insights = await ai_insight_crud.list_for_user(
        db, current_user.id, module=module, unread_only=unread_only,
        offset=offset, limit=limit,
    )
    return [InsightResponse.model_validate(i) for i in insights]


@router.get("/insights/unread-count")
async def get_unread_insights_count(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Get count of unread insights."""
    count = await ai_insight_crud.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.post("/insights/{insight_id}/read")
async def mark_insight_read(
    insight_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Mark an insight as read."""
    insight = await ai_insight_crud.mark_read(db, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {"status": "read"}


@router.post("/insights/{insight_id}/dismiss")
async def dismiss_insight(
    insight_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Dismiss an insight."""
    insight = await ai_insight_crud.dismiss(db, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {"status": "dismissed"}


# ── Usage Endpoints ──────────────────────────────────────────────────────────

@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    db: DBDep,
    current_user: CurrentUser,
    days: int = Query(30, ge=1, le=365),
) -> UsageStatsResponse:
    """Get AI usage statistics."""
    stats = await ai_usage_crud.get_stats(db, user_id=current_user.id, days=days)
    return UsageStatsResponse(**stats)


# ── Workflow Endpoints ───────────────────────────────────────────────────────

@router.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    data: WorkflowCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> WorkflowResponse:
    """Create an automation workflow."""
    workflow = await ai_workflow_crud.create(
        db,
        name=data.name,
        description=data.description,
        trigger_module=data.trigger_module,
        trigger_event=data.trigger_event,
        action_type=data.action_type,
        action_config=data.action_config,
        condition=data.condition,
        created_by_id=current_user.id,
    )
    return WorkflowResponse.model_validate(workflow)


@router.get("/workflows", response_model=list[WorkflowResponse])
async def list_workflows(
    db: DBDep,
    current_user: CurrentUser,
    module: Optional[str] = None,
) -> list[WorkflowResponse]:
    """List active workflows."""
    workflows = await ai_workflow_crud.list_active(db, trigger_module=module)
    return [WorkflowResponse.model_validate(w) for w in workflows]


# ── Dashboard ────────────────────────────────────────────────────────────────

@router.get("/dashboard")
async def ai_dashboard(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """AI module dashboard overview."""
    engine = get_ai_engine(db)

    # Usage stats
    usage = await ai_usage_crud.get_stats(db, user_id=current_user.id, days=30)

    # Unread insights
    unread_insights = await ai_insight_crud.get_unread_count(db, current_user.id)

    # Active workflows
    workflows = await ai_workflow_crud.list_active(db)

    # Recent conversations
    convs = await ai_conversation_crud.list_by_user(db, current_user.id, limit=5)

    return {
        "usage": usage,
        "unread_insights": unread_insights,
        "active_workflows": len(workflows),
        "recent_conversations": [
            {
                "id": c.id,
                "title": c.title,
                "module": c.module,
                "updated_at": c.updated_at.isoformat(),
            }
            for c in convs
        ],
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "anthropic_configured": bool(settings.ANTHROPIC_API_KEY),
        "default_model": settings.AI_MODEL,
    }
