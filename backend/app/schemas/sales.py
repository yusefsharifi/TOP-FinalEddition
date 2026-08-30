# app/schemas/sales.py
"""
Sales Module — Pydantic v2 Schemas
TOP WorX ERP System

Merged: user original + AI-improved
  • CustomerBase inheritance  (AI)
  • decimal_places=4          (AI)
  • Regex validators          (AI)
  • EmailStr                  (AI)
  • discount_not_exceed_base  (AI)
  • payment_date not-future   (AI)
  • max_length on notes/terms (AI)
  • Default values / required fields as per original (User)
  • quote_date past-check removed (backdating allowed in ERP)
"""
from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import (
    BaseModel, ConfigDict, EmailStr,
    Field, field_validator, model_validator,
)

from app.models.sales import (
    CustomerCategory, InvoiceStatus,
    PaymentMethod, PaymentStatus, QuoteStatus,
)

# ---------------------------------------------------------------------------
# Shared config & annotated types
# ---------------------------------------------------------------------------
_ro = ConfigDict(from_attributes=True)

Pos    = Annotated[Decimal, Field(gt=Decimal("0"),                     decimal_places=4)]
NonNeg = Annotated[Decimal, Field(ge=Decimal("0"),                     decimal_places=4)]
Pct    = Annotated[Decimal, Field(ge=Decimal("0"), le=Decimal("100"), decimal_places=4)]

VAT_RATE = Decimal("9")   # 9% standard Iranian VAT (مالیات بر ارزش افزوده)

# Regex patterns for Iranian data validation
_PHONE_RE  = re.compile(r"^\+?[0-9\s\-()]{7,20}$")
_POSTAL_RE = re.compile(r"^\d{5,10}$")
_TAX_RE    = re.compile(r"^\d{10,14}$")


# ===========================================================================
# Customer
# ===========================================================================

class CustomerBase(BaseModel):
    """Shared optional fields — inherited by CustomerCreate and CustomerUpdate."""
    name:                     Optional[str]              = Field(None, min_length=1, max_length=200)
    name_fa:                  Optional[str]              = Field(None, max_length=200)
    tax_id:                   Optional[str]              = Field(None, max_length=20)
    economic_code:            Optional[str]              = Field(None, max_length=20)
    phone:                    Optional[str]              = Field(None, max_length=30)
    email:                    Optional[EmailStr]         = None
    address:                  Optional[str]              = None
    city:                     Optional[str]              = Field(None, max_length=100)
    postal_code:              Optional[str]              = Field(None, max_length=20)
    credit_limit:             Optional[NonNeg]           = None
    payment_terms:            Optional[int]              = Field(None, ge=0, le=365)
    default_discount_percent: Optional[Pct]              = None
    is_vip:                   Optional[bool]             = None
    category:                 Optional[CustomerCategory] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not _PHONE_RE.match(v):
            raise ValueError("Invalid phone number format.")
        return v

    @field_validator("postal_code")
    @classmethod
    def validate_postal(cls, v: Optional[str]) -> Optional[str]:
        if v and not _POSTAL_RE.match(v):
            raise ValueError("Postal code must be 5–10 digits.")
        return v

    @field_validator("tax_id")
    @classmethod
    def validate_tax_id(cls, v: Optional[str]) -> Optional[str]:
        if v and not _TAX_RE.match(v):
            raise ValueError("tax_id must be 10–14 digits (Iranian national/tax ID).")
        return v


class CustomerCreate(CustomerBase):
    """All required fields must be provided on creation."""
    code:                     str             = Field(..., min_length=1, max_length=30)
    name:                     str             = Field(..., min_length=1, max_length=200)  # override → required
    credit_limit:             NonNeg          = Decimal("0")
    payment_terms:            int             = Field(30, ge=0, le=365)
    default_discount_percent: Pct             = Decimal("0")
    is_vip:                   bool            = False
    category:                 CustomerCategory = CustomerCategory.B

    @field_validator("code")
    @classmethod
    def upper_code(cls, v: str) -> str:
        return v.strip().upper()


class CustomerUpdate(CustomerBase):
    """All fields optional — PATCH semantics."""
    is_active: Optional[bool] = None


