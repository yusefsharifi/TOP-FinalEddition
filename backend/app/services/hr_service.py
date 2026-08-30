"""
HR Module — Payroll Accounting Bridge + HR Service
TOP WorX ERP System

PayrollAccountingBridge: generates the payroll summary journal entry when
a period is approved, and the payment entry when salaries are disbursed.

Payroll JE (on APPROVE):
  Dr 5220 — Salaries & Wages        [total_gross per dept]
  Dr 5220 — Employer Insurance      [total insurance_employer]
    Cr 2120 — Salaries Payable       [total_net]
    Cr 2120 — Tax Payable (Withheld) [total_tax]
    Cr 2120 — Insurance Payable      [total_insurance_employee + employer]

Payment JE (on PAY):
  Dr 2120 — Salaries Payable        [total_net]
    Cr 1110 — Bank                   [total_net]
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hr import (
    AttendanceRecord, Employee, EmployeeStatus,
    LeaveRequest, LeaveStatus, LeaveType,
    PayrollEntry, PayrollEntryStatus, PayrollPeriod, PayrollPeriodStatus,
)
from app.services.payroll_calculator import payroll_calculator, PayrollCalculationResult


class HRError(Exception):
    """Business rule violation in HR."""


# GL account codes — must match seeded COA
ACCT_SALARY_EXPENSE = "5220"
ACCT_SALARIES_PAYABLE = "2120"
ACCT_TAX_PAYABLE = "2130"
ACCT_INSURANCE_PAYABLE = "2120"   # Share same payable, split by cost_center
ACCT_BANK = "1110"


# ===========================================================================
# Payroll Accounting Bridge
# ===========================================================================
class PayrollAccountingBridge:

    async def generate_payroll_journal_entry(
        self,
        db: AsyncSession,
        period: PayrollPeriod,
        entries: list[PayrollEntry],
        user_id: int,
    ) -> Optional[int]:
        """
        Creates summary payroll JE grouped by cost center (department).

        Dr 5220 — Salary Expense (per dept)       [total_earnings]
        Dr 5220 — Employer Insurance (per dept)   [insurance_employer]
          Cr 2120 — Salaries Payable               [total_net]
          Cr 2130 — Tax Payable                    [total_tax]
          Cr 2120 — Insurance Payable              [total_employee_ins + employer_ins]
        """
        try:
            from app.services.accounting_service import accounting_service
            from app.models.finance import ReferenceType

            # Group earnings by cost center
            dept_earnings: dict[str, Decimal] = {}
            dept_employer_ins: dict[str, Decimal] = {}
            total_net = Decimal("0")
            total_tax = Decimal("0")
            total_ins_employee = Decimal("0")
            total_ins_employer = Decimal("0")

            for entry in entries:
                if entry.status not in (PayrollEntryStatus.APPROVED, PayrollEntryStatus.PAID):
                    continue
                cc = entry.cost_center or entry.department_code or "GENERAL"
                dept_earnings[cc] = dept_earnings.get(cc, Decimal("0")) + entry.total_earnings
                dept_employer_ins[cc] = dept_employer_ins.get(cc, Decimal("0")) + entry.insurance_employer
                total_net += entry.net_salary
                total_tax += entry.tax
                total_ins_employee += entry.insurance_employee
                total_ins_employer += entry.insurance_employer

            if total_net == Decimal("0"):
                return None

            lines = []
            # Debit lines: salary expense per cost center
            for cc, amount in dept_earnings.items():
                lines.append({
                    "account_code": ACCT_SALARY_EXPENSE,
                    "debit": amount,
                    "description": f"Payroll {period.year}/{period.month:02d} — {cc}",
                    "cost_center": cc,
                })
            # Debit lines: employer insurance per cost center
            for cc, amount in dept_employer_ins.items():
                if amount > Decimal("0"):
                    lines.append({
                        "account_code": ACCT_SALARY_EXPENSE,
                        "debit": amount,
                        "description": f"Employer insurance {period.year}/{period.month:02d} — {cc}",
                        "cost_center": cc,
                    })

            # Credit: net salaries payable
            lines.append({
                "account_code": ACCT_SALARIES_PAYABLE,
                "credit": total_net,
                "description": f"Net salaries payable {period.year}/{period.month:02d}",
            })
            # Credit: withheld tax
            if total_tax > Decimal("0"):
                lines.append({
                    "account_code": ACCT_TAX_PAYABLE,
                    "credit": total_tax,
                    "description": f"Withheld income tax {period.year}/{period.month:02d}",
                })
            # Credit: total insurance (employee + employer)
            total_ins = total_ins_employee + total_ins_employer
            if total_ins > Decimal("0"):
                lines.append({
                    "account_code": ACCT_INSURANCE_PAYABLE,
                    "credit": total_ins,
                    "description": f"Insurance payable {period.year}/{period.month:02d}",
                })

            je = await accounting_service.build_and_create_entry(
                db,
                entry_date=period.end_date,
                description=f"Payroll {period.year}/{period.month:02d} — {period.total_employees} employees",
                description_fa=f"حقوق و دستمزد {period.year}/{period.month:02d}",
                reference_type=ReferenceType.PAYROLL,
                reference_id=period.id,
                lines=lines,
                user_id=user_id,
            )
            return je.id
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to create payroll JE for period %s/%s", period.year, period.month)
            return None

    async def generate_payment_journal_entry(
        self,
        db: AsyncSession,
        period: PayrollPeriod,
        bank_account_code: str = ACCT_BANK,
        user_id: int = 1,
    ) -> Optional[int]:
        """
        Payment JE (when salaries are actually disbursed):
        Dr 2120 — Salaries Payable  [total_net]
          Cr 1110 — Bank              [total_net]
        """
        try:
            from app.services.accounting_service import accounting_service
            from app.models.finance import ReferenceType

            if period.total_net <= Decimal("0"):
                return None

            je = await accounting_service.build_and_create_entry(
                db,
                entry_date=date.today(),
                description=f"Payroll payment {period.year}/{period.month:02d}",
                description_fa=f"پرداخت حقوق {period.year}/{period.month:02d}",
                reference_type=ReferenceType.PAYROLL,
                reference_id=period.id,
                lines=[
                    {
                        "account_code": ACCT_SALARIES_PAYABLE,
                        "debit": period.total_net,
                        "description": f"Salary payment {period.year}/{period.month:02d}",
                    },
                    {
                        "account_code": bank_account_code,
                        "credit": period.total_net,
                        "description": f"Bank transfer batch: {period.payment_batch_id}",
                    },
                ],
                user_id=user_id,
            )
            return je.id
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to create payment JE for period %s/%s", period.year, period.month)
            return None


payroll_accounting_bridge = PayrollAccountingBridge()


# ===========================================================================
# Payroll Service
# ===========================================================================
class PayrollService:

    async def create_period(
        self,
        db: AsyncSession,
        year: int,
        month: int,
        start_date: date,
        end_date: date,
        user_id: int,
    ) -> PayrollPeriod:
        # Check no duplicate
        existing = await db.execute(
            select(PayrollPeriod).where(
                PayrollPeriod.year == year, PayrollPeriod.month == month
            )
        )
        if existing.scalar_one_or_none():
            raise HRError(f"Payroll period {year}/{month:02d} already exists")

        period = PayrollPeriod(
            year=year, month=month, start_date=start_date, end_date=end_date,
            status=PayrollPeriodStatus.DRAFT, created_by_id=user_id, updated_by_id=user_id,
        )
        db.add(period)
        await db.flush()
        return period

    async def calculate_period(
        self,
        db: AsyncSession,
        period: PayrollPeriod,
        user_id: int,
    ) -> list[PayrollEntry]:
        """
        Auto-calculate payroll for all ACTIVE employees.
        Reads attendance records for the period dates to get overtime.
        Existing DRAFT entries are replaced; APPROVED/PAID entries are skipped.
        """
        if period.status not in (PayrollPeriodStatus.DRAFT, PayrollPeriodStatus.PROCESSING):
            raise HRError(f"Cannot calculate period with status {period.status}")

        period.status = PayrollPeriodStatus.PROCESSING
        await db.flush()

        # Load active employees
        emp_r = await db.execute(
            select(Employee).where(
                Employee.status == EmployeeStatus.ACTIVE,
                Employee.base_salary > Decimal("0"),
            )
        )
        employees = emp_r.scalars().all()

        entries = []
        for emp in employees:
            # Get attendance summary for period
            att_r = await db.execute(
                select(
                    func.count(AttendanceRecord.id).label("total_days"),
                    func.coalesce(func.sum(AttendanceRecord.overtime_hours), Decimal("0")).label("total_ot"),
                    func.coalesce(func.sum(AttendanceRecord.night_hours), Decimal("0")).label("total_night"),
                ).where(
                    AttendanceRecord.employee_id == emp.id,
                    AttendanceRecord.record_date >= period.start_date,
                    AttendanceRecord.record_date <= period.end_date,
                )
            )
            att = att_r.one()

            # Get absence/leave days
            absent_r = await db.execute(
                select(func.count(AttendanceRecord.id)).where(
                    AttendanceRecord.employee_id == emp.id,
                    AttendanceRecord.record_date >= period.start_date,
                    AttendanceRecord.record_date <= period.end_date,
                    AttendanceRecord.status == "absent",
                )
            )
            absent_days = absent_r.scalar_one() or 0

            leave_r = await db.execute(
                select(func.sum(LeaveRequest.days_requested)).where(
                    LeaveRequest.employee_id == emp.id,
                    LeaveRequest.status == LeaveStatus.APPROVED,
                    LeaveRequest.start_date >= period.start_date,
                    LeaveRequest.end_date <= period.end_date,
                    LeaveRequest.leave_type != LeaveType.UNPAID,
                )
            )
            leave_days = int(leave_r.scalar_one() or 0)

            # Calculate using Iranian law
            result = payroll_calculator.calculate(
                employee_id=emp.id,
                base_salary=emp.base_salary,
                overtime_hours=Decimal(str(att.total_ot or 0)),
                night_hours=Decimal(str(att.total_night or 0)),
                working_days=max((att.total_days or 26) - absent_days, 0),
                absent_days=absent_days,
                leave_days=leave_days,
                children_count=emp.children_count,
                insurance_exempt=emp.insurance_exempt,
                tax_exempt=emp.tax_exempt,
            )

            # Find or create entry
            existing_entry = await db.execute(
                select(PayrollEntry).where(
                    PayrollEntry.period_id == period.id,
                    PayrollEntry.employee_id == emp.id,
                )
            )
            entry = existing_entry.scalar_one_or_none()

            if entry and entry.status in (PayrollEntryStatus.APPROVED, PayrollEntryStatus.PAID):
                entries.append(entry)
                continue

            if not entry:
                entry = PayrollEntry(
                    period_id=period.id,
                    employee_id=emp.id,
                    cost_center=emp.default_cost_center,
                    department_code=emp.department.code if emp.department else None,
                    status=PayrollEntryStatus.DRAFT,
                    created_by_id=user_id,
                    updated_by_id=user_id,
                )
                db.add(entry)

            # Apply calculation results
            entry.base_salary = result.base_salary
            entry.overtime_pay = result.overtime_pay
            entry.housing_allowance = result.housing_allowance
            entry.food_allowance = result.food_allowance
            entry.childcare_allowance = result.childcare_allowance
            entry.bonus = result.bonus
            entry.other_earnings = result.other_earnings
            entry.total_earnings = result.total_earnings
            entry.overtime_hours = result.overtime_hours
            entry.working_days = result.working_days
            entry.absent_days = result.absent_days
            entry.leave_days = result.leave_days
            entry.insurance_employee = result.insurance_employee
            entry.insurance_employer = result.insurance_employer
            entry.tax = result.tax
            entry.total_deductions = result.total_deductions
            entry.net_salary = result.net_salary
            entry.updated_by_id = user_id
            entries.append(entry)

        await db.flush()

        # Update period summary
        period.total_employees = len(entries)
        period.total_gross = sum(e.total_earnings for e in entries)
        period.total_net = sum(e.net_salary for e in entries)
        period.total_tax = sum(e.tax for e in entries)
        period.total_insurance_employee = sum(e.insurance_employee for e in entries)
        period.total_insurance_employer = sum(e.insurance_employer for e in entries)
        period.status = PayrollPeriodStatus.DRAFT
        await db.flush()
        return entries

    async def approve_period(
        self,
        db: AsyncSession,
        period: PayrollPeriod,
        user_id: int,
    ) -> PayrollPeriod:
        if period.status != PayrollPeriodStatus.DRAFT:
            raise HRError(f"Period must be DRAFT to approve. Status: {period.status}")

        # Approve all draft entries
        entries_r = await db.execute(
            select(PayrollEntry).where(
                PayrollEntry.period_id == period.id,
                PayrollEntry.status == PayrollEntryStatus.DRAFT,
            )
        )
        entries = entries_r.scalars().all()
        for e in entries:
            e.status = PayrollEntryStatus.APPROVED
            e.updated_by_id = user_id

        await db.flush()

        # Generate payroll JE
        all_entries_r = await db.execute(
            select(PayrollEntry).where(PayrollEntry.period_id == period.id)
        )
        all_entries = all_entries_r.scalars().all()

        je_id = await payroll_accounting_bridge.generate_payroll_journal_entry(
            db, period, all_entries, user_id
        )
        period.journal_entry_id = je_id
        period.status = PayrollPeriodStatus.APPROVED
        period.approved_by_id = user_id
        period.approved_at = datetime.utcnow()
        await db.flush()
        return period

    async def process_payment(
        self,
        db: AsyncSession,
        period: PayrollPeriod,
        bank_account_code: str = "1110",
        payment_batch_id: Optional[str] = None,
        user_id: int = 1,
    ) -> PayrollPeriod:
        if period.status != PayrollPeriodStatus.APPROVED:
            raise HRError(f"Period must be APPROVED to pay. Status: {period.status}")

        import random, string
        batch_id = payment_batch_id or f"BATCH-{period.year}{period.month:02d}-{''.join(random.choices(string.digits, k=6))}"
        period.payment_batch_id = batch_id

        # Create payment JE
        await payroll_accounting_bridge.generate_payment_journal_entry(
            db, period, bank_account_code, user_id
        )

        # Mark entries as PAID
        entries_r = await db.execute(
            select(PayrollEntry).where(PayrollEntry.period_id == period.id)
        )
        entries = entries_r.scalars().all()
        now = datetime.utcnow()
        for e in entries:
            e.status = PayrollEntryStatus.PAID
            e.payment_reference = batch_id
            e.paid_at = now
            e.updated_by_id = user_id

        period.status = PayrollPeriodStatus.PAID
        period.paid_at = now
        await db.flush()
        return period


payroll_service = PayrollService()


# ===========================================================================
# Leave Service
# ===========================================================================
class LeaveService:

    async def submit_request(
        self,
        db: AsyncSession,
        employee_id: int,
        leave_type: LeaveType,
        start_date: date,
        end_date: date,
        reason: Optional[str] = None,
        user_id: int = 1,
    ) -> LeaveRequest:
        days = (end_date - start_date).days + 1

        # Check annual leave balance
        emp = await db.get(Employee, employee_id)
        if not emp:
            raise HRError(f"Employee {employee_id} not found")

        if leave_type == LeaveType.ANNUAL and days > emp.annual_leave_balance:
            raise HRError(
                f"Insufficient annual leave balance. "
                f"Requested: {days}, Available: {emp.annual_leave_balance}"
            )

        request = LeaveRequest(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days_requested=days,
            reason=reason,
            status=LeaveStatus.PENDING,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(request)
        await db.flush()
        return request

    async def approve(
        self, db: AsyncSession, request: LeaveRequest, approver_id: int
    ) -> LeaveRequest:
        if request.status != LeaveStatus.PENDING:
            raise HRError(f"Leave request is not pending. Status: {request.status}")

        emp = await db.get(Employee, request.employee_id)
        if not emp:
            raise HRError("Employee not found")

        request.status = LeaveStatus.APPROVED
        request.approver_id = approver_id
        request.approved_at = datetime.utcnow()

        # Deduct from balance (annual leave only)
        if request.leave_type == LeaveType.ANNUAL:
            emp.annual_leave_balance = max(0, emp.annual_leave_balance - request.days_requested)
            request.balance_after = emp.annual_leave_balance
        elif request.leave_type == LeaveType.SICK:
            emp.sick_leave_balance = max(0, emp.sick_leave_balance - request.days_requested)
            request.balance_after = emp.sick_leave_balance

        request.updated_by_id = approver_id
        await db.flush()
        return request

    async def reject(
        self, db: AsyncSession, request: LeaveRequest, approver_id: int, reason: str
    ) -> LeaveRequest:
        if request.status != LeaveStatus.PENDING:
            raise HRError(f"Leave request is not pending. Status: {request.status}")
        request.status = LeaveStatus.REJECTED
        request.approver_id = approver_id
        request.approved_at = datetime.utcnow()
        request.rejection_reason = reason
        request.updated_by_id = approver_id
        await db.flush()
        return request


leave_service = LeaveService()


# ===========================================================================
# Attendance Service
# ===========================================================================
class AttendanceService:

    STANDARD_DAILY_HOURS = Decimal("7.33")
    NIGHT_START_HOUR = 22   # 10 PM
    NIGHT_END_HOUR = 6      # 6 AM

    def compute_hours(self, check_in: "time", check_out: "time") -> tuple[Decimal, Decimal, Decimal]:
        """
        Returns (work_hours, overtime_hours, night_hours).
        Overtime = total - 7.33 if positive.
        Night hours = hours between 22:00–06:00.
        """
        from datetime import datetime, timedelta
        ci = datetime(2000, 1, 1, check_in.hour, check_in.minute)
        co = datetime(2000, 1, 1, check_out.hour, check_out.minute)
        if co < ci:
            co += timedelta(days=1)  # overnight shift
        total = Decimal(str((co - ci).total_seconds() / 3600))
        overtime = max(total - self.STANDARD_DAILY_HOURS, Decimal("0"))

        # Count night hours
        night = Decimal("0")
        current = ci
        while current < co:
            h = current.hour
            if h >= self.NIGHT_START_HOUR or h < self.NIGHT_END_HOUR:
                night += Decimal("1") / Decimal("60")  # per minute
            current += timedelta(minutes=1)

        return (
            total.quantize(Decimal("0.01")),
            overtime.quantize(Decimal("0.01")),
            night.quantize(Decimal("0.01")),
        )

    async def check_in(
        self, db: AsyncSession, employee_id: int, record_date: date,
        check_in_time: "time", notes: Optional[str] = None, user_id: int = 1
    ) -> AttendanceRecord:
        existing = await db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.record_date == record_date,
            )
        )
        record = existing.scalar_one_or_none()
        if record:
            record.check_in = check_in_time
            record.notes = notes
        else:
            record = AttendanceRecord(
                employee_id=employee_id,
                record_date=record_date,
                check_in=check_in_time,
                status="present",
                notes=notes,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            db.add(record)
        await db.flush()
        return record

    async def check_out(
        self, db: AsyncSession, employee_id: int, record_date: date,
        check_out_time: "time", user_id: int = 1
    ) -> AttendanceRecord:
        existing = await db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.record_date == record_date,
            )
        )
        record = existing.scalar_one_or_none()
        if not record:
            raise HRError(f"No check-in record for employee {employee_id} on {record_date}")
        record.check_out = check_out_time
        if record.check_in:
            wh, ot, nh = self.compute_hours(record.check_in, check_out_time)
            record.work_hours = wh
            record.overtime_hours = ot
            record.night_hours = nh
        record.updated_by_id = user_id
        await db.flush()
        return record


attendance_service = AttendanceService()
