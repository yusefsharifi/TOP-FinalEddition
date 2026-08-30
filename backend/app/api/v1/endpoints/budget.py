"""
Budget Module — FastAPI Router
TOP WorX ERP System

INTEGRATION POINT: Register in api.py:
    from app.api.v1.endpoints.budget import router as budget_router
    api_router.include_router(budget_router, prefix="/budget", tags=["budget"])
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.deps import DBDep, CurrentUser
from app.core.cache import cache
from app.models.budget import (
    Budget, BudgetLine, BudgetRevision, BudgetPerformance,
    BudgetType, BudgetStatus, BudgetPeriod,
)
from app.models.finance import Account
from app.schemas.budget import (
    BudgetCreate, BudgetUpdate, BudgetResponse,
    BudgetLineCreate, BudgetLineUpdate, BudgetLineResponse,
    BudgetRevisionCreate, BudgetRevisionResponse,
    BudgetPerformanceResponse,
    BudgetDashboardResponse,
)

router = APIRouter()


# ── BUDGETS CRUD ─────────────────────────────────────────────────────────────

@router.get("", response_model=list[BudgetResponse])
async def list_budgets(
    db: DBDep,
    current_user: CurrentUser,
    budget_type: Optional[BudgetType] = Query(None, alias="type"),
    budget_status: Optional[BudgetStatus] = Query(None, alias="status"),
    fiscal_year: Optional[str] = None,
    search: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[BudgetResponse]:
    """List budgets with optional filtering."""
    q = select(Budget).order_by(Budget.created_at.desc())
    if budget_type:
        q = q.where(Budget.type == budget_type)
    if budget_status:
        q = q.where(Budget.status == budget_status)
    if fiscal_year:
        q = q.where(Budget.fiscal_year == fiscal_year)
    if search:
        term = f"%{search}%"
        q = q.where(
            (Budget.name.ilike(term)) | (Budget.code.ilike(term))
        )
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [BudgetResponse.model_validate(r) for r in rows]


@router.post("", response_model=BudgetResponse, status_code=201)
async def create_budget(
    data: BudgetCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetResponse:
    """Create a new budget."""
    # Check code uniqueness
    existing = await db.execute(select(Budget).where(Budget.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(409, f"Budget code '{data.code}' already exists")
    
    budget = Budget(
        **data.model_dump(),
        created_by_id=current_user.id,
        updated_by_id=current_user.id,
    )
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    return BudgetResponse.model_validate(budget)


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetResponse:
    """Get budget details."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    return BudgetResponse.model_validate(budget)


