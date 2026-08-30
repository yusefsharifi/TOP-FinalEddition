# backend/app/crud/finance.py

"""
Finance Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

import random
import string
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.finance import (
    Account, AccountType, FiscalPeriod, FiscalPeriodStatus,
    JournalEntry, JournalEntryLine, JournalEntryStatus, ReferenceType,
)
from app.schemas.finance import (
    AccountCreate, AccountUpdate, FiscalPeriodCreate,
    JournalEntryCreate, JournalEntryLineCreate, JournalEntryUpdate,
)


# ===========================================================================
# FiscalPeriod CRUD
# ===========================================================================
class FiscalPeriodCRUD:
    async def get(self, db: AsyncSession, period_id: int) -> Optional[FiscalPeriod]:
        result = await db.execute(select(FiscalPeriod).where(FiscalPeriod.id == period_id))
        return result.scalar_one_or_none()

    async def get_open_for_date(self, db: AsyncSession, entry_date: date) -> Optional[FiscalPeriod]:
        """Returns the open/adjusting period that contains entry_date."""
        result = await db.execute(
            select(FiscalPeriod).where(
                and_(
                    FiscalPeriod.start_date <= entry_date,
                    FiscalPeriod.end_date >= entry_date,
                    FiscalPeriod.status.in_(
                        [FiscalPeriodStatus.OPEN, FiscalPeriodStatus.ADJUSTING]
                    ),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, db: AsyncSession, *, year: Optional[int] = None, offset: int = 0, limit: int = 50
    ) -> tuple[int, Sequence[FiscalPeriod]]:
        q = select(FiscalPeriod)
        if year:
            q = q.where(FiscalPeriod.year == year)
        q = q.order_by(FiscalPeriod.start_date.desc())
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self, db: AsyncSession, data: FiscalPeriodCreate, user_id: Optional[int] = None
    ) -> FiscalPeriod:
        obj = FiscalPeriod(**data.model_dump(), created_by_id=user_id, updated_by_id=user_id)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def close(self, db: AsyncSession, period: FiscalPeriod, user_id: int) -> FiscalPeriod:
        period.status = FiscalPeriodStatus.CLOSED
        period.closed_by_id = user_id
        period.closed_at = datetime.utcnow()
        period.updated_by_id = user_id
        await db.flush()
        return period


# ===========================================================================
# Account CRUD
# ===========================================================================
class AccountCRUD:
    async def get(self, db: AsyncSession, account_id: int) -> Optional[Account]:
        result = await db.execute(select(Account).where(Account.id == account_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Account]:
        result = await db.execute(select(Account).where(Account.code == code))
        return result.scalar_one_or_none()

    async def get_by_subtype(self, db: AsyncSession, subtype: str) -> Optional[Account]:
        from app.models.finance import AccountSubtype
        result = await db.execute(
            select(Account).where(Account.subtype == subtype, Account.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        type: Optional[AccountType] = None,
        is_active: Optional[bool] = True,
        parent_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 200,
    ) -> tuple[int, Sequence[Account]]:
        q = select(Account).order_by(Account.code)
        if type:
            q = q.where(Account.type == type)
        if is_active is not None:
            q = q.where(Account.is_active == is_active)
        if parent_id is not None:
            q = q.where(Account.parent_id == parent_id)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def get_tree(self, db: AsyncSession) -> Sequence[Account]:
        """Fetch all accounts in code order — caller builds tree structure."""
        result = await db.execute(
            select(Account).where(Account.is_active.is_(True)).order_by(Account.code)
        )
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, data: AccountCreate, user_id: Optional[int] = None
    ) -> Account:
        obj = Account(**data.model_dump(), created_by_id=user_id, updated_by_id=user_id)

        # Compute path and depth
        if data.parent_id:
            parent = await self.get(db, data.parent_id)
            if parent:
                obj.depth = parent.depth + 1
                obj.path = f"{parent.path}.{data.code}" if parent.path else f"{parent.code}.{data.code}"
        else:
            obj.depth = 0
            obj.path = data.code

        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(
        self, db: AsyncSession, obj: Account, data: AccountUpdate, user_id: Optional[int] = None
    ) -> Account:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        obj.updated_by_id = user_id
        await db.flush()
        await db.refresh(obj)
        return obj

    async def has_journal_lines(self, db: AsyncSession, account_id: int) -> bool:
        result = await db.execute(
            select(func.count(JournalEntryLine.id)).where(
                JournalEntryLine.account_id == account_id
            )
        )
        return (result.scalar_one() or 0) > 0

    async def get_balance(
        self,
        db: AsyncSession,
        account_id: int,
        as_of_date: Optional[date] = None,
        period_id: Optional[int] = None,
    ) -> tuple[Decimal, Decimal]:
        """Returns (total_debit, total_credit) for the account."""
        q = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit), Decimal("0")).label("total_dr"),
                func.coalesce(func.sum(JournalEntryLine.credit), Decimal("0")).label("total_cr"),
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .where(
                JournalEntryLine.account_id == account_id,
                JournalEntry.status == JournalEntryStatus.POSTED,
            )
        )
        if as_of_date:
            q = q.where(JournalEntry.entry_date <= as_of_date)
        if period_id:
            q = q.where(JournalEntry.period_id == period_id)

        row = (await db.execute(q)).one()
        return Decimal(str(row.total_dr)), Decimal(str(row.total_cr))


# ===========================================================================
# JournalEntry CRUD
# ===========================================================================
class JournalEntryCRUD:

    def _generate_entry_number(self, year: int) -> str:
        rand = "".join(random.choices(string.digits, k=5))
        return f"JE-{year}-{rand}"

    async def get(
        self, db: AsyncSession, entry_id: int, with_lines: bool = True
    ) -> Optional[JournalEntry]:
        q = select(JournalEntry).where(JournalEntry.id == entry_id)
        if with_lines:
            q = q.options(
                selectinload(JournalEntry.lines).selectinload(JournalEntryLine.account)
            )
        result = await db.execute(q)
        return result.scalar_one_or_none()

    async def get_by_reference(
        self, db: AsyncSession, ref_type: ReferenceType, ref_id: int
    ) -> Sequence[JournalEntry]:
        result = await db.execute(
            select(JournalEntry).where(
                JournalEntry.reference_type == ref_type,
                JournalEntry.reference_id == ref_id,
            )
        )
        return result.scalars().all()

    async def list(
        self,
        db: AsyncSession,
        *,
        period_id: Optional[int] = None,
        status: Optional[JournalEntryStatus] = None,
        reference_type: Optional[ReferenceType] = None,
        account_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[JournalEntry]]:
        q = select(JournalEntry).order_by(JournalEntry.entry_date.desc())
        if period_id:
            q = q.where(JournalEntry.period_id == period_id)
        if status:
            q = q.where(JournalEntry.status == status)
        if reference_type:
            q = q.where(JournalEntry.reference_type == reference_type)
        if account_id:
            q = q.join(JournalEntry.lines).where(JournalEntryLine.account_id == account_id)
        if date_from:
            q = q.where(JournalEntry.entry_date >= date_from)
        if date_to:
            q = q.where(JournalEntry.entry_date <= date_to)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self,
        db: AsyncSession,
        data: JournalEntryCreate,
        user_id: Optional[int] = None,
    ) -> JournalEntry:
        period = await fiscal_period_crud.get(db, data.period_id)
        year = period.year if period else datetime.utcnow().year

        total_dr = sum(ln.debit or Decimal("0") for ln in data.lines)
        total_cr = sum(ln.credit or Decimal("0") for ln in data.lines)

        entry = JournalEntry(
            entry_number=self._generate_entry_number(year),
            entry_date=data.entry_date,
            period_id=data.period_id,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            description=data.description,
            description_fa=data.description_fa,
            total_debit=total_dr,
            total_credit=total_cr,
            status=JournalEntryStatus.DRAFT,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(entry)
        await db.flush()  # get entry.id

        for line_data in data.lines:
            line = JournalEntryLine(
                journal_entry_id=entry.id,
                **line_data.model_dump(),
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            db.add(line)

        await db.flush()
        await db.refresh(entry)
        return entry

    async def update(
        self,
        db: AsyncSession,
        entry: JournalEntry,
        data: JournalEntryUpdate,
        user_id: Optional[int] = None,
    ) -> JournalEntry:
        """Only DRAFT entries can be updated."""
        if data.entry_date is not None:
            entry.entry_date = data.entry_date
        if data.description is not None:
            entry.description = data.description
        if data.description_fa is not None:
            entry.description_fa = data.description_fa
        if data.lines is not None:
            # Replace all lines
            for existing_line in entry.lines:
                await db.delete(existing_line)
            await db.flush()
            total_dr = Decimal("0")
            total_cr = Decimal("0")
            for line_data in data.lines:
                line = JournalEntryLine(
                    journal_entry_id=entry.id,
                    **line_data.model_dump(),
                    created_by_id=user_id,
                    updated_by_id=user_id,
                )
                db.add(line)
                total_dr += line_data.debit or Decimal("0")
                total_cr += line_data.credit or Decimal("0")
            entry.total_debit = total_dr
            entry.total_credit = total_cr
        entry.updated_by_id = user_id
        await db.flush()
        await db.refresh(entry)
        return entry

    async def post(
        self, db: AsyncSession, entry: JournalEntry, user_id: int
    ) -> JournalEntry:
        entry.status = JournalEntryStatus.POSTED
        entry.posted_by_id = user_id
        entry.posted_at = datetime.utcnow()
        entry.updated_by_id = user_id
        await db.flush()
        return entry

    async def create_reversal(
        self,
        db: AsyncSession,
        original: JournalEntry,
        reversal_date: date,
        user_id: int,
    ) -> JournalEntry:
        """Creates a new DRAFT entry that reverses every debit/credit of the original."""
        period = await fiscal_period_crud.get_open_for_date(db, reversal_date)
        if not period:
            from app.services.accounting_service import AccountingError
            raise AccountingError(f"No open fiscal period for reversal date {reversal_date}")

        reversal_lines = []
        for line in original.lines:
            reversal_lines.append(
                JournalEntryLineCreate(
                    account_id=line.account_id,
                    debit=line.credit,    # swap
                    credit=line.debit,    # swap
                    description=line.description,
                    cost_center=line.cost_center,
                    contact_id=line.contact_id,
                    contact_type=line.contact_type,
                )
            )

        reversal_data = JournalEntryCreate(
            entry_date=reversal_date,
            period_id=period.id,
            reference_type=original.reference_type,
            reference_id=original.reference_id,
            description=f"Reversal of {original.entry_number}",
            description_fa=f"برگشت سند {original.entry_number}",
            lines=reversal_lines,
        )
        reversal = await self.create(db, reversal_data, user_id=user_id)
        reversal.is_reversing_entry = True
        reversal.reversed_entry_id = original.id

        # Mark original as reversed
        original.status = JournalEntryStatus.REVERSED
        original.updated_by_id = user_id

        await db.flush()
        return reversal


# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------
fiscal_period_crud = FiscalPeriodCRUD()
account_crud = AccountCRUD()
journal_entry_crud = JournalEntryCRUD()