class CustomerResponse(BaseModel):
    model_config = _ro
    id:                       int
    code:                     str
    name:                     str
    name_fa:                  Optional[str]            = None
    tax_id:                   Optional[str]            = None
    economic_code:            Optional[str]            = None
    phone:                    Optional[str]            = None
    email:                    Optional[str]            = None
    address:                  Optional[str]            = None
    city:                     Optional[str]            = None
    postal_code:              Optional[str]            = None
    credit_limit:             Decimal
    payment_terms:            int
    default_discount_percent: Decimal
    is_vip:                   bool
    is_active:                bool
    category:                 CustomerCategory
    total_invoiced:           Decimal
    total_paid:               Decimal
    balance_due:              Decimal
    created_at:               datetime
    updated_at:               datetime


class CustomerStatementLine(BaseModel):
    model_config = _ro
    date:            date
    type:            str        # "invoice" | "payment"
    reference:       str
    debit:           Decimal    # invoice amount
    credit:          Decimal    # payment amount
    running_balance: Decimal


class CustomerStatement(BaseModel):
    customer_id:    int
    customer_name:  str
    as_of_date:     date
    lines:          list[CustomerStatementLine]
    total_invoiced: Decimal
    total_paid:     Decimal
    balance_due:    Decimal


# ===========================================================================
# Quote Lines
# ===========================================================================

