"""
AI Reports Module — FastAPI Router
TOP WorX ERP System

Endpoints:
  - POST /ai/reports/nl-to-sql — Convert natural language to SQL
  - POST /ai/reports/query — Execute natural language query
  - POST /ai/reports/generate — Generate report by type
  - POST /ai/reports/ai-generate — Generate report from natural language
  - GET /ai/reports/types — List available report types
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import DBDep, CurrentUser
from app.core.ai.reports import get_ai_reports_engine

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class NLToSQLRequest(BaseModel):
    query: str = Field(..., description="Natural language query", min_length=3, max_length=500)


class NLToSQLResponse(BaseModel):
    sql: Optional[str]
    explanation: str
    parameters: list
    confidence: float
    error: Optional[str] = None


class ExecuteNLQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query", min_length=3, max_length=500)


class ExecuteNLQueryResponse(BaseModel):
    query: str
    sql: Optional[str]
    columns: list
    data: list
    row_count: int
    explanation: str
    truncated: bool = False
    error: Optional[str] = None


class GenerateReportRequest(BaseModel):
    report_type: str = Field(..., description="Report type")
    parameters: Optional[dict] = None
    format: str = Field(default="summary", description="Output format: summary, detailed, executive")


class AIGenerateReportRequest(BaseModel):
    description: str = Field(..., description="Natural language description of the report", min_length=10, max_length=1000)


class ReportResponse(BaseModel):
    report_type: str
    generated_at: str
    sections: list
    insights: list
    error: Optional[str] = None


class AIReportResponse(BaseModel):
    report_title: str
    generated_at: str
    sections: list
    ai_model: Optional[str] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None


# ── NL-to-SQL Endpoint ──────────────────────────────────────────────────────

@router.post("/reports/nl-to-sql", response_model=NLToSQLResponse)
async def nl_to_sql(
    data: NLToSQLRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> NLToSQLResponse:
    """Convert natural language query to SQL."""
    engine = get_ai_reports_engine(db)
    result = await engine.nl_to_sql(data.query)
    return NLToSQLResponse(**result)


# ── Execute NL Query Endpoint ────────────────────────────────────────────────

@router.post("/reports/query", response_model=ExecuteNLQueryResponse)
async def execute_nl_query(
    data: ExecuteNLQueryRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> ExecuteNLQueryResponse:
    """Execute a natural language query and return results."""
    engine = get_ai_reports_engine(db)
    result = await engine.execute_nl_query(data.query)
    return ExecuteNLQueryResponse(**result)


# ── Generate Report Endpoint ─────────────────────────────────────────────────

@router.post("/reports/generate", response_model=ReportResponse)
async def generate_report(
    data: GenerateReportRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> ReportResponse:
    """Generate a report by type."""
    engine = get_ai_reports_engine(db)
    result = await engine.generate_report(
        report_type=data.report_type,
        parameters=data.parameters,
        format=data.format,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return ReportResponse(**result)


# ── AI Generate Report Endpoint ──────────────────────────────────────────────

@router.post("/reports/ai-generate", response_model=AIReportResponse)
async def ai_generate_report(
    data: AIGenerateReportRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> AIReportResponse:
    """Generate a report based on natural language description."""
    engine = get_ai_reports_engine(db)
    result = await engine.ai_generate_report(data.description)
    if "error" in result and not result.get("sections"):
        raise HTTPException(status_code=400, detail=result["error"])
    return AIReportResponse(**result)


# ── List Report Types ────────────────────────────────────────────────────────

@router.get("/reports/types")
async def list_report_types(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """List available report types."""
    return {
        "report_types": [
            {
                "id": "sales_summary",
                "name": "Sales Summary",
                "description": "Summary of sales performance with revenue, orders, and trends",
                "parameters": {"days": "number of days (default: 30)"},
            },
            {
                "id": "inventory_status",
                "name": "Inventory Status",
                "description": "Current inventory levels, low stock alerts, and movement analysis",
                "parameters": {},
            },
            {
                "id": "financial_overview",
                "name": "Financial Overview",
                "description": "Account balances, transaction summaries, and financial health",
                "parameters": {},
            },
            {
                "id": "hr_summary",
                "name": "HR Summary",
                "description": "Employee counts, attendance, leave, and payroll summaries",
                "parameters": {},
            },
            {
                "id": "procurement_summary",
                "name": "Procurement Summary",
                "description": "Vendor activity, purchase orders, and spending analysis",
                "parameters": {},
            },
            {
                "id": "executive_summary",
                "name": "Executive Summary",
                "description": "Comprehensive overview combining all modules",
                "parameters": {},
            },
        ],
        "examples": [
            "Show me sales for the last 30 days",
            "What items are low on stock?",
            "Generate an executive summary",
            "Show me top 10 customers by revenue",
            "What is our total payroll this month?",
            "Compare Q1 vs Q2 revenue",
        ],
    }
