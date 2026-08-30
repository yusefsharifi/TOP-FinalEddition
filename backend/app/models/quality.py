"""
Quality Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Models for quality inspections, defect tracking, and compliance.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Enum, Float,
    ForeignKey, Index, Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class InspectionStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DefectSeverity(str, enum.Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    COSMETIC = "cosmetic"


class DefectStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class QualityInspection(Base):
    """Quality inspection record."""
    __tablename__ = "quality_inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inspection_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    inspection_type: Mapped[str] = mapped_column(String(50), nullable=False, default="incoming")
    status: Mapped[InspectionStatus] = mapped_column(
        Enum(InspectionStatus), nullable=False, default=InspectionStatus.DRAFT, index=True
    )

    # References
    item_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("inventory_items.id", ondelete="SET NULL"), nullable=True, index=True
    )
    batch_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    supplier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Quantities
    quantity_inspected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_passed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pass_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Inspector
    inspector_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    defects: Mapped[list["QualityDefect"]] = relationship(
        "QualityDefect", back_populates="inspection", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_quality_inspections_status", "status"),
        Index("ix_quality_inspections_type", "inspection_type"),
        Index("ix_quality_inspections_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<QualityInspection {self.inspection_number} {self.status}>"


class QualityDefect(Base):
    """Quality defect record linked to an inspection."""
    __tablename__ = "quality_defects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inspection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quality_inspections.id", ondelete="CASCADE"), nullable=False, index=True
    )

    defect_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[DefectSeverity] = mapped_column(
        Enum(DefectSeverity), nullable=False, default=DefectSeverity.MINOR, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity_affected: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrective_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[DefectStatus] = mapped_column(
        Enum(DefectStatus), nullable=False, default=DefectStatus.OPEN, index=True
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    inspection: Mapped["QualityInspection"] = relationship("QualityInspection", back_populates="defects")

    __table_args__ = (
        Index("ix_quality_defects_status", "status"),
        Index("ix_quality_defects_severity", "severity"),
        Index("ix_quality_defects_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<QualityDefect {self.defect_type} {self.severity}>"
