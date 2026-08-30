from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship

class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

class CareerStage(Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEADER = "leader"
    EXECUTIVE = "executive"

class DevelopmentStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class EmployeeProfile(BaseModel):
    id: int
    employee_id: int
    first_name: str
    last_name: str
    email: EmailStr
    department: str
    position: str
    career_stage: CareerStage
    hire_date: date
    skills: Dict[str, SkillLevel] = {}
    certifications: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    achievements: List[Dict[str, Any]] = []
    career_goals: List[Dict[str, Any]] = []
    development_plans: List[Dict[str, Any]] = []
    performance_history: List[Dict[str, Any]] = []
    mentoring_relationships: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    interests: List[str] = []
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    notes: List[Dict[str, Any]] = []

class DevelopmentPlan(BaseModel):
    id: int
    employee_id: int
    title: str
    description: str
    status: DevelopmentStatus
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime
    objectives: List[Dict[str, Any]] = []
    activities: List[Dict[str, Any]] = []
    resources: List[Dict[str, Any]] = []
    milestones: List[Dict[str, Any]] = []
    progress: List[Dict[str, Any]] = []
    feedback: List[Dict[str, Any]] = []
    completion_criteria: List[str] = []
    notes: List[Dict[str, Any]] = []

class SuccessionPlan(BaseModel):
    id: int
    position_id: int
    position_title: str
    department: str
    criticality: str
    current_incumbent: Optional[int] = None
    potential_successors: List[Dict[str, Any]] = []
    readiness_levels: Dict[int, str] = {}
    development_actions: List[Dict[str, Any]] = []
    risk_assessment: Dict[str, Any] = {}
    timeline: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []

class TalentManagementSystem:
    def __init__(self):
        self.employee_profiles: Dict[int, EmployeeProfile] = {}
        self.development_plans: Dict[int, DevelopmentPlan] = {}
        self.succession_plans: Dict[int, SuccessionPlan] = {}
        self.skill_matrix: Dict[str, Dict[str, List[int]]] = {}
        self.notifications: Dict[int, List[Dict[str, Any]]] = {}

    def create_employee_profile(self, employee_id: int, first_name: str, last_name: str,
                              email: EmailStr, department: str, position: str,
                              career_stage: CareerStage, hire_date: date) -> int:
        """Create a new employee profile"""
        profile_id = len(self.employee_profiles) + 1
        profile = EmployeeProfile(
            id=profile_id,
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department,
            position=position,
            career_stage=career_stage,
            hire_date=hire_date
        )
        self.employee_profiles[profile_id] = profile
        return profile_id

    def update_skills(self, profile_id: int, skills: Dict[str, SkillLevel]) -> bool:
        """Update employee skills"""
        if profile_id not in self.employee_profiles:
            return False
        
        profile = self.employee_profiles[profile_id]
        profile.skills = skills
        
        # Update skill matrix
        for skill, level in skills.items():
            if skill not in self.skill_matrix:
                self.skill_matrix[skill] = {level.value: []}
            if level.value not in self.skill_matrix[skill]:
                self.skill_matrix[skill][level.value] = []
            self.skill_matrix[skill][level.value].append(profile_id)
        
        return True

    def add_certification(self, profile_id: int, name: str, issuer: str,
                         date_earned: date, expiry_date: Optional[date] = None) -> bool:
        """Add a certification to employee profile"""
        if profile_id not in self.employee_profiles:
            return False
        
        profile = self.employee_profiles[profile_id]
        profile.certifications.append({
            "name": name,
            "issuer": issuer,
            "date_earned": date_earned,
            "expiry_date": expiry_date
        })
        return True

    def add_education(self, profile_id: int, institution: str, degree: str,
                     field: str, start_date: date, end_date: date,
                     gpa: Optional[float] = None) -> bool:
        """Add education to employee profile"""
        if profile_id not in self.employee_profiles:
            return False
        
        profile = self.employee_profiles[profile_id]
        profile.education.append({
            "institution": institution,
            "degree": degree,
            "field": field,
            "start_date": start_date,
            "end_date": end_date,
            "gpa": gpa
        })
        return True

    def add_experience(self, profile_id: int, company: str, position: str,
                      start_date: date, end_date: date, description: str) -> bool:
        """Add work experience to employee profile"""
        if profile_id not in self.employee_profiles:
            return False
        
        profile = self.employee_profiles[profile_id]
        profile.experience.append({
            "company": company,
            "position": position,
            "start_date": start_date,
            "end_date": end_date,
            "description": description
        })
        return True

    def add_achievement(self, profile_id: int, title: str, description: str,
                       date: date, impact: str) -> bool:
        """Add achievement to employee profile"""
        if profile_id not in self.employee_profiles:
            return False
        
        profile = self.employee_profiles[profile_id]
        profile.achievements.append({
            "title": title,
            "description": description,
            "date": date,
            "impact": impact
        })
        return True

    def create_development_plan(self, employee_id: int, title: str, description: str,
                              start_date: date, end_date: date,
                              objectives: List[Dict[str, Any]]) -> int:
        """Create a new development plan"""
        plan_id = len(self.development_plans) + 1
        plan = DevelopmentPlan(
            id=plan_id,
            employee_id=employee_id,
            title=title,
            description=description,
            status=DevelopmentStatus.NOT_STARTED,
            start_date=start_date,
            end_date=end_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            objectives=objectives
        )
        self.development_plans[plan_id] = plan
        self._notify_employee(employee_id, "new_development_plan")
        return plan_id

    def update_development_plan_status(self, plan_id: int, new_status: DevelopmentStatus,
                                     updated_by: int, comment: str = "") -> bool:
        """Update development plan status"""
        if plan_id not in self.development_plans:
            return False
        
        plan = self.development_plans[plan_id]
        plan.status = new_status
        plan.updated_at = datetime.now()
        
        plan.notes.append({
            "type": "status_update",
            "content": f"Status changed to {new_status.value}: {comment}",
            "updated_by": updated_by,
            "timestamp": datetime.now()
        })
        
        self._notify_employee(plan.employee_id, "development_plan_status_updated")
        return True

    def add_development_activity(self, plan_id: int, title: str, description: str,
                               due_date: date, resources: List[Dict[str, Any]] = []) -> bool:
        """Add activity to development plan"""
        if plan_id not in self.development_plans:
            return False
        
        plan = self.development_plans[plan_id]
        activity = {
            "id": len(plan.activities) + 1,
            "title": title,
            "description": description,
            "due_date": due_date,
            "resources": resources,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "completion_date": None,
            "notes": []
        }
        
        plan.activities.append(activity)
        self._notify_employee(plan.employee_id, "new_development_activity")
        return True

    def create_succession_plan(self, position_id: int, position_title: str,
                             department: str, criticality: str) -> int:
        """Create a new succession plan"""
        plan_id = len(self.succession_plans) + 1
        plan = SuccessionPlan(
            id=plan_id,
            position_id=position_id,
            position_title=position_title,
            department=department,
            criticality=criticality
        )
        self.succession_plans[plan_id] = plan
        return plan_id

    def add_potential_successor(self, plan_id: int, employee_id: int,
                              readiness_level: str, notes: str = "") -> bool:
        """Add potential successor to succession plan"""
        if plan_id not in self.succession_plans:
            return False
        
        plan = self.succession_plans[plan_id]
        successor = {
            "employee_id": employee_id,
            "readiness_level": readiness_level,
            "notes": notes,
            "added_at": datetime.now()
        }
        
        plan.potential_successors.append(successor)
        plan.readiness_levels[employee_id] = readiness_level
        return True

    def get_talent_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics for talent management system"""
        return {
            "employee_statistics": {
                "total_employees": len(self.employee_profiles),
                "career_stage_distribution": self._get_career_stage_distribution(),
                "department_distribution": self._get_department_distribution(),
                "skill_distribution": self._get_skill_distribution()
            },
            "development_metrics": {
                "active_development_plans": len([p for p in self.development_plans.values() 
                                              if p.status == DevelopmentStatus.IN_PROGRESS]),
                "completion_rate": self._calculate_development_completion_rate(),
                "skill_gaps": self._identify_skill_gaps(),
                "certification_trends": self._get_certification_trends()
            },
            "succession_metrics": {
                "critical_positions": len([p for p in self.succession_plans.values() 
                                        if p.criticality == "high"]),
                "succession_coverage": self._calculate_succession_coverage(),
                "readiness_levels": self._get_readiness_level_distribution(),
                "risk_assessment": self._get_succession_risk_assessment()
            }
        }

    def _get_career_stage_distribution(self) -> Dict[str, int]:
        """Get distribution of career stages"""
        distribution = {stage.value: 0 for stage in CareerStage}
        for profile in self.employee_profiles.values():
            distribution[profile.career_stage.value] += 1
        return distribution

    def _get_department_distribution(self) -> Dict[str, int]:
        """Get distribution of employees across departments"""
        distribution = {}
        for profile in self.employee_profiles.values():
            if profile.department not in distribution:
                distribution[profile.department] = 0
            distribution[profile.department] += 1
        return distribution

    def _get_skill_distribution(self) -> Dict[str, Dict[str, int]]:
        """Get distribution of skills across levels"""
        distribution = {}
        for skill, levels in self.skill_matrix.items():
            distribution[skill] = {level: len(employees) 
                                 for level, employees in levels.items()}
        return distribution

    def _calculate_development_completion_rate(self) -> float:
        """Calculate completion rate of development plans"""
        total_plans = len(self.development_plans)
        if total_plans == 0:
            return 0.0
            
        completed_plans = len([p for p in self.development_plans.values() 
                             if p.status == DevelopmentStatus.COMPLETED])
        return completed_plans / total_plans

    def _identify_skill_gaps(self) -> List[Dict[str, Any]]:
        """Identify skill gaps in the organization"""
        skill_gaps = []
        for skill, levels in self.skill_matrix.items():
            if SkillLevel.EXPERT.value not in levels:
                skill_gaps.append({
                    "skill": skill,
                    "gap": "No experts",
                    "impact": "high"
                })
            elif len(levels[SkillLevel.EXPERT.value]) < 2:
                skill_gaps.append({
                    "skill": skill,
                    "gap": "Limited expertise",
                    "impact": "medium"
                })
        return skill_gaps

    def _get_certification_trends(self) -> Dict[str, Any]:
        """Get certification trends"""
        trends = {
            "total_certifications": 0,
            "certifications_by_type": {},
            "expiring_soon": []
        }
        
        for profile in self.employee_profiles.values():
            for cert in profile.certifications:
                trends["total_certifications"] += 1
                cert_type = cert["name"].split()[0]  # Assuming first word is type
                if cert_type not in trends["certifications_by_type"]:
                    trends["certifications_by_type"][cert_type] = 0
                trends["certifications_by_type"][cert_type] += 1
                
                if cert.get("expiry_date"):
                    days_until_expiry = (cert["expiry_date"] - date.today()).days
                    if 0 < days_until_expiry <= 90:
                        trends["expiring_soon"].append({
                            "employee_id": profile.employee_id,
                            "certification": cert["name"],
                            "expiry_date": cert["expiry_date"]
                        })
        
        return trends

    def _calculate_succession_coverage(self) -> float:
        """Calculate succession coverage for critical positions"""
        critical_positions = [p for p in self.succession_plans.values() 
                            if p.criticality == "high"]
        if not critical_positions:
            return 0.0
            
        covered_positions = len([p for p in critical_positions 
                               if len(p.potential_successors) >= 2])
        return covered_positions / len(critical_positions)

    def _get_readiness_level_distribution(self) -> Dict[str, int]:
        """Get distribution of readiness levels"""
        distribution = {"ready_now": 0, "ready_soon": 0, "needs_development": 0}
        for plan in self.succession_plans.values():
            for level in plan.readiness_levels.values():
                if level == "ready_now":
                    distribution["ready_now"] += 1
                elif level == "ready_soon":
                    distribution["ready_soon"] += 1
                else:
                    distribution["needs_development"] += 1
        return distribution

    def _get_succession_risk_assessment(self) -> Dict[str, Any]:
        """Get succession risk assessment"""
        risk_assessment = {
            "high_risk_positions": [],
            "medium_risk_positions": [],
            "low_risk_positions": []
        }
        
        for plan in self.succession_plans.values():
            risk_level = self._calculate_position_risk(plan)
            if risk_level == "high":
                risk_assessment["high_risk_positions"].append({
                    "position": plan.position_title,
                    "department": plan.department,
                    "reason": "Limited succession coverage"
                })
            elif risk_level == "medium":
                risk_assessment["medium_risk_positions"].append({
                    "position": plan.position_title,
                    "department": plan.department,
                    "reason": "Partial succession coverage"
                })
            else:
                risk_assessment["low_risk_positions"].append({
                    "position": plan.position_title,
                    "department": plan.department,
                    "reason": "Adequate succession coverage"
                })
        
        return risk_assessment

    def _calculate_position_risk(self, plan: SuccessionPlan) -> str:
        """Calculate risk level for a position"""
        if plan.criticality == "high":
            if len(plan.potential_successors) < 2:
                return "high"
            elif len(plan.potential_successors) < 3:
                return "medium"
            else:
                return "low"
        elif plan.criticality == "medium":
            if len(plan.potential_successors) < 1:
                return "high"
            elif len(plan.potential_successors) < 2:
                return "medium"
            else:
                return "low"
        else:
            if len(plan.potential_successors) < 1:
                return "medium"
            else:
                return "low"

    def _notify_employee(self, employee_id: int, event_type: str) -> None:
        """Notify employee about talent management events"""
        if employee_id not in self.notifications:
            self.notifications[employee_id] = []
            
        self.notifications[employee_id].append({
            "type": event_type,
            "employee_id": employee_id,
            "timestamp": datetime.now(),
            "is_read": False
        }) 