"""
AI Reports Module — Natural Language to SQL & Auto-Report Generation
TOP WorX ERP System

Provides:
  - Natural Language to SQL (NL2SQL) conversion
  - Auto-report generation from natural language
  - Executive summary generation
  - Comparative analysis
  - Data visualization suggestions
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.engine import AIEngine, get_ai_engine
from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Database Schema Context for NL2SQL
# ---------------------------------------------------------------------------
DATABASE_SCHEMA = """
## Database Schema for TOP WorX ERP

### Tables:

#### Users & Auth
- users (id, email, first_name, last_name, status, created_at)
- roles (id, code, name, level, data_scope)
- user_roles (user_id, role_id)

#### Inventory
- inventory_items (id, sku, name, category_id, global_reorder_point, is_active)
- stock_levels (id, item_id, location_id, quantity_on_hand, quantity_reserved, reorder_point)
- inventory_movements (id, item_id, from_location_id, to_location_id, movement_type, quantity, movement_date)
- inventory_locations (id, code, name, warehouse)

#### Sales
- sales_orders (id, customer_id, order_date, status, total_amount, created_at)
- sales_order_items (id, order_id, product_id, quantity, unit_price, total_price)

#### Finance
- accounts (id, code, name, type, is_active)
- journal_entries (id, reference, description, date, status, created_at)
- journal_entry_lines (id, entry_id, account_id, debit, credit, description)

#### HR
- employees (id, employee_code, first_name, last_name, department_id, status, base_salary, join_date)
- departments (id, code, name, parent_id, is_active)
- attendance_records (id, employee_id, record_date, check_in_time, check_out_time, work_hours)
- leave_requests (id, employee_id, leave_type, start_date, end_date, status)
- payroll_entries (id, employee_id, period_id, base_salary, total_earnings, net_salary, tax)

#### CRM
- customers (id, code, name, email, phone, customer_type, is_active)
- customer_contacts (id, customer_id, name, email, phone, position)
- customer_notes (id, customer_id, note_type, content, created_at)

#### Procurement
- vendors (id, code, name, is_active, is_approved, total_purchased, balance_due)
- purchase_requests (id, request_number, department, status, total_estimated)
- purchase_orders (id, order_number, vendor_id, status, total_amount)
- vendor_invoices (id, invoice_number, vendor_id, total_amount, status)

#### HSE
- hse_incidents (id, title, severity, status, department, reported_by_id, incident_date)
- hse_checklists (id, title, department, status, inspector_id)

#### Tasks
- project_tasks (id, title, priority, status, assigned_to_id, due_date, completed_at)

#### Contracts
- contracts (id, contract_number, title, status, start_date, end_date, total_value)

#### Messages
- conversations (id, title, is_group, created_by_id)
- messages (id, conversation_id, sender_id, content, created_at)

