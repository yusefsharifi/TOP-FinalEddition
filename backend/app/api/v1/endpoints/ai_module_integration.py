"""
AI Module Integration — FastAPI Router
TOP WorX ERP System

Provides AI capabilities for each ERP module:
- Inventory: Stockout prediction, smart reordering, anomaly detection
- Finance: Cash flow prediction, expense anomaly detection
- HR: Attrition prediction
- Sales: Revenue forecast, churn prediction
- CRM: Lead scoring
- Procurement: Supplier risk analysis
- Quality: Defect prediction
- HSE: Incident prediction, safety score
- Projects: Risk assessment
- Support: Ticket sentiment analysis
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.api.deps import DBDep, CurrentUser
from app.core.ai.module_integration import get_ai_module_integration

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class AIInsightResponse(BaseModel):
    type: str
    data: dict


# ══════════════════════════════════════════════════════════════════════════════
# INVENTORY AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/inventory/stockout-prediction")
async def inventory_stockout_prediction(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Predict potential stockouts based on historical movement patterns."""
    ai = get_ai_module_integration(db)
    return await ai.inventory_stockout_prediction(current_user.id)


@router.get("/inventory/smart-reorder")
async def inventory_smart_reorder(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Get smart reorder suggestions."""
    ai = get_ai_module_integration(db)
    return await ai.inventory_smart_reorder_suggestions(current_user.id)


@router.get("/inventory/anomaly-detection")
async def inventory_anomaly_detection(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Detect unusual inventory movements."""
    ai = get_ai_module_integration(db)
    return await ai.inventory_anomaly_detection(current_user.id)


# ══════════════════════════════════════════════════════════════════════════════
# FINANCE AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/finance/cashflow-prediction")
async def finance_cashflow_prediction(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Predict future cash flow."""
    ai = get_ai_module_integration(db)
    return await ai.finance_cashflow_prediction(current_user.id)


@router.get("/finance/expense-anomaly")
async def finance_expense_anomaly(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Detect unusual expenses."""
    ai = get_ai_module_integration(db)
    return await ai.finance_expense_anomaly_detection(current_user.id)


# ══════════════════════════════════════════════════════════════════════════════
# HR AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/hr/attrition-prediction")
async def hr_attrition_prediction(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Predict which employees might leave."""
    ai = get_ai_module_integration(db)
    return await ai.hr_attrition_prediction(current_user.id)


# ══════════════════════════════════════════════════════════════════════════════
# SALES AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/sales/revenue-forecast")
async def sales_revenue_forecast(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Forecast revenue for next quarter."""
    ai = get_ai_module_integration(db)
    return await ai.sales_revenue_forecast(current_user.id)


@router.get("/sales/churn-prediction")
async def sales_churn_prediction(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Predict customers at risk of churning."""
    ai = get_ai_module_integration(db)
    return await ai.sales_churn_prediction(current_user.id)


# ══════════════════════════════════════════════════════════════════════════════
# CRM AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/crm/lead-scoring/{lead_id}")
async def crm_lead_scoring(
    lead_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Score a lead based on multiple factors."""
    ai = get_ai_module_integration(db)
    return await ai.crm_lead_scoring(lead_id)


# ══════════════════════════════════════════════════════════════════════════════
# PROCUREMENT AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/procurement/supplier-risk")
async def procurement_supplier_risk(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Analyze supplier risk based on delivery performance."""
    ai = get_ai_module_integration(db)
    return await ai.procurement_supplier_risk_analysis(current_user.id)


# ══════════════════════════════════════════════════════════════════════════════
# QUALITY AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/quality/defect-prediction")
async def quality_defect_prediction(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Predict potential defects based on historical patterns."""
    ai = get_ai_module_integration(db)
    return await ai.quality_defect_prediction(current_user.id)


# ══════════════════════════════════════════════════════════════════════════════
# HSE AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/hse/incident-prediction")
async def hse_incident_prediction(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Predict potential safety incidents."""
    ai = get_ai_module_integration(db)
    return await ai.hse_incident_prediction(current_user.id)


@router.get("/hse/safety-score")
async def hse_safety_score(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Calculate overall safety score."""
    ai = get_ai_module_integration(db)
    return await ai.hse_safety_score(current_user.id)


# ══════════════════════════════════════════════════════════════════════════════
# PROJECTS AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/projects/{project_id}/risk-assessment")
async def projects_risk_assessment(
    project_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Assess project risks."""
    ai = get_ai_module_integration(db)
    return await ai.projects_risk_assessment(project_id)


# ══════════════════════════════════════════════════════════════════════════════
# SUPPORT AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/support/ticket-sentiment/{ticket_id}")
async def support_ticket_sentiment(
    ticket_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Analyze ticket sentiment."""
    ai = get_ai_module_integration(db)
    return await ai.support_ticket_sentiment(ticket_id)


# ══════════════════════════════════════════════════════════════════════════════
# AI DASHBOARD (ALL MODULES)
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/dashboard/all-insights")
async def ai_all_insights(
    db: DBDep,
    current_user: CurrentUser,
    modules: Optional[str] = Query(None, description="Comma-separated module names"),
) -> dict:
    """Get AI insights from all or specific modules."""
    ai = get_ai_module_integration(db)
    
    module_list = modules.split(",") if modules else [
        "inventory", "finance", "hr", "sales", "crm",
        "procurement", "quality", "hse", "projects", "support"
    ]
    
    insights = {}
    
    try:
        if "inventory" in module_list:
            insights["inventory"] = {
                "stockout_prediction": await ai.inventory_stockout_prediction(current_user.id),
                "smart_reorder": await ai.inventory_smart_reorder_suggestions(current_user.id),
            }
    except Exception as e:
        insights["inventory"] = {"error": str(e)}
    
    try:
        if "finance" in module_list:
            insights["finance"] = {
                "cashflow_prediction": await ai.finance_cashflow_prediction(current_user.id),
                "expense_anomaly": await ai.finance_expense_anomaly_detection(current_user.id),
            }
    except Exception as e:
        insights["finance"] = {"error": str(e)}
    
    try:
        if "hr" in module_list:
            insights["hr"] = {
                "attrition_prediction": await ai.hr_attrition_prediction(current_user.id),
            }
    except Exception as e:
        insights["hr"] = {"error": str(e)}
    
    try:
        if "sales" in module_list:
            insights["sales"] = {
                "revenue_forecast": await ai.sales_revenue_forecast(current_user.id),
                "churn_prediction": await ai.sales_churn_prediction(current_user.id),
            }
    except Exception as e:
        insights["sales"] = {"error": str(e)}
    
    try:
        if "procurement" in module_list:
            insights["procurement"] = {
                "supplier_risk": await ai.procurement_supplier_risk_analysis(current_user.id),
            }
    except Exception as e:
        insights["procurement"] = {"error": str(e)}
    
    try:
        if "quality" in module_list:
            insights["quality"] = {
                "defect_prediction": await ai.quality_defect_prediction(current_user.id),
            }
    except Exception as e:
        insights["quality"] = {"error": str(e)}
    
    try:
        if "hse" in module_list:
            insights["hse"] = {
                "safety_score": await ai.hse_safety_score(current_user.id),
                "incident_prediction": await ai.hse_incident_prediction(current_user.id),
            }
    except Exception as e:
        insights["hse"] = {"error": str(e)}
    
    return {
        "modules_requested": module_list,
        "modules_with_data": list(insights.keys()),
        "insights": insights,
    }
