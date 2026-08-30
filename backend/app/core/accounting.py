from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, AuditMixin


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
AccountTypeEnum = Enum(
    "asset", "liability", "equity", "revenue", "expense",
    name="account_type_enum"
)

JournalStatusEnum = Enum(
    "draft", "posted", "cancelled",
    name="journal_status_enum"
)

BankAccountTypeEnum = Enum(
    "checking", "savings", "credit",
    name="bank_account_type_enum"
)

BankTxTypeEnum = Enum(
    "deposit", "withdrawal", "transfer", "fee", "interest",
    name="bank_tx_type_enum"
)

ReconciliationStatusEnum = Enum(
    "pending", "reconciled", "discrepancy",
    name="reconciliation_status_enum"
)

DepreciationMethodEnum = Enum(
    "straight_line", "declining_balance", "sum_of_years",
    name="depreciation_method_enum"
)

AssetStatusEnum = Enum(
    "active", "disposed", "fully_depreciated",
    name="asset_status_enum"
)

PeriodStatusEnum = Enum(
    "open", "closed", "locked",
    name="period_status_enum"
)

BudgetStatusEnum = Enum(
    "draft", "approved", "active", "closed",
    name="budget_status_enum"
)

AuditActionEnum = Enum(
    "create", "update", "delete", "approve", "post", "revert",
    name="audit_action_enum"
)


# ---------------------------------------------------------------------------
# Chart of Accounts
# ---------------------------------------------------------------------------
class ChartOfAccounts(Base, AuditMixin):
    __tablename__ = "chart_of_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(AccountTypeEnum, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    parent: Mapped[Optional["ChartOfAccounts"]] = relationship(
        "ChartOfAccounts", remote_side="ChartOfAccounts.id", back_populates="children"
    )
    children: Mapped[List["ChartOfAccounts"]] = relationship(
        "ChartOfAccounts", back_populates="parent"
    )
    journal_lines: Mapped[List["JournalEntryLine"]] = relationship(
        "JournalEntryLine", back_populates="account"
    )
    ledger_entries: Mapped[List["GeneralLedger"]] = relationship(
        "GeneralLedger", back_populates="account"
    )

    __table_args__ = (
        Index("ix_coa_type_active", "type", "is_active"),
    )


# ---------------------------------------------------------------------------
# Accounting Period
# ---------------------------------------------------------------------------
class AccountingPeriod(Base, AuditMixin):
    __tablename__ = "accounting_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    fiscal_year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(PeriodStatusEnum, default="open", nullable=False)

    journal_entries: Mapped[List["JournalEntry"]] = relationship(
        "JournalEntry", back_populates="period"
    )

    __table_args__ = (
        UniqueConstraint("fiscal_year", "name", name="uq_period_fiscal_name"),
        CheckConstraint("period_end > period_start", name="ck_period_dates"),
    )


# ---------------------------------------------------------------------------
# Journal Entry
# ---------------------------------------------------------------------------
class JournalEntry(Base, AuditMixin):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(JournalStatusEnum, default="draft", nullable=False)
    period_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_periods.id", ondelete="SET NULL"), nullable=True, index=True
    )
    total_debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    total_credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)

    period: Mapped[Optional["AccountingPeriod"]] = relationship(
        "AccountingPeriod", back_populates="journal_entries"
    )
    lines: Mapped[List["JournalEntryLine"]] = relationship(
        "JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan"
    )
    ledger_entries: Mapped[List["GeneralLedger"]] = relationship(
        "GeneralLedger", back_populates="journal_entry"
    )

    __table_args__ = (
        CheckConstraint("total_debit >= 0", name="ck_je_debit_positive"),
        CheckConstraint("total_credit >= 0", name="ck_je_credit_positive"),
        Index("ix_je_date_status", "date", "status"),
    )


# ---------------------------------------------------------------------------
# Journal Entry Line
# ---------------------------------------------------------------------------
class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journal_entry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cost_center_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cost_centers.id", ondelete="SET NULL"), nullable=True, index=True
    )

    journal_entry: Mapped["JournalEntry"] = relationship(
        "JournalEntry", back_populates="lines"
    )
    account: Mapped["ChartOfAccounts"] = relationship(
        "ChartOfAccounts", back_populates="journal_lines"
    )
    cost_center: Mapped[Optional["CostCenter"]] = relationship("CostCenter")

    __table_args__ = (
        CheckConstraint("debit_amount >= 0", name="ck_jel_debit_positive"),
        CheckConstraint("credit_amount >= 0", name="ck_jel_credit_positive"),
        CheckConstraint(
            "(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0)",
            name="ck_jel_one_side_only"
        ),
    )


# ---------------------------------------------------------------------------
# General Ledger
# ---------------------------------------------------------------------------
class GeneralLedger(Base):
    __tablename__ = "general_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    journal_entry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    fiscal_year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    account: Mapped["ChartOfAccounts"] = relationship(
        "ChartOfAccounts", back_populates="ledger_entries"
    )
    journal_entry: Mapped["JournalEntry"] = relationship(
        "JournalEntry", back_populates="ledger_entries"
    )

    __table_args__ = (
        Index("ix_gl_account_date", "account_id", "date"),
        Index("ix_gl_fiscal_year", "fiscal_year", "account_id"),
    )


# ---------------------------------------------------------------------------
# Cost Center
# ---------------------------------------------------------------------------
class CostCenter(Base, AuditMixin):
    __tablename__ = "cost_centers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cost_centers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    parent: Mapped[Optional["CostCenter"]] = relationship(
        "CostCenter", remote_side="CostCenter.id", back_populates="children"
    )
    children: Mapped[List["CostCenter"]] = relationship(
        "CostCenter", back_populates="parent"
    )


