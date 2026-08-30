"""BI/Data Warehouse — dim_date, dim_account, dim_department, dim_customer,
dim_vendor, dim_product, fact_transaction, etl_runs, kpi_snapshots,
alert_rules, alert_events, report_templates, report_schedules.
Also creates PostgreSQL materialized views for common aggregations.

Revision ID: 0006_bi_module
Revises: 0005_hr_module
Create Date: 2024-01-01 00:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006_bi_module"
down_revision = "0005_hr_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    txn_type = postgresql.ENUM(
        "sale", "purchase", "payment_received", "payment_made",
        "journal", "payroll", "inventory_in", "inventory_out", "inventory_adjust",
        name="transactiontype", create_type=True,
    )
    source_module = postgresql.ENUM(
        "sales", "procurement", "inventory", "finance", "hr",
        name="sourcemodule", create_type=True,
    )
    alert_condition = postgresql.ENUM(
        "above", "below", "equal", "change_percent_above", "change_percent_below",
        name="alertcondition", create_type=True,
    )
    alert_severity = postgresql.ENUM("info", "warning", "critical", name="alertseverity", create_type=True)
    report_frequency = postgresql.ENUM("daily", "weekly", "monthly", "quarterly", name="reportfrequency", create_type=True)

    # ── dim_date ──────────────────────────────────────────────────────────
    op.create_table(
        "dim_date",
        sa.Column("id", sa.Integer(), primary_key=True),  # YYYYMMDD
        sa.Column("gregorian_date", sa.Date(), nullable=False, unique=True),
        sa.Column("jalali_date", sa.String(10), nullable=False),
        sa.Column("jalali_year", sa.Integer(), nullable=False),
        sa.Column("jalali_month", sa.Integer(), nullable=False),
        sa.Column("jalali_day", sa.Integer(), nullable=False),
        sa.Column("jalali_month_name", sa.String(20), nullable=False),
        sa.Column("jalali_quarter", sa.Integer(), nullable=False),
        sa.Column("gregorian_year", sa.Integer(), nullable=False),
        sa.Column("gregorian_month", sa.Integer(), nullable=False),
        sa.Column("gregorian_quarter", sa.Integer(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("is_weekend", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_holiday", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("season", sa.String(20), nullable=False),
    )
    op.create_index("ix_dim_date_gregorian", "dim_date", ["gregorian_date"])
    op.create_index("ix_dim_date_jalali_ym", "dim_date", ["jalali_year", "jalali_month"])

    # ── dimension tables ──────────────────────────────────────────────────
    for tbl, source_col in [("dim_account", "source_account_id"), ("dim_department", "source_dept_id"),
                             ("dim_customer", "source_customer_id"), ("dim_vendor", "source_vendor_id"),
                             ("dim_product", "source_item_id")]:
        op.create_table(
            tbl,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(source_col, sa.Integer(), nullable=False, unique=True),
            sa.Column("code", sa.String(50), nullable=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("name_fa", sa.String(200), nullable=True),
            sa.Column("account_type", sa.String(20), nullable=True),
            sa.Column("account_subtype", sa.String(50), nullable=True),
            sa.Column("depth", sa.Integer(), nullable=True),
            sa.Column("parent_code", sa.String(20), nullable=True),
            sa.Column("category", sa.String(30), nullable=True),
            sa.Column("cost_center_code", sa.String(50), nullable=True),
            sa.Column("city", sa.String(100), nullable=True),
            sa.Column("sku", sa.String(50), nullable=True),
            sa.Column("unit_of_measure", sa.String(20), nullable=True),
            sa.Column("standard_cost", sa.Numeric(18, 4), nullable=True),
            sa.Column("category_name", sa.String(200), nullable=True),
            sa.Column("last_synced", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index(f"ix_{tbl}_{source_col}", tbl, [source_col])

    # ── fact_transaction ──────────────────────────────────────────────────
    op.create_table(
        "fact_transaction",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("date_id", sa.Integer(), sa.ForeignKey("dim_date.id"), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("account_dim_id", sa.Integer(), sa.ForeignKey("dim_account.id"), nullable=True),
        sa.Column("department_dim_id", sa.Integer(), sa.ForeignKey("dim_department.id"), nullable=True),
        sa.Column("customer_dim_id", sa.Integer(), sa.ForeignKey("dim_customer.id"), nullable=True),
        sa.Column("vendor_dim_id", sa.Integer(), sa.ForeignKey("dim_vendor.id"), nullable=True),
        sa.Column("product_dim_id", sa.Integer(), sa.ForeignKey("dim_product.id"), nullable=True),
        sa.Column("amount_debit", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("amount_credit", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("unit_cost", sa.Numeric(18, 4), nullable=True),
        sa.Column("transaction_type", txn_type, nullable=False),
        sa.Column("source_module", source_module, nullable=False),
        sa.Column("source_document_id", sa.Integer(), nullable=True),
        sa.Column("source_document_number", sa.String(30), nullable=True),
        sa.Column("account_code", sa.String(20), nullable=True),
        sa.Column("account_type", sa.String(20), nullable=True),
        sa.Column("department_code", sa.String(30), nullable=True),
        sa.Column("customer_name", sa.String(200), nullable=True),
        sa.Column("vendor_name", sa.String(200), nullable=True),
        sa.Column("product_sku", sa.String(50), nullable=True),
        sa.Column("cost_center", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    for idx_cols in [["date_id"], ["transaction_date"], ["transaction_type"], ["source_module"],
                     ["account_type"], ["customer_dim_id"], ["vendor_dim_id"], ["product_dim_id"],
                     ["department_dim_id"], ["transaction_date", "transaction_type"],
                     ["transaction_date", "account_type"]]:
        idx_name = "ix_fact_txn_" + "_".join(idx_cols).replace(",", "").replace(" ", "_")[:30]
        op.create_index(idx_name, "fact_transaction", idx_cols)

    # ── etl_runs ──────────────────────────────────────────────────────────
    op.create_table(
        "etl_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("run_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("run_type", sa.String(20), nullable=False),
        sa.Column("rows_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="success"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("last_processed_id", sa.Integer(), nullable=True),
    )

    # ── kpi_snapshots ─────────────────────────────────────────────────────
    op.create_table(
        "kpi_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("kpi_name", sa.String(100), nullable=False),
        sa.Column("value", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("period_label", sa.String(30), nullable=True),
        sa.Column("metadata_json", postgresql.JSON(), nullable=True),
    )
    op.create_index("ix_kpi_snapshots_name_time", "kpi_snapshots", ["kpi_name", "snapshot_at"])

    # ── alert_rules ───────────────────────────────────────────────────────
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metric", sa.String(100), nullable=False),
        sa.Column("metric_sql", sa.Text(), nullable=True),
        sa.Column("condition", alert_condition, nullable=False),
        sa.Column("threshold", sa.Numeric(18, 4), nullable=False),
        sa.Column("severity", alert_severity, nullable=False, server_default="info"),
        sa.Column("channels", postgresql.JSON(), nullable=False, server_default='["in_app"]'),
        sa.Column("recipient_user_ids", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("webhook_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_triggered", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cooldown_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
    )

    # ── alert_events ──────────────────────────────────────────────────────
    op.create_table(
        "alert_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("rule_id", sa.Integer(), sa.ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("metric_value", sa.Numeric(18, 4), nullable=False),
        sa.Column("threshold_value", sa.Numeric(18, 4), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("acknowledged_by_id", sa.Integer(), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_alert_events_triggered_at", "alert_events", ["triggered_at"])

    # ── report_templates ──────────────────────────────────────────────────
    op.create_table(
        "report_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("config", postgresql.JSON(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("run_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
    )

    # ── report_schedules ──────────────────────────────────────────────────
    op.create_table(
        "report_schedules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("report_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("frequency", report_frequency, nullable=False),
        sa.Column("recipients", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("formats", postgresql.JSON(), nullable=False, server_default='["excel"]'),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_sent", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
    )

    # ── Materialized views ────────────────────────────────────────────────
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_revenue AS
        SELECT
            dd.jalali_year, dd.jalali_month, dd.jalali_month_name,
            SUM(ft.amount_credit - ft.amount_debit) AS revenue
        FROM fact_transaction ft
        JOIN dim_date dd ON dd.id = ft.date_id
        WHERE ft.account_type = 'revenue'
        GROUP BY dd.jalali_year, dd.jalali_month, dd.jalali_month_name
        ORDER BY dd.jalali_year, dd.jalali_month;
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_mv_monthly_revenue ON mv_monthly_revenue (jalali_year, jalali_month);")

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_expense AS
        SELECT
            dd.jalali_year, dd.jalali_month,
            ft.account_type,
            ft.department_code,
            SUM(ft.amount_debit - ft.amount_credit) AS expense
        FROM fact_transaction ft
        JOIN dim_date dd ON dd.id = ft.date_id
        WHERE ft.account_type = 'expense'
        GROUP BY dd.jalali_year, dd.jalali_month, ft.account_type, ft.department_code;
    """)

    # ── Seed default alert rules ──────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "alert_rules",
            sa.column("name", sa.String), sa.column("metric", sa.String),
            sa.column("condition", sa.String), sa.column("threshold", sa.Numeric),
            sa.column("severity", sa.String), sa.column("channels", postgresql.JSON),
            sa.column("recipient_user_ids", postgresql.JSON),
            sa.column("is_active", sa.Boolean), sa.column("cooldown_minutes", sa.Integer),
        ),
        [
            {"name": "Low Cash Balance",            "metric": "cash_balance",       "condition": "below", "threshold": "100000000", "severity": "critical", "channels": ["in_app", "email"], "recipient_user_ids": [], "is_active": True, "cooldown_minutes": 240},
            {"name": "AR Overdue 90+ Days",         "metric": "ar_overdue_90",      "condition": "above", "threshold": "500000000", "severity": "warning",  "channels": ["in_app"],          "recipient_user_ids": [], "is_active": True, "cooldown_minutes": 1440},
            {"name": "Stock Below Reorder (10+)",   "metric": "items_below_reorder","condition": "above", "threshold": "10",        "severity": "warning",  "channels": ["in_app"],          "recipient_user_ids": [], "is_active": True, "cooldown_minutes": 60},
            {"name": "Gross Profit Margin < 20%",   "metric": "gross_profit_margin","condition": "below", "threshold": "20",        "severity": "warning",  "channels": ["in_app"],          "recipient_user_ids": [], "is_active": True, "cooldown_minutes": 1440},
        ]
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_monthly_expense")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_monthly_revenue")
    for tbl in ["report_schedules", "report_templates", "alert_events", "alert_rules",
                "kpi_snapshots", "etl_runs", "fact_transaction",
                "dim_product", "dim_vendor", "dim_customer", "dim_department", "dim_account", "dim_date"]:
        op.drop_table(tbl)
    for e in ["transactiontype", "sourcemodule", "alertcondition", "alertseverity", "reportfrequency"]:
        op.execute(f"DROP TYPE IF EXISTS {e}")
