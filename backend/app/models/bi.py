"""
Business Intelligence Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Star schema data warehouse (OLAP layer):
  FactTransaction ← DimDate, DimAccount, DimDepartment, DimCustomer,
                    DimVendor, DimEmployee, DimProduct

Plus operational BI models:
  AlertRule, AlertEvent, ReportTemplate, ReportSchedule, KPISnapshot

Design choices:
  - FactTransaction is an append-only denormalised table — never update rows
  - DimDate is pre-populated for 20 years (Jalali 1390–1410)
  - KPISnapshot stores point-in-time KPI values for trend charts
  - AlertRule uses simple threshold logic; complex rules use formula field
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Date, DateTime, Enum,
    Float, ForeignKey, Index, Integer, JSON, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class TransactionType(str, enum.Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_MADE = "payment_made"
    JOURNAL = "journal"
    PAYROLL = "payroll"
    INVENTORY_IN = "inventory_in"
    INVENTORY_OUT = "inventory_out"
    INVENTORY_ADJUST = "inventory_adjust"


class SourceModule(str, enum.Enum):
    SALES = "sales"
    PROCUREMENT = "procurement"
    INVENTORY = "inventory"
    FINANCE = "finance"
    HR = "hr"


class AlertCondition(str, enum.Enum):
    ABOVE = "above"
    BELOW = "below"
    EQUAL = "equal"
    CHANGE_PERCENT_ABOVE = "change_percent_above"
    CHANGE_PERCENT_BELOW = "change_percent_below"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class ReportFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


# ---------------------------------------------------------------------------
# Dimension Tables
# ---------------------------------------------------------------------------
class DimDate(Base):
    """
    Calendar dimension pre-populated for Jalali years 1390–1415.
    Supports fast time-series grouping without runtime calendar computation.
    """
    __tablename__ = "dim_date"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)        # YYYYMMDD format, e.g. 20240315
    gregorian_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    jalali_date: Mapped[str] = mapped_column(String(10), nullable=False)   # "1403-01-01"
    jalali_year: Mapped[int] = mapped_column(Integer, nullable=False)
    jalali_month: Mapped[int] = mapped_column(Integer, nullable=False)
    jalali_day: Mapped[int] = mapped_column(Integer, nullable=False)
    jalali_month_name: Mapped[str] = mapped_column(String(20), nullable=False)   # فروردین
    jalali_quarter: Mapped[int] = mapped_column(Integer, nullable=False)         # 1–4
    gregorian_year: Mapped[int] = mapped_column(Integer, nullable=False)
    gregorian_month: Mapped[int] = mapped_column(Integer, nullable=False)
    gregorian_quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)            # 0=Mon
    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_holiday: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    season: Mapped[str] = mapped_column(String(20), nullable=False)              # بهار

    __table_args__ = (
        Index("ix_dim_date_gregorian", "gregorian_date"),
        Index("ix_dim_date_jalali_ym", "jalali_year", "jalali_month"),
        Index("ix_dim_date_jalali_y", "jalali_year"),
    )


class DimAccount(Base):
    """Snapshot of Chart of Accounts for BI joins (no FK to avoid coupling)."""
    __tablename__ = "dim_account"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_account_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)   # asset/liability/etc.
    account_subtype: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parent_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    last_synced: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (Index("ix_dim_account_source_id", "source_account_id"),)


class DimDepartment(Base):
    """Snapshot of HR departments."""
    __tablename__ = "dim_department"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_dept_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    cost_center_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_synced: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DimCustomer(Base):
    """Snapshot of Sales customers."""
    __tablename__ = "dim_customer"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_customer_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_synced: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DimVendor(Base):
    """Snapshot of Procurement vendors."""
    __tablename__ = "dim_vendor"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_vendor_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    last_synced: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DimProduct(Base):
    """Snapshot of Inventory items."""
    __tablename__ = "dim_product"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_item_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    sku: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    category_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    unit_of_measure: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    standard_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)
    last_synced: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# ---------------------------------------------------------------------------
# Fact Table
# ---------------------------------------------------------------------------
class FactTransaction(Base):
    """
    Central fact table — append-only, never updated.
    Populated by ETL from JournalEntryLine + inventory movements + payroll.
    One row per journal entry line for financial facts,
    one row per inventory movement for quantity facts.
    """
    __tablename__ = "fact_transaction"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Time
    date_id: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.id"), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)  # denorm for fast range queries

    # Dimensions
    account_dim_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_account.id"), nullable=True)
    department_dim_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_department.id"), nullable=True)
    customer_dim_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_customer.id"), nullable=True)
    vendor_dim_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_vendor.id"), nullable=True)
    product_dim_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_product.id"), nullable=True)

    # Measures
    amount_debit: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    amount_credit: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)

    # Classification
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    source_module: Mapped[SourceModule] = mapped_column(Enum(SourceModule), nullable=False)
    source_document_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_document_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Denormalised fields for fast GROUP BY without joins
    account_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    account_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    department_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    customer_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    vendor_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    product_sku: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cost_center: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_fact_transaction_date_id", "date_id"),
        Index("ix_fact_transaction_date", "transaction_date"),
        Index("ix_fact_transaction_type", "transaction_type"),
        Index("ix_fact_transaction_module", "source_module"),
        Index("ix_fact_transaction_account_type", "account_type"),
        Index("ix_fact_transaction_customer", "customer_dim_id"),
        Index("ix_fact_transaction_vendor", "vendor_dim_id"),
        Index("ix_fact_transaction_product", "product_dim_id"),
        Index("ix_fact_transaction_dept", "department_dim_id"),
        # Composite for common dashboard queries
        Index("ix_fact_txn_date_type", "transaction_date", "transaction_type"),
        Index("ix_fact_txn_date_acct", "transaction_date", "account_type"),
    )


# ---------------------------------------------------------------------------
# ETL Metadata
# ---------------------------------------------------------------------------
class ETLRun(Base):
    """Tracks ETL execution history for incremental loading."""
    __tablename__ = "etl_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    run_type: Mapped[str] = mapped_column(String(20), nullable=False)   # "full" | "incremental"
    rows_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_processed_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


# ---------------------------------------------------------------------------
# KPI Snapshot
# ---------------------------------------------------------------------------
class KPISnapshot(Base):
    """
    Point-in-time KPI values for trend charts.
    Populated every 15 minutes by Celery beat.
    Retention: 2 years of 15-minute snapshots.
    """
    __tablename__ = "kpi_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kpi_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)   # "IRR", "%", "count"
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    period_label: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # "1403-01"
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_kpi_snapshots_name_time", "kpi_name", "snapshot_at"),
        Index("ix_kpi_snapshots_name", "kpi_name"),
    )


# ---------------------------------------------------------------------------
# Alert System
# ---------------------------------------------------------------------------
class AlertRule(AuditMixin, Base):
    """
    Threshold-based alerting rules evaluated against KPI values.
    Custom SQL metric supported via `metric_sql` field.
    """
    __tablename__ = "alert_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metric: Mapped[str] = mapped_column(String(100), nullable=False)    # KPI name
    metric_sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # Custom SQL override
    condition: Mapped[AlertCondition] = mapped_column(Enum(AlertCondition), nullable=False)
    threshold: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.INFO)
    channels: Mapped[list] = mapped_column(JSON, nullable=False, default=list)   # List of AlertChannel values
    recipient_user_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_triggered: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)

    events: Mapped[list["AlertEvent"]] = relationship("AlertEvent", back_populates="rule")

    __table_args__ = (Index("ix_alert_rules_is_active", "is_active"),)


class AlertEvent(Base):
    """Log of triggered alerts."""
    __tablename__ = "alert_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metric_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    threshold_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    acknowledged_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    rule: Mapped["AlertRule"] = relationship("AlertRule", back_populates="events")

    __table_args__ = (Index("ix_alert_events_triggered_at", "triggered_at"),)


# ---------------------------------------------------------------------------
# Report Builder
# ---------------------------------------------------------------------------
class ReportTemplate(AuditMixin, Base):
    """User-saved ad-hoc report configurations."""
    __tablename__ = "report_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)   # Full report config
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # System templates
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    run_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    schedules: Mapped[list["ReportSchedule"]] = relationship("ReportSchedule", back_populates="template")


class ReportSchedule(AuditMixin, Base):
    """Automated report delivery schedule."""
    __tablename__ = "report_schedules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("report_templates.id", ondelete="CASCADE"), nullable=False)
    frequency: Mapped[ReportFrequency] = mapped_column(Enum(ReportFrequency), nullable=False)
    recipients: Mapped[list] = mapped_column(JSON, nullable=False, default=list)   # email addresses
    formats: Mapped[list] = mapped_column(JSON, nullable=False, default=list)   # ["excel", "pdf"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_sent: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    template: Mapped["ReportTemplate"] = relationship("ReportTemplate", back_populates="schedules")