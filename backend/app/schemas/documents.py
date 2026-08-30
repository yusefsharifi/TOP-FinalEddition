"""
Documents Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

_ro = ConfigDict(from_attributes=True)


class DocumentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field("general", max_length=50)
    tags: list[str] = Field(default_factory=list)


class DocumentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[list[str]] = None


class DocumentResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    description: Optional[str] = None
    category: str
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    tags: list[str] = []
    version: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class DocumentVersionResponse(BaseModel):
    model_config = _ro
    id: int
    document_id: int
    version: int
    file_path: str
    file_size: int
    uploaded_by_id: int
    uploaded_at: datetime
    change_notes: Optional[str] = None
