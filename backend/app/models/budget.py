"""
Budget Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Budget management with line items, revisions, and performance tracking.
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, Enum,
    ForeignKey, Index, Integer, Numeric, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


# ── Enums ────────────────────────────────────────────────────────────────────

class BudgetType(str, enum.Enum):
    OPERATIONAL = "operational"
    CAPITAL = "capital"
    CASH = "cash"
    PROJECT = "project"


class BudgetStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    CLOSED = "closed"


class BudgetPeriod(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"


# ── Models ───────────────────────────────────────────────────────────────────

class Budget(Base):
    """Main budget model."""
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    type: Mapped[BudgetType] = mapped_column(Enum(BudgetType), nullable=False, index=True)
    period: Mapped[BudgetPeriod] = mapped_column(Enum(BudgetPeriod), nullable=False)
    fiscal_year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    # Dates
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Status
    status: Mapped[BudgetStatus] = mapped_column(
        Enum(BudgetStatus), nullable=False, default=BudgetStatus.DRAFT, index=True
    )
    
    # Approval
    approved_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    lines: Mapped[list["BudgetLine"]] = relationship("BudgetLine", back_populates="budget", cascade="all, delete-orphan")
    revisions: Mapped[list["BudgetRevision"]] = relationship("BudgetRevision", back_populates="budget", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_budgets_type", "type"),
        Index("ix_budgets_fiscal_year", "fiscal_year"),
        Index("ix_budgets_status", "status"),
        Index("ix_budgets_dates", "start_date", "end_date"),
    )

    def __repr__(self) -> str:
        return f"<Budget {self.code} — {self.name}>"


class BudgetLine(Base):
    """Budget line item linked to a chart of accounts."""
    __tablename__ = "budget_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    budget: Mapped["Budget"] = relationship("Budget", back_populates="lines")
    
    __table_args__ = (
        Index("ix_budget_lines_budget", "budget_id"),
        Index("ix_budget_lines_account", "account_id"),
    )


class BudgetRevision(Base):
    """Budget revision history."""
    __tablename__ = "budget_revisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[BudgetStatus] = mapped_column(
        Enum(BudgetStatus), nullable=False, default=BudgetStatus.DRAFT
    )
    
    # Approval
    approved_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    budget: Mapped["Budget"] = relationship("Budget", back_populates="revisions")
    
    __table_args__ = (
        Index("ix_budget_revisions_budget", "budget_id"),
        Index("ix_budget_revisions_number", "revision_number"),
    )


class BudgetPerformance(Base):
    """Budget vs actual performance tracking."""
    __tablename__ = "budget_performance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    period: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM format
    budget_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    actual_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    variance_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    variance_percentage: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=Decimal("0"))
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_budget_performance_budget", "budget_id"),
        Index("ix_budget_performance_account", "account_id"),
        Index("ix_budget_performance_period", "period"),
    )
