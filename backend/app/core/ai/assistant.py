"""
AI Assistant Module — Context-Aware Chat with ERP Integration
TOP WorX ERP System

Provides:
  - Context-aware conversations
  - Module-specific knowledge
  - ERP data retrieval via natural language
  - Command execution via conversation
  - Conversation memory and history
  - Multi-turn dialogue support
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.engine import AIEngine, get_ai_engine
from app.core.config import settings
from app.crud.ai import ai_conversation_crud, ai_message_crud
from app.models.ai_core import AIConversation, AIMessage, MessageRole

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ERP Context Provider
# ---------------------------------------------------------------------------
class ERPContextProvider:
    """Provide ERP context to the AI assistant."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_module_context(self, module: str) -> dict:
        """Get context data for a specific module."""
        context_providers = {
            "inventory": self._get_inventory_context,
            "sales": self._get_sales_context,
            "finance": self._get_finance_context,
            "hr": self._get_hr_context,
            "crm": self._get_crm_context,
            "procurement": self._get_procurement_context,
            "hse": self._get_hse_context,
            "tasks": self._get_tasks_context,
        }

        provider = context_providers.get(module)
        if provider:
            return await provider()
        return {"module": module, "available": True}

    async def _get_inventory_context(self) -> dict:
        """Get inventory context."""
        from app.models.inventory import InventoryItem, StockLevel

        # Get item count
        count_q = select(func.count(InventoryItem.id)).where(InventoryItem.is_active == True)
        count_result = await self.db.execute(count_q)
        total_items = count_result.scalar() or 0

        # Get low stock items
        low_stock_q = (
            select(func.count(InventoryItem.id))
            .join(StockLevel, StockLevel.item_id == InventoryItem.id)
            .where(InventoryItem.is_active == True)
            .having(func.sum(StockLevel.quantity_on_hand) < 10)
        )
        low_stock_result = await self.db.execute(low_stock_q)
        low_stock_count = low_stock_result.scalar() or 0

        return {
            "module": "inventory",
            "total_items": total_items,
            "low_stock_items": low_stock_count,
            "capabilities": [
                "Check stock levels",
                "View item details",
                "Track movements",
                "Generate low stock reports",
            ],
        }

    async def _get_sales_context(self) -> dict:
        """Get sales context."""
        from app.models.sales import SalesOrder

        # Get recent orders count
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        count_q = select(func.count(SalesOrder.id)).where(SalesOrder.created_at >= thirty_days_ago)
        count_result = await self.db.execute(count_q)
        recent_orders = count_result.scalar() or 0

        # Get total revenue
        revenue_q = select(func.coalesce(func.sum(SalesOrder.total_amount), 0)).where(SalesOrder.created_at >= thirty_days_ago)
        revenue_result = await self.db.execute(revenue_q)
        recent_revenue = float(revenue_result.scalar() or 0)

        return {
            "module": "sales",
            "recent_orders_30d": recent_orders,
            "recent_revenue_30d": recent_revenue,
            "capabilities": [
                "View sales orders",
                "Analyze revenue trends",
                "Track customer purchases",
                "Generate sales reports",
            ],
        }

    async def _get_finance_context(self) -> dict:
        """Get finance context."""
        from app.models.finance import Account, JournalEntry

        # Get account count
        account_q = select(func.count(Account.id)).where(Account.is_active == True)
        account_result = await self.db.execute(account_q)
        total_accounts = account_result.scalar() or 0

        # Get recent entries
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        entry_q = select(func.count(JournalEntry.id)).where(JournalEntry.created_at >= thirty_days_ago)
        entry_result = await self.db.execute(entry_q)
        recent_entries = entry_result.scalar() or 0

        return {
            "module": "finance",
            "total_accounts": total_accounts,
            "recent_entries_30d": recent_entries,
            "capabilities": [
                "View account balances",
                "Check journal entries",
                "Generate financial reports",
                "Analyze expenses",
            ],
        }

    async def _get_hr_context(self) -> dict:
        """Get HR context."""
        from app.models.hr import Employee, EmployeeStatus

        # Get employee counts
        count_q = select(func.count(Employee.id))
        count_result = await self.db.execute(count_q)
        total_employees = count_result.scalar() or 0

        active_q = select(func.count(Employee.id)).where(Employee.status == EmployeeStatus.ACTIVE)
        active_result = await self.db.execute(active_q)
        active_employees = active_result.scalar() or 0

        return {
            "module": "hr",
            "total_employees": total_employees,
            "active_employees": active_employees,
            "capabilities": [
                "View employee information",
                "Check attendance",
                "Manage leave requests",
                "View payroll data",
            ],
        }

    async def _get_crm_context(self) -> dict:
        """Get CRM context."""
        from app.models.crm import Customer

        count_q = select(func.count(Customer.id))
        count_result = await self.db.execute(count_q)
        total_customers = count_result.scalar() or 0

        return {
            "module": "crm",
            "total_customers": total_customers,
            "capabilities": [
                "View customer information",
                "Track customer interactions",
                "Manage customer notes",
                "Analyze customer data",
            ],
        }

    async def _get_procurement_context(self) -> dict:
        """Get procurement context."""
        from app.models.procurement import Vendor, PurchaseOrder

        vendor_q = select(func.count(Vendor.id)).where(Vendor.is_active == True)
        vendor_result = await self.db.execute(vendor_q)
        total_vendors = vendor_result.scalar() or 0

        po_q = select(func.count(PurchaseOrder.id)).where(PurchaseOrder.status == "pending")
        po_result = await self.db.execute(po_q)
        pending_pos = po_result.scalar() or 0

        return {
            "module": "procurement",
            "total_vendors": total_vendors,
            "pending_purchase_orders": pending_pos,
            "capabilities": [
                "View vendor information",
                "Track purchase orders",
                "Manage procurement requests",
                "Analyze spending",
            ],
        }

    async def _get_hse_context(self) -> dict:
        """Get HSE context."""
        from app.models.hse import HSEIncident

        count_q = select(func.count(HSEIncident.id))
        count_result = await self.db.execute(count_q)
        total_incidents = count_result.scalar() or 0

        return {
            "module": "hse",
            "total_incidents": total_incidents,
            "capabilities": [
                "View safety incidents",
                "Track checklists",
                "Monitor safety alerts",
            ],
        }

    async def _get_tasks_context(self) -> dict:
        """Get tasks context."""
        from app.models.tasks import ProjectTask

        count_q = select(func.count(ProjectTask.id))
        count_result = await self.db.execute(count_q)
        total_tasks = count_result.scalar() or 0

        return {
            "module": "tasks",
            "total_tasks": total_tasks,
            "capabilities": [
                "View tasks",
                "Track task status",
                "Manage assignments",
            ],
        }

    async def get_full_context(self, user_id: Optional[int] = None) -> dict:
        """Get full ERP context for the assistant."""
        # Get all module contexts
        modules = ["inventory", "sales", "finance", "hr", "crm", "procurement", "hse", "tasks"]
        module_contexts = {}
        for module in modules:
            module_contexts[module] = await self.get_module_context(module)

        return {
            "system": "TOP WorX ERP System",
            "version": "1.0.0",
            "modules": module_contexts,
            "available_commands": [
                "Show me [module] data",
                "What is the status of [item/order/employee]?",
                "Generate a report for [module]",
                "Create a [record type]",
                "Update [record type] [id]",
                "Search for [query]",
            ],
        }


