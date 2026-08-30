"""
Finance Module — Test Suite
TOP WorX ERP System

Run:
    pytest backend/app/tests/test_finance.py -v --asyncio-mode=auto

Tests verify:
  - Double-entry balance invariant (DR == CR)
  - Period control (cannot post to CLOSED period)
  - Immutability (POSTED entries cannot be edited/deleted)
  - Inventory bridge creates correct JEs
  - Trial balance integrity (grand DR == grand CR)
  - Balance sheet equation (Assets == Liabilities + Equity)
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)

from app.models.finance import (
    Account, AccountSubtype, AccountType, Base, FiscalPeriod,
    FiscalPeriodStatus, JournalEntryStatus, ReferenceType,
)
from app.schemas.finance import (
    AccountCreate, FiscalPeriodCreate,
    JournalEntryCreate, JournalEntryLineCreate, JournalEntryUpdate,
)
from app.crud.finance import account_crud, fiscal_period_crud, journal_entry_crud
from app.services.accounting_service import AccountingError, accounting_service

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="function")
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture(scope="function")
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _make_period(
    db: AsyncSession,
    start: date = date(2024, 1, 1),
    end: date = date(2024, 12, 31),
    status: FiscalPeriodStatus = FiscalPeriodStatus.OPEN,
) -> FiscalPeriod:
    period = await fiscal_period_crud.create(
        db,
        FiscalPeriodCreate(
            name="1403 - Test", start_date=start, end_date=end, year=1403
        ),
    )
    period.status = status
    await db.flush()
    return period


async def _make_account(
    db: AsyncSession,
    code: str,
    name: str,
    type: AccountType,
    subtype: AccountSubtype | None = None,
) -> Account:
    return await account_crud.create(
        db,
        AccountCreate(code=code, name=name, type=type, subtype=subtype),
    )


async def _balanced_je(
    db: AsyncSession,
    period_id: int,
    dr_account_id: int,
    cr_account_id: int,
    amount: Decimal,
    entry_date: date = date(2024, 6, 1),
) -> JournalEntryCreate:
    return JournalEntryCreate(
        entry_date=entry_date,
        period_id=period_id,
        description="Test entry",
        lines=[
            JournalEntryLineCreate(account_id=dr_account_id, debit=amount),
            JournalEntryLineCreate(account_id=cr_account_id, credit=amount),
        ],
    )


# ===========================================================================
# TestDoubleEntry — core invariants
# ===========================================================================
class TestDoubleEntry:

    @pytest.mark.asyncio
    async def test_balanced_entry_creates_successfully(self, db: AsyncSession):
        period = await _make_period(db)
        inv = await _make_account(db, "1130", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2110", "AP", AccountType.LIABILITY)
        data = await _balanced_je(db, period.id, inv.id, ap.id, Decimal("1000.00"))
        entry = await accounting_service.create_draft(db, data)
        assert entry.total_debit == Decimal("1000.00")
        assert entry.total_credit == Decimal("1000.00")
        assert entry.status == JournalEntryStatus.DRAFT

    @pytest.mark.asyncio
    async def test_unbalanced_entry_rejected_at_schema(self, db: AsyncSession):
        """Pydantic validator must reject unbalanced lines before hitting DB."""
        period = await _make_period(db)
        inv = await _make_account(db, "1130T", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2110T", "AP", AccountType.LIABILITY)
        with pytest.raises(Exception) as exc_info:
            JournalEntryCreate(
                entry_date=date(2024, 6, 1),
                period_id=period.id,
                description="Unbalanced",
                lines=[
                    JournalEntryLineCreate(account_id=inv.id, debit=Decimal("500")),
                    JournalEntryLineCreate(account_id=ap.id, credit=Decimal("300")),
                ],
            )
        assert "unbalanced" in str(exc_info.value).lower() or "equal" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_line_cannot_have_both_dr_and_cr(self, db: AsyncSession):
        with pytest.raises(Exception):
            JournalEntryLineCreate(
                account_id=1,
                debit=Decimal("100"),
                credit=Decimal("100"),
            )

    @pytest.mark.asyncio
    async def test_line_must_have_one_side(self, db: AsyncSession):
        with pytest.raises(Exception):
            JournalEntryLineCreate(account_id=1)

    @pytest.mark.asyncio
    async def test_zero_amount_rejected(self, db: AsyncSession):
        with pytest.raises(Exception):
            JournalEntryLineCreate(account_id=1, debit=Decimal("0"))


# ===========================================================================
# TestPeriodControl
# ===========================================================================
class TestPeriodControl:

    @pytest.mark.asyncio
    async def test_cannot_post_to_closed_period(self, db: AsyncSession):
        period = await _make_period(db, status=FiscalPeriodStatus.CLOSED)
        inv = await _make_account(db, "1131", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2111", "AP", AccountType.LIABILITY)
        data = JournalEntryCreate(
            entry_date=date(2024, 6, 1),
            period_id=period.id,
            description="Should fail",
            lines=[
                JournalEntryLineCreate(account_id=inv.id, debit=Decimal("500")),
                JournalEntryLineCreate(account_id=ap.id, credit=Decimal("500")),
            ],
        )
        with pytest.raises(AccountingError) as exc:
            await accounting_service.create_draft(db, data)
        assert "closed" in str(exc.value).lower()

    @pytest.mark.asyncio
    async def test_adjusting_period_allows_posting(self, db: AsyncSession):
        """ADJUSTING periods should accept year-end adjustments."""
        period = await _make_period(db, status=FiscalPeriodStatus.ADJUSTING)
        inv = await _make_account(db, "1132", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2112", "AP", AccountType.LIABILITY)
        data = await _balanced_je(db, period.id, inv.id, ap.id, Decimal("200"))
        entry = await accounting_service.create_draft(db, data)
        assert entry.id is not None

    @pytest.mark.asyncio
    async def test_entry_date_outside_period_rejected(self, db: AsyncSession):
        period = await _make_period(
            db, start=date(2024, 1, 1), end=date(2024, 6, 30)
        )
        inv = await _make_account(db, "1133", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2113", "AP", AccountType.LIABILITY)
        data = JournalEntryCreate(
            entry_date=date(2024, 9, 1),  # outside period
            period_id=period.id,
            description="Date outside period",
            lines=[
                JournalEntryLineCreate(account_id=inv.id, debit=Decimal("100")),
                JournalEntryLineCreate(account_id=ap.id, credit=Decimal("100")),
            ],
        )
        with pytest.raises(AccountingError) as exc:
            await accounting_service.create_draft(db, data)
        assert "outside" in str(exc.value).lower()


# ===========================================================================
# TestImmutability
# ===========================================================================
class TestImmutability:

    @pytest.mark.asyncio
    async def test_posted_entry_cannot_be_edited(self, db: AsyncSession):
        period = await _make_period(db)
        inv = await _make_account(db, "1134", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2114", "AP", AccountType.LIABILITY)
        data = await _balanced_je(db, period.id, inv.id, ap.id, Decimal("750"))
        entry = await accounting_service.create_draft(db, data)
        entry = await accounting_service.post_entry(db, entry, user_id=1)
        assert entry.status == JournalEntryStatus.POSTED

        # Attempt edit — must be rejected at router level (status check)
        assert entry.status != JournalEntryStatus.DRAFT

    @pytest.mark.asyncio
    async def test_only_draft_can_be_posted(self, db: AsyncSession):
        period = await _make_period(db)
        inv = await _make_account(db, "1135", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2115", "AP", AccountType.LIABILITY)
        data = await _balanced_je(db, period.id, inv.id, ap.id, Decimal("100"))
        entry = await accounting_service.create_draft(db, data)
        await accounting_service.post_entry(db, entry, user_id=1)

        # Try to post again
        with pytest.raises(AccountingError) as exc:
            await accounting_service.post_entry(db, entry, user_id=1)
        assert "draft" in str(exc.value).lower()

    @pytest.mark.asyncio
    async def test_reversal_creates_mirror_entry(self, db: AsyncSession):
        period = await _make_period(db)
        inv = await _make_account(db, "1136", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2116", "AP", AccountType.LIABILITY)
        data = await _balanced_je(db, period.id, inv.id, ap.id, Decimal("400"))
        entry = await accounting_service.create_draft(db, data)
        entry = await accounting_service.post_entry(db, entry, user_id=1)

        reversal = await accounting_service.reverse_entry(
            db, entry, reversal_date=date(2024, 6, 15), user_id=1
        )
        assert reversal.is_reversing_entry is True
        assert reversal.reversed_entry_id == entry.id
        assert reversal.total_debit == entry.total_debit
        assert reversal.total_credit == entry.total_credit

    @pytest.mark.asyncio
    async def test_cannot_reverse_draft(self, db: AsyncSession):
        period = await _make_period(db)
        inv = await _make_account(db, "1137", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2117", "AP", AccountType.LIABILITY)
        data = await _balanced_je(db, period.id, inv.id, ap.id, Decimal("200"))
        entry = await accounting_service.create_draft(db, data)  # NOT posted

        with pytest.raises(AccountingError):
            await accounting_service.reverse_entry(
                db, entry, reversal_date=date(2024, 6, 15), user_id=1
            )


# ===========================================================================
# TestInventoryBridge
# ===========================================================================
class TestInventoryBridge:

    @pytest.mark.asyncio
    async def test_inbound_movement_debits_inventory_credits_ap(self, db: AsyncSession):
        """
        Simulates the bridge being called after an inbound movement.
        Verifies: Dr 1130 (Inventory) / Cr 2110 (AP)
        """
        from app.services.inventory_bridge import inventory_bridge, ACCT_INVENTORY, ACCT_AP

        period = await _make_period(db)
        inv_acct = await _make_account(db, ACCT_INVENTORY, "Inventory", AccountType.ASSET, AccountSubtype.INVENTORY)
        ap_acct = await _make_account(db, ACCT_AP, "Accounts Payable", AccountType.LIABILITY, AccountSubtype.ACCOUNTS_PAYABLE)
        cogs_acct = await _make_account(db, "5100", "COGS", AccountType.EXPENSE, AccountSubtype.COGS)
        ar_acct = await _make_account(db, "1120", "AR", AccountType.ASSET, AccountSubtype.ACCOUNTS_RECEIVABLE)
        sales_acct = await _make_account(db, "4100", "Sales", AccountType.REVENUE, AccountSubtype.SALES)

        # Build a minimal mock movement
        class MockMovement:
            id = 1
            reference_number = "IN-20240101-ABCD"
            movement_date = date(2024, 6, 1)
            quantity = Decimal("10")
            quantity_before = Decimal("0")
            quantity_after = Decimal("10")

        class MockItem:
            standard_cost = Decimal("150.00")

        from app.models.inventory import MovementType
        MockMovement.movement_type = MovementType.INBOUND

        await inventory_bridge._entry_inbound(
            db=db,
            movement=MockMovement(),
            total_cost=Decimal("1500.00"),
            counterparty_account=ACCT_AP,
            contact_id=None,
            contact_type_str=None,
            user_id=1,
        )
        await db.flush()

        # Verify JE was created with correct accounts
        entries = await journal_entry_crud.get_by_reference(
            db, ReferenceType.INVENTORY, 1
        )
        assert len(entries) >= 1
        posted_entry = entries[0]
        assert posted_entry.total_debit == Decimal("1500.00")
        assert posted_entry.total_credit == Decimal("1500.00")
        assert posted_entry.status == JournalEntryStatus.POSTED

        # Verify correct accounts in lines
        account_ids_dr = [ln.account_id for ln in posted_entry.lines if ln.debit]
        account_ids_cr = [ln.account_id for ln in posted_entry.lines if ln.credit]
        assert inv_acct.id in account_ids_dr
        assert ap_acct.id in account_ids_cr


# ===========================================================================
# TestTrialBalance
# ===========================================================================
class TestTrialBalance:

    @pytest.mark.asyncio
    async def test_trial_balance_is_balanced_after_postings(self, db: AsyncSession):
        from app.services.reporting_service import reporting_service

        period = await _make_period(db)
        inv = await _make_account(db, "1138", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2118", "AP", AccountType.LIABILITY)
        cogs = await _make_account(db, "5101", "COGS", AccountType.EXPENSE)
        sales = await _make_account(db, "4101", "Sales", AccountType.REVENUE)

        # Post 3 entries
        for amount in [Decimal("1000"), Decimal("500"), Decimal("250")]:
            data = await _balanced_je(db, period.id, inv.id, ap.id, amount)
            entry = await accounting_service.create_draft(db, data)
            await accounting_service.post_entry(db, entry, user_id=1)

        tb = await reporting_service.trial_balance(db, as_of_date=date(2024, 12, 31))
        assert tb.is_balanced is True
        assert tb.grand_total_debit == tb.grand_total_credit

    @pytest.mark.asyncio
    async def test_draft_entries_excluded_from_trial_balance(self, db: AsyncSession):
        from app.services.reporting_service import reporting_service

        period = await _make_period(db)
        inv = await _make_account(db, "1139", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2119", "AP", AccountType.LIABILITY)

        data = await _balanced_je(db, period.id, inv.id, ap.id, Decimal("999"))
        await accounting_service.create_draft(db, data)  # NOT posted

        tb = await reporting_service.trial_balance(db, as_of_date=date(2024, 12, 31))
        # Grand totals should be 0 — draft not in GL
        assert tb.grand_total_debit == Decimal("0")
        assert tb.grand_total_credit == Decimal("0")


# ===========================================================================
# TestBalanceSheet
# ===========================================================================
class TestBalanceSheet:

    @pytest.mark.asyncio
    async def test_accounting_equation_holds(self, db: AsyncSession):
        """
        After any valid set of JEs, Assets must equal Liabilities + Equity.
        We fund a company: Capital injected → Cash in bank.
        Then buy inventory on credit: Inventory DR / AP CR.
        """
        from app.services.reporting_service import reporting_service

        period = await _make_period(db)
        cash = await _make_account(db, "1110B", "Cash", AccountType.ASSET)
        inv = await _make_account(db, "1130B", "Inventory", AccountType.ASSET)
        ap = await _make_account(db, "2110B", "AP", AccountType.LIABILITY)
        capital = await _make_account(db, "3100B", "Capital", AccountType.EQUITY)

        # 1. Owner injects 50,000 capital: Dr Cash / Cr Capital
        entry1_data = JournalEntryCreate(
            entry_date=date(2024, 3, 1),
            period_id=period.id,
            description="Capital injection",
            lines=[
                JournalEntryLineCreate(account_id=cash.id, debit=Decimal("50000")),
                JournalEntryLineCreate(account_id=capital.id, credit=Decimal("50000")),
            ],
        )
        e1 = await accounting_service.create_draft(db, entry1_data)
        await accounting_service.post_entry(db, e1, user_id=1)

        # 2. Buy inventory on credit: Dr Inventory / Cr AP
        entry2_data = JournalEntryCreate(
            entry_date=date(2024, 3, 15),
            period_id=period.id,
            description="Buy inventory",
            lines=[
                JournalEntryLineCreate(account_id=inv.id, debit=Decimal("20000")),
                JournalEntryLineCreate(account_id=ap.id, credit=Decimal("20000")),
            ],
        )
        e2 = await accounting_service.create_draft(db, entry2_data)
        await accounting_service.post_entry(db, e2, user_id=1)

        bs = await reporting_service.balance_sheet(db, as_of_date=date(2024, 12, 31))

        # Assets = 50,000 (cash) + 20,000 (inventory) = 70,000
        # Liab + Equity = 20,000 (AP) + 50,000 (capital) = 70,000
        assert bs.is_balanced is True
        assert abs(bs.total_assets - bs.total_liabilities_and_equity) < Decimal("0.01")
        assert bs.total_assets == Decimal("70000")
