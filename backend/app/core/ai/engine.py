"""
AI Engine — Central Orchestrator
TOP WorX ERP System

Provides:
  - LLM provider management (OpenAI, Anthropic)
  - Token usage tracking
  - Cost monitoring
  - Rate limiting
  - Conversation management
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai_core import (
    AIConversation,
    AIMessage,
    AIUsageLog,
    MessageRole,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Token pricing (per 1K tokens)
# ---------------------------------------------------------------------------
MODEL_PRICING = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "text-embedding-3-large": {"input": 0.00013, "output": 0},
    "text-embedding-3-small": {"input": 0.00002, "output": 0},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Decimal:
    """Calculate cost in USD for given token usage."""
    pricing = MODEL_PRICING.get(model, {"input": 0.01, "output": 0.03})
    cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000
    return Decimal(str(round(cost, 6)))


# ---------------------------------------------------------------------------
# AI Engine
# ---------------------------------------------------------------------------
class AIEngine:
    """
    Central AI orchestrator for TOP WorX ERP.
    
    Usage:
        engine = AIEngine(db)
        response = await engine.chat("What are our top selling products?")
        await engine.log_usage(user_id=1, endpoint="/ai/chat", ...)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._openai_client = None
        self._anthropic_client = None

    async def _get_openai_client(self):
        """Lazy-load OpenAI client."""
        if self._openai_client is None:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            from openai import AsyncOpenAI
            self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai_client

    async def _get_anthropic_client(self):
        """Lazy-load Anthropic client."""
        if self._anthropic_client is None:
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            import anthropic
            self._anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self._anthropic_client

    # -----------------------------------------------------------------------
    # Chat
    # -----------------------------------------------------------------------
    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
    ) -> dict:
        """
        Send chat messages to LLM and return response.
        
        Returns:
            {
                "content": str,
                "model": str,
                "input_tokens": int,
                "output_tokens": int,
                "cost": float,
                "duration_ms": int,
                "conversation_id": int,
            }
        """
        model = model or settings.AI_MODEL
        temperature = temperature or settings.AI_TEMPERATURE
        max_tokens = max_tokens or settings.AI_MAX_TOKENS

        # Check rate limit
        await self._check_rate_limit(user_id)

        # Build messages list
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(messages)

        start_time = time.time()

        try:
            if model.startswith("claude"):
                response = await self._chat_anthropic(api_messages, model, temperature, max_tokens)
            else:
                response = await self._chat_openai(api_messages, model, temperature, max_tokens)

            duration_ms = int((time.time() - start_time) * 1000)

            # Calculate cost
            cost = calculate_cost(model, response["input_tokens"], response["output_tokens"])

            # Log usage
            await self._log_usage(
                user_id=user_id,
                conversation_id=conversation_id,
                endpoint="chat",
                model=model,
                input_tokens=response["input_tokens"],
                output_tokens=response["output_tokens"],
                cost=cost,
                duration_ms=duration_ms,
            )

            # Update conversation total tokens
            if conversation_id:
                conv = await self.db.get(AIConversation, conversation_id)
                if conv:
                    conv.total_tokens += response["input_tokens"] + response["output_tokens"]
                    conv.total_cost += cost
                    await self.db.commit()

            return {
                "content": response["content"],
                "model": model,
                "input_tokens": response["input_tokens"],
                "output_tokens": response["output_tokens"],
                "cost": float(cost),
                "duration_ms": duration_ms,
                "conversation_id": conversation_id,
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"AI chat error: {e}")
            
            # Log failed usage
            await self._log_usage(
                user_id=user_id,
                conversation_id=conversation_id,
                endpoint="chat",
                model=model,
                input_tokens=0,
                output_tokens=0,
                cost=Decimal("0"),
                duration_ms=duration_ms,
                success=False,
                error_message=str(e),
            )
            raise

    async def _chat_openai(
        self, messages: list[dict], model: str, temperature: float, max_tokens: int
    ) -> dict:
        """Call OpenAI API."""
        client = await self._get_openai_client()
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "content": response.choices[0].message.content,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
        }

    async def _chat_anthropic(
        self, messages: list[dict], model: str, temperature: float, max_tokens: int
    ) -> dict:
        """Call Anthropic API."""
        client = await self._get_anthropic_client()
        
        # Separate system message
        system_content = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                user_messages.append(msg)
        
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_content if system_content else anthropic.NOT_GIVEN,
            messages=user_messages,
        )
        
        return {
            "content": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

    # -----------------------------------------------------------------------
    # Conversation Management
    # -----------------------------------------------------------------------
    async def create_conversation(
        self, user_id: int, title: str, module: Optional[str] = None, model: Optional[str] = None
    ) -> AIConversation:
        """Create a new AI conversation."""
        conv = AIConversation(
            user_id=user_id,
            title=title,
            module=module,
            model=model or settings.AI_MODEL,
        )
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def add_message(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
        model: Optional[str] = None,
        tokens_used: int = 0,
        cost: Decimal = Decimal("0"),
        duration_ms: Optional[int] = None,
    ) -> AIMessage:
        """Add a message to a conversation."""
        msg = AIMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            tokens_used=tokens_used,
            cost=cost,
            duration_ms=duration_ms,
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def get_conversation_history(
        self, conversation_id: int, limit: int = 50
    ) -> list[AIMessage]:
        """Get message history for a conversation."""
        result = await self.db.execute(
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # -----------------------------------------------------------------------
    # Rate Limiting
    # -----------------------------------------------------------------------
    async def _check_rate_limit(self, user_id: Optional[int]) -> None:
        """Check if user has exceeded rate limit."""
        if not user_id:
            return

        # Count requests in last minute
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        result = await self.db.execute(
            select(func.count(AIUsageLog.id)).where(
                AIUsageLog.user_id == user_id,
                AIUsageLog.created_at >= one_minute_ago,
                AIUsageLog.success == True,
            )
        )
        count = result.scalar() or 0

        if count >= settings.AI_RATE_LIMIT_PER_MINUTE:
            raise ValueError(
                f"Rate limit exceeded: {count} requests in last minute "
                f"(limit: {settings.AI_RATE_LIMIT_PER_MINUTE})"
            )

    # -----------------------------------------------------------------------
    # Usage Logging
    # -----------------------------------------------------------------------
    async def _log_usage(
        self,
        user_id: Optional[int],
        conversation_id: Optional[int],
        endpoint: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: Decimal,
        duration_ms: int,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AIUsageLog:
        """Log API usage."""
        log = AIUsageLog(
            user_id=user_id,
            conversation_id=conversation_id,
            endpoint=endpoint,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost=cost,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
        )
        self.db.add(log)
        await self.db.commit()
        return log

    # -----------------------------------------------------------------------
    # Usage Statistics
    # -----------------------------------------------------------------------
    async def get_usage_stats(
        self, user_id: Optional[int] = None, days: int = 30
    ) -> dict:
        """Get usage statistics."""
        since = datetime.utcnow() - timedelta(days=days)
        
        q = select(
            func.count(AIUsageLog.id).label("total_requests"),
            func.sum(AIUsageLog.total_tokens).label("total_tokens"),
            func.sum(AIUsageLog.cost).label("total_cost"),
            func.avg(AIUsageLog.duration_ms).label("avg_duration_ms"),
            func.sum(func.cast(AIUsageLog.success, Integer)).label("successful"),
        ).where(AIUsageLog.created_at >= since)

        if user_id:
            q = q.where(AIUsageLog.user_id == user_id)

        result = await self.db.execute(q)
        row = result.one()

        # Cost by model
        cost_by_model_q = select(
            AIUsageLog.model,
            func.count(AIUsageLog.id).label("requests"),
            func.sum(AIUsageLog.cost).label("cost"),
        ).where(AIUsageLog.created_at >= since).group_by(AIUsageLog.model)

        if user_id:
            cost_by_model_q = cost_by_model_q.where(AIUsageLog.user_id == user_id)

        cost_result = await self.db.execute(cost_by_model_q)
        cost_by_model = {r.model: {"requests": r.requests, "cost": float(r.cost or 0)} for r in cost_result.all()}

        return {
            "period_days": days,
            "total_requests": row.total_requests or 0,
            "total_tokens": row.total_tokens or 0,
            "total_cost": float(row.total_cost or 0),
            "avg_duration_ms": float(row.avg_duration_ms or 0),
            "success_rate": (row.successful or 0) / max(row.total_requests or 1, 1) * 100,
            "cost_by_model": cost_by_model,
        }


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------
def get_ai_engine(db: AsyncSession) -> AIEngine:
    """Get an AIEngine instance for the given database session."""
    return AIEngine(db)
