"""
AI Assistant Module — FastAPI Router
TOP WorX ERP System

Endpoints:
  - POST /ai/assistant/chat — Chat with AI assistant
  - POST /ai/assistant/quick-query — Execute quick predefined query
  - GET /ai/assistant/conversations — List conversations
  - GET /ai/assistant/conversations/{id} — Get conversation history
  - DELETE /ai/assistant/conversations/{id} — Delete conversation
  - GET /ai/assistant/context — Get ERP context
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import DBDep, CurrentUser
from app.core.ai.assistant import get_ai_assistant_engine

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = None
    module: Optional[str] = Field(None, description="Module context: inventory, sales, finance, hr, crm, etc.")


class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    model: str
    tokens_used: int
    cost: float
    context_used: dict
    actions: list


class QuickQueryRequest(BaseModel):
    query_type: str = Field(..., description="Query type: dashboard_summary, low_stock, recent_orders, pending_tasks, my_leave_balance")


class QuickQueryResponse(BaseModel):
    type: str
    summary: dict


class ConversationResponse(BaseModel):
    id: int
    title: str
    module: Optional[str]
    total_tokens: int
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str


class ContextResponse(BaseModel):
    system: str
    version: str
    modules: dict
    available_commands: list


# ── Chat Endpoint ────────────────────────────────────────────────────────────

@router.post("/assistant/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> ChatResponse:
    """Chat with the AI assistant."""
    engine = get_ai_assistant_engine(db)
    result = await engine.chat(
        message=data.message,
        user_id=current_user.id,
        conversation_id=data.conversation_id,
        module=data.module,
    )
    return ChatResponse(**result)


# ── Quick Query Endpoint ─────────────────────────────────────────────────────

@router.post("/assistant/quick-query", response_model=QuickQueryResponse)
async def quick_query(
    data: QuickQueryRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> QuickQueryResponse:
    """Execute a quick predefined query."""
    engine = get_ai_assistant_engine(db)
    result = await engine.quick_query(
        query_type=data.query_type,
        user_id=current_user.id,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return QuickQueryResponse(**result)


# ── List Conversations ───────────────────────────────────────────────────────

@router.get("/assistant/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    db: DBDep,
    current_user: CurrentUser,
    module: Optional[str] = None,
) -> list[ConversationResponse]:
    """List user's conversations."""
    engine = get_ai_assistant_engine(db)
    conversations = await engine.list_conversations(
        user_id=current_user.id, module=module
    )
    return [ConversationResponse(**c) for c in conversations]


# ── Get Conversation History ─────────────────────────────────────────────────

@router.get("/assistant/conversations/{conversation_id}", response_model=list[MessageResponse])
async def get_conversation_history(
    conversation_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> list[MessageResponse]:
    """Get conversation history."""
    engine = get_ai_assistant_engine(db)
    messages = await engine.get_conversation_history(
        conversation_id, current_user.id
    )
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [MessageResponse(**m) for m in messages]


# ── Delete Conversation ──────────────────────────────────────────────────────

@router.delete("/assistant/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Delete a conversation."""
    engine = get_ai_assistant_engine(db)
    success = await engine.delete_conversation(
        conversation_id, current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}


# ── Get ERP Context ──────────────────────────────────────────────────────────

@router.get("/assistant/context", response_model=ContextResponse)
async def get_erp_context(
    db: DBDep,
    current_user: CurrentUser,
) -> ContextResponse:
    """Get ERP context for the assistant."""
    engine = get_ai_assistant_engine(db)
    context = await engine.context_provider.get_full_context(current_user.id)
    return ContextResponse(**context)


# ── Available Quick Queries ──────────────────────────────────────────────────

@router.get("/assistant/quick-queries")
async def list_quick_queries(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """List available quick queries."""
    return {
        "queries": [
            {
                "id": "dashboard_summary",
                "name": "Dashboard Summary",
                "description": "Get an overview of all modules",
            },
            {
                "id": "low_stock",
                "name": "Low Stock Items",
                "description": "Check items below reorder point",
            },
            {
                "id": "recent_orders",
                "name": "Recent Orders",
                "description": "View recent sales orders",
            },
            {
                "id": "pending_tasks",
                "name": "Pending Tasks",
                "description": "View pending tasks",
            },
            {
                "id": "my_leave_balance",
                "name": "My Leave Balance",
                "description": "Check your leave balance",
            },
        ]
    }
