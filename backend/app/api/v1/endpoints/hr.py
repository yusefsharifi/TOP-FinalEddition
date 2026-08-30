"""
HR & Payroll Module — FastAPI Router
TOP WorX ERP System

INTEGRATION POINT: Register in api.py:
    from app.api.api_v1.endpoints.hr import router as hr_router
    api_router.include_router(hr_router, prefix="/hr", tags=["hr"])
"""
from __future__ import annotations

import random
import string
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hr import (
    AttendanceRecord, Department, Employee, EmployeeStatus,
    EmploymentContract, LeaveRequest, LeaveStatus, LeaveType,
    PayrollEntry, PayrollEntryStatus, PayrollPeriod, PayrollPeriodStatus,
)
from app.schemas.hr import (
    AttendanceResponse, AttendanceSummary, CheckInRequest, CheckOutRequest,
    ContractCreate, ContractResponse, DepartmentCreate, DepartmentResponse,
    EmployeeCreate, EmployeeResponse, EmployeeUpdate,
    EndOfServiceResponse, HeadcountRow, InsuranceSummaryRow,
    LeaveApprove, LeaveReject, LeaveRequestCreate, LeaveResponse,
    PayrollEntryAdjust, PayrollEntryResponse, PayrollPeriodCreate,
    PayrollPeriodResponse, PayrollSummaryRow, TaxWithholdingRow,
)
from app.services.hr_service import (
    HRError, attendance_service, leave_service, payroll_service,
)
from app.services.payroll_calculator import payroll_calculator

# ---------------------------------------------------------------------------
# Real dependencies from centralized deps module
# ---------------------------------------------------------------------------
from app.api.deps import DBDep, get_current_active_user as get_current_user

# CU = CurrentUser alias — typed dependency for this module
from typing import Annotated
from app.models.auth_enhanced import User
CU = Annotated[User, Depends(get_current_user)]

router = APIRouter()


def _err(exc: HRError) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


def _gen_emp_code() -> str:
    year = 1403
    rand = "".join(random.choices(string.digits, k=4))
    return f"EMP-{year}-{rand}"


