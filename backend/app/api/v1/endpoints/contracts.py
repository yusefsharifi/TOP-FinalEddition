"""
Contracts Module — FastAPI Router
TOP WorX ERP System

Contract lifecycle management with approval workflow and renewal tracking.
Uses SQLAlchemy models from app.models.contracts.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBDep, CurrentUser
from app.core.cache import cache
from app.models.contracts import (
    Contract, ContractHistory,
    ContractStatus, ContractType,
)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class ContractCreate(BaseModel):
    title: str
    description: Optional[str] = None
    contract_type: ContractType
    counterparty_name: str
    counterparty_contact: Optional[str] = None
    start_date: date
    end_date: date
    value: Optional[float] = None
    currency: str = "IRR"
    terms: Optional[str] = None
    auto_renew: bool = False
    renewal_days_notice: int = 30


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_contact: Optional[str] = None
    end_date: Optional[date] = None
    value: Optional[float] = None
    terms: Optional[str] = None
    auto_renew: Optional[bool] = None
    renewal_days_notice: Optional[int] = None


class ContractResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    contract_type: ContractType
    status: ContractStatus
    counterparty_name: str
    counterparty_contact: Optional[str] = None
    start_date: date
    end_date: date
    value: Optional[float] = None
    currency: str
    terms: Optional[str] = None
    auto_renew: bool
    renewal_days_notice: int
    created_by_id: int
    approved_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _log_contract_history(
    db: AsyncSession, contract_id: int, action: str,
    old_status: str = None, new_status: str = None,
    notes: str = None, user_id: int = None,
):
    entry = ContractHistory(
        contract_id=contract_id,
        action=action,
        old_status=old_status,
        new_status=new_status,
        notes=notes,
        performed_by_id=user_id,
    )
    db.add(entry)


# ── CONTRACTS CRUD ───────────────────────────────────────────────────────────

@router.get("", response_model=list[ContractResponse])
async def list_contracts(
    db: DBDep,
    current_user: CurrentUser,
    contract_type: Optional[ContractType] = None,
    contract_status: Optional[ContractStatus] = Query(None, alias="status"),
    expiring_soon: bool = False,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[ContractResponse]:
    """List contracts with optional filtering."""
    q = select(Contract).order_by(Contract.created_at.desc())
    if contract_type:
        q = q.where(Contract.contract_type == contract_type)
    if contract_status:
        q = q.where(Contract.status == contract_status)
    if expiring_soon:
        threshold = date.today() + timedelta(days=30)
        q = q.where(Contract.end_date <= threshold, Contract.status == ContractStatus.ACTIVE)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [ContractResponse.model_validate(r) for r in rows]


@router.post("", response_model=ContractResponse, status_code=201)
async def create_contract(
    data: ContractCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> ContractResponse:
    """Create a new contract."""
    contract = Contract(
        title=data.title,
        description=data.description,
        contract_type=data.contract_type,
        status=ContractStatus.DRAFT,
        counterparty_name=data.counterparty_name,
        counterparty_contact=data.counterparty_contact,
        start_date=data.start_date,
        end_date=data.end_date,
        value=data.value,
        currency=data.currency,
        terms=data.terms,
        auto_renew=data.auto_renew,
        renewal_days_notice=data.renewal_days_notice,
        created_by_id=current_user.id,
    )
    db.add(contract)
    await db.flush()
    await _log_contract_history(db, contract.id, "created", new_status="draft", user_id=current_user.id)
    await db.commit()
    await db.refresh(contract)
    return ContractResponse.model_validate(contract)


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> ContractResponse:
    """Get contract details."""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    return ContractResponse.model_validate(contract)


@router.patch("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    data: ContractUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> ContractResponse:
    """Update contract fields (only DRAFT contracts)."""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    if contract.status != ContractStatus.DRAFT:
        raise HTTPException(409, "Only DRAFT contracts can be edited")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)
    await db.commit()
    await db.refresh(contract)
    return ContractResponse.model_validate(contract)


# ── WORKFLOW ACTIONS ─────────────────────────────────────────────────────────

@router.post("/{contract_id}/submit", response_model=ContractResponse)
async def submit_for_approval(
    contract_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> ContractResponse:
    """Submit contract for approval (DRAFT → PENDING_APPROVAL)."""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    if contract.status != ContractStatus.DRAFT:
        raise HTTPException(409, f"Cannot submit a {contract.status.value} contract")

    old = contract.status.value
    contract.status = ContractStatus.PENDING_APPROVAL
    await _log_contract_history(db, contract.id, "submitted", old_status=old, new_status="pending_approval", user_id=current_user.id)
    await db.commit()
    await db.refresh(contract)
    return ContractResponse.model_validate(contract)


@router.post("/{contract_id}/approve", response_model=ContractResponse)
async def approve_contract(
    contract_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> ContractResponse:
    """Approve a contract (PENDING_APPROVAL → APPROVED)."""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    if contract.status != ContractStatus.PENDING_APPROVAL:
        raise HTTPException(409, "Contract is not pending approval")

    old = contract.status.value
    contract.status = ContractStatus.APPROVED
    contract.approved_by_id = current_user.id
    contract.approved_at = datetime.utcnow()
    await _log_contract_history(db, contract.id, "approved", old_status=old, new_status="approved", user_id=current_user.id)
    await db.commit()
    await db.refresh(contract)
    return ContractResponse.model_validate(contract)


@router.post("/{contract_id}/activate", response_model=ContractResponse)
async def activate_contract(
    contract_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> ContractResponse:
    """Activate a contract (APPROVED → ACTIVE)."""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    if contract.status != ContractStatus.APPROVED:
        raise HTTPException(409, "Contract must be approved before activation")

    old = contract.status.value
    contract.status = ContractStatus.ACTIVE
    await _log_contract_history(db, contract.id, "activated", old_status=old, new_status="active", user_id=current_user.id)
    await db.commit()
    await db.refresh(contract)
    return ContractResponse.model_validate(contract)


@router.post("/{contract_id}/terminate", response_model=ContractResponse)
async def terminate_contract(
    contract_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> ContractResponse:
    """Terminate an active contract."""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    if contract.status != ContractStatus.ACTIVE:
        raise HTTPException(409, "Only ACTIVE contracts can be terminated")

    old = contract.status.value
    contract.status = ContractStatus.TERMINATED
    await _log_contract_history(db, contract.id, "terminated", old_status=old, new_status="terminated", user_id=current_user.id)
    await db.commit()
    await db.refresh(contract)
    return ContractResponse.model_validate(contract)


@router.post("/{contract_id}/renew", response_model=ContractResponse)
async def renew_contract(
    contract_id: int,
    db: DBDep,
    current_user: CurrentUser,
    new_end_date: date = Query(..., description="New end date for renewed contract"),
) -> ContractResponse:
    """Renew a contract (extends end date, creates new active contract)."""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    if contract.status not in (ContractStatus.ACTIVE, ContractStatus.EXPIRED):
        raise HTTPException(409, "Only ACTIVE or EXPIRED contracts can be renewed")
    if new_end_date <= contract.end_date:
        raise HTTPException(400, "New end date must be after current end date")

    old = contract.status.value
    contract.status = ContractStatus.RENEWED
    await _log_contract_history(db, contract.id, "renewed", old_status=old, new_status="renewed", user_id=current_user.id)

    # Create new active contract
    new_contract = Contract(
        title=contract.title,
        description=contract.description,
        contract_type=contract.contract_type,
        status=ContractStatus.ACTIVE,
        counterparty_name=contract.counterparty_name,
        counterparty_contact=contract.counterparty_contact,
        start_date=contract.start_date,
        end_date=new_end_date,
        value=contract.value,
        currency=contract.currency,
        terms=contract.terms,
        auto_renew=contract.auto_renew,
        renewal_days_notice=contract.renewal_days_notice,
        created_by_id=current_user.id,
        approved_by_id=current_user.id,
        approved_at=datetime.utcnow(),
    )
    db.add(new_contract)
    await db.flush()
    await _log_contract_history(db, new_contract.id, "created", new_status="active", notes="Renewed from contract " + str(contract_id), user_id=current_user.id)
    await db.commit()
    await db.refresh(new_contract)
    return ContractResponse.model_validate(new_contract)


# ── DASHBOARD ────────────────────────────────────────────────────────────────

@router.get("/dashboard/stats")
async def contract_stats(
    db: DBDep,
    current_user: CurrentUser,
) -> dict:
    """Contract dashboard statistics (cached for 2 min)."""
    cache_key = "contracts:dashboard:stats"
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    # Consolidated queries: 3 instead of 10
    threshold = date.today() + timedelta(days=30)

    # Single query for all status counts (was 3 separate queries)
    status_counts = (await db.execute(
        select(Contract.status, func.count(Contract.id).label("cnt"))
        .group_by(Contract.status)
    )).all()
    by_status = {row.status.value: row.cnt for row in status_counts}

    # Single query for type counts (was 7 separate queries)
    type_counts = (await db.execute(
        select(Contract.contract_type, func.count(Contract.id).label("cnt"))
        .group_by(Contract.contract_type)
    )).all()
    by_type = {row.contract_type.value: row.cnt for row in type_counts}

    # Expiring soon count
    expiring = (await db.execute(
        select(func.count(Contract.id)).where(
            Contract.status == ContractStatus.ACTIVE,
            Contract.end_date <= threshold,
        )
    )).scalar() or 0

    result = {
        "total": sum(by_status.values()),
        "active": by_status.get("active", 0),
        "pending_approval": by_status.get("pending_approval", 0),
        "expiring_soon": expiring,
        "by_type": by_type,
    }
    await cache.set(cache_key, result, ttl=120)  # 2 min cache
    return result