# ---------------------------------------------------------------------------
# AI Assistant Engine
# ---------------------------------------------------------------------------
class AIAssistantEngine:
    """
    Context-aware AI assistant for TOP WorX ERP.
    
    Features:
      - Multi-turn conversations with memory
      - Module-specific knowledge
      - ERP data retrieval via natural language
      - Command execution
      - Context-aware responses
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_engine = get_ai_engine(db)
        self.context_provider = ERPContextProvider(db)

    # -----------------------------------------------------------------------
    # Chat with Context
    # -----------------------------------------------------------------------
    async def chat(
        self,
        message: str,
        user_id: int,
        conversation_id: Optional[int] = None,
        module: Optional[str] = None,
    ) -> dict:
        """
        Chat with the AI assistant with full ERP context.
        
        Args:
            message: User message
            user_id: Current user ID
            conversation_id: Optional existing conversation ID
            module: Optional module context (inventory, sales, etc.)
            
        Returns:
            Response with content, context used, and actions taken
        """
        # Get or create conversation
        if conversation_id:
            conv = await ai_conversation_crud.get(self.db, conversation_id)
            if not conv or conv.user_id != user_id:
                conv = await ai_conversation_crud.create(
                    self.db, user_id=user_id, title=message[:100], module=module
                )
                conversation_id = conv.id
        else:
            conv = await ai_conversation_crud.create(
                self.db, user_id=user_id, title=message[:100], module=module
            )
            conversation_id = conv.id

        # Save user message
        await ai_message_crud.create(
            self.db,
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message,
        )

        # Get conversation history
        history = await ai_message_crud.list_by_conversation(self.db, conversation_id, limit=20)
        messages = [{"role": m.role.value, "content": m.content} for m in history]

        # Get ERP context
        erp_context = await self.context_provider.get_full_context(user_id)

        # Get module-specific context if specified
        module_context = None
        if module:
            module_context = await self.context_provider.get_module_context(module)

        # Build system prompt with context
        system_prompt = self._build_system_prompt(erp_context, module_context)

        # Call AI
        try:
            response = await self.ai_engine.chat(
                messages=messages,
                system_prompt=system_prompt,
                user_id=user_id,
                conversation_id=conversation_id,
                temperature=0.7,
            )
        except Exception as e:
            logger.error(f"AI assistant error: {e}")
            response = {
                "content": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "model": settings.AI_MODEL,
                "tokens_used": 0,
                "cost": 0,
            }

        # Save assistant message
        await ai_message_crud.create(
            self.db,
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response["content"],
            model=response.get("model"),
            tokens_used=response.get("tokens_used", 0),
        )

        # Detect actions from response
        actions = self._detect_actions(response["content"], message)

        return {
            "reply": response["content"],
            "conversation_id": conversation_id,
            "model": response.get("model", settings.AI_MODEL),
            "tokens_used": response.get("tokens_used", 0),
            "cost": response.get("cost", 0),
            "context_used": {
                "modules": list(erp_context.get("modules", {}).keys()),
                "module_context": module_context,
            },
            "actions": actions,
        }

    def _build_system_prompt(
        self, erp_context: dict, module_context: Optional[dict] = None
    ) -> str:
        """Build system prompt with ERP context."""
        prompt = """You are TOP WorX AI Assistant, an intelligent helper for the TOP WorX ERP system.

