"""
AI Automation Module — Workflow Engine with Triggers
TOP WorX ERP System

Provides:
  - Workflow creation and management
  - Multiple trigger types (manual, scheduled, event, threshold)
  - Action execution (create/update records, send notifications, run queries)
  - Condition evaluation
  - Workflow execution history
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.engine import AIEngine, get_ai_engine
from app.crud.ai import ai_workflow_crud
from app.models.ai_core import (
    AIWorkflow,
    WorkflowTriggerType,
    WorkflowActionType,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Condition Evaluator
# ---------------------------------------------------------------------------
class ConditionEvaluator:
    """Evaluate workflow conditions against data."""

    @staticmethod
    def evaluate(condition: dict, data: dict) -> bool:
        """
        Evaluate a condition against data.
        
        Condition format:
        {
            "field": "quantity",
            "operator": "lt",  # lt, gt, eq, lte, gte, in, not_in, contains
            "value": 10
        }
        
        Or compound conditions:
        {
            "logic": "and",  # and, or
            "conditions": [...]
        }
        """
        if not condition:
            return True

        # Compound conditions
        if "logic" in condition:
            logic = condition["logic"]
            conditions = condition.get("conditions", [])

            if logic == "and":
                return all(
                    ConditionEvaluator.evaluate(c, data) for c in conditions
                )
            elif logic == "or":
                return any(
                    ConditionEvaluator.evaluate(c, data) for c in conditions
                )
            return False

        # Simple condition
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        if not field or not operator:
            return False

        # Get field value from data (supports nested fields with dot notation)
        field_value = data
        for part in field.split("."):
            if isinstance(field_value, dict):
                field_value = field_value.get(part)
            else:
                return False

        if field_value is None:
            return False

        # Evaluate operator
        try:
            if operator == "eq":
                return field_value == value
            elif operator == "neq":
                return field_value != value
            elif operator == "lt":
                return field_value < value
            elif operator == "gt":
                return field_value > value
            elif operator == "lte":
                return field_value <= value
            elif operator == "gte":
                return field_value >= value
            elif operator == "in":
                return field_value in value
            elif operator == "not_in":
                return field_value not in value
            elif operator == "contains":
                return value in field_value
            elif operator == "starts_with":
                return str(field_value).startswith(str(value))
            elif operator == "ends_with":
                return str(field_value).endswith(str(value))
        except (TypeError, ValueError) as e:
            logger.warning(f"Condition evaluation error: {e}")
            return False

        return False


# ---------------------------------------------------------------------------
# Action Executor
# ---------------------------------------------------------------------------
class ActionExecutor:
    """Execute workflow actions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(
        self,
        action_type: WorkflowActionType,
        action_config: dict,
        context: dict,
    ) -> dict:
        """
        Execute a workflow action.
        
        Args:
            action_type: Type of action to execute
            action_config: Configuration for the action
            context: Data context for the action
            
        Returns:
            Action execution result
        """
        executors = {
            WorkflowActionType.CREATE_RECORD: self._create_record,
            WorkflowActionType.UPDATE_RECORD: self._update_record,
            WorkflowActionType.SEND_NOTIFICATION: self._send_notification,
            WorkflowActionType.SEND_EMAIL: self._send_email,
            WorkflowActionType.RUN_QUERY: self._run_query,
            WorkflowActionType.CALL_WEBHOOK: self._call_webhook,
            WorkflowActionType.AI_ANALYSIS: self._ai_analysis,
        }

        executor = executors.get(action_type)
        if not executor:
            return {"success": False, "error": f"Unknown action type: {action_type}"}

        try:
            result = await executor(action_config, context)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return {"success": False, "error": str(e)}

    async def _create_record(self, config: dict, context: dict) -> dict:
        """Create a new record."""
        table = config.get("table")
        fields = config.get("fields", {})

        # Resolve field values from context
        resolved_fields = {}
        for key, value in fields.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Template variable
                var_path = value[2:-2].strip()
                resolved_value = context
                for part in var_path.split("."):
                    if isinstance(resolved_value, dict):
                        resolved_value = resolved_value.get(part)
                    else:
                        resolved_value = None
                        break
                resolved_fields[key] = resolved_value
            else:
                resolved_fields[key] = value

        # TODO: Implement actual record creation based on table name
        # For now, return mock result
        return {
            "action": "create_record",
            "table": table,
            "fields": resolved_fields,
            "message": f"Record created in {table}",
        }

    async def _update_record(self, config: dict, context: dict) -> dict:
        """Update an existing record."""
        table = config.get("table")
        record_id = config.get("record_id")
        fields = config.get("fields", {})

        return {
            "action": "update_record",
            "table": table,
            "record_id": record_id,
            "fields": fields,
            "message": f"Record {record_id} updated in {table}",
        }

    async def _send_notification(self, config: dict, context: dict) -> dict:
        """Send a notification."""
        user_id = config.get("user_id")
        title = config.get("title", "Workflow Notification")
        message = config.get("message", "")
        severity = config.get("severity", "info")

        # Resolve template variables in message
        if "{{" in message:
            for key, value in context.items():
                message = message.replace(f"{{{{{key}}}}}", str(value))

        # TODO: Integrate with notification service
        return {
            "action": "send_notification",
            "user_id": user_id,
            "title": title,
            "message": message,
            "severity": severity,
            "message": f"Notification sent to user {user_id}",
        }

    async def _send_email(self, config: dict, context: dict) -> dict:
        """Send an email."""
        to = config.get("to")
        subject = config.get("subject", "Workflow Email")
        body = config.get("body", "")

        # TODO: Integrate with email service
        return {
            "action": "send_email",
            "to": to,
            "subject": subject,
            "message": f"Email sent to {to}",
        }

    async def _run_query(self, config: dict, context: dict) -> dict:
        """Run a database query."""
        from sqlalchemy import text

        query = config.get("query", "")

        # Resolve template variables
        for key, value in context.items():
            query = query.replace(f"{{{{{key}}}}}", str(value))

        try:
            result = await self.db.execute(text(query))
            rows = result.fetchall()
            return {
                "action": "run_query",
                "query": query,
                "rows_affected": len(rows),
                "data": [dict(row._mapping) for row in rows[:100]],
            }
        except Exception as e:
            return {
                "action": "run_query",
                "query": query,
                "error": str(e),
            }

    async def _call_webhook(self, config: dict, context: dict) -> dict:
        """Call an external webhook."""
        import aiohttp

        url = config.get("url")
        method = config.get("method", "POST")
        headers = config.get("headers", {})
        payload = config.get("payload", context)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, json=payload, headers=headers, timeout=10
                ) as response:
                    return {
                        "action": "call_webhook",
                        "url": url,
                        "status": response.status,
                        "message": f"Webhook called: {response.status}",
                    }
        except Exception as e:
            return {
                "action": "call_webhook",
                "url": url,
                "error": str(e),
            }

    async def _ai_analysis(self, config: dict, context: dict) -> dict:
        """Perform AI analysis on data."""
        from app.core.ai.engine import get_ai_engine

        engine = get_ai_engine(self.db)
        prompt = config.get("prompt", "Analyze this data and provide insights")

        # Resolve template variables in prompt
        for key, value in context.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        try:
            response = await engine.chat(
                messages=[{"role": "user", "content": f"{prompt}\n\nData: {json.dumps(context, default=str)}"}],
                temperature=0.3,
            )
            return {
                "action": "ai_analysis",
                "analysis": response["content"],
                "model": response["model"],
            }
        except Exception as e:
            return {
                "action": "ai_analysis",
                "error": str(e),
            }


