"""
AI Analytics Module — FastAPI Router
TOP WorX ERP System

Endpoints:
  - GET /ai/analytics/cross-module — Full cross-module analysis
  - GET /ai/analytics/inventory — Inventory analytics
  - GET /ai/analytics/sales — Sales analytics
  - GET /ai/analytics/finance — Finance analytics
  - GET /ai/analytics/hr — HR analytics
  - GET /ai/analytics/crm — CRM analytics
  - POST /ai/analytics/ai-analyze — AI-powered analysis
  - POST /ai/analytics/generate-insights — Generate and store insights
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.api.deps import DBDep, CurrentUser
from app.core.ai.analytics import get_ai_analytics_engine

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class CrossModuleResponse(BaseModel):
    timestamp: str
    modules: dict
    cross_module_insights: list
    summary: dict


class ModuleAnalyticsResponse(BaseModel):
    module: str
    summary: dict
    insights: list
    trend: Optional[dict] = None


class AIAnalyzeRequest(BaseModel):
    module: str
    data: dict


class AIAnalyzeResponse(BaseModel):
    module: str
    ai_analysis: Optional[dict]
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    error: Optional[str] = None


class InsightResponse(BaseModel):
    id: int
    module: str
    type: str
    title: str


# ── Cross-Module Analysis ────────────────────────────────────────────────────

@router.get("/analytics/cross-module", response_model=CrossModuleResponse)
async def cross_module_analysis(
    db: DBDep,
    current_user: CurrentUser,
) -> CrossModuleResponse:
    """Full cross-module analysis with correlated insights."""
    engine = get_ai_analytics_engine(db)
    result = await engine.analyze_cross_module()
    return CrossModuleResponse(**result)


# ── Module-Specific Analytics ────────────────────────────────────────────────

@router.get("/analytics/inventory", response_model=ModuleAnalyticsResponse)
async def inventory_analytics(
    db: DBDep,
    current_user: CurrentUser,
) -> ModuleAnalyticsResponse:
    """Inventory analytics with stock predictions and reorder suggestions."""
    engine = get_ai_analytics_engine(db)
    result = await engine.analyze_inventory()
    return ModuleAnalyticsResponse(
        module=result["module"],
        summary=result["summary"],
        insights=result["insights"],
    )


@router.get("/analytics/sales", response_model=ModuleAnalyticsResponse)
async def sales_analytics(
    db: DBDep,
    current_user: CurrentUser,
    days: int = Query(30, ge=7, le=365),
) -> ModuleAnalyticsResponse:
    """Sales analytics with revenue forecasting and trend detection."""
    engine = get_ai_analytics_engine(db)
    result = await engine.analyze_sales(days=days)
    return ModuleAnalyticsResponse(
        module=result["module"],
        summary=result["summary"],
        insights=result["insights"],
        trend={"daily": result.get("daily_trend", [])},
    )


@router.get("/analytics/finance", response_model=ModuleAnalyticsResponse)
async def finance_analytics(
    db: DBDep,
    current_user: CurrentUser,
) -> ModuleAnalyticsResponse:
    """Finance analytics with cash flow and anomaly detection."""
    engine = get_ai_analytics_engine(db)
    result = await engine.analyze_finance()
    return ModuleAnalyticsResponse(
        module=result["module"],
        summary=result["summary"],
        insights=result["insights"],
    )


@router.get("/analytics/hr", response_model=ModuleAnalyticsResponse)
async def hr_analytics(
    db: DBDep,
    current_user: CurrentUser,
) -> ModuleAnalyticsResponse:
    """HR analytics with attrition prediction and performance insights."""
    engine = get_ai_analytics_engine(db)
    result = await engine.analyze_hr()
    return ModuleAnalyticsResponse(
        module=result["module"],
        summary=result["summary"],
        insights=result["insights"],
    )


@router.get("/analytics/crm", response_model=ModuleAnalyticsResponse)
async def crm_analytics(
    db: DBDep,
    current_user: CurrentUser,
) -> ModuleAnalyticsResponse:
    """CRM analytics with lead scoring and customer segmentation."""
    engine = get_ai_analytics_engine(db)
    result = await engine.analyze_crm()
    return ModuleAnalyticsResponse(
        module=result["module"],
        summary=result["summary"],
        insights=result["insights"],
    )


# ── AI-Powered Analysis ─────────────────────────────────────────────────────

@router.post("/analytics/ai-analyze", response_model=AIAnalyzeResponse)
async def ai_analyze(
    data: AIAnalyzeRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> AIAnalyzeResponse:
    """Use AI to analyze module data and generate natural language insights."""
    engine = get_ai_analytics_engine(db)
    result = await engine.ai_analyze_data(module=data.module, data=data.data)
    return AIAnalyzeResponse(**result)


# ── Generate and Store Insights ──────────────────────────────────────────────

@router.post("/analytics/generate-insights", response_model=list[InsightResponse])
async def generate_insights(
    db: DBDep,
    current_user: CurrentUser,
) -> list[InsightResponse]:
    """Generate insights across all modules and store them."""
    engine = get_ai_analytics_engine(db)
    insights = await engine.generate_insights(user_id=current_user.id)
    return [InsightResponse(**i) for i in insights]
