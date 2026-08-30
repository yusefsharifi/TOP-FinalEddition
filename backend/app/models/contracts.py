"""
Contracts Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Contract lifecycle management with approval workflow and renewal tracking.
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey,
    Index, Integer, String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


# ── Enums ────────────────────────────────────────────────────────────────────

class ContractType(str, enum.Enum):
    SALES = "sales"
    PURCHASE = "purchase"
    EMPLOYMENT = "employment"
    SERVICE = "service"
    LEASE = "lease"
    NDA = "nda"
    OTHER = "other"


class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


# ── Models ───────────────────────────────────────────────────────────────────

class Contract(Base):
    """Contract with full lifecycle tracking."""
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Basic info
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contract_type: Mapped[ContractType] = mapped_column(Enum(ContractType), nullable=False, index=True)
    status: Mapped[ContractStatus] = mapped_column(Enum(ContractStatus), nullable=False, default=ContractStatus.DRAFT, index=True)

    # Counterparty
    counterparty_name: Mapped[str] = mapped_column(String(200), nullable=False)
    counterparty_contact: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Dates
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)

    # Financial
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="IRR")

    # Terms
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Renewal
    auto_renew: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    renewal_days_notice: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    approved_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])
    attachments = relationship("ContractAttachment", back_populates="contract", cascade="all, delete-orphan")
    history = relationship("ContractHistory", back_populates="contract", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_contracts_status_type", "status", "contract_type"),
        Index("ix_contracts_end_date", "end_date"),
        Index("ix_contracts_counterparty", "counterparty_name"),
        Index("ix_contracts_created_by", "created_by_id"),
        Index("ix_contracts_approved_by", "approved_by_id"),
        Index("ix_contracts_start_date", "start_date"),
        Index("ix_contracts_value", "value"),
        Index("ix_contracts_auto_renew_expiry", "auto_renew", "end_date"),
        Index("ix_contracts_status_end_date", "status", "end_date"),
    )


class ContractAttachment(Base):
    """File attachment for a contract."""
    __tablename__ = "contract_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_name: Mapped[str] = mapped_column(String(300), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    uploaded_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="attachments")
    uploader = relationship("User")

    __table_args__ = (
        Index("ix_contract_attachments_uploader", "uploaded_by_id"),
    )


class ContractHistory(Base):
    """Audit trail for contract status changes and modifications."""
    __tablename__ = "contract_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # created, submitted, approved, activated, terminated, renewed
    old_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    performed_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="history")
    performer = relationship("User")

    __table_args__ = (
        Index("ix_contract_history_action", "action"),
        Index("ix_contract_history_performed_at", "performed_at"),
        Index("ix_contract_history_performed_by", "performed_by_id"),
    )