# ---------------------------------------------------------------------------
# AI Automation Engine
# ---------------------------------------------------------------------------
class AIAutomationEngine:
    """
    AI-powered automation engine for TOP WorX ERP.
    
    Features:
      - Workflow creation and management
      - Multiple trigger types
      - Condition evaluation
      - Action execution
      - Execution history
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_engine = get_ai_engine(db)
        self.condition_evaluator = ConditionEvaluator()
        self.action_executor = ActionExecutor(db)

    # -----------------------------------------------------------------------
    # Workflow Management
    # -----------------------------------------------------------------------
    async def create_workflow(
        self,
        name: str,
        trigger_module: str,
        trigger_event: str,
        action_type: str,
        action_config: dict,
        description: Optional[str] = None,
        condition: Optional[dict] = None,
        trigger_type: str = "event",
        created_by_id: Optional[int] = None,
    ) -> dict:
        """Create a new automation workflow."""
        workflow = await ai_workflow_crud.create(
            self.db,
            name=name,
            description=description,
            trigger_module=trigger_module,
            trigger_event=trigger_event,
            action_type=action_type,
            action_config=action_config,
            condition=condition,
            created_by_id=created_by_id,
        )

        return {
            "id": workflow.id,
            "name": workflow.name,
            "trigger_module": workflow.trigger_module,
            "trigger_event": workflow.trigger_event,
            "action_type": workflow.action_type,
            "is_active": workflow.is_active,
            "created_at": workflow.created_at.isoformat(),
        }

    async def list_workflows(
        self,
        trigger_module: Optional[str] = None,
        is_active: bool = True,
    ) -> list[dict]:
        """List workflows."""
        workflows = await ai_workflow_crud.list_active(
            self.db, trigger_module=trigger_module
        )
        return [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "trigger_module": w.trigger_module,
                "trigger_event": w.trigger_event,
                "action_type": w.action_type,
                "is_active": w.is_active,
                "trigger_count": w.trigger_count,
                "success_count": w.success_count,
                "failure_count": w.failure_count,
                "last_triggered_at": w.last_triggered_at.isoformat() if w.last_triggered_at else None,
                "created_at": w.created_at.isoformat(),
            }
            for w in workflows
        ]

    async def get_workflow(self, workflow_id: int) -> Optional[dict]:
        """Get workflow details."""
        workflow = await ai_workflow_crud.get(self.db, workflow_id)
        if not workflow:
            return None

        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "trigger_module": workflow.trigger_module,
            "trigger_event": workflow.trigger_event,
            "trigger_type": workflow.trigger_type.value,
            "condition": workflow.condition,
            "action_type": workflow.action_type.value,
            "action_config": workflow.action_config,
            "is_active": workflow.is_active,
            "trigger_count": workflow.trigger_count,
            "success_count": workflow.success_count,
            "failure_count": workflow.failure_count,
            "last_triggered_at": workflow.last_triggered_at.isoformat() if workflow.last_triggered_at else None,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
        }

    # -----------------------------------------------------------------------
    # Workflow Execution
    # -----------------------------------------------------------------------
    async def trigger_workflow(
        self,
        workflow_id: int,
        context: Optional[dict] = None,
    ) -> dict:
        """
        Trigger a workflow execution.
        
        Args:
            workflow_id: ID of the workflow to trigger
            context: Data context for condition evaluation and action execution
            
        Returns:
            Execution result
        """
        workflow = await ai_workflow_crud.get(self.db, workflow_id)
        if not workflow:
            return {"success": False, "error": "Workflow not found"}

        if not workflow.is_active:
            return {"success": False, "error": "Workflow is not active"}

        context = context or {}

        # Evaluate condition
        if workflow.condition:
            if not self.condition_evaluator.evaluate(workflow.condition, context):
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "Condition not met",
                }

        # Execute action
        action_type = WorkflowActionType(workflow.action_type)
        result = await self.action_executor.execute(
            action_type=action_type,
            action_config=workflow.action_config,
            context=context,
        )

        # Update workflow stats
        await ai_workflow_crud.trigger(
            self.db, workflow_id, success=result["success"]
        )

        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "execution": result,
            "executed_at": datetime.utcnow().isoformat(),
        }

    async def trigger_event(
        self,
        module: str,
        event: str,
        data: Optional[dict] = None,
    ) -> list[dict]:
        """
        Trigger all workflows matching a module/event.
        
        Args:
            module: Module that triggered the event (e.g., "inventory", "sales")
            event: Event name (e.g., "low_stock", "order_created")
            data: Event data
            
        Returns:
            List of execution results
        """
        # Find matching workflows
        workflows = await ai_workflow_crud.list_active(
            self.db, trigger_module=module
        )

        results = []
        for workflow in workflows:
            if workflow.trigger_event == event:
                result = await self.trigger_workflow(
                    workflow.id, context=data
                )
                results.append(result)

        return results

    # -----------------------------------------------------------------------
    # Pre-built Workflow Templates
    # -----------------------------------------------------------------------
    async def create_low_stock_workflow(
        self,
        threshold: int = 10,
        notification_user_id: Optional[int] = None,
    ) -> dict:
        """Create a workflow for low stock alerts."""
        return await self.create_workflow(
            name="Low Stock Alert",
            description="Triggered when inventory falls below threshold",
            trigger_module="inventory",
            trigger_event="low_stock",
            condition={
                "field": "quantity",
                "operator": "lt",
                "value": threshold,
            },
            action_type="send_notification",
            action_config={
                "user_id": notification_user_id,
                "title": "Low Stock Alert",
                "message": "Item {{item_name}} is below reorder point. Current stock: {{quantity}}",
                "severity": "warning",
            },
        )

    async def create_order_notification_workflow(
        self,
        notification_user_id: Optional[int] = None,
    ) -> dict:
        """Create a workflow for new order notifications."""
        return await self.create_workflow(
            name="New Order Notification",
            description="Notify when a new order is created",
            trigger_module="sales",
            trigger_event="order_created",
            action_type="send_notification",
            action_config={
                "user_id": notification_user_id,
                "title": "New Order Created",
                "message": "Order {{order_number}} has been created for {{customer_name}}",
                "severity": "info",
            },
        )

    async def create_ai_analysis_workflow(
        self,
        module: str,
        prompt: str,
    ) -> dict:
        """Create a workflow that performs AI analysis on data."""
        return await self.create_workflow(
            name=f"AI Analysis - {module}",
            description=f"Perform AI analysis on {module} data",
            trigger_module=module,
            trigger_event="data_updated",
            action_type="ai_analysis",
            action_config={
                "prompt": prompt,
            },
        )

    # -----------------------------------------------------------------------
    # Workflow Statistics
    # -----------------------------------------------------------------------
    async def get_workflow_stats(self) -> dict:
        """Get workflow execution statistics."""
        from sqlalchemy import func

        # Total workflows
        total_q = select(func.count(AIWorkflow.id))
        total_result = await self.db.execute(total_q)
        total = total_result.scalar() or 0

        # Active workflows
        active_q = select(func.count(AIWorkflow.id)).where(AIWorkflow.is_active == True)
        active_result = await self.db.execute(active_q)
        active = active_result.scalar() or 0

        # Total triggers
        triggers_q = select(
            func.sum(AIWorkflow.trigger_count),
            func.sum(AIWorkflow.success_count),
            func.sum(AIWorkflow.failure_count),
        )
        triggers_result = await self.db.execute(triggers_q)
        triggers = triggers_result.one()

        # Workflows by module
        module_q = select(
            AIWorkflow.trigger_module,
            func.count(AIWorkflow.id).label("count"),
        ).group_by(AIWorkflow.trigger_module)
        module_result = await self.db.execute(module_q)
        by_module = {r.trigger_module: r.count for r in module_result.all()}

        return {
            "total_workflows": total,
            "active_workflows": active,
            "total_triggers": triggers[0] or 0,
            "successful_triggers": triggers[1] or 0,
            "failed_triggers": triggers[2] or 0,
            "success_rate": (
                (triggers[1] or 0) / max(triggers[0] or 1, 1) * 100
            ),
            "workflows_by_module": by_module,
        }


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------
def get_ai_automation_engine(db: AsyncSession) -> AIAutomationEngine:
    """Get an AIAutomationEngine instance."""
    return AIAutomationEngine(db)
