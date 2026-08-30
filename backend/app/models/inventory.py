"""
Inventory Module - SQLAlchemy 2.0 Models
TOP WorX ERP System
"""
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

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
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class MovementType(str, enum.Enum):
    INBOUND = "inbound"       # receiving goods
    OUTBOUND = "outbound"     # issuing goods
    TRANSFER = "transfer"     # location-to-location
    ADJUSTMENT = "adjustment" # manual correction
    RETURN = "return"         # returned to stock
    SCRAP = "scrap"           # write-off / disposal


class MovementStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AuditStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"


# ---------------------------------------------------------------------------
# InventoryCategory  (self-referential hierarchy)
# ---------------------------------------------------------------------------
class InventoryCategory(AuditMixin, Base):
    __tablename__ = "inventory_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("inventory_categories.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    parent: Mapped[Optional["InventoryCategory"]] = relationship(
        "InventoryCategory", remote_side="InventoryCategory.id", back_populates="children"
    )
    children: Mapped[list["InventoryCategory"]] = relationship(
        "InventoryCategory", back_populates="parent"
    )
    items: Mapped[list["InventoryItem"]] = relationship(
        "InventoryItem", back_populates="category"
    )

    __table_args__ = (
        Index("ix_inventory_categories_parent_id", "parent_id"),
        Index("ix_inventory_categories_code", "code"),
    )

    def __repr__(self) -> str:
        return f"<InventoryCategory id={self.id} code={self.code}>"


# ---------------------------------------------------------------------------
# Supplier
# ---------------------------------------------------------------------------
class Supplier(AuditMixin, Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(254), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tax_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_terms_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    items: Mapped[list["InventoryItem"]] = relationship(
        "InventoryItem", back_populates="default_supplier"
    )
    movements: Mapped[list["InventoryMovement"]] = relationship(
        "InventoryMovement", back_populates="supplier"
    )

    __table_args__ = (
        Index("ix_suppliers_code", "code"),
        Index("ix_suppliers_name", "name"),
    )

    def __repr__(self) -> str:
        return f"<Supplier id={self.id} code={self.code}>"


# ---------------------------------------------------------------------------
# InventoryItem
# ---------------------------------------------------------------------------
class InventoryItem(AuditMixin, Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Identification
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    qr_code: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # base64 or path

    # Classification
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("inventory_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False)  # pcs, kg, box …

    # Supplier
    default_supplier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    supplier_item_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Costing
    standard_cost: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0.0000")
    )
    last_purchase_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 4), nullable=True
    )
    selling_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)

    # Reorder / limits (defaults; per-location overrides live in StockLevel)
    global_reorder_point: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0.0000")
    )
    global_max_stock: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_negative_stock: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_serialized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_lot_tracked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Image
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    category: Mapped[Optional["InventoryCategory"]] = relationship(
        "InventoryCategory", back_populates="items"
    )
    default_supplier: Mapped[Optional["Supplier"]] = relationship(
        "Supplier", back_populates="items"
    )
    stock_levels: Mapped[list["StockLevel"]] = relationship(
        "StockLevel", back_populates="item", cascade="all, delete-orphan"
    )
    movements: Mapped[list["InventoryMovement"]] = relationship(
        "InventoryMovement", back_populates="item"
    )
    audit_lines: Mapped[list["InventoryAuditLine"]] = relationship(
        "InventoryAuditLine", back_populates="item"
    )

    __table_args__ = (
        Index("ix_inventory_items_sku", "sku"),
        Index("ix_inventory_items_barcode", "barcode"),
        Index("ix_inventory_items_category_id", "category_id"),
        Index("ix_inventory_items_name", "name"),
        CheckConstraint("standard_cost >= 0", name="chk_items_standard_cost_non_negative"),
        CheckConstraint(
            "global_reorder_point >= 0", name="chk_items_reorder_point_non_negative"
        ),
        CheckConstraint(
            "global_max_stock IS NULL OR global_max_stock > global_reorder_point",
            name="chk_items_max_gt_reorder",
        ),
    )

    def __repr__(self) -> str:
        return f"<InventoryItem id={self.id} sku={self.sku}>"


# ---------------------------------------------------------------------------
# InventoryLocation
# ---------------------------------------------------------------------------
class InventoryLocation(AuditMixin, Base):
    __tablename__ = "inventory_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    # Hierarchy  (all optional — you may use only warehouse-level)
    warehouse: Mapped[str] = mapped_column(String(80), nullable=False)
    zone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    aisle: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    capacity: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_pickable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_receivable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    stock_levels: Mapped[list["StockLevel"]] = relationship(
        "StockLevel", back_populates="location", cascade="all, delete-orphan"
    )
    movements_from: Mapped[list["InventoryMovement"]] = relationship(
        "InventoryMovement",
        back_populates="from_location",
        foreign_keys="InventoryMovement.from_location_id",
    )
    movements_to: Mapped[list["InventoryMovement"]] = relationship(
        "InventoryMovement",
        back_populates="to_location",
        foreign_keys="InventoryMovement.to_location_id",
    )

    __table_args__ = (
        Index("ix_inventory_locations_code", "code"),
        Index("ix_inventory_locations_warehouse", "warehouse"),
    )

    def __repr__(self) -> str:
        return f"<InventoryLocation id={self.id} code={self.code}>"


