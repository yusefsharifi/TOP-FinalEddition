"""
Documents Module — FastAPI Router
TOP WorX ERP System

Manages document uploads, storage, versions, and sharing.
Uses SQLAlchemy models from app.models.document.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import DBDep, CurrentUser
from app.core.config import settings
from app.models.document import Document, DocumentVersion, DocumentCategory

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class DocumentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: DocumentCategory = DocumentCategory.GENERAL
    tags: list[str] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: DocumentCategory
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    tags: list[str]
    version: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentVersionResponse(BaseModel):
    version: int
    file_path: str
    file_size: int
    uploaded_by_id: int
    uploaded_at: datetime
    change_notes: Optional[str] = None


# ── DOCUMENTS CRUD ───────────────────────────────────────────────────────────

@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    db: DBDep,
    current_user: CurrentUser,
    category: Optional[DocumentCategory] = None,
    search: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[DocumentResponse]:
    """List documents with optional filtering."""
    q = select(Document).order_by(Document.created_at.desc())
    if category:
        q = q.where(Document.category == category)
    if search:
        term = f"%{search}%"
        q = q.where(
            (Document.name.ilike(term)) | (Document.description.ilike(term))
        )
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    
    result = []
    for r in rows:
        doc_resp = DocumentResponse(
            id=r.id,
            name=r.name,
            description=r.description,
            category=r.category,
            file_path=r.file_path,
            file_type=r.file_type,
            file_size=r.file_size,
            mime_type=r.mime_type,
            tags=json.loads(r.tags) if r.tags else [],
            version=r.version,
            created_by_id=r.created_by_id,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        result.append(doc_resp)
    return result


@router.post("", response_model=DocumentResponse, status_code=201)
async def create_document(
    data: DocumentCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> DocumentResponse:
    """Create a document metadata entry (upload file separately)."""
    doc = Document(
        name=data.name,
        description=data.description,
        category=data.category,
        tags=json.dumps(data.tags),
        version=1,
        created_by_id=current_user.id,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    
    return DocumentResponse(
        id=doc.id,
        name=doc.name,
        description=doc.description,
        category=doc.category,
        file_path=doc.file_path,
        file_type=doc.file_type,
        file_size=doc.file_size,
        mime_type=doc.mime_type,
        tags=data.tags,
        version=doc.version,
        created_by_id=doc.created_by_id,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> DocumentResponse:
    """Get document details."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    
    return DocumentResponse(
        id=doc.id,
        name=doc.name,
        description=doc.description,
        category=doc.category,
        file_path=doc.file_path,
        file_type=doc.file_type,
        file_size=doc.file_size,
        mime_type=doc.mime_type,
        tags=json.loads(doc.tags) if doc.tags else [],
        version=doc.version,
        created_by_id=doc.created_by_id,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.post("/{doc_id}/upload")
async def upload_document_file(
    doc_id: int,
    db: DBDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> dict:
    """Upload a file for an existing document entry."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    
    # Validate file size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(413, f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.0f}MB")
    
    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "documents", str(doc_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename or "unnamed")
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update document
    doc.file_path = file_path
    doc.file_type = file.filename.split(".")[-1] if file.filename else None
    doc.file_size = len(content)
    doc.mime_type = file.content_type
    doc.updated_by_id = current_user.id
    
    # Record version
    version = DocumentVersion(
        document_id=doc.id,
        version=doc.version,
        file_path=file_path,
        file_size=len(content),
        uploaded_by_id=current_user.id,
    )
    db.add(version)
    
    await db.commit()
    return {"status": "uploaded", "file_path": file_path, "size": len(content)}


@router.post("/{doc_id}/new-version")
async def upload_new_version(
    doc_id: int,
    db: DBDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    change_notes: Optional[str] = None,
) -> dict:
    """Upload a new version of a document."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(413, f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.0f}MB")
    
    # Save new version
    new_version_num = doc.version + 1
    upload_dir = os.path.join(settings.UPLOAD_DIR, "documents", str(doc_id), f"v{new_version_num}")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename or "unnamed")
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update document
    doc.version = new_version_num
    doc.file_path = file_path
    doc.file_type = file.filename.split(".")[-1] if file.filename else None
    doc.file_size = len(content)
    doc.mime_type = file.content_type
    doc.updated_by_id = current_user.id
    
    # Record version
    version = DocumentVersion(
        document_id=doc.id,
        version=new_version_num,
        file_path=file_path,
        file_size=len(content),
        change_notes=change_notes,
        uploaded_by_id=current_user.id,
    )
    db.add(version)
    
    await db.commit()
    return {"status": "uploaded", "version": new_version_num, "file_path": file_path}


@router.get("/{doc_id}/versions", response_model=list[DocumentVersionResponse])
async def list_versions(
    doc_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> list[DocumentVersionResponse]:
    """List all versions of a document."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    
    q = select(DocumentVersion).where(
        DocumentVersion.document_id == doc_id
    ).order_by(DocumentVersion.version.desc())
    rows = (await db.execute(q)).scalars().all()
    
    return [
        DocumentVersionResponse(
            version=r.version,
            file_path=r.file_path,
            file_size=r.file_size,
            uploaded_by_id=r.uploaded_by_id,
            uploaded_at=r.uploaded_at,
            change_notes=r.change_notes,
        )
        for r in rows
    ]


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    """Delete a document and its versions."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    # TODO: Check if document is referenced by other modules
    await db.delete(doc)
    await db.commit()
