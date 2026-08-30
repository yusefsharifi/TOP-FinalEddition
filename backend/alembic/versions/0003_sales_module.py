"""Sales module — customers, sales_quotes, sales_quote_lines,
sales_invoices, sales_invoice_lines, sales_payments.

Revision ID: 0003_sales_module
Revises: 0002_finance_module
Create Date: 2024-01-01 00:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_sales_module"
down_revision = "0002_finance_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    customer_cat = postgresql.ENUM("A", "B", "C", name="customercategory", create_type=True)
    quote_status = postgresql.ENUM(
        "draft", "sent", "accepted", "rejected", "expired", "converted",
        name="quotestatus", create_type=True,
    )
    invoice_status = postgresql.ENUM(
        "draft", "issued", "partial_paid", "paid", "overdue", "cancelled",
        name="invoicestatus", create_type=True,
    )
    payment_method = postgresql.ENUM(
        "cash", "check", "bank_transfer", "card", "credit_note",
        name="paymentmethod", create_type=True,
    )
    payment_status = postgresql.ENUM(
        "pending", "cleared", "bounced", name="paymentstatus", create_type=True
    )

    # ── customers ─────────────────────────────────────────────────────────
    op.create_table(
        "customers",
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
        sa.Column("credit_limit", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("payment_terms", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("default_discount_percent", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("total_invoiced", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_paid", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("balance_due", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_vip", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("category", customer_cat, nullable=False, server_default="B"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("credit_limit >= 0", name="chk_customer_credit_limit"),
        sa.CheckConstraint(
            "default_discount_percent >= 0 AND default_discount_percent <= 100",
            name="chk_customer_discount",
        ),
    )
    op.create_index("ix_customers_code", "customers", ["code"])
    op.create_index("ix_customers_name", "customers", ["name"])
    op.create_index("ix_customers_is_active", "customers", ["is_active"])

    # ── sales_invoices (create before quotes due to FK) ───────────────────
    op.create_table(
        "sales_invoices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("invoice_number", sa.String(30), nullable=False, unique=True),
        sa.Column("quote_id", sa.Integer(), nullable=True),  # FK added after quotes table
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("draft_date", sa.Date(), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("subtotal", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("amount_paid", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("amount_due", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("status", invoice_status, nullable=False, server_default="draft"),
        sa.Column("revenue_journal_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cogs_journal_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("stock_movement_id", sa.Integer(), nullable=True),
        sa.Column("tax_invoice_number", sa.String(50), nullable=True, unique=True),
        sa.Column("tax_invoice_series", sa.String(10), nullable=True),
        sa.Column("signature_data", sa.Text(), nullable=True),
        sa.Column("qr_data", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("total_amount >= 0", name="chk_invoice_total"),
        sa.CheckConstraint("amount_paid >= 0", name="chk_invoice_paid"),
        sa.CheckConstraint("amount_due >= 0", name="chk_invoice_due"),
    )
    op.create_index("ix_sales_invoices_customer_id", "sales_invoices", ["customer_id"])
    op.create_index("ix_sales_invoices_status", "sales_invoices", ["status"])
    op.create_index("ix_sales_invoices_issue_date", "sales_invoices", ["issue_date"])
    op.create_index("ix_sales_invoices_due_date", "sales_invoices", ["due_date"])

    # ── sales_quotes ──────────────────────────────────────────────────────
    op.create_table(
        "sales_quotes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("quote_number", sa.String(30), nullable=False, unique=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quote_date", sa.Date(), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        sa.Column("status", quote_status, nullable=False, server_default="draft"),
        sa.Column("subtotal", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("converted_to_invoice_id", sa.Integer(), sa.ForeignKey("sales_invoices.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("expiry_date >= quote_date", name="chk_quote_expiry"),
    )
    op.create_index("ix_sales_quotes_customer_id", "sales_quotes", ["customer_id"])
    op.create_index("ix_sales_quotes_status", "sales_quotes", ["status"])

    # ── sales_quote_lines ─────────────────────────────────────────────────
    op.create_table(
        "sales_quote_lines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("quote_id", sa.Integer(), sa.ForeignKey("sales_quotes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("discount_percent", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("tax_percent", sa.Numeric(5, 2), nullable=False, server_default="9"),
        sa.Column("line_total", sa.Numeric(18, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("quantity > 0", name="chk_quote_line_qty"),
        sa.CheckConstraint("unit_price >= 0", name="chk_quote_line_price"),
    )
    op.create_index("ix_sales_quote_lines_quote_id", "sales_quote_lines", ["quote_id"])

    # Now add FK from sales_invoices.quote_id → sales_quotes.id
    op.create_foreign_key(
        "fk_sales_invoices_quote_id",
        "sales_invoices", "sales_quotes",
        ["quote_id"], ["id"], ondelete="SET NULL",
    )

    # ── sales_invoice_lines ───────────────────────────────────────────────
    op.create_table(
        "sales_invoice_lines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("invoice_id", sa.Integer(), sa.ForeignKey("sales_invoices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("unit_of_measure", sa.String(20), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("discount_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("line_total", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("revenue_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cogs_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("stock_movement_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("quantity > 0", name="chk_invoice_line_qty"),
        sa.CheckConstraint("unit_price >= 0", name="chk_invoice_line_price"),
    )
    op.create_index("ix_sales_invoice_lines_invoice_id", "sales_invoice_lines", ["invoice_id"])

    # ── sales_payments ────────────────────────────────────────────────────
    op.create_table(
        "sales_payments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("payment_number", sa.String(30), nullable=False, unique=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("invoice_id", sa.Integer(), sa.ForeignKey("sales_invoices.id", ondelete="SET NULL"), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("method", payment_method, nullable=False, server_default="bank_transfer"),
        sa.Column("bank_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reference_number", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("journal_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", payment_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("amount > 0", name="chk_payment_amount_positive"),
    )
    op.create_index("ix_sales_payments_customer_id", "sales_payments", ["customer_id"])
    op.create_index("ix_sales_payments_payment_date", "sales_payments", ["payment_date"])
    op.create_index("ix_sales_payments_status", "sales_payments", ["status"])

    # ── Seed demo customer ────────────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "customers",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
            sa.column("name_fa", sa.String),
            sa.column("category", sa.String),
            sa.column("payment_terms", sa.Integer),
            sa.column("credit_limit", sa.Numeric),
            sa.column("is_active", sa.Boolean),
            sa.column("is_vip", sa.Boolean),
        ),
        [
            {
                "code": "CUST-001",
                "name": "Demo Customer",
                "name_fa": "مشتری نمونه",
                "category": "A",
                "payment_terms": 30,
                "credit_limit": 500000000,
                "is_active": True,
                "is_vip": True,
            }
        ],
    )


def downgrade() -> None:
    op.drop_constraint("fk_sales_invoices_quote_id", "sales_invoices", type_="foreignkey")
    op.drop_table("sales_payments")
    op.drop_table("sales_invoice_lines")
    op.drop_table("sales_quote_lines")
    op.drop_table("sales_quotes")
    op.drop_table("sales_invoices")
    op.drop_table("customers")

    for enum_name in [
        "customercategory", "quotestatus", "invoicestatus",
        "paymentmethod", "paymentstatus",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
