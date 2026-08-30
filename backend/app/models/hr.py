"""
HR & Payroll Module — SQLAlchemy 2.0 Models
TOP WorX ERP System

Employee lifecycle:
  Department → Employee → EmploymentContract → AttendanceRecord → LeaveRequest
  → PayrollPeriod → PayrollEntry → PayrollComponent

Integration points:
  • PayrollPeriod.journal_entry_id  → finance.journal_entries
  • PayrollComponent.debit_account_id / credit_account_id → finance.accounts
  • Department.cost_center_code     → used as JE cost_center label

Iranian Labor Law context:
  - Insurance: 7% employee + 23% employer (اداره کار)
  - Tax: progressive brackets per سازمان امور مالیاتی
  - Annual leave: 26 days (قانون کار)
  - Standard work: 44 hours/week, 7.33 hours/day
  - Overtime premium: 40% (1.4x)
  - Holiday premium: 80% (1.8x)
"""
from __future__ import annotations

import enum
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, Enum,
    ForeignKey, Index, Integer, Numeric, String, Text, Time,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class MaritalStatus(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class WorkSchedule(str, enum.Enum):
    STANDARD = "standard"    # 8am-5pm, Sat-Wed (Iran)
    SHIFT = "shift"
    FLEXIBLE = "flexible"


class ContractType(str, enum.Enum):
    PERMANENT = "permanent"
    FIXED_TERM = "fixed_term"
    PROJECT_BASED = "project_based"


class ContractStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"
    SICK = "sick"
    REMOTE = "remote"
    HOLIDAY = "holiday"
    HALF_DAY = "half_day"


class LeaveType(str, enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    UNPAID = "unpaid"
    MARRIAGE = "marriage"      # 3 days (Iranian law)
    BEREAVEMENT = "bereavement" # 3 days
    MATERNITY = "maternity"    # 90 days (Iranian law)
    PATERNITY = "paternity"
    HAJJ = "hajj"              # once per career (Iranian law)
    OTHER = "other"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class PayrollPeriodStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    APPROVED = "approved"
    PAID = "paid"
    CLOSED = "closed"


class PayrollEntryStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    PAID = "paid"


class ComponentType(str, enum.Enum):
    EARNING = "earning"
    DEDUCTION = "deduction"


class ComponentCategory(str, enum.Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    CALCULATED = "calculated"


class CalculationMethod(str, enum.Enum):
    FLAT_AMOUNT = "flat_amount"
    PERCENTAGE_OF_BASE = "percentage_of_base"
    PERCENTAGE_OF_GROSS = "percentage_of_gross"
    FORMULA = "formula"


class DeviceType(str, enum.Enum):
    FINGERPRINT = "fingerprint"
    CARD = "card"
    FACE = "face"
    PIN = "pin"


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------
class Department(AuditMixin, Base):
    """
    Hierarchical department tree.
    cost_center_code links to Finance JE cost_center field for expense allocation.
    """
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True)
    manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    cost_center_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    parent: Mapped[Optional["Department"]] = relationship("Department", remote_side="Department.id", back_populates="children")
    children: Mapped[list["Department"]] = relationship("Department", back_populates="parent")
    employees: Mapped[list["Employee"]] = relationship("Employee", foreign_keys="Employee.department_id", back_populates="department")

    __table_args__ = (
        Index("ix_departments_code", "code"),
        Index("ix_departments_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Department {self.code} — {self.name}>"


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------
class Employee(AuditMixin, Base):
    """
    Central HR entity. Denormalised `base_salary` reflects current active contract.
    All monetary values in IRR (Decimal 18,4).
    """
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Personal
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name_fa: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name_fa: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    national_id: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False, default=Gender.MALE)
    marital_status: Mapped[MaritalStatus] = mapped_column(Enum(MaritalStatus), nullable=False, default=MaritalStatus.SINGLE)

    # Employment
    employee_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True, index=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    employment_type: Mapped[EmploymentType] = mapped_column(Enum(EmploymentType), nullable=False, default=EmploymentType.FULL_TIME)
    join_date: Mapped[date] = mapped_column(Date, nullable=False)
    leave_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[EmployeeStatus] = mapped_column(Enum(EmployeeStatus), nullable=False, default=EmployeeStatus.ACTIVE, index=True)

    # Financial
    base_salary: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    salary_bank_account: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bank_account_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)

    # Benefits flags
    insurance_exempt: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tax_exempt: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    children_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # For tax deduction

    # Work settings
    default_cost_center: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    work_schedule: Mapped[WorkSchedule] = mapped_column(Enum(WorkSchedule), nullable=False, default=WorkSchedule.STANDARD)
    annual_leave_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=26)   # days
    sick_leave_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=12)

    # Relationships
    department: Mapped[Optional["Department"]] = relationship("Department", foreign_keys=[department_id], back_populates="employees")
    contracts: Mapped[list["EmploymentContract"]] = relationship("EmploymentContract", back_populates="employee", cascade="all, delete-orphan")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="employee", cascade="all, delete-orphan")
    leave_requests: Mapped[list["LeaveRequest"]] = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")
    payroll_entries: Mapped[list["PayrollEntry"]] = relationship("PayrollEntry", back_populates="employee")

    __table_args__ = (
        CheckConstraint("base_salary >= 0", name="chk_employee_salary"),
        CheckConstraint("children_count >= 0", name="chk_employee_children"),
        Index("ix_employees_employee_code", "employee_code"),
        Index("ix_employees_national_id", "national_id"),
        Index("ix_employees_status", "status"),
        Index("ix_employees_department_id", "department_id"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name_fa(self) -> str:
        return f"{self.first_name_fa or ''} {self.last_name_fa or ''}".strip()

    def __repr__(self) -> str:
        return f"<Employee {self.employee_code} — {self.full_name}>"


# ---------------------------------------------------------------------------
# EmploymentContract
# ---------------------------------------------------------------------------
class EmploymentContract(AuditMixin, Base):
    __tablename__ = "employment_contracts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_type: Mapped[ContractType] = mapped_column(Enum(ContractType), nullable=False, default=ContractType.PERMANENT)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    benefits_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notice_period_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    termination_clause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contract_file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    signed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[ContractStatus] = mapped_column(Enum(ContractStatus), nullable=False, default=ContractStatus.ACTIVE)
    employee: Mapped["Employee"] = relationship("Employee", back_populates="contracts")
    __table_args__ = (
        CheckConstraint("base_salary > 0", name="chk_contract_salary"),
        Index("ix_employment_contracts_employee_id", "employee_id"),
        Index("ix_employment_contracts_status", "status"),
    )


# ---------------------------------------------------------------------------
# AttendanceRecord
# ---------------------------------------------------------------------------
class AttendanceRecord(AuditMixin, Base):
    """
    One record per employee per day.
    work_hours and overtime_hours computed from check_in/check_out.
    Standard: 7.33 hours/day (44h/week ÷ 6 days, Iranian calendar Sat-Thu).
    """
    __tablename__ = "attendance_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    check_in: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    check_out: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    work_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    overtime_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    night_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    device_record_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # ID from biometric device
    employee: Mapped["Employee"] = relationship("Employee", back_populates="attendance_records")
    __table_args__ = (
        UniqueConstraint("employee_id", "record_date", name="uq_attendance_employee_date"),
        CheckConstraint("work_hours >= 0", name="chk_attendance_hours"),
        CheckConstraint("overtime_hours >= 0", name="chk_attendance_overtime"),
        Index("ix_attendance_employee_date", "employee_id", "record_date"),
    )


# ---------------------------------------------------------------------------
# LeaveRequest
# ---------------------------------------------------------------------------
class LeaveRequest(AuditMixin, Base):
    __tablename__ = "leave_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type: Mapped[LeaveType] = mapped_column(Enum(LeaveType), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_requested: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attachment_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[LeaveStatus] = mapped_column(Enum(LeaveStatus), nullable=False, default=LeaveStatus.PENDING, index=True)
    approver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    balance_after: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Remaining after approval
    employee: Mapped["Employee"] = relationship("Employee", back_populates="leave_requests")
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_leave_dates"),
        CheckConstraint("days_requested > 0", name="chk_leave_days"),
        Index("ix_leave_requests_employee_id", "employee_id"),
        Index("ix_leave_requests_status", "status"),
        Index("ix_leave_requests_dates", "start_date", "end_date"),
    )


# ---------------------------------------------------------------------------
# AttendanceDevice
# ---------------------------------------------------------------------------
class AttendanceDevice(AuditMixin, Base):
    __tablename__ = "attendance_devices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(Enum(DeviceType), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    port: Mapped[int] = mapped_column(Integer, nullable=False, default=4370)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# ---------------------------------------------------------------------------
# PayrollComponent
# ---------------------------------------------------------------------------
class PayrollComponent(AuditMixin, Base):
    """
    Configurable payroll components — both earnings and deductions.
    Insurance and tax are seeded as CALCULATED type.
    """
    __tablename__ = "payroll_components"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fa: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[ComponentType] = mapped_column(Enum(ComponentType), nullable=False, index=True)
    category: Mapped[ComponentCategory] = mapped_column(Enum(ComponentCategory), nullable=False)
    calculation_method: Mapped[CalculationMethod] = mapped_column(Enum(CalculationMethod), nullable=False)
    default_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=Decimal("0"))
    formula: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Python expression
    debit_account_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    credit_account_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_insurable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


