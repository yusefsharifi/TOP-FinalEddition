"""
BI Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

_ro = ConfigDict(from_attributes=True)


# ===========================================================================
# KPI Snapshots
# ===========================================================================
class KPISnapshotResponse(BaseModel):
    model_config = _ro
    id: int
    kpi_name: str
    value: Decimal
    unit: Optional[str] = None
    period_label: str
    metadata: Optional[dict] = None
    snapshot_at: datetime


# ===========================================================================
# Alerts
# ===========================================================================
class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    metric: str = Field(..., min_length=1, max_length=100)
    condition: str = Field(..., description="above|below|equal|change_percent_above|change_percent_below")
    threshold: Decimal
    severity: str = Field("warning", max_length=20)
    channels: list[str] = Field(default_factory=lambda: ["in_app"])
    recipient_user_ids: list[int] = Field(default_factory=list)
    cooldown_minutes: int = Field(60, ge=1, le=1440)


class AlertRuleResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    description: Optional[str] = None
    metric: str
    condition: str
    threshold: Decimal
    severity: str
    channels: Optional[list] = None
    is_active: bool
    cooldown_minutes: int
    created_by_id: Optional[int] = None
    created_at: datetime


class AlertEventResponse(BaseModel):
    model_config = _ro
    id: int
    rule_id: int
    metric_value: Decimal
    threshold_value: Decimal
    message: str
    acknowledged: bool
    acknowledged_by_id: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    triggered_at: datetime


# ===========================================================================
# Report Templates
# ===========================================================================
class ReportTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    config: dict
    is_public: bool = False


class ReportTemplateResponse(BaseModel):
    model_config = _ro
    id: int
    name: str
    description: Optional[str] = None
    config: dict
    is_system: bool
    is_public: bool
    run_count: int
    created_by_id: Optional[int] = None
    created_at: datetime


# ===========================================================================
# Report Build
# ===========================================================================
class ReportBuildRequest(BaseModel):
    base_table: str = Field("sales", max_length=50)
    dimensions: list[str] = Field(default_factory=list)
    measures: list[str] = Field(default_factory=lambda: ["total_amount"])
    filters: dict = Field(default_factory=dict)
    sort_by: list[str] = Field(default_factory=list)
    limit: int = Field(1000, ge=1, le=5000)


class ReportBuildResponse(BaseModel):
    columns: list[str]
    data: list[dict]
    row_count: int
    truncated: bool = False


# ===========================================================================
# ETL
# ===========================================================================
class ETLRunResponse(BaseModel):
    model_config = _ro
    id: int
    status: str
    rows_inserted: int
    duration_seconds: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
