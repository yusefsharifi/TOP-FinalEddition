"""
Payroll Calculator — Iranian Labor Law Compliance
TOP WorX ERP System

قانون کار ایران / Iranian Labor Law

Key rules implemented:
  • Insurance ceiling: 7% employee, 23% employer
  • Tax brackets: 1403 rates (سازمان امور مالیاتی)
  • Annual leave: 26 days
  • Overtime: 1.4x hourly rate
  • Night shift: 1.35x additional
  • Holiday: 1.8x or compensatory leave
  • End-of-service (سنوات): year 1 = 1 month, subsequent = 1.5 months

DECISION POINT ⚙️: Update INSURANCE_CEILING_MONTHLY and TAX_BRACKETS
every year from سازمان تأمین اجتماعی and سازمان امور مالیاتی.
Current values: 1403 (2024) rates.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional


# ---------------------------------------------------------------------------
# Constants — UPDATE ANNUALLY
# ---------------------------------------------------------------------------
INSURANCE_CEILING_MONTHLY = Decimal("112_000_000")   # 1403 ceiling (112M IRR)
EMPLOYEE_INSURANCE_RATE = Decimal("0.07")             # 7%
EMPLOYER_INSURANCE_RATE = Decimal("0.23")             # 23%

ANNUAL_LEAVE_DAYS = 26         # قانون کار — standard
SICK_LEAVE_DAYS = 12

STANDARD_DAILY_HOURS = Decimal("7.33")    # 44h ÷ 6 working days
STANDARD_MONTHLY_HOURS = Decimal("176")   # approximate (44h × 4 weeks)

OVERTIME_MULTIPLIER = Decimal("1.4")       # 40% premium
NIGHT_SHIFT_MULTIPLIER = Decimal("0.35")  # 35% additional on base rate
HOLIDAY_MULTIPLIER = Decimal("1.8")        # 80% premium

# Monthly tax exemption base (معافیت مالیاتی ماهانه) — 1403
MONTHLY_TAX_EXEMPTION = Decimal("10_000_000")   # 10M IRR

# Tax brackets (annual, then divide by 12 for monthly)
# Source: قانون مالیات‌های مستقیم 1403
# Format: (monthly_threshold, rate)
TAX_BRACKETS = [
    (Decimal("10_000_000"), Decimal("0.00")),   # 0–10M: exempt
    (Decimal("14_000_000"), Decimal("0.10")),   # 10–14M: 10%
    (Decimal("23_000_000"), Decimal("0.15")),   # 14–23M: 15%
    (Decimal("34_000_000"), Decimal("0.20")),   # 23–34M: 20%
    (Decimal("999_999_999"), Decimal("0.30")),  # 34M+: 30%
]

# Child deduction (کمک هزینه اولاد) per child per month
CHILD_ALLOWANCE_PER_CHILD = Decimal("3_000_000")    # 3M IRR

# Minimum wage 1403
MINIMUM_MONTHLY_WAGE = Decimal("75_000_000")   # 75M IRR (approximate 1403)


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------
@dataclass
class PayrollCalculationResult:
    """Complete payroll calculation output for one employee-month."""
    employee_id: int

    # Earnings
    base_salary: Decimal
    overtime_pay: Decimal
    housing_allowance: Decimal
    food_allowance: Decimal
    childcare_allowance: Decimal
    bonus: Decimal
    other_earnings: Decimal
    total_earnings: Decimal

    # Work data
    overtime_hours: Decimal
    working_days: int
    absent_days: int
    leave_days: int

    # Deductions
    insurance_employee: Decimal   # 7%
    insurance_employer: Decimal   # 23% (company cost — not deducted from employee)
    tax: Decimal
    advance_deduction: Decimal
    loan_deduction: Decimal
    other_deductions: Decimal
    total_deductions: Decimal

    # Net
    net_salary: Decimal

    # Tax detail (for reporting)
    taxable_income: Decimal
    tax_exemption_used: Decimal


@dataclass
class EndOfServiceResult:
    """سنوات پایان خدمت — terminal pay calculation."""
    employee_id: int
    years_of_service: Decimal
    base_salary: Decimal
    total_eos: Decimal
    calculation_detail: str


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------
class IranianPayrollCalculator:

    def _round(self, value: Decimal, places: int = 0) -> Decimal:
        """Round to nearest IRR (or 4 decimal places for internal calcs)."""
        if places == 0:
            return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return value.quantize(Decimal(f"0.{'0' * places}"), rounding=ROUND_HALF_UP)

    # -----------------------------------------------------------------------
    # Insurance
    # -----------------------------------------------------------------------
    def calculate_insurance(
        self,
        gross_insurable: Decimal,
        insurance_exempt: bool = False,
    ) -> tuple[Decimal, Decimal]:
        """
        Returns (employee_share, employer_share).
        Gross is capped at INSURANCE_CEILING_MONTHLY.
        Base for insurance includes: base + housing + food + child allowances.
        Does NOT include non-insurable allowances.
        """
        if insurance_exempt:
            return Decimal("0"), Decimal("0")
        taxable = min(gross_insurable, INSURANCE_CEILING_MONTHLY)
        employee = self._round(taxable * EMPLOYEE_INSURANCE_RATE)
        employer = self._round(taxable * EMPLOYER_INSURANCE_RATE)
        return employee, employer

    # -----------------------------------------------------------------------
    # Income Tax
    # -----------------------------------------------------------------------
    def calculate_tax(
        self,
        gross_taxable: Decimal,
        children_count: int = 0,
        tax_exempt: bool = False,
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Returns (tax_amount, taxable_income, exemption_used).

        Taxable income = gross_taxable - monthly_exemption - child_allowances
        Tax applied using progressive Iranian brackets.

        DECISION POINT ⚙️: Iranian law also allows deductions for:
        - Disability
        - Additional dependent family members
        - Approved savings plans (بیمه عمر)
        Add these as parameters if needed.
        """
        if tax_exempt:
            return Decimal("0"), gross_taxable, Decimal("0")

        # Deductions from taxable income
        child_deduction = min(
            children_count * CHILD_ALLOWANCE_PER_CHILD,
            gross_taxable,
        )
        exemption = MONTHLY_TAX_EXEMPTION + child_deduction
        taxable_income = max(gross_taxable - exemption, Decimal("0"))

        if taxable_income <= Decimal("0"):
            return Decimal("0"), Decimal("0"), exemption

        tax = Decimal("0")
        previous_threshold = Decimal("0")

        for threshold, rate in TAX_BRACKETS:
            if taxable_income <= previous_threshold:
                break
            bracket_income = min(taxable_income, threshold) - previous_threshold
            if bracket_income <= Decimal("0"):
                previous_threshold = threshold
                continue
            tax += bracket_income * rate
            previous_threshold = threshold

        return self._round(tax), self._round(taxable_income), self._round(exemption)

    # -----------------------------------------------------------------------
    # Overtime
    # -----------------------------------------------------------------------
    def calculate_overtime_pay(
        self,
        base_salary: Decimal,
        overtime_hours: Decimal,
        night_hours: Decimal = Decimal("0"),
    ) -> Decimal:
        """
        Overtime: 1.4 × hourly_rate × overtime_hours
        Night shift additional: 0.35 × hourly_rate × night_hours
        Hourly rate = base_salary / STANDARD_MONTHLY_HOURS
        """
        if overtime_hours <= Decimal("0") and night_hours <= Decimal("0"):
            return Decimal("0")
        hourly_rate = base_salary / STANDARD_MONTHLY_HOURS
        overtime_pay = self._round(hourly_rate * OVERTIME_MULTIPLIER * overtime_hours)
        night_pay = self._round(hourly_rate * NIGHT_SHIFT_MULTIPLIER * night_hours)
        return overtime_pay + night_pay

    # -----------------------------------------------------------------------
    # Standard allowances (mandatory in Iran)
    # -----------------------------------------------------------------------
    def calculate_mandatory_allowances(
        self,
        base_salary: Decimal,
        children_count: int = 0,
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Returns (housing_allowance, food_allowance, childcare_allowance).
        These are set by Ministry of Labour annually.

        DECISION POINT ⚙️: Values below are 1403 rates — update yearly.
        housing = 3,000,000 IRR/month
        food    = 2,000,000 IRR/month
        child   = 3,000,000 IRR/month per child (max 3 children for standard)
        """
        housing = Decimal("3_000_000")
        food = Decimal("2_000_000")
        child = min(children_count, 3) * CHILD_ALLOWANCE_PER_CHILD
        return housing, food, child

    # -----------------------------------------------------------------------
    # Full calculation
    # -----------------------------------------------------------------------
    def calculate(
        self,
        employee_id: int,
        base_salary: Decimal,
        *,
        overtime_hours: Decimal = Decimal("0"),
        night_hours: Decimal = Decimal("0"),
        bonus: Decimal = Decimal("0"),
        other_earnings: Decimal = Decimal("0"),
        advance_deduction: Decimal = Decimal("0"),
        loan_deduction: Decimal = Decimal("0"),
        other_deductions: Decimal = Decimal("0"),
        working_days: int = 26,
        absent_days: int = 0,
        leave_days: int = 0,
        children_count: int = 0,
        insurance_exempt: bool = False,
        tax_exempt: bool = False,
    ) -> PayrollCalculationResult:
        """
        Full Iranian payroll calculation for one employee-month.

        Earnings order (per Iranian law):
          1. Base salary (pro-rated if absent days)
          2. Mandatory allowances (housing, food, childcare)
          3. Overtime pay
          4. Bonus / other

        Insurable base = base + housing + food + childcare
        Taxable income = total_earnings - insurance_employee
        """
        # Pro-rate base salary for absent days (unpaid absences only)
        effective_base = base_salary
        if absent_days > 0 and working_days > 0:
            daily_rate = base_salary / Decimal(str(working_days + absent_days))
            effective_base = base_salary - (daily_rate * Decimal(str(absent_days)))
            effective_base = self._round(effective_base)

        # Mandatory allowances
        housing, food, childcare = self.calculate_mandatory_allowances(
            effective_base, children_count
        )

        # Overtime
        overtime_pay = self.calculate_overtime_pay(effective_base, overtime_hours, night_hours)

        total_earnings = (
            effective_base + housing + food + childcare
            + overtime_pay + bonus + other_earnings
        )

        # Insurance (on insurable portion)
        insurable_base = effective_base + housing + food + childcare
        ins_employee, ins_employer = self.calculate_insurance(insurable_base, insurance_exempt)

        # Tax (on total_earnings net of employee insurance)
        taxable_gross = total_earnings - ins_employee
        tax, taxable_income, exemption_used = self.calculate_tax(
            taxable_gross, children_count, tax_exempt
        )

        # Total deductions (employee-facing)
        total_deductions = ins_employee + tax + advance_deduction + loan_deduction + other_deductions

        net_salary = max(total_earnings - total_deductions, Decimal("0"))

        return PayrollCalculationResult(
            employee_id=employee_id,
            base_salary=effective_base,
            overtime_pay=overtime_pay,
            housing_allowance=housing,
            food_allowance=food,
            childcare_allowance=childcare,
            bonus=bonus,
            other_earnings=other_earnings,
            total_earnings=self._round(total_earnings),
            overtime_hours=overtime_hours,
            working_days=working_days,
            absent_days=absent_days,
            leave_days=leave_days,
            insurance_employee=ins_employee,
            insurance_employer=ins_employer,
            tax=tax,
            advance_deduction=advance_deduction,
            loan_deduction=loan_deduction,
            other_deductions=other_deductions,
            total_deductions=self._round(total_deductions),
            net_salary=self._round(net_salary),
            taxable_income=taxable_income,
            tax_exemption_used=exemption_used,
        )

    # -----------------------------------------------------------------------
    # End-of-service (سنوات پایان خدمت)
    # -----------------------------------------------------------------------
    def calculate_end_of_service(
        self,
        employee_id: int,
        base_salary: Decimal,
        join_date,
        termination_date=None,
    ) -> EndOfServiceResult:
        """
        قانون کار — سنوات:
        - Year 1: 1 month base salary
        - Each subsequent year: 1.5 months base salary
        - Fractions: proportional
        - Minimum wage applies if base < minimum
        """
        from datetime import date
        end = termination_date or date.today()
        delta_days = (end - join_date).days
        years = Decimal(str(delta_days)) / Decimal("365.25")

        effective_base = max(base_salary, MINIMUM_MONTHLY_WAGE)

        if years <= Decimal("1"):
            eos = effective_base * years
            detail = f"Year 1: {years:.4f} × base"
        else:
            full_years = int(years)
            fraction = years - Decimal(str(full_years))
            # Year 1 = 1 month, subsequent years = 1.5 months each
            eos = effective_base * (Decimal("1") + (years - Decimal("1")) * Decimal("1.5"))
            detail = f"1 month for year 1 + {years - Decimal('1'):.4f} × 1.5 months"

        return EndOfServiceResult(
            employee_id=employee_id,
            years_of_service=years.quantize(Decimal("0.01")),
            base_salary=effective_base,
            total_eos=self._round(eos),
            calculation_detail=detail,
        )


# Singleton
payroll_calculator = IranianPayrollCalculator()