# ---------------------------------------------------------------------------
# PayrollPeriod
# ---------------------------------------------------------------------------
class PayrollPeriod(AuditMixin, Base):
    """One payroll run per month. JE generated on APPROVED → PAID transition."""
    __tablename__ = "payroll_periods"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)          # Jalali year
    month: Mapped[int] = mapped_column(Integer, nullable=False)         # 1–12 (Jalali)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[PayrollPeriodStatus] = mapped_column(Enum(PayrollPeriodStatus), nullable=False, default=PayrollPeriodStatus.DRAFT, index=True)
    # Summary (denormalised)
    total_employees: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_gross: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_net: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_tax: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_insurance_employee: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_insurance_employer: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    # Accounting
    journal_entry_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True)
    payment_batch_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # Approval
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    entries: Mapped[list["PayrollEntry"]] = relationship("PayrollEntry", back_populates="period", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("year", "month", name="uq_payroll_period_year_month"),
        CheckConstraint("month BETWEEN 1 AND 12", name="chk_payroll_month"),
        Index("ix_payroll_periods_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<PayrollPeriod {self.year}/{self.month:02d} {self.status}>"


# ---------------------------------------------------------------------------
# PayrollEntry  (per employee per month)
# ---------------------------------------------------------------------------
class PayrollEntry(AuditMixin, Base):
    """
    All monetary fields in IRR Decimal(18,4).
    insurance_employer is the company's cost (23%) — not deducted from employee.
    """
    __tablename__ = "payroll_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_periods.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Earnings
    base_salary: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    overtime_pay: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    bonus: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    housing_allowance: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))   # حق مسکن
    food_allowance: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))      # حق خوار و بار
    childcare_allowance: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0")) # کمک هزینه اولاد
    other_earnings: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_earnings: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))

    # Deductions
    insurance_employee: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))   # 7%
    insurance_employer: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))   # 23% (company cost)
    tax: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    advance_deduction: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))    # مساعده
    loan_deduction: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    other_deductions: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))

    # Net
    net_salary: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))

    # Work data (snapshot from attendance)
    working_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overtime_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=Decimal("0"))
    absent_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    leave_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Cost allocation
    cost_center: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    department_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    status: Mapped[PayrollEntryStatus] = mapped_column(Enum(PayrollEntryStatus), nullable=False, default=PayrollEntryStatus.DRAFT)
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    individual_je_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True)

    period: Mapped["PayrollPeriod"] = relationship("PayrollPeriod", back_populates="entries")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="payroll_entries")

    __table_args__ = (
        UniqueConstraint("period_id", "employee_id", name="uq_payroll_entry_period_employee"),
        CheckConstraint("total_earnings >= 0", name="chk_payroll_earnings"),
        CheckConstraint("net_salary >= 0", name="chk_payroll_net"),
        Index("ix_payroll_entries_period_id", "period_id"),
        Index("ix_payroll_entries_employee_id", "employee_id"),
    )