"""
Sales Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Quote-to-Cash cycle:
  Customer → SalesQuote → SalesInvoice → SalesPayment

Integration points:
  • SalesInvoice.journal_entry_id    → finance.journal_entries
  • SalesInvoice.stock_movement_id   → inventory.inventory_movements
  • SalesInvoiceLine.item_id         → inventory.inventory_items
  • SalesInvoiceLine.revenue_account_id / cogs_account_id → finance.accounts
  • SalesPayment.journal_entry_id    → finance.journal_entries

VAT: 9% standard rate (Iranian law, مالیات بر ارزش افزوده)
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
class CustomerCategory(str, enum.Enum):
    A = "A"   # Premium
    B = "B"   # Standard
    C = "C"   # Low-value


class QuoteStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIAL_PAID = "partial_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CHECK = "check"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    CREDIT_NOTE = "credit_note"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CLEARED = "cleared"
    BOUNCED = "bounced"


# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------
class Customer(AuditMixin, Base):
    """
    AR subledger entity.
    balance_due is denormalised — recomputed after each invoice/payment.
    GL reconciliation: balance_due should match account 1120 filtered by contact_id.
    """
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Identity
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Iranian legal fields
    tax_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)        # شناسه ملی / کد ملی
    economic_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # کد اقتصادی

    # Contact
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Financial settings
    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0")
    )
    payment_terms: Mapped[int] = mapped_column(Integer, nullable=False, default=30)  # days
    default_discount_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0")
    )

    # AR summary (denormalised — updated by SalesService)
    total_invoiced: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0")
    )
    total_paid: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0")
    )
    balance_due: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0")
    )

    # Status & classification
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category: Mapped[CustomerCategory] = mapped_column(
        Enum(CustomerCategory), nullable=False, default=CustomerCategory.B
    )

    # Relationships
    quotes: Mapped[list["SalesQuote"]] = relationship("SalesQuote", back_populates="customer")
    invoices: Mapped[list["SalesInvoice"]] = relationship("SalesInvoice", back_populates="customer")
    payments: Mapped[list["SalesPayment"]] = relationship("SalesPayment", back_populates="customer")

    __table_args__ = (
        CheckConstraint("credit_limit >= 0", name="chk_customer_credit_limit"),
        CheckConstraint(
            "default_discount_percent >= 0 AND default_discount_percent <= 100",
            name="chk_customer_discount",
        ),
        Index("ix_customers_code", "code"),
        Index("ix_customers_name", "name"),
        Index("ix_customers_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Customer {self.code} — {self.name}>"


# ---------------------------------------------------------------------------
# SalesQuote  (پیش‌فاکتور)
# ---------------------------------------------------------------------------
class SalesQuote(AuditMixin, Base):
    __tablename__ = "sales_quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    quote_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[QuoteStatus] = mapped_column(
        Enum(QuoteStatus), nullable=False, default=QuoteStatus.DRAFT, index=True
    )

    # Amounts
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Conversion tracking
    converted_to_invoice_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_invoices.id", ondelete="SET NULL"), nullable=True
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="quotes")
    lines: Mapped[list["SalesQuoteLine"]] = relationship(
        "SalesQuoteLine", back_populates="quote", cascade="all, delete-orphan"
    )
    invoice: Mapped[Optional["SalesInvoice"]] = relationship(
        "SalesInvoice", foreign_keys=[converted_to_invoice_id]
    )

    __table_args__ = (
        CheckConstraint("expiry_date >= quote_date", name="chk_quote_expiry"),
        Index("ix_sales_quotes_customer_id", "customer_id"),
        Index("ix_sales_quotes_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<SalesQuote {self.quote_number} {self.status}>"


class SalesQuoteLine(AuditMixin, Base):
    __tablename__ = "sales_quote_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_quotes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    discount_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0")
    )
    tax_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("9")  # 9% VAT
    )
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    quote: Mapped["SalesQuote"] = relationship("SalesQuote", back_populates="lines")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_quote_line_qty"),
        CheckConstraint("unit_price >= 0", name="chk_quote_line_price"),
        CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 100", name="chk_quote_line_discount"
        ),
        Index("ix_sales_quote_lines_quote_id", "quote_id"),
    )


# ---------------------------------------------------------------------------
# SalesInvoice  (فاکتور فروش)
# ---------------------------------------------------------------------------
class SalesInvoice(AuditMixin, Base):
    """
    Legal document — immutable once ISSUED (use cancel + re-issue to correct).
    On ISSUE, triggers:
      1. Journal entry: Dr AR / Cr Sales / Cr VAT
      2. Stock movements (OUTBOUND per line)
      3. COGS journal entry: Dr COGS / Cr Inventory
    """
    __tablename__ = "sales_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    quote_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_quotes.id", ondelete="SET NULL"), nullable=True
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Dates
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    draft_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Amounts (Decimal 18,4 — never float)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))

    # Payment tracking
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    amount_due: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))

    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT, index=True
    )

    # Accounting + inventory links (populated on ISSUE)
    revenue_journal_entry_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True
    )
    cogs_journal_entry_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True
    )
    # Primary stock movement (first line; others tracked per line)
    stock_movement_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Iranian tax compliance
    tax_invoice_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    tax_invoice_series: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    signature_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    qr_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON for QR code

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="invoices")
    lines: Mapped[list["SalesInvoiceLine"]] = relationship(
        "SalesInvoiceLine", back_populates="invoice", cascade="all, delete-orphan"
    )
    payments: Mapped[list["SalesPayment"]] = relationship(
        "SalesPayment", back_populates="invoice"
    )

    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="chk_invoice_total"),
        CheckConstraint("amount_paid >= 0", name="chk_invoice_paid"),
        CheckConstraint("amount_due >= 0", name="chk_invoice_due"),
        Index("ix_sales_invoices_customer_id", "customer_id"),
        Index("ix_sales_invoices_status", "status"),
        Index("ix_sales_invoices_issue_date", "issue_date"),
        Index("ix_sales_invoices_due_date", "due_date"),
    )

    def __repr__(self) -> str:
        return f"<SalesInvoice {self.invoice_number} {self.status}>"


class SalesInvoiceLine(AuditMixin, Base):
    __tablename__ = "sales_invoice_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    unit_of_measure: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Pricing
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0")
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0")
    )
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    # Cost snapshot (FIFO cost at time of sale — immutable after issue)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))

    # GL account links
    revenue_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    cogs_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )

    # Per-line stock movement ID (populated on issue)
    stock_movement_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    invoice: Mapped["SalesInvoice"] = relationship("SalesInvoice", back_populates="lines")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_invoice_line_qty"),
        CheckConstraint("unit_price >= 0", name="chk_invoice_line_price"),
        Index("ix_sales_invoice_lines_invoice_id", "invoice_id"),
    )


# ---------------------------------------------------------------------------
# SalesPayment  (دریافت وجه)
# ---------------------------------------------------------------------------
class SalesPayment(AuditMixin, Base):
    """
    Payment received from customer.
    On creation, triggers JE: Dr Cash/Bank / Cr AR
    Can be linked to a specific invoice or left unallocated (advance).
    """
    __tablename__ = "sales_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    invoice_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_invoices.id", ondelete="SET NULL"), nullable=True, index=True
    )

    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), nullable=False, default=PaymentMethod.BANK_TRANSFER
    )

    # Bank details
    bank_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Accounting link
    journal_entry_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="payments")
    invoice: Mapped[Optional["SalesInvoice"]] = relationship(
        "SalesInvoice", back_populates="payments"
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_payment_amount_positive"),
        Index("ix_sales_payments_customer_id", "customer_id"),
        Index("ix_sales_payments_payment_date", "payment_date"),
        Index("ix_sales_payments_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<SalesPayment {self.payment_number} {self.amount} {self.status}>"