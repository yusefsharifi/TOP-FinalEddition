"""
AI CRUD Operations
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_core import (
    AIConversation,
    AIMessage,
    AIPrompt,
    AIUsageLog,
    AIWorkflow,
    AIInsight,
    InsightType,
    InsightSeverity,
    MessageRole,
)


# ---------------------------------------------------------------------------
# Conversation CRUD
# ---------------------------------------------------------------------------
class AIConversationCRUD:
    """CRUD operations for AI conversations."""

    @staticmethod
    async def get(db: AsyncSession, conversation_id: int) -> Optional[AIConversation]:
        return await db.get(AIConversation, conversation_id)

    @staticmethod
    async def list_by_user(
        db: AsyncSession,
        user_id: int,
        module: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[AIConversation]:
        q = (
            select(AIConversation)
            .where(AIConversation.user_id == user_id, AIConversation.is_active == True)
            .order_by(AIConversation.updated_at.desc())
        )
        if module:
            q = q.where(AIConversation.module == module)
        result = await db.execute(q.offset(offset).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        title: str,
        module: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AIConversation:
        conv = AIConversation(
            user_id=user_id,
            title=title,
            module=module,
            model=model or "gpt-4o",
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    @staticmethod
    async def update_title(db: AsyncSession, conversation_id: int, title: str) -> Optional[AIConversation]:
        conv = await db.get(AIConversation, conversation_id)
        if conv:
            conv.title = title
            await db.commit()
        return conv

    @staticmethod
    async def soft_delete(db: AsyncSession, conversation_id: int) -> bool:
        conv = await db.get(AIConversation, conversation_id)
        if conv:
            conv.is_active = False
            await db.commit()
            return True
        return False


# ---------------------------------------------------------------------------
# Message CRUD
# ---------------------------------------------------------------------------
class AIMessageCRUD:
    """CRUD operations for AI messages."""

    @staticmethod
    async def list_by_conversation(
        db: AsyncSession,
        conversation_id: int,
        limit: int = 100,
    ) -> list[AIMessage]:
        result = await db.execute(
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession,
        conversation_id: int,
        role: MessageRole,
        content: str,
        model: Optional[str] = None,
        tokens_used: int = 0,
        cost: Decimal = Decimal("0"),
        duration_ms: Optional[int] = None,
    ) -> AIMessage:
        msg = AIMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            tokens_used=tokens_used,
            cost=cost,
            duration_ms=duration_ms,
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg


# ---------------------------------------------------------------------------
# Prompt CRUD
# ---------------------------------------------------------------------------
class AIPromptCRUD:
    """CRUD operations for AI prompts."""

    @staticmethod
    async def get(db: AsyncSession, prompt_id: int) -> Optional[AIPrompt]:
        return await db.get(AIPrompt, prompt_id)

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[AIPrompt]:
        result = await db.execute(select(AIPrompt).where(AIPrompt.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_active(
        db: AsyncSession, module: Optional[str] = None
    ) -> list[AIPrompt]:
        q = select(AIPrompt).where(AIPrompt.is_active == True).order_by(AIPrompt.name)
        if module:
            q = q.where(AIPrompt.module == module)
        result = await db.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        system_prompt: str,
        user_prompt_template: str,
        description: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: Decimal = Decimal("0.7"),
        max_tokens: int = 2000,
        module: Optional[str] = None,
        created_by_id: Optional[int] = None,
    ) -> AIPrompt:
        prompt = AIPrompt(
            name=name,
            description=description,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            module=module,
            created_by_id=created_by_id,
        )
        db.add(prompt)
        await db.commit()
        await db.refresh(prompt)
        return prompt

    @staticmethod
    async def update(db: AsyncSession, prompt_id: int, **kwargs) -> Optional[AIPrompt]:
        prompt = await db.get(AIPrompt, prompt_id)
        if prompt:
            for key, value in kwargs.items():
                if hasattr(prompt, key):
                    setattr(prompt, key, value)
            await db.commit()
        return prompt


# ---------------------------------------------------------------------------
# Workflow CRUD
# ---------------------------------------------------------------------------
class AIWorkflowCRUD:
    """CRUD operations for AI workflows."""

    @staticmethod
    async def get(db: AsyncSession, workflow_id: int) -> Optional[AIWorkflow]:
        return await db.get(AIWorkflow, workflow_id)

    @staticmethod
    async def list_active(
        db: AsyncSession, trigger_module: Optional[str] = None
    ) -> list[AIWorkflow]:
        q = select(AIWorkflow).where(AIWorkflow.is_active == True)
        if trigger_module:
            q = q.where(AIWorkflow.trigger_module == trigger_module)
        result = await db.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        trigger_module: str,
        trigger_event: str,
        action_type: str,
        action_config: dict,
        description: Optional[str] = None,
        condition: Optional[dict] = None,
        ai_prompt_id: Optional[int] = None,
        created_by_id: Optional[int] = None,
    ) -> AIWorkflow:
        workflow = AIWorkflow(
            name=name,
            description=description,
            trigger_module=trigger_module,
            trigger_event=trigger_event,
            action_type=action_type,
            action_config=action_config,
            condition=condition,
            ai_prompt_id=ai_prompt_id,
            created_by_id=created_by_id,
        )
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        return workflow

    @staticmethod
    async def trigger(db: AsyncSession, workflow_id: int, success: bool = True) -> Optional[AIWorkflow]:
        workflow = await db.get(AIWorkflow, workflow_id)
        if workflow:
            workflow.last_triggered_at = datetime.utcnow()
            workflow.trigger_count += 1
            if success:
                workflow.success_count += 1
            else:
                workflow.failure_count += 1
            await db.commit()
        return workflow


# ---------------------------------------------------------------------------
# Insight CRUD
# ---------------------------------------------------------------------------
class AIInsightCRUD:
    """CRUD operations for AI insights."""

    @staticmethod
    async def get(db: AsyncSession, insight_id: int) -> Optional[AIInsight]:
        return await db.get(AIInsight, insight_id)

    @staticmethod
    async def list_for_user(
        db: AsyncSession,
        user_id: int,
        module: Optional[str] = None,
        unread_only: bool = False,
        offset: int = 0,
        limit: int = 20,
    ) -> list[AIInsight]:
        q = (
            select(AIInsight)
            .where(AIInsight.user_id == user_id, AIInsight.is_dismissed == False)
            .order_by(AIInsight.created_at.desc())
        )
        if module:
            q = q.where(AIInsight.module == module)
        if unread_only:
            q = q.where(AIInsight.is_read == False)
        result = await db.execute(q.offset(offset).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: Optional[int],
        insight_type: InsightType,
        module: str,
        title: str,
        description: str,
        severity: InsightSeverity = InsightSeverity.INFO,
        data: Optional[dict] = None,
        confidence: Optional[float] = None,
    ) -> AIInsight:
        insight = AIInsight(
            user_id=user_id,
            insight_type=insight_type,
            module=module,
            title=title,
            description=description,
            severity=severity,
            data=data,
            confidence=confidence,
        )
        db.add(insight)
        await db.commit()
        await db.refresh(insight)
        return insight

    @staticmethod
    async def mark_read(db: AsyncSession, insight_id: int) -> Optional[AIInsight]:
        insight = await db.get(AIInsight, insight_id)
        if insight:
            insight.is_read = True
            insight.read_at = datetime.utcnow()
            await db.commit()
        return insight

    @staticmethod
    async def dismiss(db: AsyncSession, insight_id: int) -> Optional[AIInsight]:
        insight = await db.get(AIInsight, insight_id)
        if insight:
            insight.is_dismissed = True
            await db.commit()
        return insight

    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: int) -> int:
        result = await db.execute(
            select(func.count(AIInsight.id)).where(
                AIInsight.user_id == user_id,
                AIInsight.is_read == False,
                AIInsight.is_dismissed == False,
            )
        )
        return result.scalar() or 0


# ---------------------------------------------------------------------------
# Usage CRUD
# ---------------------------------------------------------------------------
class AIUsageCRUD:
    """CRUD operations for AI usage logs."""

    @staticmethod
    async def get_stats(
        db: AsyncSession,
        user_id: Optional[int] = None,
        days: int = 30,
    ) -> dict:
        since = datetime.utcnow() - timedelta(days=days)
        q = select(
            func.count(AIUsageLog.id).label("total_requests"),
            func.sum(AIUsageLog.total_tokens).label("total_tokens"),
            func.sum(AIUsageLog.cost).label("total_cost"),
            func.avg(AIUsageLog.duration_ms).label("avg_duration_ms"),
        ).where(AIUsageLog.created_at >= since)

        if user_id:
            q = q.where(AIUsageLog.user_id == user_id)

        result = await db.execute(q)
        row = result.one()

        return {
            "period_days": days,
            "total_requests": row.total_requests or 0,
            "total_tokens": row.total_tokens or 0,
            "total_cost": float(row.total_cost or 0),
            "avg_duration_ms": float(row.avg_duration_ms or 0),
        }


# ---------------------------------------------------------------------------
# Singleton instances
# ---------------------------------------------------------------------------
ai_conversation_crud = AIConversationCRUD()
ai_message_crud = AIMessageCRUD()
ai_prompt_crud = AIPromptCRUD()
ai_workflow_crud = AIWorkflowCRUD()
ai_insight_crud = AIInsightCRUD()
ai_usage_crud = AIUsageCRUD()
