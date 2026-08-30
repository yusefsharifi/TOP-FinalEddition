"""
Documents Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Document management with versions, storage, and sharing.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime, Enum, ForeignKey,
    Index, Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


# ── Enums ────────────────────────────────────────────────────────────────────

class DocumentCategory(str, enum.Enum):
    GENERAL = "general"
    CONTRACT = "contract"
    INVOICE = "invoice"
    REPORT = "report"
    POLICY = "policy"
    PROCEDURE = "procedure"
    FORM = "form"
    OTHER = "other"


# ── Models ───────────────────────────────────────────────────────────────────

class Document(Base):
    """Document metadata with versioning."""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[DocumentCategory] = mapped_column(
        Enum(DocumentCategory), nullable=False, default=DocumentCategory.GENERAL, index=True
    )
    
    # File info
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Tags (stored as JSON string)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Audit
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_documents_category", "category"),
        Index("ix_documents_created_by", "created_by_id"),
        Index("ix_documents_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Document {self.name} v{self.version}>"


class DocumentVersion(Base):
    """Document version history."""
    __tablename__ = "document_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    change_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Audit
    uploaded_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_document_versions_document", "document_id"),
        Index("ix_document_versions_version", "version"),
    )
