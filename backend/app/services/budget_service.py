"""
Budget Module — Service Layer
TOP WorX ERP System

Business logic for budget management.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import (
    Budget, BudgetLine, BudgetRevision, BudgetPerformance,
    BudgetType, BudgetStatus, BudgetPeriod,
)


class BudgetError(Exception):
    """Budget business logic error."""
    pass


class BudgetService:
    async def create_budget(
        self,
        db: AsyncSession,
        *,
        code: str,
        name: str,
        description: Optional[str] = None,
        type: BudgetType,
        period: BudgetPeriod,
        fiscal_year: str,
        start_date: date,
        end_date: date,
        user_id: int,
    ) -> Budget:
        """Create a new budget with validation."""
        # Check code uniqueness
        existing = await db.execute(select(Budget).where(Budget.code == code))
        if existing.scalar_one_or_none():
            raise BudgetError(f"Budget code '{code}' already exists")
        
        # Validate dates
        if end_date <= start_date:
            raise BudgetError("End date must be after start date")
        
        # Validate period matches dates
        if period == BudgetPeriod.MONTHLY:
            if start_date.month != end_date.month or start_date.year != end_date.year:
                raise BudgetError("Monthly budget must be within a single month")
        elif period == BudgetPeriod.QUARTERLY:
            quarter_start_month = (start_date.month - 1) // 3 * 3 + 1
            quarter_end_month = quarter_start_month + 2
            if not (start_date.month == quarter_start_month and end_date.month == quarter_end_month):
                raise BudgetError("Quarterly budget dates must align with calendar quarters")
        
        budget = Budget(
            code=code,
            name=name,
            description=description,
            type=type,
            period=period,
            fiscal_year=fiscal_year,
            start_date=start_date,
            end_date=end_date,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(budget)
        await db.flush()
        await db.refresh(budget)
        return budget

    async def submit_budget(
        self,
        db: AsyncSession,
        budget_id: int,
        *,
        user_id: int,
    ) -> Budget:
        """Submit budget for approval."""
        budget = await db.get(Budget, budget_id)
        if not budget:
            raise BudgetError("Budget not found")
        
        if budget.status != BudgetStatus.DRAFT:
            raise BudgetError("Only DRAFT budgets can be submitted")
        
        # Check if budget has at least one line
        line_count = (await db.execute(
            select(func.count(BudgetLine.id)).where(BudgetLine.budget_id == budget_id)
        )).scalar() or 0
        
        if line_count == 0:
            raise BudgetError("Budget must have at least one line item before submission")
        
        budget.status = BudgetStatus.PENDING
        budget.updated_by_id = user_id
        await db.flush()
        await db.refresh(budget)
        return budget

    async def approve_budget(
        self,
        db: AsyncSession,
        budget_id: int,
        *,
        approver_id: int,
    ) -> Budget:
        """Approve a budget."""
        budget = await db.get(Budget, budget_id)
        if not budget:
            raise BudgetError("Budget not found")
        
        if budget.status != BudgetStatus.PENDING:
            raise BudgetError("Budget is not pending approval")
        
        budget.status = BudgetStatus.APPROVED
        budget.approved_by_id = approver_id
        budget.approved_at = datetime.utcnow()
        budget.updated_by_id = approver_id
        await db.flush()
        await db.refresh(budget)
        return budget

    async def activate_budget(
        self,
        db: AsyncSession,
        budget_id: int,
        *,
        user_id: int,
    ) -> Budget:
        """Activate a budget."""
        budget = await db.get(Budget, budget_id)
        if not budget:
            raise BudgetError("Budget not found")
        
        if budget.status != BudgetStatus.APPROVED:
            raise BudgetError("Budget must be APPROVED before activation")
        
        # Check if we're within the budget period
        today = date.today()
        if today < budget.start_date:
            raise BudgetError("Cannot activate budget before start date")
        
        budget.status = BudgetStatus.ACTIVE
        budget.updated_by_id = user_id
        await db.flush()
        await db.refresh(budget)
        return budget

    async def close_budget(
        self,
        db: AsyncSession,
        budget_id: int,
        *,
        user_id: int,
    ) -> Budget:
        """Close a budget."""
        budget = await db.get(Budget, budget_id)
        if not budget:
            raise BudgetError("Budget not found")
        
        if budget.status != BudgetStatus.ACTIVE:
            raise BudgetError("Only ACTIVE budgets can be closed")
        
        budget.status = BudgetStatus.CLOSED
        budget.updated_by_id = user_id
        await db.flush()
        await db.refresh(budget)
        return budget

    async def create_revision(
        self,
        db: AsyncSession,
        budget_id: int,
        *,
        description: str,
        user_id: int,
    ) -> BudgetRevision:
        """Create a budget revision."""
        budget = await db.get(Budget, budget_id)
        if not budget:
            raise BudgetError("Budget not found")
        
        # Get next revision number
        result = await db.execute(
            select(func.coalesce(func.max(BudgetRevision.revision_number), 0))
            .where(BudgetRevision.budget_id == budget_id)
        )
        next_number = result.scalar() + 1
        
        revision = BudgetRevision(
            budget_id=budget_id,
            revision_number=next_number,
            description=description,
            status=BudgetStatus.DRAFT,
            created_by_id=user_id,
        )
        db.add(revision)
        await db.flush()
        await db.refresh(revision)
        return revision

    async def get_budget_summary(
        self,
        db: AsyncSession,
        budget_id: int,
    ) -> dict:
        """Get budget summary with totals."""
        budget = await db.get(Budget, budget_id)
        if not budget:
            raise BudgetError("Budget not found")
        
        # Get line totals
        line_totals = (await db.execute(
            select(func.coalesce(func.sum(BudgetLine.amount), Decimal("0")))
            .where(BudgetLine.budget_id == budget_id)
        )).scalar()
        
        # Get line count
        line_count = (await db.execute(
            select(func.count(BudgetLine.id)).where(BudgetLine.budget_id == budget_id)
        )).scalar() or 0
        
        # Get revision count
        revision_count = (await db.execute(
            select(func.count(BudgetRevision.id)).where(BudgetRevision.budget_id == budget_id)
        )).scalar() or 0
        
        return {
            "id": budget.id,
            "code": budget.code,
            "name": budget.name,
            "type": budget.type.value,
            "period": budget.period.value,
            "fiscal_year": budget.fiscal_year,
            "status": budget.status.value,
            "total_amount": float(line_totals),
            "line_count": line_count,
            "revision_count": revision_count,
            "start_date": budget.start_date.isoformat(),
            "end_date": budget.end_date.isoformat(),
        }


budget_service = BudgetService()
