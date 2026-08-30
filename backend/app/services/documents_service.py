"""
Documents Module — Service Layer
TOP WorX ERP System

Handles file upload, versioning, and storage.
"""
from __future__ import annotations

import os
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.documents import document_crud
from app.models.workflow import Document


class DocumentsError(Exception):
    """Documents business logic error."""
    pass


class DocumentsService:
    async def upload_file(
        self,
        db: AsyncSession,
        doc: Document,
        *,
        file_content: bytes,
        filename: str,
        content_type: Optional[str] = None,
        user_id: int,
    ) -> Document:
        """Upload a file for a document and update its metadata."""
        # Save file to disk
        upload_dir = os.path.join(settings.UPLOAD_DIR, "documents", str(doc.id))
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        # Update document metadata
        doc = await document_crud.update_file(
            db, doc,
            file_path=file_path,
            file_type=filename.split(".")[-1] if "." in filename else None,
            file_size=len(file_content),
            mime_type=content_type,
        )
        return doc

    async def upload_new_version(
        self,
        db: AsyncSession,
        doc: Document,
        *,
        file_content: bytes,
        filename: str,
        content_type: Optional[str] = None,
        change_notes: Optional[str] = None,
        user_id: int,
    ) -> Document:
        """Upload a new version of a document."""
        doc = await document_crud.new_version(db, doc)

        # Save to versioned directory
        upload_dir = os.path.join(
            settings.UPLOAD_DIR, "documents", str(doc.id), f"v{doc.version}"
        )
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        doc = await document_crud.update_file(
            db, doc,
            file_path=file_path,
            file_type=filename.split(".")[-1] if "." in filename else None,
            file_size=len(file_content),
            mime_type=content_type,
        )
        return doc


documents_service = DocumentsService()