# ---------------------------------------------------------------------------
# Bank Account
# ---------------------------------------------------------------------------
class BankAccount(Base, AuditMixin):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    bank_name: Mapped[str] = mapped_column(String(200), nullable=False)
    branch_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="IRR", nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    account_type: Mapped[str] = mapped_column(BankAccountTypeEnum, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    gl_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id", ondelete="SET NULL"), nullable=True
    )

    transactions: Mapped[List["BankTransaction"]] = relationship(
        "BankTransaction", back_populates="bank_account"
    )
    reconciliations: Mapped[List["BankReconciliation"]] = relationship(
        "BankReconciliation", back_populates="bank_account"
    )


# ---------------------------------------------------------------------------
# Bank Transaction
# ---------------------------------------------------------------------------
class BankTransaction(Base, AuditMixin):
    __tablename__ = "bank_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bank_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(BankTxTypeEnum, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_reconciled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    journal_entry_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True
    )

    bank_account: Mapped["BankAccount"] = relationship(
        "BankAccount", back_populates="transactions"
    )

    __table_args__ = (
        CheckConstraint("amount != 0", name="ck_bt_amount_nonzero"),
        Index("ix_bt_account_date", "bank_account_id", "date"),
    )


# ---------------------------------------------------------------------------
# Bank Reconciliation
# ---------------------------------------------------------------------------
class BankReconciliation(Base, AuditMixin):
    __tablename__ = "bank_reconciliations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bank_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    statement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    statement_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    book_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    difference: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(ReconciliationStatusEnum, default="pending", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    bank_account: Mapped["BankAccount"] = relationship(
        "BankAccount", back_populates="reconciliations"
    )


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------
class Budget(Base, AuditMixin):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    fiscal_year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(BudgetStatusEnum, default="draft", nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)

    lines: Mapped[List["BudgetLine"]] = relationship(
        "BudgetLine", back_populates="budget", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("period_end > period_start", name="ck_budget_dates"),
    )


# ---------------------------------------------------------------------------
# Budget Line
# ---------------------------------------------------------------------------
class BudgetLine(Base):
    __tablename__ = "budget_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    budget_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    actual_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)

    budget: Mapped["Budget"] = relationship("Budget", back_populates="lines")
    account: Mapped["ChartOfAccounts"] = relationship("ChartOfAccounts")

    __table_args__ = (
        UniqueConstraint("budget_id", "account_id", name="uq_budget_line_account"),
        CheckConstraint("budget_amount >= 0", name="ck_bl_amount_positive"),
    )


# ---------------------------------------------------------------------------
# Tax Code
# ---------------------------------------------------------------------------
class TaxCode(Base, AuditMixin):
    __tablename__ = "tax_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tax_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id", ondelete="SET NULL"), nullable=True
    )

    transactions: Mapped[List["TaxTransaction"]] = relationship(
        "TaxTransaction", back_populates="tax_code"
    )

    __table_args__ = (
        CheckConstraint("rate >= 0 AND rate <= 100", name="ck_tax_rate_range"),
    )


# ---------------------------------------------------------------------------
# Tax Transaction
# ---------------------------------------------------------------------------
class TaxTransaction(Base, AuditMixin):
    __tablename__ = "tax_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tax_code_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tax_codes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    journal_entry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    base_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    tax_code: Mapped["TaxCode"] = relationship("TaxCode", back_populates="transactions")


# ---------------------------------------------------------------------------
# Fixed Asset
# ---------------------------------------------------------------------------
class FixedAsset(Base, AuditMixin):
    __tablename__ = "fixed_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    purchase_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    purchase_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    salvage_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    useful_life: Mapped[int] = mapped_column(Integer, nullable=False)  # months
    depreciation_method: Mapped[str] = mapped_column(DepreciationMethodEnum, nullable=False)
    accumulated_depreciation: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    book_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[str] = mapped_column(AssetStatusEnum, default="active", nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    asset_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id", ondelete="SET NULL"), nullable=True
    )

    depreciations: Mapped[List["AssetDepreciation"]] = relationship(
        "AssetDepreciation", back_populates="asset", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("purchase_cost > 0", name="ck_fa_cost_positive"),
        CheckConstraint("salvage_value >= 0", name="ck_fa_salvage_positive"),
        CheckConstraint("useful_life > 0", name="ck_fa_life_positive"),
    )


# ---------------------------------------------------------------------------
# Asset Depreciation
# ---------------------------------------------------------------------------
class AssetDepreciation(Base, AuditMixin):
    __tablename__ = "asset_depreciations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fixed_assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    depreciation_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    accumulated_depreciation: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    book_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    journal_entry_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True
    )

    asset: Mapped["FixedAsset"] = relationship("FixedAsset", back_populates="depreciations")

    __table_args__ = (
        UniqueConstraint("asset_id", "period_date", name="uq_depreciation_period"),
        CheckConstraint("depreciation_amount > 0", name="ck_dep_amount_positive"),
    )


# ---------------------------------------------------------------------------
# Audit Trail
# ---------------------------------------------------------------------------
class AccountingAuditTrail(Base):
    __tablename__ = "accounting_audit_trail"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(AuditActionEnum, nullable=False)
    performed_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    changes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    metadata_: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)  # JSON string

    __table_args__ = (
        Index("ix_aat_entity", "entity_type", "entity_id"),
        Index("ix_aat_performed_at", "performed_at"),
    )
