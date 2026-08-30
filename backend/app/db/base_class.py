"""
backend/app/db/base_class.py
Single shared SQLAlchemy 2.0 DeclarativeBase for the entire application.
ALL model files must import Base from here — never define their own.

Also exports AuditMixin with the canonical created_at/updated_at/created_by_id
fields so each module doesn't redefine them slightly differently.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Single metadata registry for the whole application."""
    pass


class AuditMixin:
    """
    Canonical audit columns — import this in every model that needs them.
    All 8 module model files previously defined their own slightly-different
    versions; this is the authoritative one.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