## Your Role
- Help users navigate and understand their ERP data
- Answer questions about business operations
- Provide insights and recommendations
- Guide users through ERP workflows

## Available Modules"""
        
        # Add module information
        for module_name, module_data in erp_context.get("modules", {}).items():
            capabilities = module_data.get("capabilities", [])
            prompt += f"\n### {module_name.title()}\n"
            prompt += f"Capabilities: {', '.join(capabilities)}\n"
            
            # Add specific data if available
            if "total_items" in module_data:
                prompt += f"Total items: {module_data['total_items']}\n"
            if "recent_orders_30d" in module_data:
                prompt += f"Recent orders (30d): {module_data['recent_orders_30d']}\n"
            if "total_employees" in module_data:
                prompt += f"Total employees: {module_data['total_employees']}\n"

        # Add module-specific context
        if module_context:
            prompt += f"\n## Current Module Context: {module_context.get('module', 'unknown').title()}\n"
            for key, value in module_context.items():
                if key not in ["module", "capabilities"]:
                    prompt += f"- {key}: {value}\n"

        prompt += """
## Guidelines
- Be helpful and professional
- Provide specific data when available
- Suggest relevant actions users can take
- If you don't have specific data, guide users on how to find it
- Use the module context to provide relevant answers
- For complex queries, suggest breaking them down into simpler steps

## Response Format
- Keep responses concise but informative
- Use bullet points for lists
- Include relevant numbers and metrics when available
- Suggest next steps when appropriate
"""
        return prompt

    def _detect_actions(self, response: str, user_message: str) -> list[dict]:
        """Detect potential actions from the response and user message."""
        actions = []
        message_lower = user_message.lower()

        # Detect common action patterns
        if any(word in message_lower for word in ["show", "display", "list", "view"]):
            actions.append({
                "type": "navigate",
                "description": "Navigate to view data",
            })

        if any(word in message_lower for word in ["create", "add", "new"]):
            actions.append({
                "type": "create",
                "description": "Create new record",
            })

        if any(word in message_lower for word in ["report", "generate", "export"]):
            actions.append({
                "type": "report",
                "description": "Generate report",
            })

        if any(word in message_lower for word in ["search", "find", "lookup"]):
            actions.append({
                "type": "search",
                "description": "Search for records",
            })

        return actions

    # -----------------------------------------------------------------------
    # Quick Queries
    # -----------------------------------------------------------------------
    async def quick_query(self, query_type: str, user_id: int) -> dict:
        """
        Execute a quick predefined query.
        
        Args:
            query_type: Type of quick query
            user_id: Current user ID
            
        Returns:
            Query results
        """
        quick_queries = {
            "dashboard_summary": self._get_dashboard_summary,
            "low_stock": self._get_low_stock_summary,
            "recent_orders": self._get_recent_orders,
            "pending_tasks": self._get_pending_tasks,
            "my_leave_balance": self._get_leave_balance,
        }

        query_func = quick_queries.get(query_type)
        if not query_func:
            return {"error": f"Unknown query type: {query_type}"}

        return await query_func(user_id)

    async def _get_dashboard_summary(self, user_id: int) -> dict:
        """Get dashboard summary."""
        erp_context = await self.context_provider.get_full_context(user_id)
        
        return {
            "type": "dashboard_summary",
            "summary": {
                "inventory": {
                    "total_items": erp_context["modules"]["inventory"]["total_items"],
                    "low_stock": erp_context["modules"]["inventory"]["low_stock_items"],
                },
                "sales": {
                    "recent_orders": erp_context["modules"]["sales"]["recent_orders_30d"],
                    "recent_revenue": erp_context["modules"]["sales"]["recent_revenue_30d"],
                },
                "hr": {
                    "total_employees": erp_context["modules"]["hr"]["total_employees"],
                    "active_employees": erp_context["modules"]["hr"]["active_employees"],
                },
            },
        }

    async def _get_low_stock_summary(self, user_id: int) -> dict:
        """Get low stock summary."""
        context = await self.context_provider.get_module_context("inventory")
        return {
            "type": "low_stock",
            "summary": context,
        }

    async def _get_recent_orders(self, user_id: int) -> dict:
        """Get recent orders summary."""
        context = await self.context_provider.get_module_context("sales")
        return {
            "type": "recent_orders",
            "summary": context,
        }

    async def _get_pending_tasks(self, user_id: int) -> dict:
        """Get pending tasks summary."""
        context = await self.context_provider.get_module_context("tasks")
        return {
            "type": "pending_tasks",
            "summary": context,
        }

    async def _get_leave_balance(self, user_id: int) -> dict:
        """Get leave balance for current user."""
        from app.models.hr import Employee, LeaveRequest, LeaveStatus

        # Get employee record
        emp_q = select(Employee).where(Employee.user_id == user_id)
        emp_result = await self.db.execute(emp_q)
        employee = emp_result.scalar_one_or_none()

        if not employee:
            return {
                "type": "leave_balance",
                "summary": {"message": "No employee record found"},
            }

        return {
            "type": "leave_balance",
            "summary": {
                "annual_leave_balance": employee.annual_leave_balance,
                "sick_leave_balance": employee.sick_leave_balance,
            },
        }

    # -----------------------------------------------------------------------
    # Conversation Management
    # -----------------------------------------------------------------------
    async def get_conversation_history(
        self, conversation_id: int, user_id: int
    ) -> list[dict]:
        """Get conversation history."""
        conv = await ai_conversation_crud.get(self.db, conversation_id)
        if not conv or conv.user_id != user_id:
            return []

        messages = await ai_message_crud.list_by_conversation(self.db, conversation_id)
        return [
            {
                "id": m.id,
                "role": m.role.value,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]

    async def list_conversations(
        self, user_id: int, module: Optional[str] = None
    ) -> list[dict]:
        """List user's conversations."""
        convs = await ai_conversation_crud.list_by_user(
            self.db, user_id, module=module
        )
        return [
            {
                "id": c.id,
                "title": c.title,
                "module": c.module,
                "total_tokens": c.total_tokens,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
            }
            for c in convs
        ]

    async def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation."""
        conv = await ai_conversation_crud.get(self.db, conversation_id)
        if not conv or conv.user_id != user_id:
            return False
        return await ai_conversation_crud.soft_delete(self.db, conversation_id)


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------
def get_ai_assistant_engine(db: AsyncSession) -> AIAssistantEngine:
    """Get an AIAssistantEngine instance."""
    return AIAssistantEngine(db)