# ===========================================================================
# DEPARTMENTS
# ===========================================================================
@router.post("/departments", response_model=DepartmentResponse, status_code=201)
async def create_department(data: DepartmentCreate, db: DBDep, cu: CU) -> DepartmentResponse:
    existing = await db.execute(select(Department).where(Department.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(409, f"Department code '{data.code}' already exists")
    obj = Department(**data.model_dump(), created_by_id=cu.id, updated_by_id=cu.id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return DepartmentResponse.model_validate(obj)


@router.get("/departments", response_model=list[DepartmentResponse])
async def list_departments(db: DBDep, cu: CU) -> list[DepartmentResponse]:
    rows = (await db.execute(
        select(Department).where(Department.is_active.is_(True)).order_by(Department.code)
    )).scalars().all()
    nodes = {d.id: DepartmentResponse.model_validate(d) for d in rows}
    roots = []
    for d in rows:
        node = nodes[d.id]
        if d.parent_id and d.parent_id in nodes:
            nodes[d.parent_id].children.append(node)
        else:
            roots.append(node)
    return roots


@router.get("/departments/{dept_id}/costs")
async def department_costs(dept_id: int, db: DBDep, cu: CU, year: int = 1403, month: int = 1) -> dict:
    """Monthly salary costs for a department."""
    r = await db.execute(
        select(
            func.count(PayrollEntry.id).label("emp_count"),
            func.coalesce(func.sum(PayrollEntry.total_earnings), Decimal("0")).label("gross"),
            func.coalesce(func.sum(PayrollEntry.net_salary), Decimal("0")).label("net"),
            func.coalesce(func.sum(PayrollEntry.tax), Decimal("0")).label("tax"),
            func.coalesce(func.sum(PayrollEntry.insurance_employee + PayrollEntry.insurance_employer), Decimal("0")).label("ins"),
        )
        .join(PayrollPeriod, PayrollPeriod.id == PayrollEntry.period_id)
        .join(Employee, Employee.id == PayrollEntry.employee_id)
        .where(
            Employee.department_id == dept_id,
            PayrollPeriod.year == year,
            PayrollPeriod.month == month,
        )
    )
    row = r.one()
    return {
        "department_id": dept_id, "year": year, "month": month,
        "employee_count": row.emp_count,
        "total_gross": float(row.gross),
        "total_net": float(row.net),
        "total_tax": float(row.tax),
        "total_insurance": float(row.ins),
        "total_cost": float(row.gross) + float(row.ins) * 23 / 30,  # approx employer share
    }


# ===========================================================================
# EMPLOYEES
# ===========================================================================
@router.post("/employees", response_model=EmployeeResponse, status_code=201)
async def onboard_employee(data: EmployeeCreate, db: DBDep, cu: CU) -> EmployeeResponse:
    # Check national ID uniqueness
    existing = await db.execute(select(Employee).where(Employee.national_id == data.national_id))
    if existing.scalar_one_or_none():
        raise HTTPException(409, f"National ID {data.national_id} already registered")
    obj = Employee(
        **data.model_dump(),
        employee_code=_gen_emp_code(),
        status=EmployeeStatus.ACTIVE,
        created_by_id=cu.id,
        updated_by_id=cu.id,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return EmployeeResponse.model_validate(obj)


@router.get("/employees", response_model=list[EmployeeResponse])
async def list_employees(
    db: DBDep, cu: CU,
    department_id: Optional[int] = None,
    status: Optional[EmployeeStatus] = None,
    search: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[EmployeeResponse]:
    q = select(Employee).order_by(Employee.employee_code)
    if department_id:
        q = q.where(Employee.department_id == department_id)
    if status:
        q = q.where(Employee.status == status)
    if search:
        from sqlalchemy import or_
        term = f"%{search}%"
        q = q.where(or_(
            Employee.first_name.ilike(term), Employee.last_name.ilike(term),
            Employee.employee_code.ilike(term), Employee.national_id.ilike(term),
        ))
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [EmployeeResponse.model_validate(r) for r in rows]


@router.get("/employees/{emp_id}", response_model=EmployeeResponse)
async def get_employee(emp_id: int, db: DBDep, cu: CU) -> EmployeeResponse:
    emp = await db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    return EmployeeResponse.model_validate(emp)


@router.put("/employees/{emp_id}", response_model=EmployeeResponse)
async def update_employee(emp_id: int, data: EmployeeUpdate, db: DBDep, cu: CU) -> EmployeeResponse:
    emp = await db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)
    emp.updated_by_id = cu.id
    await db.commit()
    return EmployeeResponse.model_validate(emp)


@router.get("/employees/{emp_id}/end-of-service", response_model=EndOfServiceResponse)
async def calculate_eos(emp_id: int, db: DBDep, cu: CU, as_of_date: Optional[date] = None) -> EndOfServiceResponse:
    emp = await db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    result = payroll_calculator.calculate_end_of_service(
        emp.id, emp.base_salary, emp.join_date, as_of_date
    )
    return EndOfServiceResponse(
        employee_id=emp.id,
        employee_name=emp.full_name,
        years_of_service=result.years_of_service,
        base_salary=result.base_salary,
        total_eos=result.total_eos,
        calculation_detail=result.calculation_detail,
    )


# ===========================================================================
# CONTRACTS
# ===========================================================================
@router.post("/contracts", response_model=ContractResponse, status_code=201)
async def create_contract(data: ContractCreate, db: DBDep, cu: CU) -> ContractResponse:
    emp = await db.get(Employee, data.employee_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    obj = EmploymentContract(**data.model_dump(), created_by_id=cu.id, updated_by_id=cu.id)
    db.add(obj)
    # Update employee base_salary from contract
    emp.base_salary = data.base_salary
    await db.commit()
    await db.refresh(obj)
    return ContractResponse.model_validate(obj)


# ===========================================================================
# ATTENDANCE
# ===========================================================================
@router.post("/attendance/check-in", response_model=AttendanceResponse, status_code=201)
async def check_in(data: CheckInRequest, db: DBDep, cu: CU) -> AttendanceResponse:
    record = await attendance_service.check_in(
        db, data.employee_id, data.record_date, data.check_in_time,
        notes=data.notes, user_id=cu.id
    )
    await db.commit()
    return AttendanceResponse.model_validate(record)


@router.post("/attendance/check-out", response_model=AttendanceResponse)
async def check_out(data: CheckOutRequest, db: DBDep, cu: CU) -> AttendanceResponse:
    try:
        record = await attendance_service.check_out(
            db, data.employee_id, data.record_date, data.check_out_time, user_id=cu.id
        )
    except HRError as exc:
        raise _err(exc)
    await db.commit()
    return AttendanceResponse.model_validate(record)


@router.get("/attendance/summary")
async def attendance_summary(
    db: DBDep, cu: CU,
    employee_id: Optional[int] = None,
    year: int = Query(default=1403),
    month: int = Query(default=1, ge=1, le=12),
) -> list[dict]:
    from sqlalchemy import extract
    q = (
        select(
            AttendanceRecord.employee_id,
            func.count(AttendanceRecord.id).label("total"),
            func.coalesce(func.sum(AttendanceRecord.work_hours), Decimal("0")).label("hours"),
            func.coalesce(func.sum(AttendanceRecord.overtime_hours), Decimal("0")).label("ot"),
        )
        .group_by(AttendanceRecord.employee_id)
    )
    # Note: Filtering by Jalali month requires calendar conversion
    # DECISION POINT ⚙️: Add jdatetime library for Jalali ↔ Gregorian conversion
    if employee_id:
        q = q.where(AttendanceRecord.employee_id == employee_id)
    rows = (await db.execute(q)).all()
    return [{"employee_id": r.employee_id, "total_days": r.total,
              "total_hours": float(r.hours), "overtime_hours": float(r.ot)} for r in rows]


@router.put("/attendance/{record_id}/approve", response_model=AttendanceResponse)
async def approve_overtime(record_id: int, db: DBDep, cu: CU) -> AttendanceResponse:
    record = await db.get(AttendanceRecord, record_id)
    if not record:
        raise HTTPException(404, "Attendance record not found")
    record.approved_by_id = cu.id
    record.approved_at = datetime.utcnow()
    await db.commit()
    return AttendanceResponse.model_validate(record)


# ===========================================================================
# LEAVE
# ===========================================================================
@router.post("/leaves", response_model=LeaveResponse, status_code=201)
async def submit_leave(data: LeaveRequestCreate, db: DBDep, cu: CU) -> LeaveResponse:
    try:
        obj = await leave_service.submit_request(
            db, data.employee_id, data.leave_type,
            data.start_date, data.end_date, data.reason, user_id=cu.id
        )
    except HRError as exc:
        raise _err(exc)
    await db.commit()
    return LeaveResponse.model_validate(obj)


@router.get("/leaves", response_model=list[LeaveResponse])
async def list_leaves(
    db: DBDep, cu: CU,
    employee_id: Optional[int] = None,
    status: Optional[LeaveStatus] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[LeaveResponse]:
    q = select(LeaveRequest).order_by(LeaveRequest.start_date.desc())
    if employee_id:
        q = q.where(LeaveRequest.employee_id == employee_id)
    if status:
        q = q.where(LeaveRequest.status == status)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [LeaveResponse.model_validate(r) for r in rows]


@router.post("/leaves/{leave_id}/approve", response_model=LeaveResponse)
async def approve_leave(leave_id: int, data: LeaveApprove, db: DBDep, cu: CU) -> LeaveResponse:
    obj = await db.get(LeaveRequest, leave_id)
    if not obj:
        raise HTTPException(404, "Leave request not found")
    try:
        obj = await leave_service.approve(db, obj, approver_id=cu.id)
    except HRError as exc:
        raise _err(exc)
    await db.commit()
    return LeaveResponse.model_validate(obj)


@router.post("/leaves/{leave_id}/reject", response_model=LeaveResponse)
async def reject_leave(leave_id: int, data: LeaveReject, db: DBDep, cu: CU) -> LeaveResponse:
    obj = await db.get(LeaveRequest, leave_id)
    if not obj:
        raise HTTPException(404, "Leave request not found")
    try:
        obj = await leave_service.reject(db, obj, approver_id=cu.id, reason=data.reason)
    except HRError as exc:
        raise _err(exc)
    await db.commit()
    return LeaveResponse.model_validate(obj)


@router.get("/leaves/balance/{employee_id}")
async def leave_balance(employee_id: int, db: DBDep, cu: CU) -> dict:
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    return {
        "employee_id": employee_id,
        "annual_leave_balance": emp.annual_leave_balance,
        "sick_leave_balance": emp.sick_leave_balance,
    }


# ===========================================================================
# PAYROLL
# ===========================================================================
@router.post("/payroll/periods", response_model=PayrollPeriodResponse, status_code=201)
async def create_payroll_period(data: PayrollPeriodCreate, db: DBDep, cu: CU) -> PayrollPeriodResponse:
    # TODO: require_role(cu, ["admin", "hr_manager", "finance_manager"])
    try:
        period = await payroll_service.create_period(
            db, data.year, data.month, data.start_date, data.end_date, user_id=cu.id
        )
    except HRError as exc:
        raise _err(exc)
    await db.commit()
    return PayrollPeriodResponse.model_validate(period)


@router.get("/payroll/periods", response_model=list[PayrollPeriodResponse])
async def list_payroll_periods(db: DBDep, cu: CU) -> list[PayrollPeriodResponse]:
    rows = (await db.execute(
        select(PayrollPeriod).order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc())
    )).scalars().all()
    return [PayrollPeriodResponse.model_validate(r) for r in rows]


@router.post("/payroll/periods/{period_id}/calculate", response_model=PayrollPeriodResponse)
async def calculate_payroll(period_id: int, db: DBDep, cu: CU) -> PayrollPeriodResponse:
    period = await db.get(PayrollPeriod, period_id)
    if not period:
        raise HTTPException(404, "Payroll period not found")
    try:
        await payroll_service.calculate_period(db, period, user_id=cu.id)
    except HRError as exc:
        raise _err(exc)
    await db.commit()
    await db.refresh(period)
    return PayrollPeriodResponse.model_validate(period)


@router.get("/payroll/periods/{period_id}/entries", response_model=list[PayrollEntryResponse])
async def get_payroll_entries(period_id: int, db: DBDep, cu: CU) -> list[PayrollEntryResponse]:
    rows = (await db.execute(
        select(PayrollEntry).where(PayrollEntry.period_id == period_id)
        .order_by(PayrollEntry.employee_id)
    )).scalars().all()
    return [PayrollEntryResponse.model_validate(r) for r in rows]


@router.put("/payroll/entries/{entry_id}", response_model=PayrollEntryResponse)
async def adjust_payroll_entry(entry_id: int, data: PayrollEntryAdjust, db: DBDep, cu: CU) -> PayrollEntryResponse:
    entry = await db.get(PayrollEntry, entry_id)
    if not entry:
        raise HTTPException(404, "Payroll entry not found")
    if entry.status == PayrollEntryStatus.PAID:
        raise HTTPException(409, "Cannot adjust a PAID entry")

    for field, value in data.model_dump(exclude_unset=True, exclude={"notes"}).items():
        if value is not None:
            setattr(entry, field, value)

    # Recalculate totals
    entry.total_deductions = (
        entry.insurance_employee + entry.tax + entry.advance_deduction
        + entry.loan_deduction + entry.other_deductions
    )
    total_earn = (
        entry.base_salary + entry.overtime_pay + entry.housing_allowance
        + entry.food_allowance + entry.childcare_allowance
        + entry.bonus + entry.other_earnings
    )
    entry.total_earnings = total_earn
    entry.net_salary = max(total_earn - entry.total_deductions, Decimal("0"))
    entry.updated_by_id = cu.id
    await db.commit()
    return PayrollEntryResponse.model_validate(entry)


@router.post("/payroll/periods/{period_id}/approve", response_model=PayrollPeriodResponse)
async def approve_payroll(period_id: int, db: DBDep, cu: CU) -> PayrollPeriodResponse:
    # TODO: require_role(cu, ["admin", "hr_manager", "finance_manager"])
    period = await db.get(PayrollPeriod, period_id)
    if not period:
        raise HTTPException(404, "Payroll period not found")
    try:
        period = await payroll_service.approve_period(db, period, user_id=cu.id)
    except HRError as exc:
        raise _err(exc)
    await db.commit()
    return PayrollPeriodResponse.model_validate(period)


@router.post("/payroll/periods/{period_id}/pay", response_model=PayrollPeriodResponse)
async def pay_payroll(
    period_id: int, db: DBDep, cu: CU,
    bank_account_code: str = "1110",
    payment_batch_id: Optional[str] = None,
) -> PayrollPeriodResponse:
    # TODO: require_role(cu, ["admin", "finance_manager"])
    period = await db.get(PayrollPeriod, period_id)
    if not period:
        raise HTTPException(404, "Payroll period not found")
    try:
        period = await payroll_service.process_payment(
            db, period, bank_account_code=bank_account_code,
            payment_batch_id=payment_batch_id, user_id=cu.id,
        )
    except HRError as exc:
        raise _err(exc)
    await db.commit()
    return PayrollPeriodResponse.model_validate(period)


@router.get("/payroll/payslips/{entry_id}/pdf")
async def get_payslip_pdf(entry_id: int, db: DBDep, cu: CU) -> Response:
    """Generate payslip PDF. Requires ReportLab."""
    entry = await db.get(PayrollEntry, entry_id)
    if not entry:
        raise HTTPException(404, "Payroll entry not found")
    emp = await db.get(Employee, entry.employee_id)
    period = await db.get(PayrollPeriod, entry.period_id)
    try:
        from app.services.payslip_pdf import generate_payslip_pdf
        pdf_bytes = generate_payslip_pdf(entry, emp, period)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="payslip-{emp.employee_code}-{period.year}-{period.month:02d}.pdf"'},
        )
    except ImportError:
        raise HTTPException(501, "PDF generation requires: pip install reportlab")


# ===========================================================================
# REPORTS
# ===========================================================================
@router.get("/reports/headcount", response_model=list[HeadcountRow])
async def headcount_report(db: DBDep, cu: CU) -> list[HeadcountRow]:
    from sqlalchemy import case
    rows = (await db.execute(
        select(
            Department.id, Department.name,
            func.count(Employee.id).label("total"),
            func.sum(case((Employee.status == EmployeeStatus.ACTIVE, 1), else_=0)).label("active"),
            func.sum(case((Employee.status == "on_leave", 1), else_=0)).label("on_leave"),
        )
        .join(Employee, Employee.department_id == Department.id, isouter=True)
        .group_by(Department.id, Department.name)
    )).all()
    return [
        HeadcountRow(
            department_id=r.id, department_name=r.name,
            total=r.total or 0, active=r.active or 0, on_leave=r.on_leave or 0,
            by_type={},
        )
        for r in rows
    ]


@router.get("/reports/payroll-summary", response_model=list[PayrollSummaryRow])
async def payroll_summary(
    db: DBDep, cu: CU,
    year: int = Query(1403), month: int = Query(1, ge=1, le=12),
) -> list[PayrollSummaryRow]:
    rows = (await db.execute(
        select(
            PayrollEntry.department_code,
            func.count(PayrollEntry.id).label("cnt"),
            func.sum(PayrollEntry.total_earnings).label("gross"),
            func.sum(PayrollEntry.net_salary).label("net"),
            func.sum(PayrollEntry.tax).label("tax"),
            func.sum(PayrollEntry.insurance_employee + PayrollEntry.insurance_employer).label("ins"),
            func.sum(PayrollEntry.insurance_employer).label("employer_ins"),
        )
        .join(PayrollPeriod, PayrollPeriod.id == PayrollEntry.period_id)
        .where(PayrollPeriod.year == year, PayrollPeriod.month == month)
        .group_by(PayrollEntry.department_code)
    )).all()
    return [
        PayrollSummaryRow(
            department=r.department_code or "N/A",
            employee_count=r.cnt,
            total_gross=Decimal(str(r.gross or 0)),
            total_net=Decimal(str(r.net or 0)),
            total_tax=Decimal(str(r.tax or 0)),
            total_insurance=Decimal(str(r.ins or 0)),
            total_cost=Decimal(str(r.gross or 0)) + Decimal(str(r.employer_ins or 0)),
        )
        for r in rows
    ]


@router.get("/reports/tax-withholding", response_model=list[TaxWithholdingRow])
async def tax_withholding_report(
    db: DBDep, cu: CU,
    year: int = Query(1403), month: int = Query(1, ge=1, le=12),
) -> list[TaxWithholdingRow]:
    rows = (await db.execute(
        select(
            Employee.employee_code, Employee.first_name, Employee.last_name,
            Employee.national_id,
            PayrollEntry.total_earnings, PayrollEntry.tax,
        )
        .join(PayrollEntry, PayrollEntry.employee_id == Employee.id)
        .join(PayrollPeriod, PayrollPeriod.id == PayrollEntry.period_id)
        .where(PayrollPeriod.year == year, PayrollPeriod.month == month)
        .order_by(Employee.employee_code)
    )).all()
    return [
        TaxWithholdingRow(
            employee_code=r.employee_code,
            employee_name=f"{r.first_name} {r.last_name}",
            national_id=r.national_id,
            gross_salary=Decimal(str(r.total_earnings)),
            tax_withheld=Decimal(str(r.tax)),
            cumulative_tax=Decimal(str(r.tax)),  # TODO: YTD accumulation
        )
        for r in rows
    ]


@router.get("/reports/insurance-summary", response_model=list[InsuranceSummaryRow])
async def insurance_summary_report(
    db: DBDep, cu: CU,
    year: int = Query(1403), month: int = Query(1, ge=1, le=12),
) -> list[InsuranceSummaryRow]:
    rows = (await db.execute(
        select(
            Employee.employee_code, Employee.first_name, Employee.last_name,
            Employee.national_id,
            (PayrollEntry.base_salary + PayrollEntry.housing_allowance +
             PayrollEntry.food_allowance + PayrollEntry.childcare_allowance).label("insurable"),
            PayrollEntry.insurance_employee,
            PayrollEntry.insurance_employer,
        )
        .join(PayrollEntry, PayrollEntry.employee_id == Employee.id)
        .join(PayrollPeriod, PayrollPeriod.id == PayrollEntry.period_id)
        .where(PayrollPeriod.year == year, PayrollPeriod.month == month)
        .order_by(Employee.employee_code)
    )).all()
    return [
        InsuranceSummaryRow(
            employee_code=r.employee_code,
            employee_name=f"{r.first_name} {r.last_name}",
            national_id=r.national_id,
            insurable_salary=Decimal(str(r.insurable or 0)),
            employee_share=Decimal(str(r.insurance_employee)),
            employer_share=Decimal(str(r.insurance_employer)),
            total=Decimal(str(r.insurance_employee)) + Decimal(str(r.insurance_employer)),
        )
        for r in rows
    ]
