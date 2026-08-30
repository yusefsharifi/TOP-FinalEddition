"""
HR Module — Pydantic v2 Schemas
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.hr import (
    AttendanceStatus, ContractStatus, ContractType, EmployeeStatus,
    EmploymentType, Gender, LeaveStatus, LeaveType, MaritalStatus,
    PayrollEntryStatus, PayrollPeriodStatus, WorkSchedule,
)

_ro = ConfigDict(from_attributes=True)


# ===========================================================================
# Department
# ===========================================================================
class DepartmentCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=200)
    name_fa: Optional[str] = None
    parent_id: Optional[int] = None
    cost_center_code: Optional[str] = None
    is_active: bool = True


class DepartmentResponse(DepartmentCreate):
    model_config = _ro
    id: int
    manager_id: Optional[int] = None
    children: list["DepartmentResponse"] = []


# ===========================================================================
# Employee
# ===========================================================================
class EmployeeCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    first_name_fa: Optional[str] = None
    last_name_fa: Optional[str] = None
    national_id: str = Field(..., min_length=10, max_length=10)
    birth_date: Optional[date] = None
    gender: Gender = Gender.MALE
    marital_status: MaritalStatus = MaritalStatus.SINGLE
    department_id: Optional[int] = None
    job_title: Optional[str] = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    join_date: date
    base_salary: Decimal = Field(ge=Decimal("0"))
    salary_bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    insurance_exempt: bool = False
    tax_exempt: bool = False
    children_count: int = Field(0, ge=0)
    default_cost_center: Optional[str] = None
    work_schedule: WorkSchedule = WorkSchedule.STANDARD
    annual_leave_balance: int = Field(26, ge=0)
    sick_leave_balance: int = Field(12, ge=0)

    @field_validator("national_id")
    @classmethod
    def validate_national_id(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 10:
            raise ValueError("National ID must be exactly 10 digits")
        return v


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    first_name_fa: Optional[str] = None
    last_name_fa: Optional[str] = None
    job_title: Optional[str] = None
    department_id: Optional[int] = None
    employment_type: Optional[EmploymentType] = None
    base_salary: Optional[Decimal] = Field(None, ge=Decimal("0"))
    salary_bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    marital_status: Optional[MaritalStatus] = None
    children_count: Optional[int] = Field(None, ge=0)
    status: Optional[EmployeeStatus] = None
    insurance_exempt: Optional[bool] = None
    tax_exempt: Optional[bool] = None
    default_cost_center: Optional[str] = None
    annual_leave_balance: Optional[int] = None
    sick_leave_balance: Optional[int] = None
    leave_date: Optional[date] = None


class EmployeeResponse(BaseModel):
    model_config = _ro
    id: int
    employee_code: str
    first_name: str
    last_name: str
    first_name_fa: Optional[str] = None
    last_name_fa: Optional[str] = None
    national_id: str
    birth_date: Optional[date] = None
    gender: Gender
    marital_status: MaritalStatus
    department_id: Optional[int] = None
    job_title: Optional[str] = None
    employment_type: EmploymentType
    join_date: date
    leave_date: Optional[date] = None
    status: EmployeeStatus
    base_salary: Decimal
    salary_bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    insurance_exempt: bool
    tax_exempt: bool
    children_count: int
    default_cost_center: Optional[str] = None
    work_schedule: WorkSchedule
    annual_leave_balance: int
    sick_leave_balance: int
    created_at: datetime


# ===========================================================================
# Contract
# ===========================================================================
class ContractCreate(BaseModel):
    employee_id: int
    contract_type: ContractType = ContractType.PERMANENT
    start_date: date
    end_date: Optional[date] = None
    base_salary: Decimal = Field(gt=Decimal("0"))
    benefits_description: Optional[str] = None
    notice_period_days: int = 30
    signed_date: Optional[date] = None


class ContractResponse(ContractCreate):
    model_config = _ro
    id: int
    status: ContractStatus


# ===========================================================================
# Attendance
# ===========================================================================
class CheckInRequest(BaseModel):
    employee_id: int
    record_date: date
    check_in_time: time
    notes: Optional[str] = None


class CheckOutRequest(BaseModel):
    employee_id: int
    record_date: date
    check_out_time: time


class AttendanceResponse(BaseModel):
    model_config = _ro
    id: int
    employee_id: int
    record_date: date
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    work_hours: Decimal
    overtime_hours: Decimal
    night_hours: Decimal
    status: AttendanceStatus
    approved_by_id: Optional[int] = None
    notes: Optional[str] = None


class AttendanceSummary(BaseModel):
    employee_id: int
    employee_name: str
    month: int
    year: int
    total_working_days: int
    present_days: int
    absent_days: int
    leave_days: int
    total_hours: Decimal
    total_overtime: Decimal
    total_night_hours: Decimal


# ===========================================================================
# Leave
# ===========================================================================
class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveApprove(BaseModel):
    notes: Optional[str] = None


class LeaveReject(BaseModel):
    reason: str = Field(..., min_length=1)


class LeaveResponse(BaseModel):
    model_config = _ro
    id: int
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    days_requested: int
    status: LeaveStatus
    approver_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    balance_after: Optional[int] = None
    created_at: datetime


# ===========================================================================
# Payroll
# ===========================================================================
class PayrollPeriodCreate(BaseModel):
    year: int = Field(..., ge=1380, le=1450)
    month: int = Field(..., ge=1, le=12)
    start_date: date
    end_date: date


class PayrollEntryAdjust(BaseModel):
    """Manually adjust an individual payroll entry."""
    bonus: Optional[Decimal] = Field(None, ge=Decimal("0"))
    other_earnings: Optional[Decimal] = Field(None, ge=Decimal("0"))
    advance_deduction: Optional[Decimal] = Field(None, ge=Decimal("0"))
    loan_deduction: Optional[Decimal] = Field(None, ge=Decimal("0"))
    other_deductions: Optional[Decimal] = Field(None, ge=Decimal("0"))
    notes: Optional[str] = None


class PayrollEntryResponse(BaseModel):
    model_config = _ro
    id: int
    period_id: int
    employee_id: int
    base_salary: Decimal
    overtime_pay: Decimal
    housing_allowance: Decimal
    food_allowance: Decimal
    childcare_allowance: Decimal
    bonus: Decimal
    other_earnings: Decimal
    total_earnings: Decimal
    working_days: int
    overtime_hours: Decimal
    absent_days: int
    leave_days: int
    insurance_employee: Decimal
    insurance_employer: Decimal
    tax: Decimal
    advance_deduction: Decimal
    loan_deduction: Decimal
    other_deductions: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    cost_center: Optional[str] = None
    status: PayrollEntryStatus
    payment_reference: Optional[str] = None
    paid_at: Optional[datetime] = None


class PayrollPeriodResponse(BaseModel):
    model_config = _ro
    id: int
    year: int
    month: int
    start_date: date
    end_date: date
    status: PayrollPeriodStatus
    total_employees: int
    total_gross: Decimal
    total_net: Decimal
    total_tax: Decimal
    total_insurance_employee: Decimal
    total_insurance_employer: Decimal
    journal_entry_id: Optional[int] = None
    payment_batch_id: Optional[str] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime


# ===========================================================================
# Reports
# ===========================================================================
class HeadcountRow(BaseModel):
    department_id: Optional[int] = None
    department_name: str
    total: int
    active: int
    on_leave: int
    by_type: dict[str, int]


class PayrollSummaryRow(BaseModel):
    department: str
    employee_count: int
    total_gross: Decimal
    total_net: Decimal
    total_tax: Decimal
    total_insurance: Decimal
    total_cost: Decimal   # gross + employer insurance


class TaxWithholdingRow(BaseModel):
    """For سازمان امور مالیاتی report."""
    employee_code: str
    employee_name: str
    national_id: str
    gross_salary: Decimal
    tax_withheld: Decimal
    cumulative_tax: Decimal


class InsuranceSummaryRow(BaseModel):
    """For سازمان تأمین اجتماعی monthly report."""
    employee_code: str
    employee_name: str
    national_id: str
    insurable_salary: Decimal
    employee_share: Decimal    # 7%
    employer_share: Decimal    # 23%
    total: Decimal


class EndOfServiceResponse(BaseModel):
    employee_id: int
    employee_name: str
    years_of_service: Decimal
    base_salary: Decimal
    total_eos: Decimal
    calculation_detail: str
