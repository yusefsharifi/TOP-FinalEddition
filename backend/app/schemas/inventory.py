"""
Inventory Module - Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.inventory import AuditStatus, MovementStatus, MovementType

# ---------------------------------------------------------------------------
# Shared config
# ---------------------------------------------------------------------------
_ro = ConfigDict(from_attributes=True)  # read-only (response) models

# SKU: uppercase letters, digits, and hyphens, 3–50 chars
_SKU_RE = re.compile(r"^[A-Z0-9\-]{3,50}$")
# Supplier/Category code: similar but shorter
_CODE_RE = re.compile(r"^[A-Z0-9\-]{2,30}$")

PositiveDecimal = Annotated[Decimal, Field(gt=Decimal("0"))]
NonNegativeDecimal = Annotated[Decimal, Field(ge=Decimal("0"))]


# ===========================================================================
# InventoryCategory
# ===========================================================================
class InventoryCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=2, max_length=30)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.upper().strip()
        if not _CODE_RE.match(v):
            raise ValueError("Code must be 2-30 uppercase letters, digits, or hyphens")
        return v


class InventoryCategoryCreate(InventoryCategoryBase):
    pass


class InventoryCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class InventoryCategoryResponse(InventoryCategoryBase):
    model_config = _ro
    id: int
    created_at: datetime
    updated_at: datetime


# ===========================================================================
# Supplier
# ===========================================================================
class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=2, max_length=30)
    contact_name: Optional[str] = Field(None, max_length=150)
    email: Optional[str] = Field(None, max_length=254)
    phone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = None
    tax_number: Optional[str] = Field(None, max_length=50)
    payment_terms_days: int = Field(30, ge=0, le=365)
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.upper().strip()
        if not _CODE_RE.match(v):
            raise ValueError("Code must be 2-30 uppercase letters, digits, or hyphens")
        return v


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    payment_terms_days: Optional[int] = Field(None, ge=0, le=365)
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    model_config = _ro
    id: int
    created_at: datetime
    updated_at: datetime


# ===========================================================================
# InventoryItem
# ===========================================================================
class InventoryItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    unit_of_measure: str = Field(..., min_length=1, max_length=20)
    category_id: Optional[int] = None
    default_supplier_id: Optional[int] = None
    supplier_item_code: Optional[str] = Field(None, max_length=50)
    standard_cost: NonNegativeDecimal = Decimal("0.0000")
    selling_price: Optional[NonNegativeDecimal] = None
    global_reorder_point: NonNegativeDecimal = Decimal("0.0000")
    global_max_stock: Optional[NonNegativeDecimal] = None
    lead_time_days: int = Field(0, ge=0)
    is_active: bool = True
    allow_negative_stock: bool = False
    is_serialized: bool = False
    is_lot_tracked: bool = False

    @model_validator(mode="after")
    def validate_max_gt_reorder(self) -> "InventoryItemBase":
        if (
            self.global_max_stock is not None
            and self.global_max_stock <= self.global_reorder_point
        ):
            raise ValueError("global_max_stock must be greater than global_reorder_point")
        return self


class InventoryItemCreate(InventoryItemBase):
    # SKU is optional on create — service will auto-generate if omitted
    sku: Optional[str] = Field(None, min_length=3, max_length=50)

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper().strip()
        if not _SKU_RE.match(v):
            raise ValueError(
                "SKU must be 3-50 uppercase letters, digits, or hyphens (e.g. ITEM-001)"
            )
        return v


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    unit_of_measure: Optional[str] = Field(None, min_length=1, max_length=20)
    category_id: Optional[int] = None
    default_supplier_id: Optional[int] = None
    supplier_item_code: Optional[str] = None
    standard_cost: Optional[NonNegativeDecimal] = None
    selling_price: Optional[NonNegativeDecimal] = None
    global_reorder_point: Optional[NonNegativeDecimal] = None
    global_max_stock: Optional[NonNegativeDecimal] = None
    lead_time_days: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    allow_negative_stock: Optional[bool] = None


class InventoryItemResponse(InventoryItemBase):
    model_config = _ro
    id: int
    sku: str
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    last_purchase_price: Optional[Decimal] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None


class InventoryItemDetailResponse(InventoryItemResponse):
    """Full item response including all stock levels."""
    model_config = _ro
    category: Optional[InventoryCategoryResponse] = None
    default_supplier: Optional[SupplierResponse] = None
    stock_levels: list["StockLevelResponse"] = []


# ===========================================================================
# InventoryLocation
# ===========================================================================
class InventoryLocationBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=30)
    name: str = Field(..., min_length=1, max_length=150)
    warehouse: str = Field(..., min_length=1, max_length=80)
    zone: Optional[str] = Field(None, max_length=50)
    aisle: Optional[str] = Field(None, max_length=20)
    bin: Optional[str] = Field(None, max_length=20)
    capacity: Optional[NonNegativeDecimal] = None
    is_active: bool = True
    is_pickable: bool = True
    is_receivable: bool = True

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        return v.upper().strip()


class InventoryLocationCreate(InventoryLocationBase):
    pass


class InventoryLocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    zone: Optional[str] = None
    aisle: Optional[str] = None
    bin: Optional[str] = None
    capacity: Optional[NonNegativeDecimal] = None
    is_active: Optional[bool] = None
    is_pickable: Optional[bool] = None
    is_receivable: Optional[bool] = None


class InventoryLocationResponse(InventoryLocationBase):
    model_config = _ro
    id: int
    created_at: datetime
    updated_at: datetime


# ===========================================================================
# StockLevel
# ===========================================================================
class StockLevelResponse(BaseModel):
    model_config = _ro
    id: int
    item_id: int
    location_id: int
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_available: Decimal  # computed property
    reorder_point: Optional[Decimal] = None
    max_stock: Optional[Decimal] = None
    is_below_reorder: bool
    location: Optional[InventoryLocationResponse] = None
    updated_at: datetime


class StockAdjustRequest(BaseModel):
    """Manual stock adjustment — always creates an audit trail."""
    item_id: int
    location_id: int
    # Provide EITHER new_quantity (absolute) OR quantity_delta (relative), not both
    new_quantity: Optional[NonNegativeDecimal] = None
    quantity_delta: Optional[Decimal] = None  # can be negative for write-downs
    reason: str = Field(..., min_length=3, max_length=500)
    notes: Optional[str] = None
    external_reference: Optional[str] = Field(None, max_length=100)

    @model_validator(mode="after")
    def exactly_one_quantity_mode(self) -> "StockAdjustRequest":
        if self.new_quantity is None and self.quantity_delta is None:
            raise ValueError("Provide either new_quantity or quantity_delta")
        if self.new_quantity is not None and self.quantity_delta is not None:
            raise ValueError("Provide only one of new_quantity or quantity_delta, not both")
        return self


class StockTransferRequest(BaseModel):
    """Atomic transfer between two locations."""
    item_id: int
    from_location_id: int
    to_location_id: int
    quantity: PositiveDecimal
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    external_reference: Optional[str] = Field(None, max_length=100)

    @model_validator(mode="after")
    def different_locations(self) -> "StockTransferRequest":
        if self.from_location_id == self.to_location_id:
            raise ValueError("from_location_id and to_location_id must be different")
        return self


# ===========================================================================
# InventoryMovement
# ===========================================================================
class InboundMovementCreate(BaseModel):
    """Receive goods into a location."""
    item_id: int
    to_location_id: int
    quantity: PositiveDecimal
    unit_cost: Optional[NonNegativeDecimal] = None
    supplier_id: Optional[int] = None
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    external_reference: Optional[str] = Field(None, max_length=100)  # PO number etc.


class OutboundMovementCreate(BaseModel):
    """Issue goods from a location."""
    item_id: int
    from_location_id: int
    quantity: PositiveDecimal
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    external_reference: Optional[str] = Field(None, max_length=100)  # SO number etc.


class InventoryMovementResponse(BaseModel):
    model_config = _ro
    id: int
    reference_number: str
    item_id: int
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    supplier_id: Optional[int] = None
    movement_type: MovementType
    status: MovementStatus
    quantity: Decimal
    unit_cost: Optional[Decimal] = None
    quantity_before: Decimal
    quantity_after: Decimal
    movement_date: datetime
    reason: Optional[str] = None
    notes: Optional[str] = None
    external_reference: Optional[str] = None
    created_at: datetime
    created_by: Optional[int] = None


# ===========================================================================
# InventoryAudit
# ===========================================================================
class InventoryAuditCreate(BaseModel):
    description: Optional[str] = None
    location_id: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None


class InventoryAuditLineCreate(BaseModel):
    item_id: int
    location_id: int
    counted_quantity: NonNegativeDecimal


class InventoryAuditLineResponse(BaseModel):
    model_config = _ro
    id: int
    audit_id: int
    item_id: int
    location_id: int
    system_quantity: Decimal
    counted_quantity: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    is_reconciled: bool
    notes: Optional[str] = None


class InventoryAuditResponse(BaseModel):
    model_config = _ro
    id: int
    reference_number: str
    description: Optional[str] = None
    location_id: Optional[int] = None
    status: AuditStatus
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    approved_by: Optional[int] = None
    notes: Optional[str] = None
    lines: list[InventoryAuditLineResponse] = []
    created_at: datetime
    updated_at: datetime


# ===========================================================================
# Reports
# ===========================================================================
class LowStockReportItem(BaseModel):
    model_config = _ro
    item_id: int
    sku: str
    item_name: str
    location_id: int
    location_code: str
    quantity_on_hand: Decimal
    quantity_available: Decimal
    reorder_point: Decimal
    shortage: Decimal  # reorder_point - quantity_available


class MovementSummaryItem(BaseModel):
    model_config = _ro
    movement_type: MovementType
    item_id: int
    sku: str
    item_name: str
    total_quantity: Decimal
    movement_count: int
    period_start: datetime
    period_end: datetime


# ===========================================================================
# Pagination envelope
# ===========================================================================
class PaginatedResponse(BaseModel):
    """Generic pagination wrapper."""
    total: int
    limit: int
    offset: int
    items: list  # typed per endpoint via generics in the router
