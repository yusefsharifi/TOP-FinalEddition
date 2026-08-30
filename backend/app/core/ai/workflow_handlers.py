"""
AI Workflow Handlers — B3 Spec Automated Workflows
TOP WorX ERP System

Implements the 8 required automated workflows from the B3 specification:
  1. Low Stock → Auto PO
  2. Invoice Due → Auto Reminder
  3. Lead Score High → Auto Assign
  4. Expense Anomaly → Auto Alert
  5. Employee Anniversary → Auto Review
  6. Project Delay → Auto Escalation
  7. Quality Issue → Auto Quarantine
  8. Customer Churn Risk → Auto Retention

Each handler:
  - Scans the relevant module for trigger conditions
  - Executes the appropriate action
  - Returns results for logging
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import select, func, and_, case, text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Handler Registry
# ═══════════════════════════════════════════════════════════════════════════════

WORKFLOW_HANDLERS: dict[str, Any] = {}


def register_handler(name: str):
    """Decorator to register a workflow handler."""
    def decorator(func):
        WORKFLOW_HANDLERS[name] = func
        return func
    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Low Stock → Auto PO
# ═══════════════════════════════════════════════════════════════════════════════

@register_handler("low_stock_auto_po")
async def handle_low_stock_auto_po(
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """
    Scan inventory for items below reorder point.
    Generate purchase order suggestions for each.
    """
    from app.models.inventory import InventoryItem, StockLevel

    threshold_multiplier = (config or {}).get("threshold_multiplier", 1.0)

    # Find items below reorder point
    query = (
        select(
            InventoryItem.id,
            InventoryItem.sku,
            InventoryItem.name,
            InventoryItem.global_reorder_point,
            func.coalesce(func.sum(StockLevel.quantity_on_hand), 0).label("current_stock"),
        )
        .outerjoin(StockLevel, StockLevel.item_id == InventoryItem.id)
        .where(InventoryItem.is_active == True)
        .where(InventoryItem.global_reorder_point.isnot(None))
        .group_by(
            InventoryItem.id, InventoryItem.sku,
            InventoryItem.name, InventoryItem.global_reorder_point,
        )
        .having(
            func.coalesce(func.sum(StockLevel.quantity_on_hand), 0)
            < InventoryItem.global_reorder_point * threshold_multiplier
        )
    )

    result = await db.execute(query)
    low_stock_items = [dict(r._mapping) for r in result.all()]

    if not low_stock_items:
        return {
            "handler": "low_stock_auto_po",
            "triggered": False,
            "message": "No items below reorder point",
            "items_found": 0,
        }

    # Generate PO suggestions
    po_suggestions = []
    for item in low_stock_items:
        reorder_point = item["global_reorder_point"]
        current_stock = item["current_stock"]
        # Order enough to reach 2x reorder point
        suggested_qty = max(1, (reorder_point * 2) - current_stock)

        po_suggestions.append({
            "item_id": item["id"],
            "sku": item["sku"],
            "name": item["name"],
            "current_stock": current_stock,
            "reorder_point": reorder_point,
            "suggested_order_qty": suggested_qty,
            "urgency": "critical" if current_stock == 0 else "high",
        })

    # Create notification
    summary = (
        f"Low stock alert: {len(po_suggestions)} items need reorder. "
        f"Critical: {sum(1 for p in po_suggestions if p['urgency'] == 'critical')}"
    )

    return {
        "handler": "low_stock_auto_po",
        "triggered": True,
        "message": summary,
        "items_found": len(po_suggestions),
        "po_suggestions": po_suggestions,
        "action": "create_purchase_order",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Invoice Due → Auto Reminder
# ═══════════════════════════════════════════════════════════════════════════════

@register_handler("invoice_due_reminder")
async def handle_invoice_due_reminder(
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """
    Find invoices approaching or past due date.
    Send reminders for overdue and upcoming invoices.
    """
    from app.models.sales import SalesInvoice, InvoiceStatus

    days_ahead = (config or {}).get("days_ahead", 7)
    today = datetime.utcnow().date()
    deadline = today + timedelta(days=days_ahead)

    # Find overdue invoices
    overdue_query = select(
        SalesInvoice.id,
        SalesInvoice.invoice_number,
        SalesInvoice.customer_id,
        SalesInvoice.due_date,
        SalesInvoice.amount_due,
        SalesInvoice.status,
    ).where(
        SalesInvoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIAL_PAID, InvoiceStatus.OVERDUE]),
        SalesInvoice.due_date < today,
        SalesInvoice.amount_due > 0,
    )
    overdue_result = await db.execute(overdue_query)
    overdue_invoices = [dict(r._mapping) for r in overdue_result.all()]

    # Find invoices due soon
    upcoming_query = select(
        SalesInvoice.id,
        SalesInvoice.invoice_number,
        SalesInvoice.customer_id,
        SalesInvoice.due_date,
        SalesInvoice.amount_due,
        SalesInvoice.status,
    ).where(
        SalesInvoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIAL_PAID]),
        SalesInvoice.due_date >= today,
        SalesInvoice.due_date <= deadline,
        SalesInvoice.amount_due > 0,
    )
    upcoming_result = await db.execute(upcoming_query)
    upcoming_invoices = [dict(r._mapping) for r in upcoming_result.all()]

    total_due = sum(float(inv["amount_due"]) for inv in overdue_invoices + upcoming_invoices)

    reminders = []
    for inv in overdue_invoices:
        days_overdue = (today - inv["due_date"]).days
        reminders.append({
            "invoice_id": inv["id"],
            "invoice_number": inv["invoice_number"],
            "customer_id": inv["customer_id"],
            "amount_due": float(inv["amount_due"]),
            "days_overdue": days_overdue,
            "type": "overdue",
        })

    for inv in upcoming_invoices:
        days_until = (inv["due_date"] - today).days
        reminders.append({
            "invoice_id": inv["id"],
            "invoice_number": inv["invoice_number"],
            "customer_id": inv["customer_id"],
            "amount_due": float(inv["amount_due"]),
            "days_until_due": days_until,
            "type": "upcoming",
        })

    summary = (
        f"Invoice reminders: {len(overdue_invoices)} overdue, "
        f"{len(upcoming_invoices)} upcoming. Total due: ${total_due:,.2f}"
    )

    return {
        "handler": "invoice_due_reminder",
        "triggered": len(reminders) > 0,
        "message": summary,
        "overdue_count": len(overdue_invoices),
        "upcoming_count": len(upcoming_invoices),
        "total_amount_due": total_due,
        "reminders": reminders,
        "action": "send_reminder",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Lead Score High → Auto Assign
# ═══════════════════════════════════════════════════════════════════════════════

@register_handler("lead_high_score_assign")
async def handle_lead_high_score_assign(
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """
    Find high-scoring unassigned leads and assign to sales reps.
    Uses round-robin or weighted assignment.
    """
    from app.models.crm import Customer

    score_threshold = (config or {}).get("score_threshold", 80)

    # Find high-value unassigned customers (leads)
    # Customers with high total_invoiced but no recent activity
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    query = select(
        Customer.id,
        Customer.code,
        Customer.name,
        Customer.total_invoiced,
        Customer.balance_due,
        Customer.is_active,
    ).where(
        Customer.is_active == True,
        Customer.total_invoiced > 0,
    ).order_by(Customer.total_invoiced.desc()).limit(50)

    result = await db.execute(query)
    high_value_customers = [dict(r._mapping) for r in result.all()]

    # Score customers based on value and balance
    scored_leads = []
    for cust in high_value_customers:
        # Simple scoring: value (0-50) + balance ratio (0-30) + active bonus (20)
        value_score = min(50, float(cust["total_invoiced"]) / 10000)
        balance_ratio = float(cust["balance_due"]) / max(float(cust["total_invoiced"]), 1)
        balance_score = 30 * (1 - balance_ratio)  # Lower balance = higher score
        active_score = 20 if cust["is_active"] else 0
        total_score = value_score + balance_score + active_score

        if total_score >= score_threshold:
            scored_leads.append({
                "customer_id": cust["id"],
                "customer_code": cust["code"],
                "customer_name": cust["name"],
                "score": round(total_score, 1),
                "total_invoiced": float(cust["total_invoiced"]),
            })

    summary = (
        f"Lead scoring: {len(scored_leads)} high-value leads identified "
        f"(threshold: {score_threshold})"
    )

    return {
        "handler": "lead_high_score_assign",
        "triggered": len(scored_leads) > 0,
        "message": summary,
        "leads_found": len(scored_leads),
        "leads": scored_leads[:10],
        "action": "assign_to_sales_rep",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Expense Anomaly → Auto Alert
# ═══════════════════════════════════════════════════════════════════════════════

@register_handler("expense_anomaly_alert")
async def handle_expense_anomaly_alert(
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """
    Detect unusual expense patterns by comparing recent vs historical.
    Flags expenses that exceed 2x the rolling average.
    """
    from app.models.finance import Account, JournalEntry, JournalEntryLine

    lookback_days = (config or {}).get("lookback_days", 30)
    deviation_threshold = (config or {}).get("deviation_threshold", 2.0)

    today = datetime.utcnow()
    recent_start = today - timedelta(days=lookback_days)
    historical_start = today - timedelta(days=lookback_days * 3)
    historical_end = recent_start

    # Get recent expenses by account
    recent_query = (
        select(
            Account.id,
            Account.code,
            Account.name,
            func.coalesce(func.sum(JournalEntryLine.amount_debit), 0).label("recent_total"),
        )
        .join(JournalEntryLine, JournalEntryLine.account_id == Account.id)
        .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
        .where(Account.type == "expense")
        .where(JournalEntry.entry_date >= recent_start)
        .group_by(Account.id, Account.code, Account.name)
    )
    recent_result = await db.execute(recent_query)
    recent_expenses = {r.id: dict(r._mapping) for r in recent_result.all()}

    # Get historical average expenses
    historical_query = (
        select(
            Account.id,
            func.coalesce(func.sum(JournalEntryLine.amount_debit), 0).label("hist_total"),
        )
        .join(JournalEntryLine, JournalEntryLine.account_id == Account.id)
        .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
        .where(Account.type == "expense")
        .where(JournalEntry.entry_date >= historical_start)
        .where(JournalEntry.entry_date < historical_end)
        .group_by(Account.id)
    )
    historical_result = await db.execute(historical_query)
    historical_expenses = {r.id: float(r.hist_total) for r in historical_result.all()}

    # Find anomalies
    anomalies = []
    for account_id, recent_data in recent_expenses.items():
        recent_total = float(recent_data["recent_total"])
        hist_avg = historical_expenses.get(account_id, 0) / 3  # 3 periods

        if hist_avg > 0 and recent_total > hist_avg * deviation_threshold:
            deviation_pct = ((recent_total - hist_avg) / hist_avg) * 100
            anomalies.append({
                "account_id": account_id,
                "account_code": recent_data["code"],
                "account_name": recent_data["name"],
                "recent_total": recent_total,
                "historical_avg": round(hist_avg, 2),
                "deviation_pct": round(deviation_pct, 1),
                "severity": "critical" if deviation_pct > 300 else "high" if deviation_pct > 200 else "medium",
            })

    anomalies.sort(key=lambda x: x["deviation_pct"], reverse=True)

    summary = (
        f"Expense anomaly detection: {len(anomalies)} anomalies found "
        f"(threshold: {deviation_threshold}x average)"
    )

    return {
        "handler": "expense_anomaly_alert",
        "triggered": len(anomalies) > 0,
        "message": summary,
        "anomalies_found": len(anomalies),
        "anomalies": anomalies[:10],
        "action": "alert_manager",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Employee Anniversary → Auto Review
# ═══════════════════════════════════════════════════════════════════════════════

@register_handler("employee_anniversary_review")
async def handle_employee_anniversary_review(
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """
    Find employees with work anniversaries coming up.
    Schedule performance reviews for anniversaries.
    """
    from app.models.hr import Employee, EmployeeStatus

    days_ahead = (config or {}).get("days_ahead", 30)
    today = datetime.utcnow().date()

    # Find active employees with join_date anniversaries approaching
    employees_query = select(
        Employee.id,
        Employee.first_name,
        Employee.last_name,
        Employee.employee_code,
        Employee.join_date,
        Employee.department_id,
        Employee.job_title,
        Employee.status,
    ).where(
        Employee.status == EmployeeStatus.ACTIVE,
        Employee.join_date.isnot(None),
    )
    result = await db.execute(employees_query)
    employees = [dict(r._mapping) for r in result.all()]

    upcoming_anniversaries = []
    for emp in employees:
        join_date = emp["join_date"]
        if not join_date:
            continue

        # Calculate next anniversary
        current_year = today.year
        try:
            next_anniversary = join_date.replace(year=current_year)
            if next_anniversary < today:
                next_anniversary = join_date.replace(year=current_year + 1)
        except ValueError:
            # Feb 29 → Mar 1 in non-leap years
            next_anniversary = join_date.replace(year=current_year, day=1) + timedelta(days=60)
            if next_anniversary < today:
                next_anniversary = join_date.replace(year=current_year + 1, day=1) + timedelta(days=60)

        days_until = (next_anniversary - today).days
        if 0 <= days_until <= days_ahead:
            years_of_service = current_year - join_date.year
            upcoming_anniversaries.append({
                "employee_id": emp["id"],
                "employee_name": f"{emp['first_name']} {emp['last_name']}",
                "employee_code": emp["employee_code"],
                "join_date": join_date.isoformat(),
                "anniversary_date": next_anniversary.isoformat(),
                "years_of_service": years_of_service,
                "department_id": emp["department_id"],
                "job_title": emp["job_title"],
                "days_until": days_until,
            })

    upcoming_anniversaries.sort(key=lambda x: x["days_until"])

    summary = (
        f"Employee anniversaries: {len(upcoming_anniversaries)} in next {days_ahead} days. "
        f"Performance reviews recommended."
    )

    return {
        "handler": "employee_anniversary_review",
        "triggered": len(upcoming_anniversaries) > 0,
        "message": summary,
        "anniversaries_found": len(upcoming_anniversaries),
        "anniversaries": upcoming_anniversaries,
        "action": "schedule_performance_review",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Project Delay → Auto Escalation
# ═══════════════════════════════════════════════════════════════════════════════

@register_handler("project_delay_escalation")
async def handle_project_delay_escalation(
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """
    Find tasks that are past due date and not completed.
    Escalate delayed tasks to management.
    """
    from app.models.tasks import ProjectTask, TaskStatus

    today = datetime.utcnow()

    # Find overdue tasks
    query = select(
        ProjectTask.id,
        ProjectTask.name,
        ProjectTask.status,
        ProjectTask.priority,
        ProjectTask.due_date,
        ProjectTask.assigned_to_id,
        ProjectTask.created_at,
    ).where(
        ProjectTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED]),
        ProjectTask.due_date.isnot(None),
        ProjectTask.due_date < today,
    ).order_by(ProjectTask.due_date)

    result = await db.execute(query)
    overdue_tasks = [dict(r._mapping) for r in result.all()]

    escalations = []
    for task in overdue_tasks:
        days_overdue = (today - task["due_date"]).days
        escalations.append({
            "task_id": task["id"],
            "task_name": task["name"],
            "status": task["status"].value if hasattr(task["status"], "value") else str(task["status"]),
            "priority": task["priority"].value if hasattr(task["priority"], "value") else str(task["priority"]),
            "due_date": task["due_date"].isoformat(),
            "assigned_to_id": task["assigned_to_id"],
            "days_overdue": days_overdue,
            "severity": "critical" if days_overdue > 14 else "high" if days_overdue > 7 else "medium",
        })

    # Sort by days overdue descending
    escalations.sort(key=lambda x: x["days_overdue"], reverse=True)

    summary = (
        f"Project delays: {len(escalations)} overdue tasks. "
        f"Critical (>14 days): {sum(1 for e in escalations if e['severity'] == 'critical')}"
    )

    return {
        "handler": "project_delay_escalation",
        "triggered": len(escalations) > 0,
        "message": summary,
        "overdue_count": len(escalations),
        "escalations": escalations[:20],
        "action": "escalate_to_management",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Quality Issue → Auto Quarantine
# ═══════════════════════════════════════════════════════════════════════════════

@register_handler("quality_issue_quarantine")
async def handle_quality_issue_quarantine(
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """
    Find quality inspections with high failure rates.
    Flag related inventory for quarantine.
    """
    from app.models.quality import QualityInspection, QualityDefect, InspectionStatus, DefectStatus

    fail_rate_threshold = (config or {}).get("fail_rate_threshold", 10.0)  # percent

    # Find recent inspections with high failure rates
    query = select(
        QualityInspection.id,
        QualityInspection.inspection_number,
        QualityInspection.name,
        QualityInspection.item_id,
        QualityInspection.quantity_inspected,
        QualityInspection.quantity_passed,
        QualityInspection.quantity_failed,
        QualityInspection.pass_rate,
        QualityInspection.status,
        QualityInspection.batch_number,
    ).where(
        QualityInspection.status == InspectionStatus.COMPLETED,
        QualityInspection.quantity_inspected > 0,
    ).order_by(QualityInspection.created_at.desc()).limit(100)

    result = await db.execute(query)
    inspections = [dict(r._mapping) for r in result.all()]

    # Find inspections with high failure rate
    quality_issues = []
    for insp in inspections:
        if insp["quantity_inspected"] > 0:
            fail_rate = (insp["quantity_failed"] / insp["quantity_inspected"]) * 100
        else:
            fail_rate = 0

        if fail_rate >= fail_rate_threshold:
            # Get open defects for this inspection
            defect_query = select(
                func.count(QualityDefect.id).label("open_defects"),
            ).where(
                QualityDefect.inspection_id == insp["id"],
                QualityDefect.status == DefectStatus.OPEN,
            )
            defect_result = await db.execute(defect_query)
            open_defects = defect_result.scalar() or 0

            quality_issues.append({
                "inspection_id": insp["id"],
                "inspection_number": insp["inspection_number"],
                "inspection_name": insp["name"],
                "item_id": insp["item_id"],
                "quantity_inspected": insp["quantity_inspected"],
                "quantity_failed": insp["quantity_failed"],
                "pass_rate": round(100 - fail_rate, 1),
                "fail_rate": round(fail_rate, 1),
                "open_defects": open_defects,
                "batch_number": insp["batch_number"],
                "severity": "critical" if fail_rate > 30 else "high" if fail_rate > 20 else "medium",
            })

    quality_issues.sort(key=lambda x: x["fail_rate"], reverse=True)

    summary = (
        f"Quality issues: {len(quality_issues)} inspections with fail rate >= {fail_rate_threshold}%. "
        f"Quarantine recommended for {sum(1 for q in quality_issues if q['severity'] == 'critical')} critical."
    )

    return {
        "handler": "quality_issue_quarantine",
        "triggered": len(quality_issues) > 0,
        "message": summary,
        "issues_found": len(quality_issues),
        "quality_issues": quality_issues[:10],
        "action": "quarantine_stock",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Customer Churn Risk → Auto Retention
# ═══════════════════════════════════════════════════════════════════════════════

@register_handler("customer_churn_retention")
async def handle_customer_churn_retention(
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """
    Identify customers at risk of churning.
    Criteria: No orders in last 90 days + had orders before.
    """
    from app.models.sales import Customer, SalesInvoice

    inactive_days = (config or {}).get("inactive_days", 90)
    today = datetime.utcnow()
    cutoff_date = today - timedelta(days=inactive_days)

    # Find customers with past orders but no recent orders
    # Subquery: customers with recent invoices
    recent_customers_subq = (
        select(SalesInvoice.customer_id)
        .where(SalesInvoice.created_at >= cutoff_date)
        .distinct()
    ).subquery()

    # Find active customers NOT in recent list
    query = (
        select(
            Customer.id,
            Customer.code,
            Customer.name,
            Customer.email,
            Customer.phone,
            Customer.total_invoiced,
            Customer.total_paid,
            Customer.balance_due,
            Customer.category,
            Customer.created_at,
        )
        .where(
            Customer.is_active == True,
            Customer.total_invoiced > 0,
        )
        .where(Customer.id.notin_(select(recent_customers_subq.c.customer_id)))
        .order_by(Customer.total_invoiced.desc())
    )

    result = await db.execute(query)
    churn_risk_customers = [dict(r._mapping) for r in result.all()]

    # Score churn risk
    retention_candidates = []
    for cust in churn_risk_customers:
        # Risk score based on historical value and outstanding balance
        total_invoiced = float(cust["total_invoiced"])
        balance_due = float(cust["balance_due"])
        total_paid = float(cust["total_paid"])

        # Higher value + higher balance = higher churn risk
        value_score = min(50, total_invoiced / 5000)
        balance_score = 30 if balance_due > 0 else 0
        payment_ratio = total_paid / max(total_invoiced, 1)
        payment_score = 20 * (1 - payment_ratio)  # Lower payment = higher risk

        risk_score = value_score + balance_score + payment_score

        if risk_score >= 20:  # Minimum threshold
            retention_candidates.append({
                "customer_id": cust["id"],
                "customer_code": cust["code"],
                "customer_name": cust["name"],
                "email": cust["email"],
                "phone": cust["phone"],
                "total_invoiced": total_invoiced,
                "balance_due": balance_due,
                "risk_score": round(risk_score, 1),
                "category": cust["category"].value if hasattr(cust["category"], "value") else str(cust["category"]),
                "last_order_days_ago": (today - cust["created_at"]).days if cust["created_at"] else None,
            })

    retention_candidates.sort(key=lambda x: x["risk_score"], reverse=True)

    total_at_risk_value = sum(c["balance_due"] for c in retention_candidates)

    summary = (
        f"Customer churn risk: {len(retention_candidates)} customers at risk. "
        f"Total value at risk: ${total_at_risk_value:,.2f}"
    )

    return {
        "handler": "customer_churn_retention",
        "triggered": len(retention_candidates) > 0,
        "message": summary,
        "customers_at_risk": len(retention_candidates),
        "total_value_at_risk": total_at_risk_value,
        "retention_candidates": retention_candidates[:15],
        "action": "trigger_retention_campaign",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Runner — Execute all handlers
# ═══════════════════════════════════════════════════════════════════════════════

async def run_all_handlers(
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """
    Run all registered workflow handlers.
    Returns combined results from all handlers.
    """
    results = {}
    for name, handler in WORKFLOW_HANDLERS.items():
        try:
            result = await handler(db, config)
            results[name] = result
        except Exception as e:
            logger.error(f"Handler '{name}' failed: {e}")
            results[name] = {
                "handler": name,
                "triggered": False,
                "error": str(e),
            }

    # Summary
    triggered = [name for name, r in results.items() if r.get("triggered")]
    errors = [name for name, r in results.items() if "error" in r]

    return {
        "handlers_run": len(results),
        "handlers_triggered": len(triggered),
        "handlers_errors": len(errors),
        "triggered_handlers": triggered,
        "error_handlers": errors,
        "results": results,
        "executed_at": datetime.utcnow().isoformat(),
    }


async def run_handler(
    handler_name: str,
    db: AsyncSession,
    config: Optional[dict] = None,
) -> dict:
    """Run a specific workflow handler."""
    handler = WORKFLOW_HANDLERS.get(handler_name)
    if not handler:
        return {
            "error": f"Handler '{handler_name}' not found",
            "available_handlers": list(WORKFLOW_HANDLERS.keys()),
        }

    try:
        return await handler(db, config)
    except Exception as e:
        logger.error(f"Handler '{handler_name}' failed: {e}")
        return {
            "handler": handler_name,
            "triggered": False,
            "error": str(e),
        }


def list_handlers() -> list[dict]:
    """List all available workflow handlers."""
    return [
        {
            "name": name,
            "description": handler.__doc__.strip().split("\n")[0] if handler.__doc__ else "",
        }
        for name, handler in WORKFLOW_HANDLERS.items()
    ]
