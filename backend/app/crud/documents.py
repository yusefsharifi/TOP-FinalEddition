"""
Documents Module — CRUD Layer
TOP WorX ERP System

Replaces in-memory dict storage with proper database operations.
"""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Document


class DocumentCRUD:
    async def get(self, db: AsyncSession, doc_id: int) -> Optional[Document]:
        result = await db.execute(
            select(Document).where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        category: Optional[str] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[Document]]:
        q = select(Document).order_by(Document.created_at.desc())
        if category:
            q = q.where(Document.category == category)
        if search:
            term = f"%{search}%"
            q = q.where(or_(
                Document.name.ilike(term),
                Document.description.ilike(term),
            ))
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self,
        db: AsyncSession,
        *,
        name: str,
        description: Optional[str] = None,
        category: str = "general",
        tags: list[str] = None,
        created_by_id: int,
    ) -> Document:
        doc = Document(
            name=name,
            description=description,
            category=category,
            tags=tags or [],
            version=1,
            created_by_id=created_by_id,
        )
        db.add(doc)
        await db.flush()
        await db.refresh(doc)
        return doc

    async def update_file(
        self,
        db: AsyncSession,
        doc: Document,
        *,
        file_path: str,
        file_type: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
    ) -> Document:
        doc.file_path = file_path
        doc.file_type = file_type
        doc.file_size = file_size
        doc.mime_type = mime_type
        await db.flush()
        return doc

    async def new_version(
        self,
        db: AsyncSession,
        doc: Document,
    ) -> Document:
        doc.version += 1
        await db.flush()
        return doc


# Singleton
document_crud = DocumentCRUD()
