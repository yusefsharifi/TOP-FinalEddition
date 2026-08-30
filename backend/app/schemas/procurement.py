"""
Procurement Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.procurement import (
    MatchResult, POLineStatus, POStatus, PRLineStatus, PRPriority, PRStatus,
    VendorCategory, VendorInvoiceStatus, VendorPaymentMethod, VendorPaymentStatus,
)

_ro = ConfigDict(from_attributes=True)
Pos = Annotated[Decimal, Field(gt=Decimal("0"))]
NonNeg = Annotated[Decimal, Field(ge=Decimal("0"))]
Pct = Annotated[Decimal, Field(ge=Decimal("0"), le=Decimal("100"))]
VAT = Decimal("9")


# ===========================================================================
# Vendor
# ===========================================================================
class VendorCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=200)
    name_fa: Optional[str] = None
    tax_id: Optional[str] = None
    economic_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    contact_person: Optional[str] = None
    credit_limit: NonNeg = Decimal("0")
    payment_terms: int = Field(30, ge=0, le=365)
    category: VendorCategory = VendorCategory.SUPPLIER
    is_approved: bool = False


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    name_fa: Optional[str] = None
    tax_id: Optional[str] = None
    economic_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    contact_person: Optional[str] = None
    credit_limit: Optional[NonNeg] = None
    payment_terms: Optional[int] = Field(None, ge=0, le=365)
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None
    category: Optional[VendorCategory] = None


class VendorResponse(VendorCreate):
    model_config = _ro
    id: int
    is_active: bool
    rating: int
    on_time_delivery_rate: float
    quality_score: float
    total_purchased: Decimal
    total_paid: Decimal
    balance_due: Decimal
    created_at: datetime
    updated_at: datetime


# ===========================================================================
# ApprovalRule
# ===========================================================================
class ApprovalRuleCreate(BaseModel):
    department: Optional[str] = None
    min_amount: NonNeg = Decimal("0")
    max_amount: Optional[Pos] = None
    approver_role: str = Field(..., min_length=1, max_length=50)
    approver_user_id: Optional[int] = None
    sort_order: int = 0
    description: Optional[str] = None


class ApprovalRuleResponse(ApprovalRuleCreate):
    model_config = _ro
    id: int
    is_active: bool


# ===========================================================================
# PurchaseRequest
# ===========================================================================
class PRLineCreate(BaseModel):
    item_id: Optional[int] = None
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Pos
    estimated_unit_price: NonNeg = Decimal("0")
    uom: Optional[str] = None
    specifications: Optional[str] = None
    sort_order: int = 0


class PRLineResponse(BaseModel):
    model_config = _ro
    id: int
    item_id: Optional[int] = None
    description: str
    quantity: Decimal
    estimated_unit_price: Decimal
    uom: Optional[str] = None
    status: PRLineStatus
    sort_order: int


class PRCreate(BaseModel):
    department: str = Field(..., min_length=1, max_length=100)
    priority: PRPriority = PRPriority.MEDIUM
    required_date: Optional[date] = None
    justification: Optional[str] = None
    lines: list[PRLineCreate] = Field(..., min_length=1)


class PRApprove(BaseModel):
    notes: Optional[str] = None


class PRReject(BaseModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class PRResponse(BaseModel):
    model_config = _ro
    id: int
    request_number: str
    requester_id: int
    department: str
    priority: PRPriority
    required_date: Optional[date] = None
    justification: Optional[str] = None
    status: PRStatus
    total_estimated: Decimal
    approver_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    lines: list[PRLineResponse] = []
    created_at: datetime


# ===========================================================================
# PurchaseOrder
# ===========================================================================
class POLineCreate(BaseModel):
    item_id: int
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Pos
    unit_price: NonNeg
    discount_percent: Pct = Decimal("0")
    tax_percent: Pct = VAT
    request_line_id: Optional[int] = None
    sort_order: int = 0


class POLineResponse(BaseModel):
    model_config = _ro
    id: int
    item_id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal
    tax_percent: Decimal
    line_total: Decimal
    quantity_received: Decimal
    quantity_invoiced: Decimal
    status: POLineStatus


class POCreate(BaseModel):
    vendor_id: int
    request_id: Optional[int] = None
    order_date: date
    expected_delivery: Optional[date] = None
    delivery_location_id: Optional[int] = None
    terms: Optional[str] = None
    notes: Optional[str] = None
    lines: list[POLineCreate] = Field(..., min_length=1)


class POResponse(BaseModel):
    model_config = _ro
    id: int
    po_number: str
    vendor_id: int
    request_id: Optional[int] = None
    order_date: date
    expected_delivery: Optional[date] = None
    actual_delivery: Optional[date] = None
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    shipping_cost: Decimal
    total_amount: Decimal
    status: POStatus
    lines: list[POLineResponse] = []
    created_at: datetime


# ===========================================================================
# GoodsReceipt
# ===========================================================================
class ReceiptLineCreate(BaseModel):
    po_line_id: int
    item_id: int
    quantity_received: Pos
    unit_price: NonNeg
    condition: str = "good"
    rejection_reason: Optional[str] = None


class ReceiptCreate(BaseModel):
    po_id: int
    receipt_date: date
    delivery_note_number: Optional[str] = None
    notes: Optional[str] = None
    lines: list[ReceiptLineCreate] = Field(..., min_length=1)


class ReceiptLineResponse(BaseModel):
    model_config = _ro
    id: int
    po_line_id: int
    item_id: int
    quantity_received: Decimal
    unit_price: Decimal
    condition: str
    stock_movement_id: Optional[int] = None


class ReceiptResponse(BaseModel):
    model_config = _ro
    id: int
    receipt_number: str
    po_id: int
    receipt_date: date
    received_by_id: int
    delivery_note_number: Optional[str] = None
    journal_entry_id: Optional[int] = None
    lines: list[ReceiptLineResponse] = []
    created_at: datetime


# ===========================================================================
# VendorInvoice
# ===========================================================================
class VendorInvoiceCreate(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=100)
    po_id: Optional[int] = None
    vendor_id: int
    invoice_date: date
    due_date: date
    received_date: Optional[date] = None
    amount: Pos
    tax_amount: NonNeg = Decimal("0")
    notes: Optional[str] = None

    @model_validator(mode="after")
    def total_computed(self) -> "VendorInvoiceCreate":
        return self

    @property
    def total_amount(self) -> Decimal:
        return self.amount + self.tax_amount


class VendorInvoiceResponse(BaseModel):
    model_config = _ro
    id: int
    invoice_number: str
    po_id: Optional[int] = None
    vendor_id: int
    invoice_date: date
    due_date: date
    amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    status: VendorInvoiceStatus
    match_result: Optional[MatchResult] = None
    match_notes: Optional[str] = None
    verified_by_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    journal_entry_id: Optional[int] = None
    created_at: datetime


# ===========================================================================
# 3-Way Match
# ===========================================================================
class ThreeWayMatchResult(BaseModel):
    po_id: int
    receipt_id: int
    invoice_id: int
    result: MatchResult
    po_total: Decimal
    receipt_total: Decimal
    invoice_total: Decimal
    qty_variance: Decimal
    price_variance_pct: Decimal
    notes: str
    auto_approved: bool


# ===========================================================================
# PaymentToVendor
# ===========================================================================
class VendorPaymentCreate(BaseModel):
    vendor_id: int
    vendor_invoice_id: Optional[int] = None
    payment_date: date
    amount: Pos
    method: VendorPaymentMethod = VendorPaymentMethod.BANK_TRANSFER
    bank_account_id: Optional[int] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class VendorPaymentResponse(BaseModel):
    model_config = _ro
    id: int
    payment_number: str
    vendor_id: int
    vendor_invoice_id: Optional[int] = None
    payment_date: date
    amount: Decimal
    method: VendorPaymentMethod
    reference_number: Optional[str] = None
    journal_entry_id: Optional[int] = None
    status: VendorPaymentStatus
    created_at: datetime


# ===========================================================================
# Reports
# ===========================================================================
class SpendByVendorRow(BaseModel):
    vendor_id: int
    vendor_code: str
    vendor_name: str
    po_count: int
    total_ordered: Decimal
    total_received: Decimal
    total_paid: Decimal
    balance_due: Decimal


class PriceHistoryRow(BaseModel):
    item_id: int
    sku: str
    item_name: str
    po_date: date
    vendor_name: str
    unit_price: Decimal
    quantity: Decimal


class DeliveryPerformanceRow(BaseModel):
    vendor_id: int
    vendor_name: str
    total_orders: int
    on_time_deliveries: int
    late_deliveries: int
    on_time_rate: float
    avg_delay_days: float


class PendingApprovalRow(BaseModel):
    request_id: int
    request_number: str
    requester_name: str
    department: str
    priority: PRPriority
    total_estimated: Decimal
    submitted_at: datetime
    required_approver_role: str
    days_pending: int