@router.patch("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetResponse:
    """Update budget fields (only DRAFT budgets)."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    if budget.status != BudgetStatus.DRAFT:
        raise HTTPException(409, "Only DRAFT budgets can be edited")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(budget, field, value)
    
    budget.updated_by_id = current_user.id
    await db.commit()
    await db.refresh(budget)
    return BudgetResponse.model_validate(budget)


@router.delete("/{budget_id}", status_code=204)
async def delete_budget(
    budget_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    """Delete a budget (only if DRAFT)."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    if budget.status != BudgetStatus.DRAFT:
        raise HTTPException(409, "Cannot delete a non-DRAFT budget")
    await db.delete(budget)
    await db.commit()


# ── BUDGET WORKFLOW ──────────────────────────────────────────────────────────

@router.post("/{budget_id}/submit", response_model=BudgetResponse)
async def submit_budget(
    budget_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetResponse:
    """Submit budget for approval (DRAFT → PENDING)."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    if budget.status != BudgetStatus.DRAFT:
        raise HTTPException(409, "Only DRAFT budgets can be submitted")
    
    budget.status = BudgetStatus.PENDING
    budget.updated_by_id = current_user.id
    await db.commit()
    await db.refresh(budget)
    return BudgetResponse.model_validate(budget)


@router.post("/{budget_id}/approve", response_model=BudgetResponse)
async def approve_budget(
    budget_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetResponse:
    """Approve a budget (PENDING → APPROVED)."""
    # TODO: require_role(current_user, ["admin", "cfo", "finance_manager"])
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    if budget.status != BudgetStatus.PENDING:
        raise HTTPException(409, "Budget is not pending approval")
    
    budget.status = BudgetStatus.APPROVED
    budget.approved_by_id = current_user.id
    budget.approved_at = datetime.utcnow()
    budget.updated_by_id = current_user.id
    await db.commit()
    await db.refresh(budget)
    return BudgetResponse.model_validate(budget)


@router.post("/{budget_id}/activate", response_model=BudgetResponse)
async def activate_budget(
    budget_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetResponse:
    """Activate a budget (APPROVED → ACTIVE)."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    if budget.status != BudgetStatus.APPROVED:
        raise HTTPException(409, "Budget must be APPROVED before activation")
    
    budget.status = BudgetStatus.ACTIVE
    budget.updated_by_id = current_user.id
    await db.commit()
    await db.refresh(budget)
    return BudgetResponse.model_validate(budget)


@router.post("/{budget_id}/close", response_model=BudgetResponse)
async def close_budget(
    budget_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetResponse:
    """Close a budget (ACTIVE → CLOSED)."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    if budget.status != BudgetStatus.ACTIVE:
        raise HTTPException(409, "Only ACTIVE budgets can be closed")
    
    budget.status = BudgetStatus.CLOSED
    budget.updated_by_id = current_user.id
    await db.commit()
    await db.refresh(budget)
    return BudgetResponse.model_validate(budget)


# ── BUDGET LINES ─────────────────────────────────────────────────────────────

@router.get("/{budget_id}/lines", response_model=list[BudgetLineResponse])
async def list_budget_lines(
    budget_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> list[BudgetLineResponse]:
    """List budget line items."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    
    q = select(BudgetLine).where(BudgetLine.budget_id == budget_id).order_by(BudgetLine.id)
    rows = (await db.execute(q)).scalars().all()
    return [BudgetLineResponse.model_validate(r) for r in rows]


@router.post("/{budget_id}/lines", response_model=BudgetLineResponse, status_code=201)
async def create_budget_line(
    budget_id: int,
    data: BudgetLineCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetLineResponse:
    """Add a line item to a budget."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    if budget.status not in (BudgetStatus.DRAFT, BudgetStatus.PENDING):
        raise HTTPException(409, "Cannot add lines to a non-editable budget")
    
    # Verify account exists
    account = await db.get(Account, data.account_id)
    if not account:
        raise HTTPException(404, "Account not found")
    
    line = BudgetLine(
        budget_id=budget_id,
        **data.model_dump(),
        created_by_id=current_user.id,
    )
    db.add(line)
    await db.commit()
    await db.refresh(line)
    return BudgetLineResponse.model_validate(line)


@router.patch("/{budget_id}/lines/{line_id}", response_model=BudgetLineResponse)
async def update_budget_line(
    budget_id: int,
    line_id: int,
    data: BudgetLineUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetLineResponse:
    """Update a budget line item."""
    line = await db.get(BudgetLine, line_id)
    if not line or line.budget_id != budget_id:
        raise HTTPException(404, "Line not found")
    
    budget = await db.get(Budget, budget_id)
    if budget.status not in (BudgetStatus.DRAFT, BudgetStatus.PENDING):
        raise HTTPException(409, "Cannot update lines in a non-editable budget")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(line, field, value)
    
    await db.commit()
    await db.refresh(line)
    return BudgetLineResponse.model_validate(line)


@router.delete("/{budget_id}/lines/{line_id}", status_code=204)
async def delete_budget_line(
    budget_id: int,
    line_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    """Delete a budget line item."""
    line = await db.get(BudgetLine, line_id)
    if not line or line.budget_id != budget_id:
        raise HTTPException(404, "Line not found")
    
    budget = await db.get(Budget, budget_id)
    if budget.status not in (BudgetStatus.DRAFT, BudgetStatus.PENDING):
        raise HTTPException(409, "Cannot delete lines from a non-editable budget")
    
    await db.delete(line)
    await db.commit()


# ── REVISIONS ────────────────────────────────────────────────────────────────

@router.get("/{budget_id}/revisions", response_model=list[BudgetRevisionResponse])
async def list_revisions(
    budget_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> list[BudgetRevisionResponse]:
    """List budget revisions."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    
    q = select(BudgetRevision).where(
        BudgetRevision.budget_id == budget_id
    ).order_by(BudgetRevision.revision_number.desc())
    rows = (await db.execute(q)).scalars().all()
    return [BudgetRevisionResponse.model_validate(r) for r in rows]


@router.post("/{budget_id}/revisions", response_model=BudgetRevisionResponse, status_code=201)
async def create_revision(
    budget_id: int,
    data: BudgetRevisionCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> BudgetRevisionResponse:
    """Create a budget revision."""
    budget = await db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(404, "Budget not found")
    
    # Get next revision number
    result = await db.execute(
        select(func.coalesce(func.max(BudgetRevision.revision_number), 0))
        .where(BudgetRevision.budget_id == budget_id)
    )
    next_number = result.scalar() + 1
    
    revision = BudgetRevision(
        budget_id=budget_id,
        revision_number=next_number,
        description=data.description,
        status=BudgetStatus.DRAFT,
        created_by_id=current_user.id,
    )
    db.add(revision)
    await db.commit()
    await db.refresh(revision)
    return BudgetRevisionResponse.model_validate(revision)


# ── DASHBOARD ────────────────────────────────────────────────────────────────

@router.get("/dashboard/stats")
async def budget_stats(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Budget dashboard statistics (cached for 2 min)."""
    cache_key = "budget:dashboard:stats"
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Consolidated queries
    total = (await db.execute(select(func.count(Budget.id)))).scalar() or 0
    
    # Status counts
    status_counts = (await db.execute(
        select(Budget.status, func.count(Budget.id).label("cnt"))
        .group_by(Budget.status)
    )).all()
    by_status = {row.status.value: row.cnt for row in status_counts}
    
    # Type counts
    type_counts = (await db.execute(
        select(Budget.type, func.count(Budget.id).label("cnt"))
        .group_by(Budget.type)
    )).all()
    by_type = {row.type.value: row.cnt for row in type_counts}
    
    # Recent budgets
    recent_q = select(Budget).order_by(Budget.created_at.desc()).limit(5)
    recent_rows = (await db.execute(recent_q)).scalars().all()
    
    result = {
        "total_budgets": total,
        "active_budgets": by_status.get("active", 0),
        "draft_budgets": by_status.get("draft", 0),
        "total_budget_amount": 0,  # Would need to sum lines
        "total_actual_amount": 0,  # Would need performance data
        "budgets_by_status": by_status,
        "budgets_by_type": by_type,
        "recent_budgets": [BudgetResponse.model_validate(b).model_dump() for b in recent_rows],
    }
    await cache.set(cache_key, result, ttl=120)  # 2 min cache
    return result
