from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field
import enum
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field
import enum
from .payroll import PayrollManager, Employee as PayrollEmployee, Attendance, Leave, Payroll

class EmployeeStatus(enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"

class EmploymentType(enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"

class SkillLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Employee(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    hire_date: date
    department: str
    position: str
    status: EmployeeStatus
    employment_type: EmploymentType
    salary: float
    skills: Dict[str, SkillLevel]
    performance_metrics: Dict[str, float]
    documents: List[str]
    emergency_contact: Dict[str, str]
    work_schedule: Dict[str, Any]
    benefits: List[str]
    certifications: List[Dict[str, Any]]
    training_history: List[Dict[str, Any]]
    leave_balance: Dict[str, int]
    career_goals: List[str]
    achievements: List[Dict[str, Any]]
    notes: Optional[str] = None

class RecruitmentProcess(BaseModel):
    id: int
    position: str
    department: str
    requirements: List[str]
    responsibilities: List[str]
    status: str
    applicants: List[Dict[str, Any]]
    interview_schedule: List[Dict[str, Any]]
    assessment_results: Dict[str, Any]
    hiring_decision: Optional[Dict[str, Any]] = None

class PerformanceReview(BaseModel):
    id: int
    employee_id: int
    review_date: date
    reviewer_id: int
    goals: List[Dict[str, Any]]
    achievements: List[Dict[str, Any]]
    skills_assessment: Dict[str, float]
    feedback: str
    recommendations: List[str]
    overall_rating: float
    next_review_date: date

class TrainingProgram(BaseModel):
    id: int
    title: str
    description: str
    duration: int
    required_skills: List[str]
    participants: List[int]
    schedule: Dict[str, Any]
    materials: List[str]
    assessments: List[Dict[str, Any]]
    completion_status: Dict[int, bool]
    feedback: Dict[int, str]

class HRSystem:
    def __init__(self):
        self.employees: Dict[int, Employee] = {}
        self.recruitment_processes: Dict[int, RecruitmentProcess] = {}
        self.performance_reviews: Dict[int, PerformanceReview] = {}
        self.training_programs: Dict[int, TrainingProgram] = {}

    def add_employee(self, employee: Employee) -> int:
        """Add a new employee to the system"""
        employee_id = len(self.employees) + 1
        self.employees[employee_id] = employee
        return employee_id

    def update_employee(self, employee_id: int, updates: Dict[str, Any]) -> bool:
        """Update employee information"""
        if employee_id not in self.employees:
            return False
        employee = self.employees[employee_id]
        for key, value in updates.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
        return True

    def initiate_recruitment(self, position: str, department: str, requirements: List[str]) -> int:
        """Start a new recruitment process"""
        process_id = len(self.recruitment_processes) + 1
        process = RecruitmentProcess(
            id=process_id,
            position=position,
            department=department,
            requirements=requirements,
            responsibilities=[],
            status="open",
            applicants=[],
            interview_schedule=[],
            assessment_results={}
        )
        self.recruitment_processes[process_id] = process
        return process_id

    def schedule_interview(self, process_id: int, candidate_id: int, date: datetime) -> bool:
        """Schedule an interview for a candidate"""
        if process_id not in self.recruitment_processes:
            return False
        process = self.recruitment_processes[process_id]
        process.interview_schedule.append({
            "candidate_id": candidate_id,
            "date": date,
            "status": "scheduled"
        })
        return True

    def create_performance_review(self, employee_id: int, reviewer_id: int) -> int:
        """Create a new performance review"""
        if employee_id not in self.employees:
            return -1
        review_id = len(self.performance_reviews) + 1
        review = PerformanceReview(
            id=review_id,
            employee_id=employee_id,
            review_date=date.today(),
            reviewer_id=reviewer_id,
            goals=[],
            achievements=[],
            skills_assessment={},
            feedback="",
            recommendations=[],
            overall_rating=0.0,
            next_review_date=date.today()
        )
        self.performance_reviews[review_id] = review
        return review_id

    def create_training_program(self, title: str, description: str, duration: int) -> int:
        """Create a new training program"""
        program_id = len(self.training_programs) + 1
        program = TrainingProgram(
            id=program_id,
            title=title,
            description=description,
            duration=duration,
            required_skills=[],
            participants=[],
            schedule={},
            materials=[],
            assessments=[],
            completion_status={},
            feedback={}
        )
        self.training_programs[program_id] = program
        return program_id

    def enroll_employee_in_training(self, program_id: int, employee_id: int) -> bool:
        """Enroll an employee in a training program"""
        if program_id not in self.training_programs or employee_id not in self.employees:
            return False
        program = self.training_programs[program_id]
        program.participants.append(employee_id)
        program.completion_status[employee_id] = False
        return True

    def get_employee_analytics(self, employee_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for an employee"""
        if employee_id not in self.employees:
            return {}
        
        employee = self.employees[employee_id]
        reviews = [r for r in self.performance_reviews.values() if r.employee_id == employee_id]
        trainings = [t for t in self.training_programs.values() if employee_id in t.participants]
        
        return {
            "performance_history": [{
                "date": r.review_date,
                "rating": r.overall_rating
            } for r in reviews],
            "skill_progression": employee.skills,
            "training_completion": {
                t.id: t.completion_status.get(employee_id, False)
                for t in trainings
            },
            "attendance": employee.work_schedule,
            "leave_utilization": employee.leave_balance,
            "career_growth": employee.achievements
        }

    def get_department_analytics(self, department: str) -> Dict[str, Any]:
        """Get analytics for an entire department"""
        department_employees = [
            e for e in self.employees.values() 
            if e.department == department
        ]
        
        return {
            "employee_count": len(department_employees),
            "average_salary": sum(e.salary for e in department_employees) / len(department_employees) if department_employees else 0,
            "performance_distribution": {
                "high": len([e for e in department_employees if e.performance_metrics.get("overall", 0) >= 4]),
                "medium": len([e for e in department_employees if 2 <= e.performance_metrics.get("overall", 0) < 4]),
                "low": len([e for e in department_employees if e.performance_metrics.get("overall", 0) < 2])
            },
            "skill_gaps": self._analyze_skill_gaps(department_employees),
            "training_needs": self._analyze_training_needs(department_employees)
        }

    def _analyze_skill_gaps(self, employees: List[Employee]) -> Dict[str, Any]:
        """Analyze skill gaps in a group of employees"""
        required_skills = set()
        for employee in employees:
            required_skills.update(employee.skills.keys())
        
        skill_levels = {}
        for skill in required_skills:
            skill_levels[skill] = {
                "expert": 0,
                "advanced": 0,
                "intermediate": 0,
                "beginner": 0
            }
            for employee in employees:
                level = employee.skills.get(skill, SkillLevel.BEGINNER)
                skill_levels[skill][level.value] += 1
        
        return skill_levels

    def _analyze_training_needs(self, employees: List[Employee]) -> List[Dict[str, Any]]:
        """Analyze training needs based on performance and skills"""
        training_needs = []
        for employee in employees:
            for skill, level in employee.skills.items():
                if level in [SkillLevel.BEGINNER, SkillLevel.INTERMEDIATE]:
                    training_needs.append({
                        "employee_id": employee.id,
                        "skill": skill,
                        "current_level": level.value,
                        "recommended_level": SkillLevel.ADVANCED.value
                    })
        return training_needs

    def generate_hr_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate a comprehensive HR report for a date range"""
        return {
            "employee_statistics": {
                "total_employees": len(self.employees),
                "new_hires": len([e for e in self.employees.values() if e.hire_date >= start_date]),
                "departures": len([e for e in self.employees.values() if e.status == EmployeeStatus.TERMINATED and e.hire_date >= start_date]),
                "department_distribution": self._get_department_distribution()
            },
            "recruitment_metrics": {
                "open_positions": len([p for p in self.recruitment_processes.values() if p.status == "open"]),
                "hired_candidates": len([p for p in self.recruitment_processes.values() if p.hiring_decision and p.hiring_decision.get("date") >= start_date])
            },
            "performance_metrics": {
                "average_rating": self._calculate_average_performance_rating(),
                "review_completion_rate": self._calculate_review_completion_rate(start_date, end_date)
            },
            "training_metrics": {
                "active_programs": len([t for t in self.training_programs.values() if t.schedule.get("end_date") >= date.today()]),
                "completion_rate": self._calculate_training_completion_rate()
            },
            "cost_analysis": {
                "salary_costs": sum(e.salary for e in self.employees.values()),
                "training_costs": self._calculate_training_costs(start_date, end_date),
                "recruitment_costs": self._calculate_recruitment_costs(start_date, end_date)
            }
        }

    def _get_department_distribution(self) -> Dict[str, int]:
        """Get employee distribution across departments"""
        distribution = {}
        for employee in self.employees.values():
            distribution[employee.department] = distribution.get(employee.department, 0) + 1
        return distribution

    def _calculate_average_performance_rating(self) -> float:
        """Calculate average performance rating across all employees"""
        ratings = [r.overall_rating for r in self.performance_reviews.values()]
        return sum(ratings) / len(ratings) if ratings else 0.0

    def _calculate_review_completion_rate(self, start_date: date, end_date: date) -> float:
        """Calculate the rate of completed performance reviews"""
        total_employees = len(self.employees)
        completed_reviews = len([r for r in self.performance_reviews.values() 
                               if start_date <= r.review_date <= end_date])
        return completed_reviews / total_employees if total_employees > 0 else 0.0

    def _calculate_training_completion_rate(self) -> float:
        """Calculate the overall training program completion rate"""
        total_enrollments = sum(len(p.participants) for p in self.training_programs.values())
        completed_trainings = sum(
            sum(1 for status in p.completion_status.values() if status)
            for p in self.training_programs.values()
        )
        return completed_trainings / total_enrollments if total_enrollments > 0 else 0.0

    def _calculate_training_costs(self, start_date: date, end_date: date) -> float:
        """Calculate total training costs for a period"""
        # This would typically include costs for materials, instructors, facilities, etc.
        # For now, returning a placeholder value
        return 0.0

    def _calculate_recruitment_costs(self, start_date: date, end_date: date) -> float:
        """Calculate total recruitment costs for a period"""
        # This would typically include costs for job postings, interviews, assessments, etc.
        # For now, returning a placeholder value
        return 0.0

class HRIntegration:
    def __init__(self, hr_system, payroll_manager: PayrollManager):
        self.hr_system = hr_system
        self.payroll_manager = payroll_manager

    def sync_employee_data(self, employee_id: int) -> bool:
        """Sync employee data between HR and Payroll systems"""
        try:
            # Get employee from HR system
            hr_employee = self.hr_system.employees.get(employee_id)
            if not hr_employee:
                return False

            # Convert HR employee to Payroll employee format
            payroll_employee = PayrollEmployee(
                id=str(employee_id),
                code=hr_employee.employee_code,
                first_name=hr_employee.first_name,
                last_name=hr_employee.last_name,
                national_id=hr_employee.national_id,
                birth_date=hr_employee.birth_date,
                hire_date=hr_employee.hire_date,
                type=hr_employee.employment_type,
                department_id=hr_employee.department,
                position=hr_employee.position,
                base_salary=hr_employee.salary,
                bank_account=hr_employee.bank_account,
                bank_name=hr_employee.bank_name,
                insurance_number=hr_employee.insurance_number,
                tax_number=hr_employee.tax_number,
                is_active=hr_employee.status == "active"
            )

            # Add/Update employee in Payroll system
            if str(employee_id) in self.payroll_manager.employees:
                # Update existing employee
                self.payroll_manager.employees[str(employee_id)] = payroll_employee
            else:
                # Add new employee
                self.payroll_manager.add_employee(payroll_employee)

            return True
        except Exception as e:
            print(f"Error syncing employee data: {str(e)}")
            return False

    def get_employee_attendance(self, employee_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get employee attendance records"""
        try:
            attendance_records = self.payroll_manager.attendance.get(str(employee_id), [])
            filtered_records = [
                a for a in attendance_records
                if start_date <= a.date <= end_date
            ]
            
            return [{
                "date": record.date.isoformat(),
                "check_in": record.check_in.isoformat() if record.check_in else None,
                "check_out": record.check_out.isoformat() if record.check_out else None,
                "status": record.status,
                "description": record.description
            } for record in filtered_records]
        except Exception as e:
            print(f"Error getting attendance records: {str(e)}")
            return []

    def get_employee_leaves(self, employee_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get employee leave records"""
        try:
            leave_records = self.payroll_manager.leaves.get(str(employee_id), [])
            filtered_records = [
                l for l in leave_records
                if start_date <= l.start_date <= end_date or start_date <= l.end_date <= end_date
            ]
            
            return [{
                "type": record.type,
                "start_date": record.start_date.isoformat(),
                "end_date": record.end_date.isoformat(),
                "status": record.status,
                "approved_by": record.approved_by,
                "approved_at": record.approved_at.isoformat() if record.approved_at else None,
                "description": record.description
            } for record in filtered_records]
        except Exception as e:
            print(f"Error getting leave records: {str(e)}")
            return []

    def get_employee_payroll(self, employee_id: int, period_id: str) -> Dict[str, Any]:
        """Get employee payroll information"""
        try:
            return self.payroll_manager.get_employee_payslip(str(employee_id), period_id)
        except Exception as e:
            print(f"Error getting payroll information: {str(e)}")
            return {}

    def get_employee_payroll_history(self, employee_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get employee payroll history"""
        try:
            history = []
            for period_id, period in self.payroll_manager.payroll_periods.items():
                if start_date <= period.start_date <= end_date:
                    payroll = next(
                        (p for p in self.payroll_manager.payrolls.get(period_id, [])
                         if p.employee_id == str(employee_id)),
                        None
                    )
                    if payroll:
                        history.append({
                            "period_id": period_id,
                            "start_date": period.start_date.isoformat(),
                            "end_date": period.end_date.isoformat(),
                            "gross_salary": payroll.gross_salary,
                            "net_salary": payroll.net_salary,
                            "status": payroll.status.value,
                            "payment_date": payroll.payment_date.isoformat() if payroll.payment_date else None
                        })
            return history
        except Exception as e:
            print(f"Error getting payroll history: {str(e)}")
            return []

    def get_employee_analytics(self, employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get comprehensive employee analytics including attendance and payroll"""
        try:
            # Get HR analytics
            hr_analytics = self.hr_system.get_employee_analytics(employee_id)
            
            # Get attendance analytics
            attendance_records = self.get_employee_attendance(employee_id, start_date, end_date)
            attendance_analytics = {
                "total_days": len(attendance_records),
                "present_days": len([r for r in attendance_records if r["status"] == "present"]),
                "absent_days": len([r for r in attendance_records if r["status"] == "absent"]),
                "late_days": len([r for r in attendance_records if r["status"] == "late"]),
                "early_leaves": len([r for r in attendance_records if r["status"] == "early_leave"])
            }
            
            # Get leave analytics
            leave_records = self.get_employee_leaves(employee_id, start_date, end_date)
            leave_analytics = {
                "total_leaves": len(leave_records),
                "approved_leaves": len([l for l in leave_records if l["status"] == "approved"]),
                "pending_leaves": len([l for l in leave_records if l["status"] == "pending"]),
                "rejected_leaves": len([l for l in leave_records if l["status"] == "rejected"]),
                "by_type": {}
            }
            
            # Calculate leaves by type
            for leave in leave_records:
                leave_type = leave["type"]
                if leave_type not in leave_analytics["by_type"]:
                    leave_analytics["by_type"][leave_type] = 0
                leave_analytics["by_type"][leave_type] += 1
            
            # Get payroll analytics
            payroll_history = self.get_employee_payroll_history(employee_id, start_date, end_date)
            payroll_analytics = {
                "total_periods": len(payroll_history),
                "total_gross_salary": sum(p["gross_salary"] for p in payroll_history),
                "total_net_salary": sum(p["net_salary"] for p in payroll_history),
                "average_gross_salary": sum(p["gross_salary"] for p in payroll_history) / len(payroll_history) if payroll_history else 0,
                "average_net_salary": sum(p["net_salary"] for p in payroll_history) / len(payroll_history) if payroll_history else 0
            }
            
            return {
                "hr_analytics": hr_analytics,
                "attendance_analytics": attendance_analytics,
                "leave_analytics": leave_analytics,
                "payroll_analytics": payroll_analytics
            }
        except Exception as e:
            print(f"Error getting employee analytics: {str(e)}")
            return {} 