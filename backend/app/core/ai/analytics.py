"""
AI Analytics Module — Cross-Module Data Analysis
TOP WorX ERP System

Provides:
  - Cross-module data aggregation
  - Trend detection
  - Anomaly detection
  - Predictive analytics
  - Recommendation engine
  - Insight generation
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import select, func, and_, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.engine import AIEngine, get_ai_engine
from app.crud.ai import ai_insight_crud
from app.models.ai_core import InsightType, InsightSeverity

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# AI Analytics Engine
# ---------------------------------------------------------------------------
class AIAnalyticsEngine:
    """
    Cross-module AI analytics engine for TOP WorX ERP.
    
    Analyzes data across all modules to generate insights,
    predictions, and recommendations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_engine = get_ai_engine(db)

    # -----------------------------------------------------------------------
    # Inventory Analytics
    # -----------------------------------------------------------------------
    async def analyze_inventory(self) -> dict:
        """Analyze inventory data and generate insights."""
        from app.models.inventory import InventoryItem, StockLevel, InventoryMovement

        # Get stock levels
        stock_query = (
            select(
                InventoryItem.id,
                InventoryItem.sku,
                InventoryItem.name,
                InventoryItem.global_reorder_point,
                func.coalesce(func.sum(StockLevel.quantity_on_hand), 0).label("total_stock"),
            )
            .outerjoin(StockLevel, StockLevel.item_id == InventoryItem.id)
            .where(InventoryItem.is_active == True)
            .group_by(InventoryItem.id, InventoryItem.sku, InventoryItem.name, InventoryItem.global_reorder_point)
        )
        result = await self.db.execute(stock_query)
        items = result.all()

        # Analyze each item
        low_stock_items = []
        overstock_items = []
        total_value = Decimal("0")

        for item in items:
            stock = item.total_stock or 0
            reorder_point = item.global_reorder_point or 0

            if reorder_point > 0 and stock <= reorder_point:
                low_stock_items.append({
                    "item_id": item.id,
                    "sku": item.sku,
                    "name": item.name,
                    "current_stock": stock,
                    "reorder_point": reorder_point,
                    "shortage": reorder_point - stock,
                })
            elif reorder_point > 0 and stock > reorder_point * 3:
                overstock_items.append({
                    "item_id": item.id,
                    "sku": item.sku,
                    "name": item.name,
                    "current_stock": stock,
                    "reorder_point": reorder_point,
                    "excess": stock - reorder_point,
                })

        # Get recent movements
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        movement_query = (
            select(
                InventoryMovement.item_id,
                func.sum(InventoryMovement.quantity).label("total_moved"),
                func.count(InventoryMovement.id).label("movement_count"),
            )
            .where(InventoryMovement.movement_date >= thirty_days_ago)
            .group_by(InventoryMovement.item_id)
        )
        movement_result = await self.db.execute(movement_query)
        movement_data = {r.item_id: {"moved": r.total_moved, "count": r.movement_count} for r in movement_result.all()}

        # Generate insights
        insights = []
        if low_stock_items:
            insights.append({
                "type": "alert",
                "severity": "high",
                "title": f"{len(low_stock_items)} items below reorder point",
                "description": f"Critical: {len(low_stock_items)} items need immediate reorder.",
                "data": {"items": low_stock_items[:10]},
            })

        if overstock_items:
            insights.append({
                "type": "recommendation",
                "severity": "medium",
                "title": f"{len(overstock_items)} items overstocked",
                "description": f"Consider reducing orders for {len(overstock_items)} items with excess inventory.",
                "data": {"items": overstock_items[:10]},
            })

        return {
            "module": "inventory",
            "summary": {
                "total_items": len(items),
                "low_stock_count": len(low_stock_items),
                "overstock_count": len(overstock_items),
                "total_moved_30d": sum(d["moved"] for d in movement_data.values()),
            },
            "low_stock_items": low_stock_items,
            "overstock_items": overstock_items,
            "insights": insights,
        }

    # -----------------------------------------------------------------------
    # Sales Analytics
    # -----------------------------------------------------------------------
    async def analyze_sales(self, days: int = 30) -> dict:
        """Analyze sales data and generate insights."""
        from app.models.sales import SalesOrder, SalesOrderItem

        since = datetime.utcnow() - timedelta(days=days)

        # Get sales summary
        sales_query = (
            select(
                func.count(SalesOrder.id).label("order_count"),
                func.coalesce(func.sum(SalesOrder.total_amount), 0).label("total_revenue"),
                func.coalesce(func.avg(SalesOrder.total_amount), 0).label("avg_order_value"),
            )
            .where(SalesOrder.created_at >= since)
        )
        result = await self.db.execute(sales_query)
        summary = result.one()

        # Get daily trend
        daily_query = (
            select(
                func.date(SalesOrder.created_at).label("date"),
                func.count(SalesOrder.id).label("orders"),
                func.sum(SalesOrder.total_amount).label("revenue"),
            )
            .where(SalesOrder.created_at >= since)
            .group_by(func.date(SalesOrder.created_at))
            .order_by(func.date(SalesOrder.created_at))
        )
        daily_result = await self.db.execute(daily_query)
        daily_trend = [
            {"date": str(r.date), "orders": r.orders, "revenue": float(r.revenue or 0)}
            for r in daily_result.all()
        ]

        # Calculate trend
        if len(daily_trend) >= 7:
            recent_avg = sum(d["revenue"] for d in daily_trend[-7:]) / 7
            older_avg = sum(d["revenue"] for d in daily_trend[:7]) / max(len(daily_trend[:7]), 1)
            trend_pct = ((recent_avg - older_avg) / max(older_avg, 1)) * 100
        else:
            trend_pct = 0

        # Generate insights
        insights = []
        if trend_pct < -10:
            insights.append({
                "type": "alert",
                "severity": "high",
                "title": "Sales declining",
                "description": f"Sales revenue dropped {abs(trend_pct):.1f}% in the last 7 days compared to the previous period.",
                "data": {"trend_pct": trend_pct},
            })
        elif trend_pct > 10:
            insights.append({
                "type": "trend",
                "severity": "info",
                "title": "Sales growing",
                "description": f"Sales revenue increased {trend_pct:.1f}% in the last 7 days.",
                "data": {"trend_pct": trend_pct},
            })

        return {
            "module": "sales",
            "period_days": days,
            "summary": {
                "total_orders": summary.order_count or 0,
                "total_revenue": float(summary.total_revenue or 0),
                "avg_order_value": float(summary.avg_order_value or 0),
                "trend_pct": trend_pct,
            },
            "daily_trend": daily_trend,
            "insights": insights,
        }

    # -----------------------------------------------------------------------
    # Finance Analytics
    # -----------------------------------------------------------------------
    async def analyze_finance(self) -> dict:
        """Analyze finance data and generate insights."""
        from app.models.finance import Account, JournalEntry

        # Get account balances
        account_query = (
            select(
                Account.id,
                Account.code,
                Account.name,
                Account.type,
                func.coalesce(func.sum(JournalEntry.amount_debit), 0).label("total_debit"),
                func.coalesce(func.sum(JournalEntry.amount_credit), 0).label("total_credit"),
            )
            .outerjoin(JournalEntry, JournalEntry.account_id == Account.id)
            .where(Account.is_active == True)
            .group_by(Account.id, Account.code, Account.name, Account.type)
        )
        result = await self.db.execute(account_query)
        accounts = result.all()

        # Calculate totals by type
        totals_by_type = {}
        for acc in accounts:
            acc_type = acc.type.value if hasattr(acc.type, 'value') else str(acc.type)
            if acc_type not in totals_by_type:
                totals_by_type[acc_type] = {"debit": 0, "credit": 0, "balance": 0}
            totals_by_type[acc_type]["debit"] += float(acc.total_debit)
            totals_by_type[acc_type]["credit"] += float(acc.total_credit)
            totals_by_type[acc_type]["balance"] += float(acc.total_debit) - float(acc.total_credit)

        # Get recent journal entries
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        entry_query = (
            select(
                func.count(JournalEntry.id).label("entry_count"),
                func.coalesce(func.sum(JournalEntry.amount_debit), 0).label("total_debit"),
            )
            .where(JournalEntry.created_at >= thirty_days_ago)
        )
        entry_result = await self.db.execute(entry_query)
        entry_summary = entry_result.one()

        # Generate insights
        insights = []
        revenue = totals_by_type.get("revenue", {}).get("credit", 0)
        expense = totals_by_type.get("expense", {}).get("debit", 0)
        if revenue > 0 and expense > 0:
            profit_margin = ((revenue - expense) / revenue) * 100
            if profit_margin < 10:
                insights.append({
                    "type": "alert",
                    "severity": "medium",
                    "title": "Low profit margin",
                    "description": f"Profit margin is {profit_margin:.1f}%. Consider reviewing expenses.",
                    "data": {"profit_margin": profit_margin, "revenue": revenue, "expense": expense},
                })

        return {
            "module": "finance",
            "summary": {
                "total_accounts": len(accounts),
                "journal_entries_30d": entry_summary.entry_count or 0,
                "total_debit_30d": float(entry_summary.total_debit or 0),
            },
            "totals_by_type": totals_by_type,
            "insights": insights,
        }

    # -----------------------------------------------------------------------
    # HR Analytics
    # -----------------------------------------------------------------------
    async def analyze_hr(self) -> dict:
        """Analyze HR data and generate insights."""
        from app.models.hr import Employee, EmployeeStatus, LeaveRequest, LeaveStatus

        # Get employee counts by status
        employee_query = (
            select(
                Employee.status,
                func.count(Employee.id).label("count"),
            )
            .group_by(Employee.status)
        )
        result = await self.db.execute(employee_query)
        status_counts = {r.status.value: r.count for r in result.all()}

        total_employees = sum(status_counts.values())
        active_employees = status_counts.get("active", 0)

        # Get leave requests
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        leave_query = (
            select(
                func.count(LeaveRequest.id).label("total"),
                func.sum(case((LeaveRequest.status == LeaveStatus.APPROVED, 1), else_=0)).label("approved"),
            )
            .where(LeaveRequest.created_at >= thirty_days_ago)
        )
        leave_result = await self.db.execute(leave_query)
        leave_summary = leave_result.one()

        # Generate insights
        insights = []
        on_leave = status_counts.get("on_leave", 0)
        if total_employees > 0 and on_leave / total_employees > 0.1:
            insights.append({
                "type": "alert",
                "severity": "medium",
                "title": "High leave ratio",
                "description": f"{on_leave} employees ({on_leave/total_employees*100:.1f}%) are currently on leave.",
                "data": {"on_leave": on_leave, "total": total_employees},
            })

        return {
            "module": "hr",
            "summary": {
                "total_employees": total_employees,
                "active_employees": active_employees,
                "status_breakdown": status_counts,
                "leaves_30d": leave_summary.total or 0,
                "leaves_approved_30d": leave_summary.approved or 0,
            },
            "insights": insights,
        }

    # -----------------------------------------------------------------------
    # CRM Analytics
    # -----------------------------------------------------------------------
    async def analyze_crm(self) -> dict:
        """Analyze CRM data and generate insights."""
        from app.models.crm import Customer

        # Get customer counts
        customer_query = (
            select(
                func.count(Customer.id).label("total"),
                func.sum(case((Customer.is_active == True, 1), else_=0)).label("active"),
            )
        )
        result = await self.db.execute(customer_query)
        summary = result.one()

        # Get new customers (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_query = select(func.count(Customer.id)).where(Customer.created_at >= thirty_days_ago)
        new_result = await self.db.execute(new_query)
        new_customers = new_result.scalar() or 0

        return {
            "module": "crm",
            "summary": {
                "total_customers": summary.total or 0,
                "active_customers": summary.active or 0,
                "new_customers_30d": new_customers,
            },
            "insights": [],
        }

    # -----------------------------------------------------------------------
    # Cross-Module Analysis
    # -----------------------------------------------------------------------
    async def analyze_cross_module(self) -> dict:
        """Perform cross-module analysis and generate correlated insights."""
        # Run all module analyses
        inventory = await self.analyze_inventory()
        sales = await self.analyze_sales()
        finance = await self.analyze_finance()
        hr = await self.analyze_hr()
        crm = await self.analyze_crm()

        # Generate cross-module insights
        cross_insights = []

        # Sales + Inventory correlation
        if sales["summary"]["trend_pct"] > 20 and inventory["summary"]["low_stock_count"] > 5:
            cross_insights.append({
                "type": "recommendation",
                "severity": "high",
                "title": "Sales growth with low stock risk",
                "description": f"Sales are growing {sales['summary']['trend_pct']:.1f}% but {inventory['summary']['low_stock_count']} items are low on stock. Increase orders to avoid stockouts.",
                "modules": ["sales", "inventory"],
            })

        # Finance + HR correlation
        if finance["summary"].get("journal_entries_30d", 0) > 100 and hr["summary"]["active_employees"] < 10:
            cross_insights.append({
                "type": "insight",
                "severity": "low",
                "title": "High workload per employee",
                "description": f"High financial activity ({finance['summary']['journal_entries_30d']} entries) with only {hr['summary']['active_employees']} active employees.",
                "modules": ["finance", "hr"],
            })

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "modules": {
                "inventory": inventory,
                "sales": sales,
                "finance": finance,
                "hr": hr,
                "crm": crm,
            },
            "cross_module_insights": cross_insights,
            "summary": {
                "total_insights": (
                    len(inventory.get("insights", []))
                    + len(sales.get("insights", []))
                    + len(finance.get("insights", []))
                    + len(hr.get("insights", []))
                    + len(crm.get("insights", []))
                    + len(cross_insights)
                ),
            },
        }

    # -----------------------------------------------------------------------
    # Generate and Store Insights
    # -----------------------------------------------------------------------
    async def generate_insights(self, user_id: Optional[int] = None) -> list[dict]:
        """Generate insights across all modules and store them."""
        analysis = await self.analyze_cross_module()
        stored_insights = []

        for module_name, module_data in analysis["modules"].items():
            for insight_data in module_data.get("insights", []):
                insight = await ai_insight_crud.create(
                    self.db,
                    user_id=user_id,
                    insight_type=InsightType(insight_data["type"]),
                    module=module_name,
                    title=insight_data["title"],
                    description=insight_data["description"],
                    severity=InsightSeverity(insight_data.get("severity", "info")),
                    data=insight_data.get("data"),
                )
                stored_insights.append({
                    "id": insight.id,
                    "module": module_name,
                    "type": insight_data["type"],
                    "title": insight_data["title"],
                })

        # Store cross-module insights
        for insight_data in analysis.get("cross_module_insights", []):
            insight = await ai_insight_crud.create(
                self.db,
                user_id=user_id,
                insight_type=InsightType(insight_data["type"]),
                module="cross_module",
                title=insight_data["title"],
                description=insight_data["description"],
                severity=InsightSeverity(insight_data.get("severity", "info")),
                data={"modules": insight_data.get("modules", [])},
            )
            stored_insights.append({
                "id": insight.id,
                "module": "cross_module",
                "type": insight_data["type"],
                "title": insight_data["title"],
            })

        return stored_insights

    # -----------------------------------------------------------------------
    # AI-Powered Analysis (uses LLM)
    # -----------------------------------------------------------------------
    async def ai_analyze_data(self, module: str, data: dict) -> dict:
        """Use AI to analyze data and generate natural language insights."""
        # Build prompt
        system_prompt = """You are an AI business analyst for TOP WorX ERP system.
Analyze the provided data and generate actionable insights.
Format your response as JSON with:
- summary: One-line summary
- insights: Array of {title, description, severity, recommendation}
- risks: Array of identified risks
- opportunities: Array of opportunities"""

        user_prompt = f"""Analyze the following {module} data and provide insights:

{json.dumps(data, indent=2, default=str)}"""

        try:
            response = await self.ai_engine.chat(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt,
                model="gpt-4o",
                temperature=0.3,
            )

            # Parse response
            import json
            try:
                analysis = json.loads(response["content"])
            except json.JSONDecodeError:
                analysis = {
                    "summary": response["content"][:500],
                    "insights": [],
                    "risks": [],
                    "opportunities": [],
                }

            return {
                "module": module,
                "ai_analysis": analysis,
                "model": response["model"],
                "tokens_used": response["tokens_used"],
                "cost": response["cost"],
            }

        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {
                "module": module,
                "ai_analysis": None,
                "error": str(e),
            }


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------
def get_ai_analytics_engine(db: AsyncSession) -> AIAnalyticsEngine:
    """Get an AIAnalyticsEngine instance."""
    return AIAnalyticsEngine(db)
