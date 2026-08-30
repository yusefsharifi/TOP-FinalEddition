"""
AI Automation Module — FastAPI Router
TOP WorX ERP System

Endpoints:
  - POST /ai/automation/workflows — Create workflow
  - GET /ai/automation/workflows — List workflows
  - GET /ai/automation/workflows/{id} — Get workflow details
  - POST /ai/automation/workflows/{id}/trigger — Trigger workflow
  - POST /ai/automation/event — Trigger event-based workflows
  - GET /ai/automation/stats — Workflow statistics
  - POST /ai/automation/templates/low-stock — Create low stock workflow
  - POST /ai/automation/templates/order-notification — Create order notification workflow
  - POST /ai/automation/templates/ai-analysis — Create AI analysis workflow
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import DBDep, CurrentUser
from app.core.ai.automation import get_ai_automation_engine

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class WorkflowCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    trigger_module: str = Field(..., description="Module that triggers the workflow")
    trigger_event: str = Field(..., description="Event that triggers the workflow")
    action_type: str = Field(..., description="Type of action to execute")
    action_config: dict = Field(..., description="Action configuration")
    condition: Optional[dict] = Field(None, description="Condition to evaluate before execution")


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
    last_triggered_at: Optional[str]
    created_at: str


class WorkflowDetailResponse(WorkflowResponse):
    trigger_type: Optional[str] = None
    condition: Optional[dict] = None
    action_config: dict
    updated_at: str


class TriggerWorkflowRequest(BaseModel):
    context: Optional[dict] = None


class TriggerEventRequest(BaseModel):
    module: str
    event: str
    data: Optional[dict] = None


class TriggerResponse(BaseModel):
    workflow_id: Optional[int] = None
    workflow_name: Optional[str] = None
    execution: dict
    executed_at: str


class WorkflowStatsResponse(BaseModel):
    total_workflows: int
    active_workflows: int
    total_triggers: int
    successful_triggers: int
    failed_triggers: int
    success_rate: float
    workflows_by_module: dict


class LowStockWorkflowRequest(BaseModel):
    threshold: int = Field(default=10, ge=1, le=1000)
    notification_user_id: Optional[int] = None


class OrderNotificationRequest(BaseModel):
    notification_user_id: Optional[int] = None


class AIAnalysisWorkflowRequest(BaseModel):
    module: str
    prompt: str


# ── Create Workflow ──────────────────────────────────────────────────────────

@router.post("/automation/workflows", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    data: WorkflowCreateRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> WorkflowResponse:
    """Create a new automation workflow."""
    engine = get_ai_automation_engine(db)
    result = await engine.create_workflow(
        name=data.name,
        description=data.description,
        trigger_module=data.trigger_module,
        trigger_event=data.trigger_event,
        action_type=data.action_type,
        action_config=data.action_config,
        condition=data.condition,
        created_by_id=current_user.id,
    )
    return WorkflowResponse(**result)


# ── List Workflows ───────────────────────────────────────────────────────────

@router.get("/automation/workflows", response_model=list[WorkflowResponse])
async def list_workflows(
    db: DBDep,
    current_user: CurrentUser,
    module: Optional[str] = None,
) -> list[WorkflowResponse]:
    """List automation workflows."""
    engine = get_ai_automation_engine(db)
    workflows = await engine.list_workflows(trigger_module=module)
    return [WorkflowResponse(**w) for w in workflows]


# ── Get Workflow Details ─────────────────────────────────────────────────────

@router.get("/automation/workflows/{workflow_id}", response_model=WorkflowDetailResponse)
async def get_workflow(
    workflow_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> WorkflowDetailResponse:
    """Get workflow details."""
    engine = get_ai_automation_engine(db)
    workflow = await engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowDetailResponse(**workflow)


# ── Trigger Workflow ─────────────────────────────────────────────────────────

@router.post("/automation/workflows/{workflow_id}/trigger", response_model=TriggerResponse)
async def trigger_workflow(
    workflow_id: int,
    data: TriggerWorkflowRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> TriggerResponse:
    """Trigger a workflow execution."""
    engine = get_ai_automation_engine(db)
    result = await engine.trigger_workflow(
        workflow_id, context=data.context
    )
    if not result.get("success") and not result.get("skipped"):
        raise HTTPException(status_code=400, detail=result.get("error", "Execution failed"))
    return TriggerResponse(**result)


# ── Trigger Event ────────────────────────────────────────────────────────────

@router.post("/automation/event", response_model=list[TriggerResponse])
async def trigger_event(
    data: TriggerEventRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> list[TriggerResponse]:
    """Trigger all workflows matching a module/event."""
    engine = get_ai_automation_engine(db)
    results = await engine.trigger_event(
        module=data.module,
        event=data.event,
        data=data.data,
    )
    return [TriggerResponse(**r) for r in results]


# ── Workflow Statistics ──────────────────────────────────────────────────────

@router.get("/automation/stats", response_model=WorkflowStatsResponse)
async def get_workflow_stats(
    db: DBDep,
    current_user: CurrentUser,
) -> WorkflowStatsResponse:
    """Get workflow execution statistics."""
    engine = get_ai_automation_engine(db)
    stats = await engine.get_workflow_stats()
    return WorkflowStatsResponse(**stats)


# ── Template: Low Stock Workflow ─────────────────────────────────────────────

@router.post("/automation/templates/low-stock", response_model=WorkflowResponse, status_code=201)
async def create_low_stock_workflow(
    data: LowStockWorkflowRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> WorkflowResponse:
    """Create a pre-built low stock alert workflow."""
    engine = get_ai_automation_engine(db)
    result = await engine.create_low_stock_workflow(
        threshold=data.threshold,
        notification_user_id=data.notification_user_id,
    )
    return WorkflowResponse(**result)


# ── Template: Order Notification Workflow ────────────────────────────────────

@router.post("/automation/templates/order-notification", response_model=WorkflowResponse, status_code=201)
async def create_order_notification_workflow(
    data: OrderNotificationRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> WorkflowResponse:
    """Create a pre-built order notification workflow."""
    engine = get_ai_automation_engine(db)
    result = await engine.create_order_notification_workflow(
        notification_user_id=data.notification_user_id,
    )
    return WorkflowResponse(**result)


# ── Template: AI Analysis Workflow ───────────────────────────────────────────

@router.post("/automation/templates/ai-analysis", response_model=WorkflowResponse, status_code=201)
async def create_ai_analysis_workflow(
    data: AIAnalysisWorkflowRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> WorkflowResponse:
    """Create a pre-built AI analysis workflow."""
    engine = get_ai_automation_engine(db)
    result = await engine.create_ai_analysis_workflow(
        module=data.module,
        prompt=data.prompt,
    )
    return WorkflowResponse(**result)
