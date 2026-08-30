# backend/app/schemas/finance.py

"""
Finance Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.finance import (
    AccountSubtype, AccountType, ContactType, FiscalPeriodStatus,
    JournalEntryStatus, ReferenceType,
)

_ro = ConfigDict(from_attributes=True)
NonNeg = Annotated[Decimal, Field(ge=Decimal("0"))]
Pos = Annotated[Decimal, Field(gt=Decimal("0"))]


# ===========================================================================
# FiscalPeriod
# ===========================================================================
class FiscalPeriodCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    name_fa: Optional[str] = Field(None, max_length=100)
    start_date: date
    end_date: date
    year: int = Field(..., ge=1300, le=1500)   # Jalali year range
    quarter: Optional[int] = Field(None, ge=1, le=4)
    is_adjustment_period: bool = False

    @model_validator(mode="after")
    def end_after_start(self) -> "FiscalPeriodCreate":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class FiscalPeriodResponse(FiscalPeriodCreate):
    model_config = _ro
    id: int
    status: FiscalPeriodStatus
    closed_by_id: Optional[int] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ===========================================================================
# Account
# ===========================================================================
class AccountCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=1, max_length=200)
    name_fa: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    type: AccountType
    subtype: Optional[AccountSubtype] = None
    parent_id: Optional[int] = None
    is_bank_account: bool = False
    allow_direct_posting: bool = True
    is_active: bool = True
    currency: str = Field("IRR", min_length=3, max_length=3)

    @field_validator("code")
    @classmethod
    def code_format(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("Account code must be numeric (e.g. 1130)")
        return v


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    name_fa: Optional[str] = None
    description: Optional[str] = None
    subtype: Optional[AccountSubtype] = None
    is_bank_account: Optional[bool] = None
    allow_direct_posting: Optional[bool] = None
    is_active: Optional[bool] = None


class AccountResponse(AccountCreate):
    model_config = _ro
    id: int
    path: Optional[str] = None
    depth: int
    created_at: datetime
    updated_at: datetime


class AccountWithBalanceResponse(AccountResponse):
    """Account response enriched with computed GL balance."""
    model_config = _ro
    total_debit: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")
    balance: Decimal = Decimal("0")      # signed, per normal_balance convention
    children: list["AccountWithBalanceResponse"] = []


class AccountTreeResponse(AccountResponse):
    model_config = _ro
    children: list["AccountTreeResponse"] = []


# ===========================================================================
# JournalEntryLine
# ===========================================================================
class JournalEntryLineCreate(BaseModel):
    account_id: int
    debit: Optional[Pos] = None
    credit: Optional[Pos] = None
    description: Optional[str] = Field(None, max_length=500)
    cost_center: Optional[str] = Field(None, max_length=100)
    contact_id: Optional[int] = None
    contact_type: Optional[ContactType] = None

    @model_validator(mode="after")
    def exactly_one_side(self) -> "JournalEntryLineCreate":
        if self.debit is not None and self.credit is not None:
            raise ValueError("A journal line cannot have both debit and credit")
        if self.debit is None and self.credit is None:
            raise ValueError("A journal line must have either debit or credit")
        return self


class JournalEntryLineResponse(BaseModel):
    model_config = _ro
    id: int
    journal_entry_id: int
    account_id: int
    debit: Optional[Decimal] = None
    credit: Optional[Decimal] = None
    description: Optional[str] = None
    cost_center: Optional[str] = None
    contact_id: Optional[int] = None
    contact_type: Optional[ContactType] = None
    # Denormalised from account for display
    account_code: Optional[str] = None
    account_name: Optional[str] = None


# ===========================================================================
# JournalEntry
# ===========================================================================
class JournalEntryCreate(BaseModel):
    entry_date: date
    period_id: int
    reference_type: ReferenceType = ReferenceType.MANUAL
    reference_id: Optional[int] = None
    description: str = Field(..., min_length=1, max_length=500)
    description_fa: Optional[str] = Field(None, max_length=500)
    lines: list[JournalEntryLineCreate] = Field(..., min_length=2)

    @model_validator(mode="after")
    def debits_equal_credits(self) -> "JournalEntryCreate":
        total_dr = sum(ln.debit or Decimal("0") for ln in self.lines)
        total_cr = sum(ln.credit or Decimal("0") for ln in self.lines)
        if total_dr != total_cr:
            raise ValueError(
                f"Journal entry is unbalanced: debits={total_dr} credits={total_cr}. "
                "بدهکارها و بستانکارها باید برابر باشند."
            )
        if total_dr == Decimal("0"):
            raise ValueError("Journal entry cannot have zero total amount")
        return self


class JournalEntryUpdate(BaseModel):
    """Only DRAFT entries can be updated."""
    entry_date: Optional[date] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    description_fa: Optional[str] = None
    lines: Optional[list[JournalEntryLineCreate]] = Field(None, min_length=2)

    @model_validator(mode="after")
    def debits_equal_credits_if_lines(self) -> "JournalEntryUpdate":
        if self.lines is not None:
            total_dr = sum(ln.debit or Decimal("0") for ln in self.lines)
            total_cr = sum(ln.credit or Decimal("0") for ln in self.lines)
            if total_dr != total_cr:
                raise ValueError(f"Updated lines are unbalanced: DR={total_dr} CR={total_cr}")
        return self


class JournalEntryResponse(BaseModel):
    model_config = _ro
    id: int
    entry_number: str
    entry_date: date
    period_id: int
    reference_type: ReferenceType
    reference_id: Optional[int] = None
    description: str
    description_fa: Optional[str] = None
    total_debit: Decimal
    total_credit: Decimal
    status: JournalEntryStatus
    is_reversing_entry: bool
    reversed_entry_id: Optional[int] = None
    posted_by_id: Optional[int] = None
    posted_at: Optional[datetime] = None
    created_at: datetime
    created_by_id: Optional[int] = None
    lines: list[JournalEntryLineResponse] = []


# ===========================================================================
# Reporting schemas
# ===========================================================================
class AccountBalance(BaseModel):
    """Single account row in a trial balance or report."""
    model_config = _ro
    account_id: int
    code: str
    name: str
    name_fa: Optional[str] = None
    type: AccountType
    subtype: Optional[AccountSubtype] = None
    depth: int
    total_debit: Decimal
    total_credit: Decimal
    balance: Decimal   # signed per normal balance convention


class TrialBalanceResponse(BaseModel):
    as_of_date: date
    rows: list[AccountBalance]
    grand_total_debit: Decimal
    grand_total_credit: Decimal
    is_balanced: bool   # grand_total_debit == grand_total_credit


class IncomeStatementRow(BaseModel):
    account_id: int
    code: str
    name: str
    name_fa: Optional[str] = None
    amount: Decimal


class IncomeStatementResponse(BaseModel):
    period_start: date
    period_end: date
    revenue: list[IncomeStatementRow]
    cogs: list[IncomeStatementRow]
    operating_expenses: list[IncomeStatementRow]
    total_revenue: Decimal
    total_cogs: Decimal
    gross_profit: Decimal
    total_operating_expenses: Decimal
    net_income: Decimal


class BalanceSheetSection(BaseModel):
    accounts: list[AccountBalance]
    total: Decimal


class BalanceSheetResponse(BaseModel):
    as_of_date: date
    assets: BalanceSheetSection
    liabilities: BalanceSheetSection
    equity: BalanceSheetSection
    total_assets: Decimal
    total_liabilities_and_equity: Decimal
    is_balanced: bool


class InventoryValuationRow(BaseModel):
    item_id: int
    sku: str
    item_name: str
    quantity_on_hand: Decimal
    unit_cost: Decimal
    total_value: Decimal


class InventoryValuationResponse(BaseModel):
    as_of_date: date
    items: list[InventoryValuationRow]
    total_physical_value: Decimal
    gl_account_balance: Decimal        # Balance of account 1130
    variance: Decimal                  # physical - GL
    is_reconciled: bool


class AgingBucket(BaseModel):
    contact_id: int
    contact_name: str
    current: Decimal        # 0-30 days
    days_31_60: Decimal
    days_61_90: Decimal
    over_90: Decimal
    total: Decimal


class AgingReportResponse(BaseModel):
    as_of_date: date
    contact_type: ContactType
    rows: list[AgingBucket]
    grand_total: Decimal


# ===========================================================================
# ExchangeRate
# ===========================================================================
class ExchangeRateCreate(BaseModel):
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    rate: Pos
    rate_date: date
