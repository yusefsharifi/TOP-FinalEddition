"""
Contracts Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.contracts import ContractStatus, ContractType

_ro = ConfigDict(from_attributes=True)


class ContractCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    contract_type: ContractType
    counterparty_name: str = Field(..., min_length=1, max_length=200)
    counterparty_contact: Optional[str] = Field(None, max_length=200)
    start_date: date
    end_date: date
    value: Optional[float] = Field(None, ge=0)
    currency: str = Field("IRR", max_length=3)
    terms: Optional[str] = None
    auto_renew: bool = False
    renewal_days_notice: int = Field(30, ge=1, le=365)


class ContractUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    counterparty_name: Optional[str] = Field(None, min_length=1, max_length=200)
    counterparty_contact: Optional[str] = None
    end_date: Optional[date] = None
    value: Optional[float] = Field(None, ge=0)
    terms: Optional[str] = None
    auto_renew: Optional[bool] = None
    renewal_days_notice: Optional[int] = Field(None, ge=1, le=365)


class ContractResponse(BaseModel):
    model_config = _ro
    id: int
    title: str
    description: Optional[str] = None
    contract_type: ContractType
    status: ContractStatus
    counterparty_name: str
    counterparty_contact: Optional[str] = None
    start_date: date
    end_date: date
    value: Optional[float] = None
    currency: str
    terms: Optional[str] = None
    auto_renew: bool
    renewal_days_notice: int
    created_by_id: int
    approved_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
