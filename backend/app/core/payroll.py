from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

class EmployeeType(Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    PART_TIME = "part_time"

class SalaryComponent(Enum):
    BASE_SALARY = "base_salary"
    HOUSING_ALLOWANCE = "housing_allowance"
    TRANSPORTATION_ALLOWANCE = "transportation_allowance"
    FOOD_ALLOWANCE = "food_allowance"
    OVERTIME = "overtime"
    BONUS = "bonus"
    INSURANCE = "insurance"
    TAX = "tax"
    LOAN = "loan"
    ADVANCE = "advance"
    OTHER = "other"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    PAID = "paid"
    CANCELLED = "cancelled"

@dataclass
class Employee:
    id: str
    code: str
    first_name: str
    last_name: str
    national_id: str
    birth_date: date
    hire_date: date
    type: EmployeeType
    department_id: str
    position: str
    base_salary: Decimal
    bank_account: str
    bank_name: str
    insurance_number: str
    tax_number: str
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalaryComponent:
    id: str
    employee_id: str
    component_type: SalaryComponent
    amount: Decimal
    is_percentage: bool = False
    percentage_of: Optional[SalaryComponent] = None
    description: str = ""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Attendance:
    id: str
    employee_id: str
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str = "present"  # present, absent, late, early_leave
    description: str = ""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Leave:
    id: str
    employee_id: str
    type: str  # annual, sick, maternity, paternity, etc.
    start_date: date
    end_date: date
    status: str = "pending"  # pending, approved, rejected
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    description: str = ""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PayrollPeriod:
    id: str
    start_date: date
    end_date: date
    status: PaymentStatus = PaymentStatus.PENDING
    processed_by: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Payroll:
    id: str
    period_id: str
    employee_id: str
    gross_salary: Decimal
    net_salary: Decimal
    status: PaymentStatus = PaymentStatus.PENDING
    payment_date: Optional[date] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class PayrollManager:
    def __init__(self, accounting_system):
        self.logger = logging.getLogger(__name__)
        self.accounting_system = accounting_system
        self.employees: Dict[str, Employee] = {}
        self.salary_components: Dict[str, List[SalaryComponent]] = {}
        self.attendance: Dict[str, List[Attendance]] = {}
        self.leaves: Dict[str, List[Leave]] = {}
        self.payroll_periods: Dict[str, PayrollPeriod] = {}
        self.payrolls: Dict[str, List[Payroll]] = {}
    
    def add_employee(self, employee: Employee) -> bool:
        """Add new employee"""
        try:
            if employee.id in self.employees:
                self.logger.warning(f"Employee with ID {employee.id} already exists")
                return False
            
            self.employees[employee.id] = employee
            self.salary_components[employee.id] = []
            self.attendance[employee.id] = []
            self.leaves[employee.id] = []
            self.logger.info(f"Employee {employee.first_name} {employee.last_name} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding employee: {str(e)}")
            return False
    
    def add_salary_component(self, component: SalaryComponent) -> bool:
        """Add salary component for employee"""
        try:
            if component.employee_id not in self.employees:
                self.logger.error(f"Employee {component.employee_id} not found")
                return False
            
            if component.id in [c.id for c in self.salary_components[component.employee_id]]:
                self.logger.warning(f"Component with ID {component.id} already exists")
                return False
            
            self.salary_components[component.employee_id].append(component)
            self.logger.info(f"Salary component added for employee {component.employee_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding salary component: {str(e)}")
            return False
    
    def record_attendance(self, attendance: Attendance) -> bool:
        """Record employee attendance"""
        try:
            if attendance.employee_id not in self.employees:
                self.logger.error(f"Employee {attendance.employee_id} not found")
                return False
            
            if attendance.id in [a.id for a in self.attendance[attendance.employee_id]]:
                self.logger.warning(f"Attendance record with ID {attendance.id} already exists")
                return False
            
            self.attendance[attendance.employee_id].append(attendance)
            self.logger.info(f"Attendance recorded for employee {attendance.employee_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error recording attendance: {str(e)}")
            return False
    
    def request_leave(self, leave: Leave) -> bool:
        """Request leave for employee"""
        try:
            if leave.employee_id not in self.employees:
                self.logger.error(f"Employee {leave.employee_id} not found")
                return False
            
            if leave.id in [l.id for l in self.leaves[leave.employee_id]]:
                self.logger.warning(f"Leave request with ID {leave.id} already exists")
                return False
            
            self.leaves[leave.employee_id].append(leave)
            self.logger.info(f"Leave requested for employee {leave.employee_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error requesting leave: {str(e)}")
            return False
    
    def approve_leave(self, leave_id: str, employee_id: str, approver_id: str) -> bool:
        """Approve leave request"""
        try:
            leave = next((l for l in self.leaves[employee_id] if l.id == leave_id), None)
            if not leave:
                return False
            
            if leave.status != "pending":
                self.logger.warning(f"Leave request {leave_id} is not pending")
                return False
            
            leave.status = "approved"
            leave.approved_by = approver_id
            leave.approved_at = datetime.now()
            leave.updated_at = datetime.now()
            
            self.logger.info(f"Leave request {leave_id} approved")
            return True
        except Exception as e:
            self.logger.error(f"Error approving leave: {str(e)}")
            return False
    
    def create_payroll_period(self, period: PayrollPeriod) -> bool:
        """Create new payroll period"""
        try:
            if period.id in self.payroll_periods:
                self.logger.warning(f"Payroll period with ID {period.id} already exists")
                return False
            
            self.payroll_periods[period.id] = period
            self.payrolls[period.id] = []
            self.logger.info(f"Payroll period created: {period.start_date} to {period.end_date}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating payroll period: {str(e)}")
            return False
    
    def process_payroll(self, period_id: str, processed_by: str) -> bool:
        """Process payroll for period"""
        try:
            period = self.payroll_periods.get(period_id)
            if not period:
                return False
            
            if period.status != PaymentStatus.PENDING:
                self.logger.warning(f"Payroll period {period_id} is not pending")
                return False
            
            # Calculate payroll for each employee
            for employee in self.employees.values():
                if not employee.is_active:
                    continue
                
                # Calculate gross salary
                gross_salary = self._calculate_gross_salary(employee, period)
                
                # Calculate deductions
                deductions = self._calculate_deductions(employee, gross_salary)
                
                # Calculate net salary
                net_salary = gross_salary - deductions
                
                # Create payroll record
                payroll = Payroll(
                    id=f"PAY_{period_id}_{employee.id}",
                    period_id=period_id,
                    employee_id=employee.id,
                    gross_salary=gross_salary,
                    net_salary=net_salary,
                    status=PaymentStatus.PROCESSED
                )
                
                self.payrolls[period_id].append(payroll)
            
            # Update period status
            period.status = PaymentStatus.PROCESSED
            period.processed_by = processed_by
            period.processed_at = datetime.now()
            period.updated_at = datetime.now()
            
            self.logger.info(f"Payroll processed for period {period_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error processing payroll: {str(e)}")
            return False
    
    def _calculate_gross_salary(self, employee: Employee, period: PayrollPeriod) -> Decimal:
        """Calculate gross salary for employee"""
        try:
            gross_salary = employee.base_salary
            
            # Add allowances and bonuses
            for component in self.salary_components.get(employee.id, []):
                if component.component_type in [
                    SalaryComponent.HOUSING_ALLOWANCE,
                    SalaryComponent.TRANSPORTATION_ALLOWANCE,
                    SalaryComponent.FOOD_ALLOWANCE,
                    SalaryComponent.BONUS
                ]:
                    if component.is_percentage:
                        gross_salary += employee.base_salary * (component.amount / Decimal('100'))
                    else:
                        gross_salary += component.amount
            
            # Add overtime
            overtime = self._calculate_overtime(employee, period)
            gross_salary += overtime
            
            return gross_salary
        except Exception as e:
            self.logger.error(f"Error calculating gross salary: {str(e)}")
            return Decimal('0')
    
    def _calculate_deductions(self, employee: Employee, gross_salary: Decimal) -> Decimal:
        """Calculate deductions for employee"""
        try:
            deductions = Decimal('0')
            
            # Calculate insurance
            insurance = self._calculate_insurance(gross_salary)
            deductions += insurance
            
            # Calculate tax
            tax = self._calculate_tax(gross_salary - insurance)
            deductions += tax
            
            # Add other deductions
            for component in self.salary_components.get(employee.id, []):
                if component.component_type in [
                    SalaryComponent.LOAN,
                    SalaryComponent.ADVANCE
                ]:
                    deductions += component.amount
            
            return deductions
        except Exception as e:
            self.logger.error(f"Error calculating deductions: {str(e)}")
            return Decimal('0')
    
    def _calculate_overtime(self, employee: Employee, period: PayrollPeriod) -> Decimal:
        """Calculate overtime for employee"""
        try:
            overtime = Decimal('0')
            overtime_rate = Decimal('1.5')  # 150% of base salary
            
            # Get attendance records for period
            attendance_records = [
                a for a in self.attendance.get(employee.id, [])
                if period.start_date <= a.date <= period.end_date
            ]
            
            for record in attendance_records:
                if record.check_in and record.check_out:
                    # Calculate hours worked
                    hours_worked = (record.check_out - record.check_in).total_seconds() / 3600
                    
                    # Calculate overtime hours (more than 8 hours per day)
                    if hours_worked > 8:
                        overtime_hours = hours_worked - 8
                        daily_overtime = (employee.base_salary / Decimal('176')) * overtime_rate * Decimal(str(overtime_hours))
                        overtime += daily_overtime
            
            return overtime
        except Exception as e:
            self.logger.error(f"Error calculating overtime: {str(e)}")
            return Decimal('0')
    
    def _calculate_insurance(self, gross_salary: Decimal) -> Decimal:
        """Calculate insurance deduction"""
        try:
            # 7% of gross salary for employee contribution
            return gross_salary * Decimal('0.07')
        except Exception as e:
            self.logger.error(f"Error calculating insurance: {str(e)}")
            return Decimal('0')
    
    def _calculate_tax(self, taxable_income: Decimal) -> Decimal:
        """Calculate tax deduction"""
        try:
            # Simple tax calculation (can be modified based on tax rules)
            if taxable_income <= Decimal('30000000'):
                return Decimal('0')
            elif taxable_income <= Decimal('50000000'):
                return (taxable_income - Decimal('30000000')) * Decimal('0.1')
            elif taxable_income <= Decimal('100000000'):
                return Decimal('2000000') + (taxable_income - Decimal('50000000')) * Decimal('0.15')
            else:
                return Decimal('9500000') + (taxable_income - Decimal('100000000')) * Decimal('0.2')
        except Exception as e:
            self.logger.error(f"Error calculating tax: {str(e)}")
            return Decimal('0')
    
    def get_employee_payslip(self, employee_id: str, period_id: str) -> Dict[str, Any]:
        """Generate payslip for employee"""
        try:
            employee = self.employees.get(employee_id)
            if not employee:
                return {}
            
            payroll = next((p for p in self.payrolls.get(period_id, []) if p.employee_id == employee_id), None)
            if not payroll:
                return {}
            
            period = self.payroll_periods.get(period_id)
            if not period:
                return {}
            
            # Get salary components
            components = []
            for component in self.salary_components.get(employee_id, []):
                if component.component_type in [
                    SalaryComponent.HOUSING_ALLOWANCE,
                    SalaryComponent.TRANSPORTATION_ALLOWANCE,
                    SalaryComponent.FOOD_ALLOWANCE,
                    SalaryComponent.BONUS
                ]:
                    amount = (employee.base_salary * (component.amount / Decimal('100'))) if component.is_percentage else component.amount
                    components.append({
                        "type": component.component_type.value,
                        "amount": amount,
                        "is_percentage": component.is_percentage,
                        "percentage_of": component.percentage_of.value if component.percentage_of else None
                    })
            
            # Get deductions
            deductions = []
            insurance = self._calculate_insurance(payroll.gross_salary)
            tax = self._calculate_tax(payroll.gross_salary - insurance)
            
            deductions.append({
                "type": "insurance",
                "amount": insurance
            })
            
            deductions.append({
                "type": "tax",
                "amount": tax
            })
            
            for component in self.salary_components.get(employee_id, []):
                if component.component_type in [
                    SalaryComponent.LOAN,
                    SalaryComponent.ADVANCE
                ]:
                    deductions.append({
                        "type": component.component_type.value,
                        "amount": component.amount
                    })
            
            return {
                "employee": {
                    "id": employee.id,
                    "code": employee.code,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "national_id": employee.national_id,
                    "department": employee.department_id,
                    "position": employee.position
                },
                "period": {
                    "id": period.id,
                    "start_date": period.start_date.isoformat(),
                    "end_date": period.end_date.isoformat()
                },
                "salary": {
                    "base": employee.base_salary,
                    "gross": payroll.gross_salary,
                    "net": payroll.net_salary
                },
                "components": components,
                "deductions": deductions,
                "status": payroll.status.value,
                "payment_date": payroll.payment_date.isoformat() if payroll.payment_date else None
            }
        except Exception as e:
            self.logger.error(f"Error generating payslip: {str(e)}")
            return {}
    
    def get_employee_list(self, department_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of employees with optional filter"""
        try:
            employees = []
            for employee in self.employees.values():
                if department_id and employee.department_id != department_id:
                    continue
                
                employees.append({
                    "id": employee.id,
                    "code": employee.code,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "national_id": employee.national_id,
                    "type": employee.type.value,
                    "department": employee.department_id,
                    "position": employee.position,
                    "base_salary": employee.base_salary,
                    "is_active": employee.is_active
                })
            
            return sorted(employees, key=lambda x: x["name"])
        except Exception as e:
            self.logger.error(f"Error getting employee list: {str(e)}")
            return [] 