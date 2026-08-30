"""inventory_module

Revision ID: 0001_inventory_module
Revises: (set to your previous revision or leave empty for first migration)
Create Date: 2024-01-01 00:00:00.000000

Creates:
  - inventory_categories
  - suppliers
  - inventory_items
  - inventory_locations
  - stock_levels
  - inventory_movements
  - inventory_audits
  - inventory_audit_lines

Includes seed data for root categories and units of measure (as categories).
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "0001_inventory_module"
down_revision = None  # CHANGE: set to your current head revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # inventory_categories
    # ------------------------------------------------------------------
    op.create_table(
        "inventory_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("inventory_categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_inventory_categories_code", "inventory_categories", ["code"])
    op.create_index("ix_inventory_categories_parent_id", "inventory_categories", ["parent_id"])

    # ------------------------------------------------------------------
    # suppliers
    # ------------------------------------------------------------------
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("contact_name", sa.String(150), nullable=True),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("tax_number", sa.String(50), nullable=True),
        sa.Column("payment_terms_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_suppliers_code", "suppliers", ["code"])
    op.create_index("ix_suppliers_name", "suppliers", ["name"])

    # ------------------------------------------------------------------
    # inventory_items
    # ------------------------------------------------------------------
    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sku", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("barcode", sa.String(50), nullable=True, unique=True),
        sa.Column("qr_code", sa.String(500), nullable=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("inventory_categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("unit_of_measure", sa.String(20), nullable=False),
        sa.Column("default_supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("supplier_item_code", sa.String(50), nullable=True),
        sa.Column("standard_cost", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("last_purchase_price", sa.Numeric(18, 4), nullable=True),
        sa.Column("selling_price", sa.Numeric(18, 4), nullable=True),
        sa.Column("global_reorder_point", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("global_max_stock", sa.Numeric(18, 4), nullable=True),
        sa.Column("lead_time_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("allow_negative_stock", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_serialized", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_lot_tracked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("standard_cost >= 0", name="chk_items_standard_cost_non_negative"),
        sa.CheckConstraint("global_reorder_point >= 0", name="chk_items_reorder_point_non_negative"),
        sa.CheckConstraint(
            "global_max_stock IS NULL OR global_max_stock > global_reorder_point",
            name="chk_items_max_gt_reorder",
        ),
    )
    op.create_index("ix_inventory_items_sku", "inventory_items", ["sku"])
    op.create_index("ix_inventory_items_barcode", "inventory_items", ["barcode"])
    op.create_index("ix_inventory_items_category_id", "inventory_items", ["category_id"])
    op.create_index("ix_inventory_items_name", "inventory_items", ["name"])

    # ------------------------------------------------------------------
    # inventory_locations
    # ------------------------------------------------------------------
    op.create_table(
        "inventory_locations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("warehouse", sa.String(80), nullable=False),
        sa.Column("zone", sa.String(50), nullable=True),
        sa.Column("aisle", sa.String(20), nullable=True),
        sa.Column("bin", sa.String(20), nullable=True),
        sa.Column("capacity", sa.Numeric(18, 4), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_pickable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_receivable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_inventory_locations_code", "inventory_locations", ["code"])
    op.create_index("ix_inventory_locations_warehouse", "inventory_locations", ["warehouse"])

    # ------------------------------------------------------------------
    # stock_levels
    # ------------------------------------------------------------------
    op.create_table(
        "stock_levels",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("inventory_locations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity_on_hand", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("quantity_reserved", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("reorder_point", sa.Numeric(18, 4), nullable=True),
        sa.Column("max_stock", sa.Numeric(18, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("item_id", "location_id", name="uq_stock_levels_item_location"),
        sa.CheckConstraint("quantity_on_hand >= 0", name="chk_stock_qty_on_hand_non_negative"),
        sa.CheckConstraint("quantity_reserved >= 0", name="chk_stock_qty_reserved_non_negative"),
        sa.CheckConstraint("quantity_reserved <= quantity_on_hand", name="chk_stock_reserved_lte_on_hand"),
        sa.CheckConstraint("reorder_point IS NULL OR reorder_point >= 0", name="chk_stock_reorder_point_non_negative"),
        sa.CheckConstraint("max_stock IS NULL OR reorder_point IS NULL OR max_stock > reorder_point", name="chk_stock_max_gt_reorder"),
    )
    op.create_index("ix_stock_levels_item_id", "stock_levels", ["item_id"])
    op.create_index("ix_stock_levels_location_id", "stock_levels", ["location_id"])

    # ------------------------------------------------------------------
    # inventory_movements  (append-only audit log)
    # ------------------------------------------------------------------
    movement_type_enum = postgresql.ENUM(
        "inbound", "outbound", "transfer", "adjustment", "return", "scrap",
        name="movementtype", create_type=True
    )
    movement_status_enum = postgresql.ENUM(
        "pending", "completed", "cancelled",
        name="movementstatus", create_type=True
    )
    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("reference_number", sa.String(50), nullable=False, unique=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("from_location_id", sa.Integer(), sa.ForeignKey("inventory_locations.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("to_location_id", sa.Integer(), sa.ForeignKey("inventory_locations.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("movement_type", movement_type_enum, nullable=False),
        sa.Column("status", movement_status_enum, nullable=False, server_default="completed"),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(18, 4), nullable=True),
        sa.Column("quantity_before", sa.Numeric(18, 4), nullable=False),
        sa.Column("quantity_after", sa.Numeric(18, 4), nullable=False),
        sa.Column("movement_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("external_reference", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("quantity > 0", name="chk_movements_quantity_positive"),
    )
    op.create_index("ix_inventory_movements_item_id", "inventory_movements", ["item_id"])
    op.create_index("ix_inventory_movements_movement_date", "inventory_movements", ["movement_date"])
    op.create_index("ix_inventory_movements_type", "inventory_movements", ["movement_type"])
    op.create_index("ix_inventory_movements_reference_number", "inventory_movements", ["reference_number"])

    # ------------------------------------------------------------------
    # inventory_audits
    # ------------------------------------------------------------------
    audit_status_enum = postgresql.ENUM(
        "draft", "in_progress", "completed", "approved",
        name="auditstatus", create_type=True
    )
    op.create_table(
        "inventory_audits",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("reference_number", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("inventory_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", audit_status_enum, nullable=False, server_default="draft"),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_inventory_audits_reference_number", "inventory_audits", ["reference_number"])
    op.create_index("ix_inventory_audits_location_id", "inventory_audits", ["location_id"])

    # ------------------------------------------------------------------
    # inventory_audit_lines
    # ------------------------------------------------------------------
    op.create_table(
        "inventory_audit_lines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("audit_id", sa.Integer(), sa.ForeignKey("inventory_audits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("inventory_locations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("system_quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("counted_quantity", sa.Numeric(18, 4), nullable=True),
        sa.Column("variance", sa.Numeric(18, 4), nullable=True),
        sa.Column("is_reconciled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("audit_id", "item_id", "location_id", name="uq_audit_item_location"),
    )
    op.create_index("ix_inventory_audit_lines_audit_id", "inventory_audit_lines", ["audit_id"])
    op.create_index("ix_inventory_audit_lines_item_id", "inventory_audit_lines", ["item_id"])

    # ------------------------------------------------------------------
    # Seed data
    # ------------------------------------------------------------------
    now = datetime.utcnow()

    # Root categories
    op.bulk_insert(
        sa.table(
            "inventory_categories",
            sa.column("name", sa.String),
            sa.column("code", sa.String),
            sa.column("description", sa.String),
            sa.column("is_active", sa.Boolean),
        ),
        [
            {"name": "Raw Materials",    "code": "RAW",   "description": "Unprocessed materials", "is_active": True},
            {"name": "Finished Goods",   "code": "FG",    "description": "Ready-to-sell products", "is_active": True},
            {"name": "Spare Parts",      "code": "SPARE", "description": "Equipment spare parts",  "is_active": True},
            {"name": "Consumables",      "code": "CONS",  "description": "Supplies and consumables", "is_active": True},
            {"name": "Tools",            "code": "TOOL",  "description": "Tools and equipment",    "is_active": True},
            {"name": "Packaging",        "code": "PKG",   "description": "Packaging materials",    "is_active": True},
            {"name": "Office Supplies",  "code": "OFFICE","description": "Office stationery",      "is_active": True},
        ],
    )


def downgrade() -> None:
    op.drop_table("inventory_audit_lines")
    op.drop_table("inventory_audits")
    op.drop_table("inventory_movements")
    op.drop_table("stock_levels")
    op.drop_table("inventory_locations")
    op.drop_table("inventory_items")
    op.drop_table("suppliers")
    op.drop_table("inventory_categories")

    # Drop PostgreSQL enums
    op.execute("DROP TYPE IF EXISTS movementtype")
    op.execute("DROP TYPE IF EXISTS movementstatus")
    op.execute("DROP TYPE IF EXISTS auditstatus")