class QuoteLineCreate(BaseModel):
    item_id:          int
    description:      str    = Field(..., min_length=1, max_length=500)
    quantity:         Pos
    unit_price:       NonNeg
    discount_percent: Pct    = Decimal("0")
    tax_percent:      Pct    = VAT_RATE
    sort_order:       int    = Field(0, ge=0)

    @field_validator("unit_price")
    @classmethod
    def price_precision(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.0001"))

    @property
    def line_total(self) -> Decimal:
        base = self.quantity * self.unit_price
        disc = base * self.discount_percent / Decimal("100")
        net  = base - disc
        tax  = net * self.tax_percent / Decimal("100")
        return (net + tax).quantize(Decimal("0.0001"))


class QuoteLineResponse(BaseModel):
    model_config = _ro
    id:               int
    item_id:          int
    description:      str
    quantity:         Decimal
    unit_price:       Decimal
    discount_percent: Decimal
    tax_percent:      Decimal
    line_total:       Decimal
    sort_order:       int


# ===========================================================================
# SalesQuote
# ===========================================================================

class QuoteCreate(BaseModel):
    customer_id: int
    quote_date:  date
    expiry_date: date
    notes:       Optional[str] = Field(None, max_length=2000)
    terms:       Optional[str] = Field(None, max_length=2000)
    lines:       list[QuoteLineCreate] = Field(..., min_length=1, max_length=500)

    @model_validator(mode="after")
    def expiry_after_date(self) -> "QuoteCreate":
        if self.expiry_date < self.quote_date:
            raise ValueError("expiry_date must be >= quote_date.")
        return self


class QuoteResponse(BaseModel):
    model_config = _ro
    id:                      int
    quote_number:            str
    customer_id:             int
    quote_date:              date
    expiry_date:             date
    status:                  QuoteStatus
    subtotal:                Decimal
    discount_amount:         Decimal
    tax_amount:              Decimal
    total:                   Decimal
    notes:                   Optional[str] = None
    terms:                   Optional[str] = None
    converted_to_invoice_id: Optional[int] = None
    lines:                   list[QuoteLineResponse] = []


# ===========================================================================
# Invoice Lines
# ===========================================================================

class InvoiceLineCreate(BaseModel):
    item_id:            int
    description:        str           = Field(..., min_length=1, max_length=500)
    unit_of_measure:    Optional[str] = Field(None, max_length=20)
    quantity:           Pos
    unit_price:         NonNeg
    discount_amount:    NonNeg        = Decimal("0")
    tax_percent:        Pct           = VAT_RATE
    sort_order:         int           = Field(0, ge=0)
    revenue_account_id: Optional[int] = None   # defaults to account 4100
    cogs_account_id:    Optional[int] = None   # defaults to account 5100

    @model_validator(mode="after")
    def discount_not_exceed_base(self) -> "InvoiceLineCreate":
        base = self.quantity * self.unit_price
        if self.discount_amount > base:
            raise ValueError(
                f"discount_amount ({self.discount_amount}) "
                f"cannot exceed line base ({base})."
            )
        return self


class InvoiceLineResponse(BaseModel):
    model_config = _ro
    id:                 int
    item_id:            int
    description:        str
    unit_of_measure:    Optional[str] = None
    quantity:           Decimal
    unit_price:         Decimal
    discount_amount:    Decimal
    tax_amount:         Decimal
    line_total:         Decimal
    unit_cost:          Decimal
    total_cost:         Decimal
    revenue_account_id: Optional[int] = None
    cogs_account_id:    Optional[int] = None
    sort_order:         int


# ===========================================================================
# SalesInvoice
# ===========================================================================

class InvoiceCreate(BaseModel):
    customer_id: int
    draft_date:  date
    due_date:    Optional[date] = None   # defaults to draft_date + customer.payment_terms
    quote_id:    Optional[int]  = None
    notes:       Optional[str]  = Field(None, max_length=2000)
    terms:       Optional[str]  = Field(None, max_length=2000)
    lines:       list[InvoiceLineCreate] = Field(..., min_length=1, max_length=500)

    @model_validator(mode="after")
    def due_after_draft(self) -> "InvoiceCreate":
        if self.due_date and self.due_date < self.draft_date:
            raise ValueError("due_date must be >= draft_date.")
        return self


class InvoiceResponse(BaseModel):
    model_config = _ro
    id:                       int
    invoice_number:           str
    customer_id:              int
    quote_id:                 Optional[int]  = None
    draft_date:               date
    issue_date:               Optional[date] = None
    due_date:                 Optional[date] = None
    subtotal:                 Decimal
    discount_amount:          Decimal
    tax_amount:               Decimal
    total_amount:             Decimal
    amount_paid:              Decimal
    amount_due:               Decimal
    status:                   InvoiceStatus
    revenue_journal_entry_id: Optional[int]  = None
    cogs_journal_entry_id:    Optional[int]  = None
    tax_invoice_number:       Optional[str]  = None
    qr_data:                  Optional[str]  = None
    notes:                    Optional[str]  = None
    lines:                    list[InvoiceLineResponse] = []


class InvoiceListItem(BaseModel):
    """Lightweight invoice for list views — no lines."""
    model_config = _ro
    id:             int
    invoice_number: str
    customer_id:    int
    customer_name:  Optional[str]  = None
    issue_date:     Optional[date] = None
    due_date:       Optional[date] = None
    total_amount:   Decimal
    amount_due:     Decimal
    status:         InvoiceStatus
    age_days:       Optional[int]  = None   # computed in service


# ===========================================================================
# SalesPayment
# ===========================================================================

class PaymentCreate(BaseModel):
    customer_id:      int
    invoice_id:       Optional[int]  = None
    payment_date:     date
    amount:           Pos
    method:           PaymentMethod  = PaymentMethod.BANK_TRANSFER
    bank_account_id:  Optional[int]  = None   # FK → finance.accounts (cash/bank)
    reference_number: Optional[str]  = Field(None, max_length=100)
    notes:            Optional[str]  = Field(None, max_length=1000)

    @field_validator("payment_date")
    @classmethod
    def not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("payment_date cannot be in the future.")
        return v


class PaymentAllocate(BaseModel):
    """Allocate an unallocated payment to a specific invoice."""
    invoice_id: int
    amount:     Pos


class PaymentResponse(BaseModel):
    model_config = _ro
    id:               int
    payment_number:   str
    customer_id:      int
    invoice_id:       Optional[int]  = None
    payment_date:     date
    amount:           Decimal
    method:           PaymentMethod
    reference_number: Optional[str]  = None
    journal_entry_id: Optional[int]  = None
    status:           PaymentStatus


# ===========================================================================
# Reports
# ===========================================================================

class RevenueByPeriodRow(BaseModel):
    period:        str      # "1403-01" (Jalali year-month)
    invoice_count: int
    subtotal:      Decimal
    discount:      Decimal
    tax:           Decimal
    total:         Decimal
    total_paid:    Decimal
    outstanding:   Decimal


class TopCustomerRow(BaseModel):
    customer_id:   int
    customer_code: str
    customer_name: str
    invoice_count: int
    total_revenue: Decimal
    total_paid:    Decimal
    balance_due:   Decimal


class ProductMarginRow(BaseModel):
    item_id:       int
    sku:           str
    item_name:     str
    quantity_sold: Decimal
    revenue:       Decimal
    cogs:          Decimal
    gross_profit:  Decimal
    margin_percent: Decimal


class TaxExportLine(BaseModel):
    """Format for Iranian tax authority (my.tax.gov.ir)."""
    invoice_number:     str
    tax_invoice_number: str
    issue_date:         str       # Jalali date string
    customer_name:      str
    customer_tax_id:    str
    economic_code:      str
    subtotal:           Decimal
    discount:           Decimal
    tax_base:           Decimal
    vat_amount:         Decimal
    total_amount:       Decimal
