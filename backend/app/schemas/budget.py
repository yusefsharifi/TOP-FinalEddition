"""
Budget Module — Pydantic Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.budget import BudgetType, BudgetStatus, BudgetPeriod


# ── Budget Schemas ───────────────────────────────────────────────────────────

class BudgetCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=300)
    description: Optional[str] = None
    type: BudgetType
    period: BudgetPeriod
    fiscal_year: str = Field(..., max_length=10)
    start_date: date
    end_date: date


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[BudgetType] = None
    period: Optional[BudgetPeriod] = None
    fiscal_year: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class BudgetResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    type: BudgetType
    period: BudgetPeriod
    fiscal_year: str
    start_date: date
    end_date: date
    status: BudgetStatus
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Budget Line Schemas ──────────────────────────────────────────────────────

class BudgetLineCreate(BaseModel):
    account_id: int
    amount: Decimal
    description: Optional[str] = None


class BudgetLineUpdate(BaseModel):
    account_id: Optional[int] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None


class BudgetLineResponse(BaseModel):
    id: int
    budget_id: int
    account_id: int
    amount: Decimal
    description: Optional[str] = None
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Budget Revision Schemas ──────────────────────────────────────────────────

class BudgetRevisionCreate(BaseModel):
    description: str


class BudgetRevisionResponse(BaseModel):
    id: int
    budget_id: int
    revision_number: int
    description: str
    status: BudgetStatus
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Budget Performance Schemas ───────────────────────────────────────────────

class BudgetPerformanceResponse(BaseModel):
    id: int
    budget_id: int
    account_id: int
    period: str
    budget_amount: Decimal
    actual_amount: Decimal
    variance_amount: Decimal
    variance_percentage: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard ────────────────────────────────────────────────────────────────

class BudgetDashboardResponse(BaseModel):
    total_budgets: int
    active_budgets: int
    draft_budgets: int
    total_budget_amount: Decimal
    total_actual_amount: Decimal
    budgets_by_status: dict
    budgets_by_type: dict
    recent_budgets: list[BudgetResponse]
