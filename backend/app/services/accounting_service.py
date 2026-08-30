"""
Finance Module — Accounting Service (Core Business Logic)
TOP WorX ERP System

Enforces all double-entry invariants:
  - SUM(DR) == SUM(CR) before any posting
  - Period must be OPEN or ADJUSTING
  - POSTED entries are immutable
  - Reversals create mirror entries
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.finance import account_crud, fiscal_period_crud, journal_entry_crud
from app.models.finance import (
    Account, AccountSubtype, AccountType, FiscalPeriodStatus,
    JournalEntry, JournalEntryLine, JournalEntryStatus, ReferenceType,
)
from app.schemas.finance import (
    AccountBalance, BalanceSheetResponse, BalanceSheetSection,
    IncomeStatementResponse, IncomeStatementRow,
    JournalEntryCreate, JournalEntryLineCreate,
    TrialBalanceResponse,
)


class AccountingError(Exception):
    """Business rule violation in the accounting layer."""


class AccountingService:

    # -----------------------------------------------------------------------
    # Journal Entry lifecycle
    # -----------------------------------------------------------------------

    async def create_draft(
        self,
        db: AsyncSession,
        data: JournalEntryCreate,
        user_id: Optional[int] = None,
    ) -> JournalEntry:
        """Validate and save a DRAFT journal entry (not yet in GL)."""
        # 1. Period must exist and be open
        period = await fiscal_period_crud.get(db, data.period_id)
        if not period:
            raise AccountingError(f"Fiscal period {data.period_id} not found")
        if period.status not in (FiscalPeriodStatus.OPEN, FiscalPeriodStatus.ADJUSTING):
            raise AccountingError(
                f"Cannot post to period '{period.name}' — status is '{period.status}'. "
                "دوره مالی بسته است."
            )
        if not (period.start_date <= data.entry_date <= period.end_date):
            raise AccountingError(
                f"Entry date {data.entry_date} is outside period "
                f"{period.start_date} – {period.end_date}"
            )

        # 2. Validate all accounts exist and allow direct posting
        for line in data.lines:
            account = await account_crud.get(db, line.account_id)
            if not account:
                raise AccountingError(f"Account {line.account_id} not found")
            if not account.allow_direct_posting:
                raise AccountingError(
                    f"Account {account.code} ({account.name}) is a header account "
                    "and does not allow direct posting"
                )
            if not account.is_active:
                raise AccountingError(f"Account {account.code} is inactive")

        # 3. Balance check already enforced by Pydantic validator in JournalEntryCreate
        return await journal_entry_crud.create(db, data, user_id=user_id)

    async def post_entry(
        self,
        db: AsyncSession,
        entry: JournalEntry,
        user_id: int,
    ) -> JournalEntry:
        """
        Post a DRAFT entry to the General Ledger.
        Once posted, the entry is immutable — use reverse() to correct it.
        """
        if entry.status != JournalEntryStatus.DRAFT:
            raise AccountingError(
                f"Only DRAFT entries can be posted. "
                f"Entry {entry.entry_number} is '{entry.status}'."
            )

        # Re-verify balance (belt-and-suspenders — Pydantic caught it on create)
        total_dr = sum(ln.debit or Decimal("0") for ln in entry.lines)
        total_cr = sum(ln.credit or Decimal("0") for ln in entry.lines)
        if total_dr != total_cr:
            raise AccountingError(
                f"Cannot post unbalanced entry: DR={total_dr} CR={total_cr}. "
                "بدهکارها و بستانکارها باید برابر باشند."
            )

        # Verify period still open
        period = await fiscal_period_crud.get(db, entry.period_id)
        if period and period.status not in (
            FiscalPeriodStatus.OPEN, FiscalPeriodStatus.ADJUSTING
        ):
            raise AccountingError(
                f"Period '{period.name}' has been closed since this entry was drafted."
            )

        return await journal_entry_crud.post(db, entry, user_id=user_id)

    async def reverse_entry(
        self,
        db: AsyncSession,
        entry: JournalEntry,
        reversal_date: date,
        user_id: int,
    ) -> JournalEntry:
        """
        Create a mirror entry that cancels the original.
        Both the original and the reversal remain in the GL.
        The reversal is created as DRAFT and must be posted separately.
        """
        if entry.status != JournalEntryStatus.POSTED:
            raise AccountingError(
                f"Only POSTED entries can be reversed. "
                f"Entry {entry.entry_number} is '{entry.status}'."
            )
        if entry.status == JournalEntryStatus.REVERSED:
            raise AccountingError(
                f"Entry {entry.entry_number} has already been reversed."
            )
        return await journal_entry_crud.create_reversal(db, entry, reversal_date, user_id)

    # -----------------------------------------------------------------------
    # Low-level JE builder (used by InventoryAccountingBridge)
    # -----------------------------------------------------------------------

    async def build_and_create_entry(
        self,
        db: AsyncSession,
        *,
        entry_date: date,
        description: str,
        description_fa: Optional[str] = None,
        reference_type: ReferenceType,
        reference_id: Optional[int] = None,
        lines: list[dict],   # [{"account_code": "1130", "debit": 100}, ...]
        user_id: Optional[int] = None,
    ) -> JournalEntry:
        """
        Convenience method for programmatic JE creation (e.g. from bridge).
        Lines format: [{"account_code": str, "debit": Decimal | None, "credit": Decimal | None}]
        """
        period = await fiscal_period_crud.get_open_for_date(db, entry_date)
        if not period:
            raise AccountingError(
                f"No open fiscal period for date {entry_date}. "
                f"دوره مالی باز برای تاریخ {entry_date} وجود ندارد."
            )

        je_lines: list[JournalEntryLineCreate] = []
        for raw in lines:
            account = await account_crud.get_by_code(db, raw["account_code"])
            if not account:
                raise AccountingError(f"Account code '{raw['account_code']}' not found in COA")
            je_lines.append(
                JournalEntryLineCreate(
                    account_id=account.id,
                    debit=raw.get("debit"),
                    credit=raw.get("credit"),
                    description=raw.get("description"),
                    cost_center=raw.get("cost_center"),
                    contact_id=raw.get("contact_id"),
                    contact_type=raw.get("contact_type"),
                )
            )

        data = JournalEntryCreate(
            entry_date=entry_date,
            period_id=period.id,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            description_fa=description_fa,
            lines=je_lines,
        )
        entry = await self.create_draft(db, data, user_id=user_id)
        # Auto-post system-generated entries
        return await self.post_entry(db, entry, user_id=user_id or 0)


# Singleton
accounting_service = AccountingService()
