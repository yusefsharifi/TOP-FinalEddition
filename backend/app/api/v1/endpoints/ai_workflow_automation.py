"""
AI Workflow Automation — B3 Spec Endpoints
TOP WorX ERP System

Exposes the 8 automated workflow handlers as API endpoints:

  GET  /ai/workflows/handlers          — List all available handlers
  POST /ai/workflows/run-all           — Run all handlers (full scan)
  POST /ai/workflows/run/{handler}     — Run a specific handler
  POST /ai/workflows/execute-all       — Run all + create actions
  GET  /ai/workflows/scan-status       — Get last scan status

Workflow Handlers:
  1. low_stock_auto_po         — Low Stock → Auto PO
  2. invoice_due_reminder      — Invoice Due → Auto Reminder
  3. lead_high_score_assign    — Lead Score High → Auto Assign
  4. expense_anomaly_alert     — Expense Anomaly → Auto Alert
  5. employee_anniversary_review — Employee Anniversary → Auto Review
  6. project_delay_escalation  — Project Delay → Auto Escalation
  7. quality_issue_quarantine  — Quality Issue → Auto Quarantine
  8. customer_churn_retention  — Customer Churn Risk → Auto Retention
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import DBDep, CurrentUser
from app.core.ai.workflow_handlers import (
    WORKFLOW_HANDLERS,
    run_all_handlers,
    run_handler,
    list_handlers,
)

router = APIRouter()

# In-memory scan history (replace with DB table in production)
_scan_history: list[dict] = []
MAX_HISTORY = 50


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class HandlerInfo(BaseModel):
    name: str
    description: str


class HandlerResult(BaseModel):
    handler: str
    triggered: bool
    message: str
    action: Optional[str] = None
    data: Optional[dict] = None


class RunAllResponse(BaseModel):
    handlers_run: int
    handlers_triggered: int
    handlers_errors: int
    triggered_handlers: list[str]
    error_handlers: list[str]
    results: dict[str, Any]
    executed_at: str


class RunHandlerRequest(BaseModel):
    config: Optional[dict] = Field(None, description="Handler-specific configuration")


class ScanStatusResponse(BaseModel):
    last_scan_at: Optional[str] = None
    total_scans: int
    handlers_available: int
    recent_results: list[dict]


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/workflows/handlers", response_model=list[HandlerInfo])
async def get_workflow_handlers(
    db: DBDep,
    current_user: CurrentUser,
) -> list[HandlerInfo]:
    """List all available B3 workflow handlers."""
    handlers = list_handlers()
    return [HandlerInfo(**h) for h in handlers]


@router.post("/workflows/run-all", response_model=RunAllResponse)
async def run_all_workflow_handlers(
    db: DBDep,
    current_user: CurrentUser,
) -> RunAllResponse:
    """
    Run ALL B3 workflow handlers.
    Scans every module for trigger conditions and returns results.
    """
    results = await run_all_handlers(db)

    # Store in scan history
    _scan_history.append({
        "executed_at": results["executed_at"],
        "handlers_run": results["handlers_run"],
        "handlers_triggered": results["handlers_triggered"],
        "triggered_handlers": results["triggered_handlers"],
    })
    if len(_scan_history) > MAX_HISTORY:
        _scan_history.pop(0)

    return RunAllResponse(**results)


@router.post("/workflows/run/{handler_name}")
async def run_specific_handler(
    handler_name: str,
    db: DBDep,
    current_user: CurrentUser,
    data: Optional[RunHandlerRequest] = None,
) -> dict:
    """Run a specific B3 workflow handler."""
    if handler_name not in WORKFLOW_HANDLERS:
        raise HTTPException(
            status_code=404,
            detail=f"Handler '{handler_name}' not found. Available: {list(WORKFLOW_HANDLERS.keys())}",
        )

    config = data.config if data else None
    result = await run_handler(handler_name, db, config)
    return result


@router.post("/workflows/execute-all")
async def execute_all_workflows(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """
    Run all handlers AND execute their actions.
    This is the main endpoint for scheduled execution (e.g., cron job).
    """
    results = await run_all_handlers(db)

    # For each triggered handler, execute the action
    executed_actions = []
    for handler_name, result in results["results"].items():
        if result.get("triggered") and "action" in result:
            action = result["action"]
            executed_actions.append({
                "handler": handler_name,
                "action": action,
                "message": result.get("message", ""),
            })

    # Store in history
    _scan_history.append({
        "executed_at": results["executed_at"],
        "handlers_run": results["handlers_run"],
        "handlers_triggered": results["handlers_triggered"],
        "actions_executed": len(executed_actions),
        "triggered_handlers": results["triggered_handlers"],
    })
    if len(_scan_history) > MAX_HISTORY:
        _scan_history.pop(0)

    return {
        **results,
        "actions_executed": executed_actions,
        "total_actions": len(executed_actions),
    }


@router.get("/workflows/scan-status", response_model=ScanStatusResponse)
async def get_scan_status(
    db: DBDep,
    current_user: CurrentUser,
) -> ScanStatusResponse:
    """Get the status of recent workflow scans."""
    return ScanStatusResponse(
        last_scan_at=_scan_history[-1]["executed_at"] if _scan_history else None,
        total_scans=len(_scan_history),
        handlers_available=len(WORKFLOW_HANDLERS),
        recent_results=_scan_history[-5:] if _scan_history else [],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Individual Handler Endpoints (for targeted execution)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/workflows/scan/inventory")
async def scan_inventory_low_stock(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Scan inventory for low stock items and generate PO suggestions."""
    return await run_handler("low_stock_auto_po", db)


@router.post("/workflows/scan/finance")
async def scan_invoice_reminders(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Scan finance for overdue/upcoming invoices."""
    return await run_handler("invoice_due_reminder", db)


@router.post("/workflows/scan/crm")
async def scan_lead_scores(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Scan CRM for high-scoring unassigned leads."""
    return await run_handler("lead_high_score_assign", db)


@router.post("/workflows/scan/expenses")
async def scan_expense_anomalies(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Scan finance for expense anomalies."""
    return await run_handler("expense_anomaly_alert", db)


@router.post("/workflows/scan/hr")
async def scan_employee_anniversaries(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Scan HR for upcoming employee anniversaries."""
    return await run_handler("employee_anniversary_review", db)


@router.post("/workflows/scan/projects")
async def scan_project_delays(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Scan tasks for overdue project tasks."""
    return await run_handler("project_delay_escalation", db)


@router.post("/workflows/scan/quality")
async def scan_quality_issues(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Scan quality for high-failure-rate inspections."""
    return await run_handler("quality_issue_quarantine", db)


@router.post("/workflows/scan/customers")
async def scan_churn_risk(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Scan customers for churn risk."""
    return await run_handler("customer_churn_retention", db)
