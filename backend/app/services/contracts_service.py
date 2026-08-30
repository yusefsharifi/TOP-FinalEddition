"""
Contracts Module — Service Layer
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.contracts import contract_history_crud
from app.models.contracts import Contract, ContractStatus


class ContractsError(Exception):
    """Contracts business logic error."""
    pass


class ContractsService:
    async def submit_for_approval(
        self, db: AsyncSession, contract: Contract, *, user_id: int
    ) -> Contract:
        if contract.status != ContractStatus.DRAFT:
            raise ContractsError(f"Cannot submit a {contract.status.value} contract")
        old = contract.status.value
        contract.status = ContractStatus.PENDING_APPROVAL
        await contract_history_crud.log(
            db, contract.id, "submitted", old_status=old,
            new_status="pending_approval", user_id=user_id,
        )
        await db.flush()
        return contract

    async def approve(
        self, db: AsyncSession, contract: Contract, *, user_id: int
    ) -> Contract:
        if contract.status != ContractStatus.PENDING_APPROVAL:
            raise ContractsError("Contract is not pending approval")
        old = contract.status.value
        contract.status = ContractStatus.APPROVED
        contract.approved_by_id = user_id
        contract.approved_at = datetime.utcnow()
        await contract_history_crud.log(
            db, contract.id, "approved", old_status=old,
            new_status="approved", user_id=user_id,
        )
        await db.flush()
        return contract

    async def activate(
        self, db: AsyncSession, contract: Contract, *, user_id: int
    ) -> Contract:
        if contract.status != ContractStatus.APPROVED:
            raise ContractsError("Contract must be approved before activation")
        old = contract.status.value
        contract.status = ContractStatus.ACTIVE
        await contract_history_crud.log(
            db, contract.id, "activated", old_status=old,
            new_status="active", user_id=user_id,
        )
        await db.flush()
        return contract

    async def terminate(
        self, db: AsyncSession, contract: Contract, *, user_id: int
    ) -> Contract:
        if contract.status != ContractStatus.ACTIVE:
            raise ContractsError("Only ACTIVE contracts can be terminated")
        old = contract.status.value
        contract.status = ContractStatus.TERMINATED
        await contract_history_crud.log(
            db, contract.id, "terminated", old_status=old,
            new_status="terminated", user_id=user_id,
        )
        await db.flush()
        return contract


contracts_service = ContractsService()
