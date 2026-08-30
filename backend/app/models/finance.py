"""
Finance Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Double-entry accounting following IFRS/GAAP standards.
Iranian business context: supports IRR, USD, EUR; Jalali calendar labels.

DEBIT/CREDIT RULES (قوانین بدهکار/بستانکار):
  دارایی  (Asset):     بدهکار (+) / بستانکار (-)
  بدهی    (Liability): بستانکار (+) / بدهکار (-)
  سرمایه  (Equity):    بستانکار (+) / بدهکار (-)
  درآمد   (Revenue):   بستانکار (+) / بدهکار (-)
  هزینه   (Expense):   بدهکار (+) / بستانکار (-)

  قانون طلایی: مجموع بدهکارها = مجموع بستانکارها
  (Golden Rule: Sum of Debits MUST equal Sum of Credits for every JE)
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, Enum,
    ForeignKey, Index, Integer, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class AccountType(str, enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class AccountSubtype(str, enum.Enum):
    CASH = "cash"
    BANK = "bank"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    INVENTORY = "inventory"
    PREPAID = "prepaid"
    FIXED_ASSET = "fixed_asset"
    ACCUMULATED_DEPRECIATION = "accumulated_depreciation"
    OTHER_ASSET = "other_asset"
    ACCOUNTS_PAYABLE = "accounts_payable"
    ACCRUED_EXPENSE = "accrued_expense"
    TAX_PAYABLE = "tax_payable"
    OTHER_LIABILITY = "other_liability"
    CAPITAL = "capital"
    RETAINED_EARNINGS = "retained_earnings"
    SALES = "sales"
    OTHER_INCOME = "other_income"
    COGS = "cogs"
    SALARY = "salary"
    RENT = "rent"
    UTILITIES = "utilities"
    DEPRECIATION_EXP = "depreciation_exp"
    OTHER_EXPENSE = "other_expense"
    INVENTORY_ADJUSTMENT = "inventory_adjustment"


class JournalEntryStatus(str, enum.Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"


class FiscalPeriodStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    ADJUSTING = "adjusting"


class ReferenceType(str, enum.Enum):
    INVENTORY = "inventory"
    INVOICE = "invoice"
    PAYMENT = "payment"
    MANUAL = "manual"
    PAYROLL = "payroll"
    DEPRECIATION = "depreciation"
    PERIOD_CLOSE = "period_close"


class ContactType(str, enum.Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"


# ---------------------------------------------------------------------------
# FiscalPeriod
# ---------------------------------------------------------------------------
class FiscalPeriod(AuditMixin, Base):
    __tablename__ = "fiscal_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    quarter: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[FiscalPeriodStatus] = mapped_column(
        Enum(FiscalPeriodStatus), nullable=False, default=FiscalPeriodStatus.OPEN
    )
    is_adjustment_period: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    closed_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        "JournalEntry", back_populates="period"
    )

    __table_args__ = (
        CheckConstraint("end_date > start_date", name="chk_period_dates"),
        CheckConstraint("quarter IS NULL OR quarter BETWEEN 1 AND 4", name="chk_period_quarter"),
        Index("ix_fiscal_periods_year", "year"),
        Index("ix_fiscal_periods_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<FiscalPeriod {self.name} status={self.status}>"


# ---------------------------------------------------------------------------
# Account  (Chart of Accounts)
# ---------------------------------------------------------------------------
class Account(AuditMixin, Base):
    """
    Hierarchical COA node.
    Code scheme: 1xxx=Assets, 2xxx=Liabilities, 3xxx=Equity,
                 4xxx=Revenue, 5xxx=Expenses
    Header accounts (allow_direct_posting=False) cannot receive JE lines.
    """
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False, index=True)
    subtype: Mapped[Optional[AccountSubtype]] = mapped_column(
        Enum(AccountSubtype), nullable=True, index=True
    )

    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True
    )
    path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_bank_account: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_direct_posting: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="IRR")

    parent: Mapped[Optional["Account"]] = relationship(
        "Account", remote_side="Account.id", back_populates="children"
    )
    children: Mapped[list["Account"]] = relationship("Account", back_populates="parent")
    journal_lines: Mapped[list["JournalEntryLine"]] = relationship(
        "JournalEntryLine", back_populates="account"
    )

    @property
    def normal_balance(self) -> str:
        """Side that increases this account."""
        if self.type in (AccountType.ASSET, AccountType.EXPENSE):
            return "debit"
        return "credit"

    def compute_balance(self, total_debit: Decimal, total_credit: Decimal) -> Decimal:
        """
        Returns signed balance from raw DR/CR totals.
        Assets/Expenses: positive = debit balance
        Liabilities/Equity/Revenue: positive = credit balance
        """
        if self.type in (AccountType.ASSET, AccountType.EXPENSE):
            return total_debit - total_credit
        return total_credit - total_debit

    __table_args__ = (
        Index("ix_accounts_code", "code"),
        Index("ix_accounts_type", "type"),
        Index("ix_accounts_parent_id", "parent_id"),
        Index("ix_accounts_subtype", "subtype"),
    )

    def __repr__(self) -> str:
        return f"<Account {self.code} — {self.name}>"


# ---------------------------------------------------------------------------
# JournalEntry
# ---------------------------------------------------------------------------
class JournalEntry(AuditMixin, Base):
    """
    Core accounting document. Immutable once POSTED.
    Invariant: SUM(debit lines) == SUM(credit lines).
    Auto-generated by InventoryAccountingBridge for inventory movements.
    """
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fiscal_periods.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    reference_type: Mapped[ReferenceType] = mapped_column(
        Enum(ReferenceType), nullable=False, default=ReferenceType.MANUAL
    )
    reference_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    description_fa: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Denormalised totals — kept in sync whenever lines change
    total_debit: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0.0000")
    )
    total_credit: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0.0000")
    )

    status: Mapped[JournalEntryStatus] = mapped_column(
        Enum(JournalEntryStatus), nullable=False, default=JournalEntryStatus.DRAFT, index=True
    )

    is_reversing_entry: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reversed_entry_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True
    )

    posted_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    period: Mapped["FiscalPeriod"] = relationship("FiscalPeriod", back_populates="journal_entries")
    lines: Mapped[list["JournalEntryLine"]] = relationship(
        "JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan"
    )
    reversed_entry: Mapped[Optional["JournalEntry"]] = relationship(
        "JournalEntry", remote_side="JournalEntry.id", foreign_keys=[reversed_entry_id]
    )

    __table_args__ = (
        CheckConstraint("total_debit >= 0", name="chk_je_total_debit_non_negative"),
        CheckConstraint("total_credit >= 0", name="chk_je_total_credit_non_negative"),
        Index("ix_journal_entries_period_id", "period_id"),
        Index("ix_journal_entries_entry_date", "entry_date"),
        Index("ix_journal_entries_reference", "reference_type", "reference_id"),
        Index("ix_journal_entries_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<JournalEntry {self.entry_number} {self.status}>"


# ---------------------------------------------------------------------------
# JournalEntryLine
# ---------------------------------------------------------------------------
class JournalEntryLine(AuditMixin, Base):
    """
    Each line has EITHER debit OR credit — never both, never neither.
    Constraint enforced at DB level via CHECK.
    Lines cannot be edited once parent JE is POSTED.
    """
    __tablename__ = "journal_entry_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journal_entry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    debit: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)
    credit: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)

    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cost_center: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Subledger linkage (AR/AP)
    contact_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    contact_type: Mapped[Optional[ContactType]] = mapped_column(Enum(ContactType), nullable=True)

    journal_entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="lines")
    account: Mapped["Account"] = relationship("Account", back_populates="journal_lines")

    __table_args__ = (
        CheckConstraint(
            "(debit IS NOT NULL AND credit IS NULL AND debit > 0) OR "
            "(credit IS NOT NULL AND debit IS NULL AND credit > 0)",
            name="chk_jel_exactly_one_side",
        ),
        Index("ix_journal_entry_lines_je_id", "journal_entry_id"),
        Index("ix_journal_entry_lines_account_id", "account_id"),
    )

    def __repr__(self) -> str:
        side = f"DR {self.debit}" if self.debit else f"CR {self.credit}"
        return f"<JELine acct={self.account_id} {side}>"


# ---------------------------------------------------------------------------
# ExchangeRate
# ---------------------------------------------------------------------------
class ExchangeRate(AuditMixin, Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    rate_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("from_currency", "to_currency", "rate_date", name="uq_exchange_rate"),
        Index("ix_exchange_rates_date", "rate_date"),
        CheckConstraint("rate > 0", name="chk_exchange_rate_positive"),
    )