# ---------------------------------------------------------------------------
# StockLevel  (junction: item × location)
# ---------------------------------------------------------------------------
class StockLevel(AuditMixin, Base):
    __tablename__ = "stock_levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False
    )
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_locations.id", ondelete="CASCADE"), nullable=False
    )

    quantity_on_hand: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0.0000")
    )
    quantity_reserved: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("0.0000")
    )
    # quantity_available is a computed property — not stored (avoids sync issues)

    reorder_point: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 4), nullable=True
    )  # None = fall back to item.global_reorder_point
    max_stock: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)

    # Relationships
    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="stock_levels")
    location: Mapped["InventoryLocation"] = relationship(
        "InventoryLocation", back_populates="stock_levels"
    )

    @property
    def quantity_available(self) -> Decimal:
        return self.quantity_on_hand - self.quantity_reserved

    @property
    def effective_reorder_point(self) -> Decimal:
        if self.reorder_point is not None:
            return self.reorder_point
        return self.item.global_reorder_point if self.item else Decimal("0")

    @property
    def is_below_reorder(self) -> bool:
        return self.quantity_on_hand <= self.effective_reorder_point

    __table_args__ = (
        UniqueConstraint("item_id", "location_id", name="uq_stock_levels_item_location"),
        Index("ix_stock_levels_item_id", "item_id"),
        Index("ix_stock_levels_location_id", "location_id"),
        CheckConstraint("quantity_on_hand >= 0", name="chk_stock_qty_on_hand_non_negative"),
        CheckConstraint(
            "quantity_reserved >= 0", name="chk_stock_qty_reserved_non_negative"
        ),
        CheckConstraint(
            "quantity_reserved <= quantity_on_hand",
            name="chk_stock_reserved_lte_on_hand",
        ),
        CheckConstraint(
            "reorder_point IS NULL OR reorder_point >= 0",
            name="chk_stock_reorder_point_non_negative",
        ),
        CheckConstraint(
            "max_stock IS NULL OR reorder_point IS NULL OR max_stock > reorder_point",
            name="chk_stock_max_gt_reorder",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<StockLevel item_id={self.item_id} location_id={self.location_id} "
            f"on_hand={self.quantity_on_hand}>"
        )


# ---------------------------------------------------------------------------
# InventoryMovement  (immutable audit trail)
# ---------------------------------------------------------------------------
class InventoryMovement(AuditMixin, Base):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_number: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )

    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False
    )
    from_location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("inventory_locations.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    to_location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("inventory_locations.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    supplier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True
    )

    movement_type: Mapped[MovementType] = mapped_column(
        Enum(MovementType), nullable=False, index=True
    )
    status: Mapped[MovementStatus] = mapped_column(
        Enum(MovementStatus), nullable=False, default=MovementStatus.COMPLETED
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)

    # Snapshot values at time of movement (immutable record)
    quantity_before: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    quantity_after: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    movement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True
    )
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # External references (PO number, SO number, etc.)
    external_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="movements")
    from_location: Mapped[Optional["InventoryLocation"]] = relationship(
        "InventoryLocation",
        back_populates="movements_from",
        foreign_keys=[from_location_id],
    )
    to_location: Mapped[Optional["InventoryLocation"]] = relationship(
        "InventoryLocation",
        back_populates="movements_to",
        foreign_keys=[to_location_id],
    )
    supplier: Mapped[Optional["Supplier"]] = relationship(
        "Supplier", back_populates="movements"
    )

    __table_args__ = (
        Index("ix_inventory_movements_item_id", "item_id"),
        Index("ix_inventory_movements_movement_date", "movement_date"),
        Index("ix_inventory_movements_type", "movement_type"),
        CheckConstraint("quantity > 0", name="chk_movements_quantity_positive"),
    )

    def __repr__(self) -> str:
        return (
            f"<InventoryMovement id={self.id} ref={self.reference_number} "
            f"type={self.movement_type}>"
        )


# ---------------------------------------------------------------------------
# InventoryAudit  (physical count sessions)
# ---------------------------------------------------------------------------
class InventoryAudit(AuditMixin, Base):
    __tablename__ = "inventory_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_number: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("inventory_locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[AuditStatus] = mapped_column(
        Enum(AuditStatus), nullable=False, default=AuditStatus.DRAFT
    )
    scheduled_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    lines: Mapped[list["InventoryAuditLine"]] = relationship(
        "InventoryAuditLine", back_populates="audit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<InventoryAudit id={self.id} ref={self.reference_number}>"


# ---------------------------------------------------------------------------
# InventoryAuditLine  (per-item count result)
# ---------------------------------------------------------------------------
class InventoryAuditLine(AuditMixin, Base):
    __tablename__ = "inventory_audit_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_audits.id", ondelete="CASCADE"), nullable=False
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False
    )
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_locations.id", ondelete="RESTRICT"), nullable=False
    )

    system_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    counted_quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)
    variance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 4), nullable=True
    )  # counted - system; populated after count
    is_reconciled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    audit: Mapped["InventoryAudit"] = relationship("InventoryAudit", back_populates="lines")
    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="audit_lines")

    __table_args__ = (
        UniqueConstraint("audit_id", "item_id", "location_id", name="uq_audit_item_location"),
        Index("ix_inventory_audit_lines_audit_id", "audit_id"),
        Index("ix_inventory_audit_lines_item_id", "item_id"),
    )

    def __repr__(self) -> str:
        return f"<InventoryAuditLine audit_id={self.audit_id} item_id={self.item_id}>"
