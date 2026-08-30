"""
Procurement Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Purchase-to-Pay cycle:
  Vendor → PurchaseRequest → PurchaseOrder → GoodsReceipt → VendorInvoice → PaymentToVendor
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, Enum,
    Float, ForeignKey, Index, Integer, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)


class VendorCategory(str, enum.Enum):
    SUPPLIER = "supplier"
    CONTRACTOR = "contractor"
    SERVICE = "service"
    LOGISTICS = "logistics"
    OTHER = "other"


class PRPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PRStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED = "converted"


class PRLineStatus(str, enum.Enum):
    PENDING = "pending"
    FULFILLED = "fulfilled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class POStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    PARTIAL_RECEIVED = "partial_received"
    RECEIVED = "received"
    INVOICED = "invoiced"
    PAID = "paid"
    CANCELLED = "cancelled"


class POLineStatus(str, enum.Enum):
    ORDERED = "ordered"
    PARTIAL = "partial"
    RECEIVED = "received"
    INVOICED = "invoiced"
    CLOSED = "closed"


class VendorInvoiceStatus(str, enum.Enum):
    PENDING_VERIFICATION = "pending_verification"
    APPROVED = "approved"
    DISPUTED = "disputed"
    PAID = "paid"


class VendorPaymentMethod(str, enum.Enum):
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CASH = "cash"
    CREDIT_NOTE = "credit_note"


class VendorPaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CLEARED = "cleared"
    RECONCILED = "reconciled"


class MatchResult(str, enum.Enum):
    MATCH = "match"
    QUANTITY_MISMATCH = "quantity_mismatch"
    PRICE_MISMATCH = "price_mismatch"
    BOTH_MISMATCH = "both_mismatch"


# ---------------------------------------------------------------------------
# Vendor
# ---------------------------------------------------------------------------
class Vendor(AuditMixin, Base):
    """AP subledger entity. balance_due reconciles with GL 2110."""
    __tablename__ = "vendors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    economic_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    payment_terms: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    default_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="IRR")
    # Denormalised AP summary — updated on every receipt/payment
    total_purchased: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_paid: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    balance_due: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    # Evaluation metrics
    rating: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    on_time_delivery_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category: Mapped[VendorCategory] = mapped_column(Enum(VendorCategory), nullable=False, default=VendorCategory.SUPPLIER)
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="vendor")
    vendor_invoices: Mapped[list["VendorInvoice"]] = relationship("VendorInvoice", back_populates="vendor")
    payments: Mapped[list["PaymentToVendor"]] = relationship("PaymentToVendor", back_populates="vendor")
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="chk_vendor_rating"),
        CheckConstraint("credit_limit >= 0", name="chk_vendor_credit_limit"),
        Index("ix_vendors_code", "code"),
        Index("ix_vendors_is_active", "is_active"),
    )


# ---------------------------------------------------------------------------
# ApprovalRule
# ---------------------------------------------------------------------------
class ApprovalRule(AuditMixin, Base):
    """
    Threshold-based approval routing for Purchase Requests.
    Seed data: < 10M → MANAGER, 10–50M → DIRECTOR, > 50M → CFO
    """
    __tablename__ = "approval_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)   # null = all depts
    min_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    max_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)  # null = unlimited
    approver_role: Mapped[str] = mapped_column(String(50), nullable=False)
    approver_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    __table_args__ = (Index("ix_approval_rules_sort_order", "sort_order"),)


# ---------------------------------------------------------------------------
# PurchaseRequest  (درخواست خرید)
# ---------------------------------------------------------------------------
class PurchaseRequest(AuditMixin, Base):
    __tablename__ = "purchase_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    requester_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[PRPriority] = mapped_column(Enum(PRPriority), nullable=False, default=PRPriority.MEDIUM)
    required_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[PRStatus] = mapped_column(Enum(PRStatus), nullable=False, default=PRStatus.DRAFT, index=True)
    total_estimated: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    approver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lines: Mapped[list["PurchaseRequestLine"]] = relationship("PurchaseRequestLine", back_populates="request", cascade="all, delete-orphan")
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="request")
    __table_args__ = (
        Index("ix_purchase_requests_status", "status"),
        Index("ix_purchase_requests_department", "department"),
    )


class PurchaseRequestLine(AuditMixin, Base):
    __tablename__ = "purchase_request_lines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("purchase_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    estimated_unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    uom: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    specifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[PRLineStatus] = mapped_column(Enum(PRLineStatus), nullable=False, default=PRLineStatus.PENDING)
    converted_to_po_line_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    request: Mapped["PurchaseRequest"] = relationship("PurchaseRequest", back_populates="lines")
    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_pr_line_qty"),
        Index("ix_purchase_request_lines_request_id", "request_id"),
    )


# ---------------------------------------------------------------------------
# PurchaseOrder  (سفارش خرید)
# ---------------------------------------------------------------------------
class PurchaseOrder(AuditMixin, Base):
    __tablename__ = "purchase_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    po_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False, index=True)
    request_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("purchase_requests.id", ondelete="SET NULL"), nullable=True)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_delivery: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    status: Mapped[POStatus] = mapped_column(Enum(POStatus), nullable=False, default=POStatus.DRAFT, index=True)
    delivery_location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("inventory_locations.id", ondelete="SET NULL"), nullable=True)
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ap_invoice_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="purchase_orders")
    request: Mapped[Optional["PurchaseRequest"]] = relationship("PurchaseRequest", back_populates="purchase_orders")
    lines: Mapped[list["PurchaseOrderLine"]] = relationship("PurchaseOrderLine", back_populates="purchase_order", cascade="all, delete-orphan")
    receipts: Mapped[list["GoodsReceipt"]] = relationship("GoodsReceipt", back_populates="purchase_order")
    vendor_invoices: Mapped[list["VendorInvoice"]] = relationship("VendorInvoice", back_populates="purchase_order")
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="chk_po_total"),
        Index("ix_purchase_orders_vendor_id", "vendor_id"),
        Index("ix_purchase_orders_status", "status"),
        Index("ix_purchase_orders_order_date", "order_date"),
    )


class PurchaseOrderLine(AuditMixin, Base):
    __tablename__ = "purchase_order_lines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    request_line_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("purchase_request_lines.id", ondelete="SET NULL"), nullable=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    tax_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("9"))
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    quantity_received: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    quantity_invoiced: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    status: Mapped[POLineStatus] = mapped_column(Enum(POLineStatus), nullable=False, default=POLineStatus.ORDERED)
    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="lines")
    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_po_line_qty"),
        CheckConstraint("unit_price >= 0", name="chk_po_line_price"),
        CheckConstraint("quantity_received >= 0", name="chk_po_line_received"),
        Index("ix_purchase_order_lines_po_id", "po_id"),
    )


# ---------------------------------------------------------------------------
# GoodsReceipt  (رسید کالا)
# ---------------------------------------------------------------------------
class GoodsReceipt(AuditMixin, Base):
    """
    Physical receipt of goods against a PO.
    On acceptance → triggers inventory INBOUND + AP journal entry.
    Used as document in 3-way match: PO ↔ GoodsReceipt ↔ VendorInvoice.
    """
    __tablename__ = "goods_receipts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receipt_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    po_id: Mapped[int] = mapped_column(Integer, ForeignKey("purchase_orders.id", ondelete="RESTRICT"), nullable=False, index=True)
    receipt_date: Mapped[date] = mapped_column(Date, nullable=False)
    received_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    delivery_note_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    journal_entry_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True)
    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="receipts")
    lines: Mapped[list["GoodsReceiptLine"]] = relationship("GoodsReceiptLine", back_populates="receipt", cascade="all, delete-orphan")
    __table_args__ = (
        Index("ix_goods_receipts_po_id", "po_id"),
        Index("ix_goods_receipts_date", "receipt_date"),
    )


class GoodsReceiptLine(AuditMixin, Base):
    __tablename__ = "goods_receipt_lines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receipt_id: Mapped[int] = mapped_column(Integer, ForeignKey("goods_receipts.id", ondelete="CASCADE"), nullable=False, index=True)
    po_line_id: Mapped[int] = mapped_column(Integer, ForeignKey("purchase_order_lines.id", ondelete="RESTRICT"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False)
    quantity_received: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    condition: Mapped[str] = mapped_column(String(50), nullable=False, default="good")
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    stock_movement_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    receipt: Mapped["GoodsReceipt"] = relationship("GoodsReceipt", back_populates="lines")
    __table_args__ = (
        CheckConstraint("quantity_received > 0", name="chk_receipt_line_qty"),
        CheckConstraint("unit_price >= 0", name="chk_receipt_line_price"),
        Index("ix_goods_receipt_lines_receipt_id", "receipt_id"),
    )


# ---------------------------------------------------------------------------
# VendorInvoice  (فاکتور دریافتی)
# ---------------------------------------------------------------------------
class VendorInvoice(AuditMixin, Base):
    """
    Vendor's invoice to us.
    Must pass 3-way match before payment approval.
    JE created on approval (not receipt): Dr Inventory / Cr AP.
    """
    __tablename__ = "vendor_invoices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    po_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("purchase_orders.id", ondelete="SET NULL"), nullable=True, index=True)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False, index=True)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    received_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    amount_due: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    status: Mapped[VendorInvoiceStatus] = mapped_column(Enum(VendorInvoiceStatus), nullable=False, default=VendorInvoiceStatus.PENDING_VERIFICATION, index=True)
    match_result: Mapped[Optional[MatchResult]] = mapped_column(Enum(MatchResult), nullable=True)
    match_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    journal_entry_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="vendor_invoices")
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="vendor_invoices")
    payments: Mapped[list["PaymentToVendor"]] = relationship("PaymentToVendor", back_populates="vendor_invoice")
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="chk_vendor_invoice_total"),
        UniqueConstraint("vendor_id", "invoice_number", name="uq_vendor_invoice_number"),
        Index("ix_vendor_invoices_vendor_id", "vendor_id"),
        Index("ix_vendor_invoices_status", "status"),
        Index("ix_vendor_invoices_due_date", "due_date"),
    )


# ---------------------------------------------------------------------------
# PaymentToVendor  (پرداخت به تأمین‌کننده)
# ---------------------------------------------------------------------------
class PaymentToVendor(AuditMixin, Base):
    """Vendor payment. JE: Dr 2110 AP / Cr Bank."""
    __tablename__ = "payments_to_vendors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False, index=True)
    vendor_invoice_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("vendor_invoices.id", ondelete="SET NULL"), nullable=True, index=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    method: Mapped[VendorPaymentMethod] = mapped_column(Enum(VendorPaymentMethod), nullable=False, default=VendorPaymentMethod.BANK_TRANSFER)
    bank_account_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    journal_entry_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[VendorPaymentStatus] = mapped_column(Enum(VendorPaymentStatus), nullable=False, default=VendorPaymentStatus.PENDING, index=True)
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="payments")
    vendor_invoice: Mapped[Optional["VendorInvoice"]] = relationship("VendorInvoice", back_populates="payments")
    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_vendor_payment_positive"),
        Index("ix_payments_to_vendors_vendor_id", "vendor_id"),
    )