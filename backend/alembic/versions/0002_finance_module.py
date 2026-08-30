"""Finance module — fiscal_periods, accounts (COA), journal_entries, journal_entry_lines,
exchange_rates. Seeded with IFRS-compliant Chart of Accounts for Iranian business context.

Revision ID: 0002_finance_module
Revises: 0001_initial_schema
Create Date: 2024-01-01 00:00:00.000000
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_finance_module"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ──────────────────────────────────────────────────────────────
    account_type_enum = postgresql.ENUM(
        "asset", "liability", "equity", "revenue", "expense",
        name="accounttype", create_type=True,
    )
    account_subtype_enum = postgresql.ENUM(
        "cash", "bank", "accounts_receivable", "inventory", "prepaid",
        "fixed_asset", "accumulated_depreciation", "other_asset",
        "accounts_payable", "accrued_expense", "tax_payable", "other_liability",
        "capital", "retained_earnings",
        "sales", "other_income",
        "cogs", "salary", "rent", "utilities", "depreciation_exp",
        "other_expense", "inventory_adjustment",
        name="accountsubtype", create_type=True,
    )
    fiscal_period_status_enum = postgresql.ENUM(
        "open", "closed", "adjusting", name="fiscalperiodstatus", create_type=True
    )
    je_status_enum = postgresql.ENUM(
        "draft", "posted", "reversed", name="journalentrystatus", create_type=True
    )
    reference_type_enum = postgresql.ENUM(
        "inventory", "invoice", "payment", "manual", "payroll",
        "depreciation", "period_close", name="referencetype", create_type=True
    )
    contact_type_enum = postgresql.ENUM(
        "customer", "vendor", name="contacttype", create_type=True
    )

    # ── fiscal_periods ──────────────────────────────────────────────────────
    op.create_table(
        "fiscal_periods",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("name_fa", sa.String(100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("quarter", sa.Integer(), nullable=True),
        sa.Column("status", fiscal_period_status_enum, nullable=False, server_default="open"),
        sa.Column("is_adjustment_period", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("closed_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("end_date > start_date", name="chk_period_dates"),
        sa.CheckConstraint("quarter IS NULL OR quarter BETWEEN 1 AND 4", name="chk_period_quarter"),
    )
    op.create_index("ix_fiscal_periods_year", "fiscal_periods", ["year"])
    op.create_index("ix_fiscal_periods_status", "fiscal_periods", ["status"])

    # ── accounts ────────────────────────────────────────────────────────────
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", account_type_enum, nullable=False),
        sa.Column("subtype", account_subtype_enum, nullable=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("path", sa.String(500), nullable=True),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_bank_account", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("allow_direct_posting", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="IRR"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_accounts_code", "accounts", ["code"])
    op.create_index("ix_accounts_type", "accounts", ["type"])
    op.create_index("ix_accounts_parent_id", "accounts", ["parent_id"])
    op.create_index("ix_accounts_subtype", "accounts", ["subtype"])

    # ── journal_entries ─────────────────────────────────────────────────────
    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entry_number", sa.String(30), nullable=False, unique=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("fiscal_periods.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reference_type", reference_type_enum, nullable=False, server_default="manual"),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("description_fa", sa.String(500), nullable=True),
        sa.Column("total_debit", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("total_credit", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("status", je_status_enum, nullable=False, server_default="draft"),
        sa.Column("is_reversing_entry", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("reversed_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("posted_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("total_debit >= 0", name="chk_je_total_debit_non_negative"),
        sa.CheckConstraint("total_credit >= 0", name="chk_je_total_credit_non_negative"),
    )
    op.create_index("ix_journal_entries_period_id", "journal_entries", ["period_id"])
    op.create_index("ix_journal_entries_entry_date", "journal_entries", ["entry_date"])
    op.create_index("ix_journal_entries_status", "journal_entries", ["status"])
    op.create_index("ix_journal_entries_reference", "journal_entries", ["reference_type", "reference_id"])

    # ── journal_entry_lines ─────────────────────────────────────────────────
    op.create_table(
        "journal_entry_lines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("journal_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("debit", sa.Numeric(18, 4), nullable=True),
        sa.Column("credit", sa.Numeric(18, 4), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("cost_center", sa.String(100), nullable=True),
        sa.Column("contact_id", sa.Integer(), nullable=True),
        sa.Column("contact_type", contact_type_enum, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint(
            "(debit IS NOT NULL AND credit IS NULL AND debit > 0) OR "
            "(credit IS NOT NULL AND debit IS NULL AND credit > 0)",
            name="chk_jel_exactly_one_side",
        ),
    )
    op.create_index("ix_journal_entry_lines_je_id", "journal_entry_lines", ["journal_entry_id"])
    op.create_index("ix_journal_entry_lines_account_id", "journal_entry_lines", ["account_id"])

    # ── exchange_rates ──────────────────────────────────────────────────────
    op.create_table(
        "exchange_rates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("from_currency", sa.String(3), nullable=False),
        sa.Column("to_currency", sa.String(3), nullable=False),
        sa.Column("rate", sa.Numeric(18, 6), nullable=False),
        sa.Column("rate_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("from_currency", "to_currency", "rate_date", name="uq_exchange_rate"),
        sa.CheckConstraint("rate > 0", name="chk_exchange_rate_positive"),
    )
    op.create_index("ix_exchange_rates_date", "exchange_rates", ["rate_date"])

    # ── COA Seed Data (IFRS-compliant, Iranian business context) ────────────
    # Insert in two passes: headers first (no parent), then children
    accounts_tbl = sa.table(
        "accounts",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("name_fa", sa.String),
        sa.column("type", sa.String),
        sa.column("subtype", sa.String),
        sa.column("allow_direct_posting", sa.Boolean),
        sa.column("is_active", sa.Boolean),
        sa.column("currency", sa.String),
        sa.column("depth", sa.Integer),
        sa.column("path", sa.String),
    )

    # Level 0 — root headers (no parent, allow_direct_posting=False)
    op.bulk_insert(accounts_tbl, [
        # ── ASSETS ──────────────────────────────────────────────────────
        {"code": "1000", "name": "Assets",           "name_fa": "دارایی‌ها",           "type": "asset",     "subtype": None,              "allow_direct_posting": False, "is_active": True, "currency": "IRR", "depth": 0, "path": "1000"},
        {"code": "1100", "name": "Current Assets",   "name_fa": "دارایی‌های جاری",     "type": "asset",     "subtype": None,              "allow_direct_posting": False, "is_active": True, "currency": "IRR", "depth": 1, "path": "1000.1100"},
        {"code": "1110", "name": "Cash & Bank",      "name_fa": "صندوق و بانک",        "type": "asset",     "subtype": "cash",            "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "1000.1100.1110"},
        {"code": "1120", "name": "Accounts Receivable","name_fa": "حساب‌های دریافتنی", "type": "asset",     "subtype": "accounts_receivable","allow_direct_posting": True,"is_active": True, "currency": "IRR", "depth": 2, "path": "1000.1100.1120"},
        {"code": "1130", "name": "Inventory",        "name_fa": "موجودی کالا",          "type": "asset",     "subtype": "inventory",       "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "1000.1100.1130"},
        {"code": "1140", "name": "Prepaid Expenses", "name_fa": "پیش‌پرداخت‌ها",       "type": "asset",     "subtype": "prepaid",         "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "1000.1100.1140"},
        {"code": "1200", "name": "Fixed Assets",     "name_fa": "دارایی‌های ثابت",     "type": "asset",     "subtype": None,              "allow_direct_posting": False, "is_active": True, "currency": "IRR", "depth": 1, "path": "1000.1200"},
        {"code": "1210", "name": "Equipment",        "name_fa": "ماشین‌آلات و تجهیزات","type": "asset",     "subtype": "fixed_asset",     "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "1000.1200.1210"},
        {"code": "1220", "name": "Accumulated Depreciation","name_fa": "استهلاک انباشته","type": "asset",   "subtype": "accumulated_depreciation","allow_direct_posting": True,"is_active": True,"currency": "IRR","depth": 2,"path": "1000.1200.1220"},

        # ── LIABILITIES ──────────────────────────────────────────────────
        {"code": "2000", "name": "Liabilities",         "name_fa": "بدهی‌ها",                "type": "liability", "subtype": None,              "allow_direct_posting": False, "is_active": True, "currency": "IRR", "depth": 0, "path": "2000"},
        {"code": "2100", "name": "Current Liabilities", "name_fa": "بدهی‌های جاری",          "type": "liability", "subtype": None,              "allow_direct_posting": False, "is_active": True, "currency": "IRR", "depth": 1, "path": "2000.2100"},
        {"code": "2110", "name": "Accounts Payable",    "name_fa": "حساب‌های پرداختنی",      "type": "liability", "subtype": "accounts_payable","allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "2000.2100.2110"},
        {"code": "2120", "name": "Accrued Expenses",    "name_fa": "هزینه‌های تعهد شده",     "type": "liability", "subtype": "accrued_expense", "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "2000.2100.2120"},
        {"code": "2130", "name": "VAT Payable",         "name_fa": "مالیات بر ارزش افزوده",  "type": "liability", "subtype": "tax_payable",     "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "2000.2100.2130"},

        # ── EQUITY ──────────────────────────────────────────────────────
        {"code": "3000", "name": "Equity",             "name_fa": "حقوق صاحبان سهام",    "type": "equity",    "subtype": None,              "allow_direct_posting": False, "is_active": True, "currency": "IRR", "depth": 0, "path": "3000"},
        {"code": "3100", "name": "Capital",            "name_fa": "سرمایه",               "type": "equity",    "subtype": "capital",         "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 1, "path": "3000.3100"},
        {"code": "3200", "name": "Retained Earnings",  "name_fa": "سود انباشته",          "type": "equity",    "subtype": "retained_earnings","allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 1, "path": "3000.3200"},

        # ── REVENUE ──────────────────────────────────────────────────────
        {"code": "4000", "name": "Revenue",            "name_fa": "درآمدها",              "type": "revenue",   "subtype": None,              "allow_direct_posting": False, "is_active": True, "currency": "IRR", "depth": 0, "path": "4000"},
        {"code": "4100", "name": "Sales Revenue",      "name_fa": "درآمد فروش",           "type": "revenue",   "subtype": "sales",           "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 1, "path": "4000.4100"},
        {"code": "4200", "name": "Other Income",       "name_fa": "سایر درآمدها",         "type": "revenue",   "subtype": "other_income",    "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 1, "path": "4000.4200"},

        # ── EXPENSES ─────────────────────────────────────────────────────
        {"code": "5000", "name": "Expenses",                    "name_fa": "هزینه‌ها",                       "type": "expense", "subtype": None,                 "allow_direct_posting": False, "is_active": True, "currency": "IRR", "depth": 0, "path": "5000"},
        {"code": "5100", "name": "Cost of Goods Sold",          "name_fa": "بهای تمام شده کالای فروش رفته", "type": "expense", "subtype": "cogs",               "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 1, "path": "5000.5100"},
        {"code": "5200", "name": "Operating Expenses",          "name_fa": "هزینه‌های عملیاتی",             "type": "expense", "subtype": None,                 "allow_direct_posting": False, "is_active": True, "currency": "IRR", "depth": 1, "path": "5000.5200"},
        {"code": "5210", "name": "Inventory Adjustment Expense","name_fa": "زیان تعدیل موجودی",             "type": "expense", "subtype": "inventory_adjustment","allow_direct_posting": True, "is_active": True, "currency": "IRR", "depth": 2, "path": "5000.5200.5210"},
        {"code": "5220", "name": "Salaries & Wages",            "name_fa": "حقوق و دستمزد",                 "type": "expense", "subtype": "salary",             "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "5000.5200.5220"},
        {"code": "5230", "name": "Rent",                        "name_fa": "اجاره",                          "type": "expense", "subtype": "rent",               "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "5000.5200.5230"},
        {"code": "5240", "name": "Utilities",                   "name_fa": "آب، برق، گاز",                  "type": "expense", "subtype": "utilities",          "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "5000.5200.5240"},
        {"code": "5250", "name": "Depreciation Expense",        "name_fa": "هزینه استهلاک",                 "type": "expense", "subtype": "depreciation_exp",   "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "5000.5200.5250"},
        {"code": "5260", "name": "Other Operating Expenses",    "name_fa": "سایر هزینه‌های عملیاتی",       "type": "expense", "subtype": "other_expense",      "allow_direct_posting": True,  "is_active": True, "currency": "IRR", "depth": 2, "path": "5000.5200.5260"},
    ])

    # ── Seed initial fiscal period (Jalali 1403) ─────────────────────────
    op.bulk_insert(
        sa.table(
            "fiscal_periods",
            sa.column("name", sa.String),
            sa.column("name_fa", sa.String),
            sa.column("start_date", sa.Date),
            sa.column("end_date", sa.Date),
            sa.column("year", sa.Integer),
            sa.column("quarter", sa.Integer),
            sa.column("status", sa.String),
            sa.column("is_adjustment_period", sa.Boolean),
        ),
        [
            {"name": "1403 - Q1", "name_fa": "بهار ۱۴۰۳", "start_date": "2024-03-20", "end_date": "2024-06-20", "year": 1403, "quarter": 1, "status": "open", "is_adjustment_period": False},
            {"name": "1403 - Q2", "name_fa": "تابستان ۱۴۰۳", "start_date": "2024-06-21", "end_date": "2024-09-21", "year": 1403, "quarter": 2, "status": "open", "is_adjustment_period": False},
            {"name": "1403 - Q3", "name_fa": "پاییز ۱۴۰۳", "start_date": "2024-09-22", "end_date": "2024-12-21", "year": 1403, "quarter": 3, "status": "open", "is_adjustment_period": False},
            {"name": "1403 - Q4", "name_fa": "زمستان ۱۴۰۳", "start_date": "2024-12-22", "end_date": "2025-03-19", "year": 1403, "quarter": 4, "status": "open", "is_adjustment_period": False},
        ],
    )


def downgrade() -> None:
    op.drop_table("exchange_rates")
    op.drop_table("journal_entry_lines")
    op.drop_table("journal_entries")
    op.drop_table("accounts")
    op.drop_table("fiscal_periods")

    op.execute("DROP TYPE IF EXISTS accounttype")
    op.execute("DROP TYPE IF EXISTS accountsubtype")
    op.execute("DROP TYPE IF EXISTS fiscalperiodstatus")
    op.execute("DROP TYPE IF EXISTS journalentrystatus")
    op.execute("DROP TYPE IF EXISTS referencetype")
    op.execute("DROP TYPE IF EXISTS contacttype")
