"""
Finance Module — Reporting Service
TOP WorX ERP System

Generates financial statements from posted journal entries.
All monetary amounts use Decimal(18,4) — never float.

Standard report hierarchy:
  Trial Balance → verifies DR == CR
  Income Statement → Revenue - Expenses = Net Income
  Balance Sheet → Assets == Liabilities + Equity  (accounting equation)
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.finance import account_crud, fiscal_period_crud, journal_entry_crud
from app.models.finance import (
    Account, AccountType, FiscalPeriod, JournalEntry,
    JournalEntryLine, JournalEntryStatus,
)
from app.schemas.finance import (
    AccountBalance, AgingBucket, AgingReportResponse, BalanceSheetResponse,
    BalanceSheetSection, IncomeStatementResponse, IncomeStatementRow,
    InventoryValuationResponse, InventoryValuationRow, TrialBalanceResponse,
)


class ReportingService:

    # -----------------------------------------------------------------------
    # Trial Balance
    # -----------------------------------------------------------------------

    async def trial_balance(
        self, db: AsyncSession, as_of_date: date
    ) -> TrialBalanceResponse:
        """
        For every account with posted activity up to as_of_date:
        shows total debits, total credits, and signed balance.
        Grand total DR must equal grand total CR.
        """
        rows_raw = await db.execute(
            select(
                Account.id,
                Account.code,
                Account.name,
                Account.name_fa,
                Account.type,
                Account.subtype,
                Account.depth,
                func.coalesce(func.sum(JournalEntryLine.debit), Decimal("0")).label("total_dr"),
                func.coalesce(func.sum(JournalEntryLine.credit), Decimal("0")).label("total_cr"),
            )
            .join(JournalEntryLine, JournalEntryLine.account_id == Account.id)
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date <= as_of_date,
            )
            .group_by(
                Account.id, Account.code, Account.name, Account.name_fa,
                Account.type, Account.subtype, Account.depth,
            )
            .order_by(Account.code)
        )

        rows: list[AccountBalance] = []
        grand_dr = Decimal("0")
        grand_cr = Decimal("0")

        for r in rows_raw.all():
            dr = Decimal(str(r.total_dr))
            cr = Decimal(str(r.total_cr))
            # Signed balance follows normal balance convention
            if r.type in (AccountType.ASSET, AccountType.EXPENSE):
                balance = dr - cr
            else:
                balance = cr - dr
            grand_dr += dr
            grand_cr += cr
            rows.append(
                AccountBalance(
                    account_id=r.id,
                    code=r.code,
                    name=r.name,
                    name_fa=r.name_fa,
                    type=r.type,
                    subtype=r.subtype,
                    depth=r.depth,
                    total_debit=dr,
                    total_credit=cr,
                    balance=balance,
                )
            )

        return TrialBalanceResponse(
            as_of_date=as_of_date,
            rows=rows,
            grand_total_debit=grand_dr,
            grand_total_credit=grand_cr,
            is_balanced=(abs(grand_dr - grand_cr) < Decimal("0.0001")),
        )

    # -----------------------------------------------------------------------
    # Income Statement (P&L)
    # -----------------------------------------------------------------------

    async def income_statement(
        self,
        db: AsyncSession,
        period_id: int,
    ) -> IncomeStatementResponse:
        """
        Revenue (4xxx) — Credits > Debits
        COGS (5100)
        Operating Expenses (5xxx except 5100)
        Net Income = Revenue - COGS - OpEx
        """
        period = await fiscal_period_crud.get(db, period_id)
        if not period:
            raise ValueError(f"Fiscal period {period_id} not found")

        def _make_query(type_: AccountType):
            return (
                select(
                    Account.id,
                    Account.code,
                    Account.name,
                    Account.name_fa,
                    Account.subtype,
                    func.coalesce(func.sum(JournalEntryLine.debit), Decimal("0")).label("dr"),
                    func.coalesce(func.sum(JournalEntryLine.credit), Decimal("0")).label("cr"),
                )
                .join(JournalEntryLine, JournalEntryLine.account_id == Account.id)
                .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
                .where(
                    Account.type == type_,
                    JournalEntry.status == JournalEntryStatus.POSTED,
                    JournalEntry.period_id == period_id,
                )
                .group_by(Account.id, Account.code, Account.name, Account.name_fa, Account.subtype)
                .order_by(Account.code)
            )

        rev_rows = (await db.execute(_make_query(AccountType.REVENUE))).all()
        exp_rows = (await db.execute(_make_query(AccountType.EXPENSE))).all()

        revenue: list[IncomeStatementRow] = []
        cogs: list[IncomeStatementRow] = []
        opex: list[IncomeStatementRow] = []
        total_revenue = Decimal("0")
        total_cogs = Decimal("0")
        total_opex = Decimal("0")

        for r in rev_rows:
            amount = Decimal(str(r.cr)) - Decimal(str(r.dr))  # revenue: credit-normal
            revenue.append(IncomeStatementRow(
                account_id=r.id, code=r.code, name=r.name, name_fa=r.name_fa, amount=amount
            ))
            total_revenue += amount

        from app.models.finance import AccountSubtype
        for r in exp_rows:
            amount = Decimal(str(r.dr)) - Decimal(str(r.cr))  # expense: debit-normal
            row = IncomeStatementRow(
                account_id=r.id, code=r.code, name=r.name, name_fa=r.name_fa, amount=amount
            )
            if r.subtype == AccountSubtype.COGS:
                cogs.append(row)
                total_cogs += amount
            else:
                opex.append(row)
                total_opex += amount

        gross_profit = total_revenue - total_cogs
        net_income = gross_profit - total_opex

        return IncomeStatementResponse(
            period_start=period.start_date,
            period_end=period.end_date,
            revenue=revenue,
            cogs=cogs,
            operating_expenses=opex,
            total_revenue=total_revenue,
            total_cogs=total_cogs,
            gross_profit=gross_profit,
            total_operating_expenses=total_opex,
            net_income=net_income,
        )

    # -----------------------------------------------------------------------
    # Balance Sheet
    # -----------------------------------------------------------------------

    async def balance_sheet(
        self, db: AsyncSession, as_of_date: date
    ) -> BalanceSheetResponse:
        """
        Assets (1xxx)              = debit balance
        Liabilities (2xxx)         = credit balance
        Equity (3xxx)              = credit balance
        Net Income (from P&L)      added to Retained Earnings

        Accounting equation: Assets == Liabilities + Equity
        """

        async def _section(acct_type: AccountType) -> tuple[list[AccountBalance], Decimal]:
            rows = await db.execute(
                select(
                    Account.id, Account.code, Account.name, Account.name_fa,
                    Account.type, Account.subtype, Account.depth,
                    func.coalesce(func.sum(JournalEntryLine.debit), Decimal("0")).label("dr"),
                    func.coalesce(func.sum(JournalEntryLine.credit), Decimal("0")).label("cr"),
                )
                .join(JournalEntryLine, JournalEntryLine.account_id == Account.id)
                .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
                .where(
                    Account.type == acct_type,
                    JournalEntry.status == JournalEntryStatus.POSTED,
                    JournalEntry.entry_date <= as_of_date,
                )
                .group_by(
                    Account.id, Account.code, Account.name, Account.name_fa,
                    Account.type, Account.subtype, Account.depth,
                )
                .order_by(Account.code)
            )
            balances: list[AccountBalance] = []
            total = Decimal("0")
            for r in rows.all():
                dr, cr = Decimal(str(r.dr)), Decimal(str(r.cr))
                if acct_type == AccountType.ASSET:
                    balance = dr - cr
                else:
                    balance = cr - dr
                total += balance
                balances.append(AccountBalance(
                    account_id=r.id, code=r.code, name=r.name, name_fa=r.name_fa,
                    type=r.type, subtype=r.subtype, depth=r.depth,
                    total_debit=dr, total_credit=cr, balance=balance,
                ))
            return balances, total

        asset_rows, total_assets = await _section(AccountType.ASSET)
        liab_rows, total_liab = await _section(AccountType.LIABILITY)
        equity_rows, total_equity = await _section(AccountType.EQUITY)

        # Include current-year net income in equity (before period close)
        # This is the "retained earnings" adjustment for the current year
        rev_rows = await db.execute(
            select(
                func.coalesce(func.sum(JournalEntryLine.credit), Decimal("0"))
                - func.coalesce(func.sum(JournalEntryLine.debit), Decimal("0"))
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .join(Account, Account.id == JournalEntryLine.account_id)
            .where(
                Account.type == AccountType.REVENUE,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date <= as_of_date,
            )
        )
        exp_rows = await db.execute(
            select(
                func.coalesce(func.sum(JournalEntryLine.debit), Decimal("0"))
                - func.coalesce(func.sum(JournalEntryLine.credit), Decimal("0"))
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .join(Account, Account.id == JournalEntryLine.account_id)
            .where(
                Account.type == AccountType.EXPENSE,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date <= as_of_date,
            )
        )
        current_net_income = (
            Decimal(str(rev_rows.scalar_one() or "0"))
            - Decimal(str(exp_rows.scalar_one() or "0"))
        )
        total_equity += current_net_income
        total_liab_and_equity = total_liab + total_equity

        return BalanceSheetResponse(
            as_of_date=as_of_date,
            assets=BalanceSheetSection(accounts=asset_rows, total=total_assets),
            liabilities=BalanceSheetSection(accounts=liab_rows, total=total_liab),
            equity=BalanceSheetSection(accounts=equity_rows, total=total_equity),
            total_assets=total_assets,
            total_liabilities_and_equity=total_liab_and_equity,
            is_balanced=(abs(total_assets - total_liab_and_equity) < Decimal("0.01")),
        )

    # -----------------------------------------------------------------------
    # Inventory Valuation Reconciliation
    # -----------------------------------------------------------------------

    async def inventory_valuation(
        self, db: AsyncSession, as_of_date: date
    ) -> InventoryValuationResponse:
        """
        Compares physical inventory value (StockLevel × cost) with
        General Ledger balance of account 1130.
        """
        from app.models.inventory import InventoryItem, StockLevel  # avoid circular
        from app.services.inventory_bridge import inventory_bridge

        # Physical valuation rows
        rows_raw = await db.execute(
            select(
                InventoryItem.id,
                InventoryItem.sku,
                InventoryItem.name,
                func.coalesce(func.sum(StockLevel.quantity_on_hand), Decimal("0")).label("qty"),
                InventoryItem.standard_cost,
            )
            .join(StockLevel, StockLevel.item_id == InventoryItem.id, isouter=True)
            .where(InventoryItem.is_active.is_(True))
            .group_by(InventoryItem.id, InventoryItem.sku, InventoryItem.name, InventoryItem.standard_cost)
            .order_by(InventoryItem.sku)
        )

        items: list[InventoryValuationRow] = []
        total_physical = Decimal("0")
        for r in rows_raw.all():
            qty = Decimal(str(r.qty))
            cost = Decimal(str(r.standard_cost))
            value = qty * cost
            total_physical += value
            items.append(InventoryValuationRow(
                item_id=r.id, sku=r.sku, item_name=r.name,
                quantity_on_hand=qty, unit_cost=cost, total_value=value,
            ))

        gl_balance = await inventory_bridge.get_inventory_gl_balance(db)
        variance = total_physical - gl_balance

        return InventoryValuationResponse(
            as_of_date=as_of_date,
            items=items,
            total_physical_value=total_physical,
            gl_account_balance=gl_balance,
            variance=variance,
            is_reconciled=(abs(variance) < Decimal("0.01")),
        )

    # -----------------------------------------------------------------------
    # AR/AP Aging
    # -----------------------------------------------------------------------

    async def aging_report(
        self,
        db: AsyncSession,
        as_of_date: date,
        contact_type: str,  # "customer" | "vendor"
    ) -> AgingReportResponse:
        """
        Groups outstanding AR or AP balances into aging buckets.
        Uses JE line contact_id / contact_type for subledger linkage.
        DECISION POINT ⚙️: Connect contact_id to your Customer/Vendor model.
        """
        from app.models.finance import ContactType
        ct = ContactType.CUSTOMER if contact_type == "customer" else ContactType.VENDOR
        acct_code = "1120" if ct == ContactType.CUSTOMER else "2110"

        account = await account_crud.get_by_code(db, acct_code)
        if not account:
            return AgingReportResponse(
                as_of_date=as_of_date, contact_type=ct, rows=[], grand_total=Decimal("0")
            )

        # Fetch all posted lines for this account with contact info
        lines_raw = await db.execute(
            select(
                JournalEntryLine.contact_id,
                JournalEntryLine.debit,
                JournalEntryLine.credit,
                JournalEntry.entry_date,
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .where(
                JournalEntryLine.account_id == account.id,
                JournalEntryLine.contact_type == ct,
                JournalEntryLine.contact_id.isnot(None),
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date <= as_of_date,
            )
        )

        # Group by contact_id and compute age buckets
        from collections import defaultdict
        contact_buckets: dict[int, dict] = defaultdict(
            lambda: {"current": Decimal("0"), "31_60": Decimal("0"),
                     "61_90": Decimal("0"), "over_90": Decimal("0")}
        )
        for ln in lines_raw.all():
            age = (as_of_date - ln.entry_date).days
            amount = (Decimal(str(ln.debit or 0)) - Decimal(str(ln.credit or 0)))
            bucket = contact_buckets[ln.contact_id]
            if age <= 30:
                bucket["current"] += amount
            elif age <= 60:
                bucket["31_60"] += amount
            elif age <= 90:
                bucket["61_90"] += amount
            else:
                bucket["over_90"] += amount

        rows = []
        grand_total = Decimal("0")
        for contact_id, b in contact_buckets.items():
            total = b["current"] + b["31_60"] + b["61_90"] + b["over_90"]
            grand_total += total
            rows.append(AgingBucket(
                contact_id=contact_id,
                contact_name=f"Contact {contact_id}",  # TODO: join Customer/Vendor table
                current=b["current"],
                days_31_60=b["31_60"],
                days_61_90=b["61_90"],
                over_90=b["over_90"],
                total=total,
            ))

        from app.models.finance import ContactType
        return AgingReportResponse(
            as_of_date=as_of_date, contact_type=ct, rows=rows, grand_total=grand_total
        )


# Singleton
reporting_service = ReportingService()
