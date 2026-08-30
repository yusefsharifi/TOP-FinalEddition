"""Procurement module — vendors, approval_rules, purchase_requests,
purchase_orders, goods_receipts, vendor_invoices, payments_to_vendors.

Revision ID: 0004_procurement_module
Revises: 0003_sales_module
Create Date: 2024-01-01 00:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004_procurement_module"
down_revision = "0003_sales_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    vendor_cat = postgresql.ENUM(
        "supplier", "contractor", "service", "logistics", "other",
        name="vendorcategory", create_type=True,
    )
    pr_priority = postgresql.ENUM("low", "medium", "high", "critical", name="prpriority", create_type=True)
    pr_status = postgresql.ENUM("draft", "pending_approval", "approved", "rejected", "converted", name="prstatus", create_type=True)
    pr_line_status = postgresql.ENUM("pending", "fulfilled", "partial", "cancelled", name="prlinestatus", create_type=True)
    po_status = postgresql.ENUM("draft", "sent", "acknowledged", "partial_received", "received", "invoiced", "paid", "cancelled", name="postatus", create_type=True)
    po_line_status = postgresql.ENUM("ordered", "partial", "received", "invoiced", "closed", name="polinestatus", create_type=True)
    vi_status = postgresql.ENUM("pending_verification", "approved", "disputed", "paid", name="vendorinvoicestatus", create_type=True)
    vp_method = postgresql.ENUM("bank_transfer", "check", "cash", "credit_note", name="vendorpaymentmethod", create_type=True)
    vp_status = postgresql.ENUM("pending", "cleared", "reconciled", name="vendorpaymentstatus", create_type=True)
    match_result = postgresql.ENUM("match", "quantity_mismatch", "price_mismatch", "both_mismatch", name="matchresult", create_type=True)

    # ── vendors ────────────────────────────────────────────────────────────
    op.create_table(
        "vendors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=True),
        sa.Column("tax_id", sa.String(20), nullable=True),
        sa.Column("economic_code", sa.String(20), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("contact_person", sa.String(200), nullable=True),
        sa.Column("credit_limit", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("payment_terms", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("default_currency", sa.String(3), nullable=False, server_default="IRR"),
        sa.Column("total_purchased", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_paid", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("balance_due", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("rating", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("on_time_delivery_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("quality_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("category", vendor_cat, nullable=False, server_default="supplier"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="chk_vendor_rating"),
        sa.CheckConstraint("credit_limit >= 0", name="chk_vendor_credit_limit"),
    )
    op.create_index("ix_vendors_code", "vendors", ["code"])
    op.create_index("ix_vendors_is_active", "vendors", ["is_active"])

    # ── approval_rules ────────────────────────────────────────────────────
    op.create_table(
        "approval_rules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("min_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("max_amount", sa.Numeric(18, 4), nullable=True),
        sa.Column("approver_role", sa.String(50), nullable=False),
        sa.Column("approver_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_approval_rules_sort_order", "approval_rules", ["sort_order"])

    # ── purchase_requests ─────────────────────────────────────────────────
    op.create_table(
        "purchase_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("request_number", sa.String(30), nullable=False, unique=True),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("priority", pr_priority, nullable=False, server_default="medium"),
        sa.Column("required_date", sa.Date(), nullable=True),
        sa.Column("justification", sa.Text(), nullable=True),
        sa.Column("status", pr_status, nullable=False, server_default="draft"),
        sa.Column("total_estimated", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("approver_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approval_notes", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_purchase_requests_status", "purchase_requests", ["status"])
    op.create_index("ix_purchase_requests_department", "purchase_requests", ["department"])

    # ── purchase_request_lines ────────────────────────────────────────────
    op.create_table(
        "purchase_request_lines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("purchase_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("estimated_unit_price", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("uom", sa.String(20), nullable=True),
        sa.Column("specifications", sa.Text(), nullable=True),
        sa.Column("status", pr_line_status, nullable=False, server_default="pending"),
        sa.Column("converted_to_po_line_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("quantity > 0", name="chk_pr_line_qty"),
    )
    op.create_index("ix_purchase_request_lines_request_id", "purchase_request_lines", ["request_id"])

    # ── purchase_orders ───────────────────────────────────────────────────
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("po_number", sa.String(30), nullable=False, unique=True),
        sa.Column("vendor_id", sa.Integer(), sa.ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("purchase_requests.id", ondelete="SET NULL"), nullable=True),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("expected_delivery", sa.Date(), nullable=True),
        sa.Column("actual_delivery", sa.Date(), nullable=True),
        sa.Column("subtotal", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("shipping_cost", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("status", po_status, nullable=False, server_default="draft"),
        sa.Column("delivery_location_id", sa.Integer(), sa.ForeignKey("inventory_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("ap_invoice_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("total_amount >= 0", name="chk_po_total"),
    )
    op.create_index("ix_purchase_orders_vendor_id", "purchase_orders", ["vendor_id"])
    op.create_index("ix_purchase_orders_status", "purchase_orders", ["status"])
    op.create_index("ix_purchase_orders_order_date", "purchase_orders", ["order_date"])

    # ── purchase_order_lines ──────────────────────────────────────────────
    op.create_table(
        "purchase_order_lines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("po_id", sa.Integer(), sa.ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("request_line_id", sa.Integer(), sa.ForeignKey("purchase_request_lines.id", ondelete="SET NULL"), nullable=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("discount_percent", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("tax_percent", sa.Numeric(5, 2), nullable=False, server_default="9"),
        sa.Column("line_total", sa.Numeric(18, 4), nullable=False),
        sa.Column("quantity_received", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("quantity_invoiced", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("status", po_line_status, nullable=False, server_default="ordered"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("quantity > 0", name="chk_po_line_qty"),
        sa.CheckConstraint("unit_price >= 0", name="chk_po_line_price"),
        sa.CheckConstraint("quantity_received >= 0", name="chk_po_line_received"),
    )
    op.create_index("ix_purchase_order_lines_po_id", "purchase_order_lines", ["po_id"])

    # ── goods_receipts ────────────────────────────────────────────────────
    op.create_table(
        "goods_receipts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("receipt_number", sa.String(30), nullable=False, unique=True),
        sa.Column("po_id", sa.Integer(), sa.ForeignKey("purchase_orders.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("receipt_date", sa.Date(), nullable=False),
        sa.Column("received_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("delivery_note_number", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("journal_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_goods_receipts_po_id", "goods_receipts", ["po_id"])
    op.create_index("ix_goods_receipts_date", "goods_receipts", ["receipt_date"])

    # ── goods_receipt_lines ───────────────────────────────────────────────
    op.create_table(
        "goods_receipt_lines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("receipt_id", sa.Integer(), sa.ForeignKey("goods_receipts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("po_line_id", sa.Integer(), sa.ForeignKey("purchase_order_lines.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity_received", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("condition", sa.String(50), nullable=False, server_default="good"),
        sa.Column("rejection_reason", sa.String(500), nullable=True),
        sa.Column("stock_movement_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("quantity_received > 0", name="chk_receipt_line_qty"),
        sa.CheckConstraint("unit_price >= 0", name="chk_receipt_line_price"),
    )
    op.create_index("ix_goods_receipt_lines_receipt_id", "goods_receipt_lines", ["receipt_id"])

    # ── vendor_invoices ───────────────────────────────────────────────────
    op.create_table(
        "vendor_invoices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("invoice_number", sa.String(100), nullable=False),
        sa.Column("po_id", sa.Integer(), sa.ForeignKey("purchase_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("vendor_id", sa.Integer(), sa.ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("received_date", sa.Date(), nullable=True),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("tax_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("amount_paid", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("amount_due", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("status", vi_status, nullable=False, server_default="pending_verification"),
        sa.Column("match_result", match_result, nullable=True),
        sa.Column("match_notes", sa.Text(), nullable=True),
        sa.Column("verified_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("journal_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("total_amount >= 0", name="chk_vendor_invoice_total"),
        sa.UniqueConstraint("vendor_id", "invoice_number", name="uq_vendor_invoice_number"),
    )
    op.create_index("ix_vendor_invoices_vendor_id", "vendor_invoices", ["vendor_id"])
    op.create_index("ix_vendor_invoices_status", "vendor_invoices", ["status"])
    op.create_index("ix_vendor_invoices_due_date", "vendor_invoices", ["due_date"])

    # ── payments_to_vendors ───────────────────────────────────────────────
    op.create_table(
        "payments_to_vendors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("payment_number", sa.String(30), nullable=False, unique=True),
        sa.Column("vendor_id", sa.Integer(), sa.ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("vendor_invoice_id", sa.Integer(), sa.ForeignKey("vendor_invoices.id", ondelete="SET NULL"), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("method", vp_method, nullable=False, server_default="bank_transfer"),
        sa.Column("bank_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reference_number", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("journal_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", vp_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("amount > 0", name="chk_vendor_payment_positive"),
    )
    op.create_index("ix_payments_to_vendors_vendor_id", "payments_to_vendors", ["vendor_id"])

    # ── Seed approval rules ───────────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "approval_rules",
            sa.column("department", sa.String),
            sa.column("min_amount", sa.Numeric),
            sa.column("max_amount", sa.Numeric),
            sa.column("approver_role", sa.String),
            sa.column("is_active", sa.Boolean),
            sa.column("sort_order", sa.Integer),
            sa.column("description", sa.String),
        ),
        [
            # < 10M Toman → Department Manager
            {"department": None, "min_amount": "0", "max_amount": "100000000",
             "approver_role": "MANAGER", "is_active": True, "sort_order": 1,
             "description": "Up to 100M IRR — Department Manager"},
            # 10–50M Toman → Director
            {"department": None, "min_amount": "100000001", "max_amount": "500000000",
             "approver_role": "DIRECTOR", "is_active": True, "sort_order": 2,
             "description": "100M–500M IRR — Director"},
            # > 50M Toman → CFO
            {"department": None, "min_amount": "500000001", "max_amount": None,
             "approver_role": "CFO", "is_active": True, "sort_order": 3,
             "description": "Over 500M IRR — CFO"},
        ],
    )

    # ── Seed demo vendor ──────────────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "vendors",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
            sa.column("name_fa", sa.String),
            sa.column("category", sa.String),
            sa.column("payment_terms", sa.Integer),
            sa.column("is_active", sa.Boolean),
            sa.column("is_approved", sa.Boolean),
            sa.column("rating", sa.Integer),
        ),
        [
            {"code": "VEND-001", "name": "Demo Supplier Co.",
             "name_fa": "شرکت تأمین‌کننده نمونه",
             "category": "supplier", "payment_terms": 45,
             "is_active": True, "is_approved": True, "rating": 4},
        ],
    )


def downgrade() -> None:
    for tbl in [
        "payments_to_vendors", "vendor_invoices", "goods_receipt_lines",
        "goods_receipts", "purchase_order_lines", "purchase_orders",
        "purchase_request_lines", "purchase_requests", "approval_rules", "vendors",
    ]:
        op.drop_table(tbl)

    for enum_name in [
        "vendorcategory", "prpriority", "prstatus", "prlinestatus",
        "postatus", "polinestatus", "vendorinvoicestatus",
        "vendorpaymentmethod", "vendorpaymentstatus", "matchresult",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