### Relationships:
- users.id → user_roles.user_id
- roles.id → user_roles.role_id
- inventory_items.id → stock_levels.item_id
- inventory_items.id → inventory_movements.item_id
- customers.id → sales_orders.customer_id
- sales_orders.id → sales_order_items.order_id
- accounts.id → journal_entry_lines.account_id
- journal_entries.id → journal_entry_lines.entry_id
- employees.id → attendance_records.employee_id
- employees.id → leave_requests.employee_id
- employees.id → payroll_entries.employee_id
- departments.id → employees.department_id
- vendors.id → purchase_orders.vendor_id
- purchase_orders.id → vendor_invoices.po_id
"""


# ---------------------------------------------------------------------------
# AI Reports Engine
# ---------------------------------------------------------------------------
class AIReportsEngine:
    """
    AI-powered reports engine for TOP WorX ERP.
    
    Features:
      - NL-to-SQL conversion using LLM
      - Auto-report generation
      - Executive summary generation
      - Comparative analysis
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_engine = get_ai_engine(db)

    # -----------------------------------------------------------------------
    # NL-to-SQL Conversion
    # -----------------------------------------------------------------------
    async def nl_to_sql(self, query: str) -> dict:
        """
        Convert natural language query to SQL.
        
        Args:
            query: Natural language query (e.g., "Show me top 10 customers by revenue")
            
        Returns:
            {
                "sql": str,
                "explanation": str,
                "parameters": list,
                "confidence": float,
            }
        """
        system_prompt = f"""You are an expert SQL developer for PostgreSQL database.

{DATABASE_SCHEMA}

Rules:
1. Generate ONLY PostgreSQL-compatible SQL
2. Use proper JOINs based on foreign key relationships
3. Always include LIMIT clause (default 100 rows max)
4. Use table aliases for readability
5. Return results in a format that can be directly executed
6. Never use DELETE or UPDATE statements - only SELECT
7. Use proper WHERE clauses for filtering
8. Use GROUP BY for aggregations
9. Use ORDER BY for sorting

Response format (JSON):
{{
    "sql": "SELECT ...",
    "explanation": "Explanation of what the query does",
    "parameters": [],
    "confidence": 0.95
}}"""

        user_prompt = f"Convert this natural language query to SQL:\n\n{query}"

        try:
            response = await self.ai_engine.chat(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt,
                model="gpt-4o",
                temperature=0.1,
                max_tokens=1000,
            )

            # Parse response
            try:
                result = json.loads(response["content"])
            except json.JSONDecodeError:
                # Try to extract SQL from response
                content = response["content"]
                if "```sql" in content:
                    sql = content.split("```sql")[1].split("```")[0].strip()
                elif "```" in content:
                    sql = content.split("```")[1].split("```")[0].strip()
                else:
                    sql = content.strip()

                result = {
                    "sql": sql,
                    "explanation": "Generated from natural language query",
                    "parameters": [],
                    "confidence": 0.7,
                }

            return result

        except Exception as e:
            logger.error(f"NL-to-SQL error: {e}")
            return {
                "sql": None,
                "explanation": f"Error generating SQL: {str(e)}",
                "parameters": [],
                "confidence": 0,
                "error": str(e),
            }

    # -----------------------------------------------------------------------
    # Execute SQL and Return Results
    # -----------------------------------------------------------------------
    async def execute_nl_query(self, query: str) -> dict:
        """
        Execute a natural language query and return results.
        
        Args:
            query: Natural language query
            
        Returns:
            {
                "query": str,
                "sql": str,
                "columns": list,
                "data": list,
                "row_count": int,
                "explanation": str,
            }
        """
        # Convert to SQL
        nl_result = await self.nl_to_sql(query)

        if not nl_result.get("sql"):
            return {
                "query": query,
                "sql": None,
                "columns": [],
                "data": [],
                "row_count": 0,
                "explanation": nl_result.get("explanation", "Failed to generate SQL"),
                "error": nl_result.get("error"),
            }

        sql = nl_result["sql"]

        # Validate SQL (basic safety check)
        sql_upper = sql.upper().strip()
        if any(keyword in sql_upper for keyword in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]):
            return {
                "query": query,
                "sql": sql,
                "columns": [],
                "data": [],
                "row_count": 0,
                "explanation": "Query rejected: Only SELECT queries are allowed",
                "error": "Only SELECT queries are allowed",
            }

        try:
            # Execute SQL
            result = await self.db.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys()) if rows else []

            # Convert to list of dicts
            data = [dict(zip(columns, row)) for row in rows]

            return {
                "query": query,
                "sql": sql,
                "columns": columns,
                "data": data[:100],  # Limit to 100 rows
                "row_count": len(rows),
                "explanation": nl_result.get("explanation", ""),
                "truncated": len(rows) > 100,
            }

        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return {
                "query": query,
                "sql": sql,
                "columns": [],
                "data": [],
                "row_count": 0,
                "explanation": f"SQL execution error: {str(e)}",
                "error": str(e),
            }

    # -----------------------------------------------------------------------
    # Auto-Report Generation
    # -----------------------------------------------------------------------
    async def generate_report(
        self,
        report_type: str,
        parameters: Optional[dict] = None,
        format: str = "summary",
    ) -> dict:
        """
        Generate an automatic report based on type.
        
        Args:
            report_type: Type of report (sales_summary, inventory_status, financial_overview, hr_summary, etc.)
            parameters: Optional parameters for the report
            format: Output format (summary, detailed, executive)
            
        Returns:
            Report data with sections and insights
        """
        parameters = parameters or {}

        # Define report generators
        report_generators = {
            "sales_summary": self._generate_sales_summary,
            "inventory_status": self._generate_inventory_status,
            "financial_overview": self._generate_financial_overview,
            "hr_summary": self._generate_hr_summary,
            "procurement_summary": self._generate_procurement_summary,
            "executive_summary": self._generate_executive_summary,
        }

        generator = report_generators.get(report_type)
        if not generator:
            return {
                "error": f"Unknown report type: {report_type}",
                "available_types": list(report_generators.keys()),
            }

        return await generator(parameters, format)

    async def _generate_sales_summary(self, params: dict, format: str) -> dict:
        """Generate sales summary report."""
        from app.models.sales import SalesOrder

        days = params.get("days", 30)
        since = datetime.utcnow() - timedelta(days=days)

        # Get sales data
        query = (
            select(
                func.count(SalesOrder.id).label("total_orders"),
                func.coalesce(func.sum(SalesOrder.total_amount), 0).label("total_revenue"),
                func.coalesce(func.avg(SalesOrder.total_amount), 0).label("avg_order_value"),
            )
            .where(SalesOrder.created_at >= since)
        )
        result = await self.db.execute(query)
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
        daily_data = [
            {"date": str(r.date), "orders": r.orders, "revenue": float(r.revenue or 0)}
            for r in daily_result.all()
        ]

        return {
            "report_type": "sales_summary",
            "period": f"Last {days} days",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": [
                {
                    "title": "Sales Overview",
                    "metrics": {
                        "total_orders": summary.total_orders or 0,
                        "total_revenue": float(summary.total_revenue or 0),
                        "avg_order_value": float(summary.avg_order_value or 0),
                    },
                },
                {
                    "title": "Daily Trend",
                    "data": daily_data,
                },
            ],
            "insights": [
                f"Total revenue for the last {days} days: {float(summary.total_revenue or 0):,.0f}",
                f"Average order value: {float(summary.avg_order_value or 0):,.0f}",
            ],
        }

    async def _generate_inventory_status(self, params: dict, format: str) -> dict:
        """Generate inventory status report."""
        from app.models.inventory import InventoryItem, StockLevel

        # Get inventory summary
        query = (
            select(
                func.count(InventoryItem.id).label("total_items"),
                func.sum(case((InventoryItem.is_active == True, 1), else_=0)).label("active_items"),
            )
        )
        result = await self.db.execute(query)
        summary = result.one()

        # Get low stock items
        low_stock_query = (
            select(
                InventoryItem.id,
                InventoryItem.sku,
                InventoryItem.name,
                func.coalesce(func.sum(StockLevel.quantity_on_hand), 0).label("stock"),
            )
            .outerjoin(StockLevel, StockLevel.item_id == InventoryItem.id)
            .where(InventoryItem.is_active == True)
            .group_by(InventoryItem.id, InventoryItem.sku, InventoryItem.name)
            .having(func.coalesce(func.sum(StockLevel.quantity_on_hand), 0) < 10)
        )
        low_stock_result = await self.db.execute(low_stock_query)
        low_stock = [
            {"id": r.id, "sku": r.sku, "name": r.name, "stock": r.stock}
            for r in low_stock_result.all()
        ]

        return {
            "report_type": "inventory_status",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": [
                {
                    "title": "Inventory Overview",
                    "metrics": {
                        "total_items": summary.total_items or 0,
                        "active_items": summary.active_items or 0,
                        "low_stock_count": len(low_stock),
                    },
                },
                {
                    "title": "Low Stock Items",
                    "data": low_stock,
                },
            ],
            "insights": [
                f"Total items: {summary.total_items or 0}",
                f"Low stock items requiring attention: {len(low_stock)}",
            ],
        }

    async def _generate_financial_overview(self, params: dict, format: str) -> dict:
        """Generate financial overview report."""
        from app.models.finance import Account, JournalEntry

        # Get account summary
        query = (
            select(
                Account.type,
                func.count(Account.id).label("count"),
                func.coalesce(func.sum(JournalEntry.amount_debit), 0).label("total_debit"),
                func.coalesce(func.sum(JournalEntry.amount_credit), 0).label("total_credit"),
            )
            .outerjoin(JournalEntry, JournalEntry.account_id == Account.id)
            .where(Account.is_active == True)
            .group_by(Account.type)
        )
        result = await self.db.execute(query)
        accounts = [
            {
                "type": r.type.value if hasattr(r.type, 'value') else str(r.type),
                "count": r.count,
                "debit": float(r.total_debit or 0),
                "credit": float(r.total_credit or 0),
            }
            for r in result.all()
        ]

        return {
            "report_type": "financial_overview",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": [
                {
                    "title": "Account Summary",
                    "data": accounts,
                },
            ],
            "insights": [
                f"Total accounts: {sum(a['count'] for a in accounts)}",
            ],
        }

    async def _generate_hr_summary(self, params: dict, format: str) -> dict:
        """Generate HR summary report."""
        from app.models.hr import Employee, EmployeeStatus

        # Get employee counts
        query = (
            select(
                Employee.status,
                func.count(Employee.id).label("count"),
            )
            .group_by(Employee.status)
        )
        result = await self.db.execute(query)
        status_counts = {r.status.value: r.count for r in result.all()}

        return {
            "report_type": "hr_summary",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": [
                {
                    "title": "Employee Overview",
                    "metrics": {
                        "total_employees": sum(status_counts.values()),
                        "status_breakdown": status_counts,
                    },
                },
            ],
            "insights": [
                f"Total employees: {sum(status_counts.values())}",
                f"Active employees: {status_counts.get('active', 0)}",
            ],
        }

    async def _generate_procurement_summary(self, params: dict, format: str) -> dict:
        """Generate procurement summary report."""
        from app.models.procurement import Vendor, PurchaseOrder

        # Get vendor count
        vendor_query = select(func.count(Vendor.id)).where(Vendor.is_active == True)
        vendor_result = await self.db.execute(vendor_query)
        vendor_count = vendor_result.scalar() or 0

        # Get pending POs
        po_query = select(func.count(PurchaseOrder.id)).where(PurchaseOrder.status == "pending")
        po_result = await self.db.execute(po_query)
        pending_pos = po_result.scalar() or 0

        return {
            "report_type": "procurement_summary",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": [
                {
                    "title": "Procurement Overview",
                    "metrics": {
                        "active_vendors": vendor_count,
                        "pending_purchase_orders": pending_pos,
                    },
                },
            ],
            "insights": [
                f"Active vendors: {vendor_count}",
                f"Pending purchase orders: {pending_pos}",
            ],
        }

    async def _generate_executive_summary(self, params: dict, format: str) -> dict:
        """Generate executive summary combining all modules."""
        # Get summaries from all modules
        sales = await self._generate_sales_summary({"days": 30}, format)
        inventory = await self._generate_inventory_status({}, format)
        hr = await self._generate_hr_summary({}, format)

        # Combine metrics
        return {
            "report_type": "executive_summary",
            "period": "Last 30 days",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": [
                {
                    "title": "Sales Performance",
                    "metrics": sales["sections"][0]["metrics"],
                },
                {
                    "title": "Inventory Status",
                    "metrics": inventory["sections"][0]["metrics"],
                },
                {
                    "title": "HR Overview",
                    "metrics": hr["sections"][0]["metrics"],
                },
            ],
            "insights": sales.get("insights", []) + inventory.get("insights", []) + hr.get("insights", []),
        }

    # -----------------------------------------------------------------------
    # AI-Powered Report with Natural Language
    # -----------------------------------------------------------------------
    async def ai_generate_report(self, description: str) -> dict:
        """
        Generate a report based on natural language description.
        
        Args:
            description: Natural language description of the desired report
            
        Returns:
            Report data with AI-generated insights
        """
        system_prompt = """You are an AI report generator for TOP WorX ERP system.

Based on the user's description, determine:
1. What data to fetch (which tables, what filters)
2. What metrics to calculate
3. What insights to generate

Response format (JSON):
{
    "report_title": "Title of the report",
    "sections": [
        {
            "title": "Section title",
            "query_type": "sales_summary|inventory_status|financial_overview|hr_summary|custom",
            "parameters": {"key": "value"}
        }
    ],
    "insight_instructions": "What insights to generate from this data"
}"""

        user_prompt = f"Generate a report based on this description:\n\n{description}"

        try:
            response = await self.ai_engine.chat(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=1500,
            )

            # Parse response
            try:
                report_config = json.loads(response["content"])
            except json.JSONDecodeError:
                return {
                    "error": "Failed to parse AI response",
                    "raw_response": response["content"],
                }

            # Generate each section
            sections = []
            for section_config in report_config.get("sections", []):
                query_type = section_config.get("query_type", "sales_summary")
                parameters = section_config.get("parameters", {})

                section_report = await self.generate_report(query_type, parameters)
                sections.append({
                    "title": section_config.get("title", query_type),
                    "data": section_report,
                })

            return {
                "report_title": report_config.get("report_title", "AI Generated Report"),
                "generated_at": datetime.utcnow().isoformat(),
                "sections": sections,
                "ai_model": response["model"],
                "tokens_used": response["tokens_used"],
            }

        except Exception as e:
            logger.error(f"AI report generation error: {e}")
            return {
                "error": str(e),
                "report_title": "Error generating report",
            }


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------
def get_ai_reports_engine(db: AsyncSession) -> AIReportsEngine:
    """Get an AIReportsEngine instance."""
    return AIReportsEngine(db)
