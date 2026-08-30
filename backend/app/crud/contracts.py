"""
Contracts Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contracts import Contract, ContractHistory, ContractStatus


class ContractCRUD:
    async def get(self, db: AsyncSession, contract_id: int) -> Optional[Contract]:
        result = await db.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        contract_type: Optional[str] = None,
        status: Optional[ContractStatus] = None,
        expiring_soon: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[Contract]]:
        q = select(Contract).order_by(Contract.created_at.desc())
        if contract_type:
            q = q.where(Contract.contract_type == contract_type)
        if status:
            q = q.where(Contract.status == status)
        if expiring_soon:
            threshold = date.today() + timedelta(days=30)
            q = q.where(Contract.end_date <= threshold, Contract.status == ContractStatus.ACTIVE)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def stats(self, db: AsyncSession) -> dict:
        threshold = date.today() + timedelta(days=30)
        status_counts = (await db.execute(
            select(Contract.status, func.count(Contract.id).label("cnt"))
            .group_by(Contract.status)
        )).all()
        by_status = {row.status.value: row.cnt for row in status_counts}

        type_counts = (await db.execute(
            select(Contract.contract_type, func.count(Contract.id).label("cnt"))
            .group_by(Contract.contract_type)
        )).all()
        by_type = {row.contract_type.value: row.cnt for row in type_counts}

        expiring = (await db.execute(
            select(func.count(Contract.id)).where(
                Contract.status == ContractStatus.ACTIVE,
                Contract.end_date <= threshold,
            )
        )).scalar() or 0

        return {
            "total": sum(by_status.values()),
            "active": by_status.get("active", 0),
            "pending_approval": by_status.get("pending_approval", 0),
            "expiring_soon": expiring,
            "by_type": by_type,
        }


class ContractHistoryCRUD:
    async def log(
        self,
        db: AsyncSession,
        contract_id: int,
        action: str,
        old_status: Optional[str] = None,
        new_status: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> ContractHistory:
        entry = ContractHistory(
            contract_id=contract_id,
            action=action,
            old_status=old_status,
            new_status=new_status,
            notes=notes,
            performed_by_id=user_id,
        )
        db.add(entry)
        return entry


# Singletons
contract_crud = ContractCRUD()
contract_history_crud = ContractHistoryCRUD()
