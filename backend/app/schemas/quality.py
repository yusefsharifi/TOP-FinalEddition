"""
Quality Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

_ro = ConfigDict(from_attributes=True)


class QualityInspectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    inspection_type: str = Field("incoming", max_length=50)
    item_id: Optional[int] = None
    batch_number: Optional[str] = Field(None, max_length=100)
    supplier_id: Optional[int] = None
    quantity_inspected: int = Field(0, ge=0)
    quantity_passed: int = Field(0, ge=0)
    quantity_failed: int = Field(0, ge=0)
    notes: Optional[str] = None


class QualityInspectionResponse(BaseModel):
    model_config = _ro
    id: int
    inspection_number: str
    name: str
    description: Optional[str] = None
    inspection_type: str
    status: str
    item_id: Optional[int] = None
    batch_number: Optional[str] = None
    supplier_id: Optional[int] = None
    quantity_inspected: int
    quantity_passed: int
    quantity_failed: int
    pass_rate: float
    inspector_id: int
    notes: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class QualityInspectionUpdate(BaseModel):
    status: Optional[str] = None
    quantity_inspected: Optional[int] = Field(None, ge=0)
    quantity_passed: Optional[int] = Field(None, ge=0)
    quantity_failed: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class QualityDefectCreate(BaseModel):
    inspection_id: int
    defect_type: str = Field(..., max_length=100)
    severity: str = Field("minor", max_length=20)
    description: str = Field(..., min_length=1)
    quantity_affected: int = Field(1, ge=0)
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None


class QualityDefectResponse(BaseModel):
    model_config = _ro
    id: int
    inspection_id: int
    defect_type: str
    severity: str
    description: str
    quantity_affected: int
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None


class QualityDefectUpdate(BaseModel):
    status: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None


class QualityDashboardResponse(BaseModel):
    total_inspections: int
    pass_rate: float
    total_defects: int
    open_defects: int
    defects_by_severity: dict[str, int]
    recent_inspections: list[QualityInspectionResponse]
