from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship

class CourseType(Enum):
    IN_PERSON = "in_person"
    ONLINE = "online"
    HYBRID = "hybrid"
    WORKSHOP = "workshop"
    SEMINAR = "seminar"
    CERTIFICATION = "certification"

class CourseStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"

class EnrollmentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    DROPPED = "dropped"

class Course(BaseModel):
    id: int
    title: str
    description: str
    type: CourseType
    status: CourseStatus
    instructor_id: int
    created_at: datetime
    updated_at: datetime
    start_date: date
    end_date: date
    duration: int  # in hours
    max_participants: int
    prerequisites: List[Dict[str, Any]] = []
    objectives: List[str] = []
    outline: List[Dict[str, Any]] = []
    materials: List[Dict[str, Any]] = []
    assessments: List[Dict[str, Any]] = []
    resources: List[Dict[str, Any]] = []
    schedule: List[Dict[str, Any]] = []
    location: Optional[str] = None
    cost: float
    category: str
    tags: List[str] = []
    ratings: List[Dict[str, Any]] = []
    feedback: List[Dict[str, Any]] = []
    completion_criteria: List[str] = []
    certificate_template: Optional[Dict[str, Any]] = None
    notes: List[Dict[str, Any]] = []

class TrainingProgram(BaseModel):
    id: int
    name: str
    description: str
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime
    target_audience: List[str] = []
    objectives: List[str] = []
    courses: List[Dict[str, Any]] = []
    participants: List[Dict[str, Any]] = []
    progress_tracking: Dict[int, float] = {}
    assessments: Dict[int, List[Dict[str, Any]]] = {}
    feedback: Dict[int, str] = {}
    completion_status: Dict[int, bool] = {}
    resources: List[Dict[str, Any]] = []
    budget: float
    actual_cost: float
    notes: List[Dict[str, Any]] = []

class LearningDevelopmentSystem:
    def __init__(self):
        self.courses: Dict[int, Course] = {}
        self.training_programs: Dict[int, TrainingProgram] = {}
        self.enrollments: Dict[int, Dict[str, Any]] = {}
        self.certificates: Dict[int, Dict[str, Any]] = {}
        self.notifications: Dict[int, List[Dict[str, Any]]] = {}

    def create_course(self, title: str, description: str, course_type: CourseType,
                     instructor_id: int, start_date: date, end_date: date,
                     duration: int, max_participants: int, cost: float,
                     category: str) -> int:
        """Create a new course"""
        course_id = len(self.courses) + 1
        course = Course(
            id=course_id,
            title=title,
            description=description,
            type=course_type,
            status=CourseStatus.DRAFT,
            instructor_id=instructor_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            start_date=start_date,
            end_date=end_date,
            duration=duration,
            max_participants=max_participants,
            cost=cost,
            category=category
        )
        self.courses[course_id] = course
        return course_id

    def update_course(self, course_id: int, updates: Dict[str, Any]) -> bool:
        """Update course details"""
        if course_id not in self.courses:
            return False
        
        course = self.courses[course_id]
        for key, value in updates.items():
            if hasattr(course, key):
                setattr(course, key, value)
        
        course.updated_at = datetime.now()
        return True

    def publish_course(self, course_id: int) -> bool:
        """Publish a course"""
        if course_id not in self.courses:
            return False
        
        course = self.courses[course_id]
        course.status = CourseStatus.PUBLISHED
        course.updated_at = datetime.now()
        return True

    def enroll_participant(self, course_id: int, employee_id: int) -> bool:
        """Enroll a participant in a course"""
        if course_id not in self.courses:
            return False
        
        course = self.courses[course_id]
        if len(self.enrollments.get(course_id, [])) >= course.max_participants:
            return False
        
        enrollment_id = len(self.enrollments) + 1
        enrollment = {
            "id": enrollment_id,
            "course_id": course_id,
            "employee_id": employee_id,
            "status": EnrollmentStatus.PENDING,
            "enrolled_at": datetime.now(),
            "progress": 0.0,
            "completed_at": None,
            "assessments": [],
            "feedback": None
        }
        
        if course_id not in self.enrollments:
            self.enrollments[course_id] = []
        self.enrollments[course_id].append(enrollment)
        
        self._notify_employee(employee_id, "course_enrollment")
        return True

    def update_enrollment_status(self, course_id: int, employee_id: int,
                               new_status: EnrollmentStatus) -> bool:
        """Update enrollment status"""
        if course_id not in self.enrollments:
            return False
        
        for enrollment in self.enrollments[course_id]:
            if enrollment["employee_id"] == employee_id:
                enrollment["status"] = new_status
                if new_status == EnrollmentStatus.COMPLETED:
                    enrollment["completed_at"] = datetime.now()
                return True
        return False

    def create_training_program(self, name: str, description: str,
                              start_date: date, end_date: date,
                              target_audience: List[str], budget: float) -> int:
        """Create a new training program"""
        program_id = len(self.training_programs) + 1
        program = TrainingProgram(
            id=program_id,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            target_audience=target_audience,
            budget=budget,
            actual_cost=0.0
        )
        self.training_programs[program_id] = program
        return program_id

    def add_course_to_program(self, program_id: int, course_id: int) -> bool:
        """Add a course to a training program"""
        if program_id not in self.training_programs or course_id not in self.courses:
            return False
        
        program = self.training_programs[program_id]
        course = self.courses[course_id]
        
        program.courses.append({
            "course_id": course_id,
            "title": course.title,
            "type": course.type,
            "duration": course.duration,
            "cost": course.cost
        })
        
        program.actual_cost += course.cost
        program.updated_at = datetime.now()
        return True

    def enroll_participant_in_program(self, program_id: int, employee_id: int) -> bool:
        """Enroll a participant in a training program"""
        if program_id not in self.training_programs:
            return False
        
        program = self.training_programs[program_id]
        program.participants.append({
            "employee_id": employee_id,
            "enrolled_at": datetime.now(),
            "progress": 0.0,
            "completed_at": None
        })
        
        program.progress_tracking[employee_id] = 0.0
        program.completion_status[employee_id] = False
        program.updated_at = datetime.now()
        
        self._notify_employee(employee_id, "program_enrollment")
        return True

    def update_program_progress(self, program_id: int, employee_id: int,
                              progress: float) -> bool:
        """Update participant progress in a program"""
        if program_id not in self.training_programs:
            return False
        
        program = self.training_programs[program_id]
        program.progress_tracking[employee_id] = progress
        
        if progress >= 100:
            program.completion_status[employee_id] = True
            for participant in program.participants:
                if participant["employee_id"] == employee_id:
                    participant["completed_at"] = datetime.now()
                    participant["progress"] = 100.0
        
        program.updated_at = datetime.now()
        return True

    def generate_certificate(self, course_id: int, employee_id: int) -> Optional[Dict[str, Any]]:
        """Generate a certificate for course completion"""
        if course_id not in self.courses:
            return None
        
        course = self.courses[course_id]
        enrollment = None
        
        for e in self.enrollments.get(course_id, []):
            if e["employee_id"] == employee_id and e["status"] == EnrollmentStatus.COMPLETED:
                enrollment = e
                break
        
        if not enrollment:
            return None
        
        certificate_id = len(self.certificates) + 1
        certificate = {
            "id": certificate_id,
            "course_id": course_id,
            "employee_id": employee_id,
            "course_title": course.title,
            "completion_date": enrollment["completed_at"],
            "instructor_id": course.instructor_id,
            "template": course.certificate_template,
            "issued_at": datetime.now()
        }
        
        self.certificates[certificate_id] = certificate
        return certificate

    def get_learning_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics for learning and development system"""
        return {
            "course_statistics": {
                "total_courses": len(self.courses),
                "active_courses": len([c for c in self.courses.values() 
                                     if c.status == CourseStatus.PUBLISHED]),
                "enrollment_distribution": self._get_enrollment_distribution(),
                "completion_rates": self._calculate_completion_rates()
            },
            "program_statistics": {
                "total_programs": len(self.training_programs),
                "active_programs": len([p for p in self.training_programs.values() 
                                      if p.end_date >= date.today()]),
                "participant_distribution": self._get_participant_distribution(),
                "program_completion": self._calculate_program_completion()
            },
            "learning_metrics": {
                "average_progress": self._calculate_average_progress(),
                "course_ratings": self._get_course_ratings(),
                "popular_courses": self._get_popular_courses(),
                "skill_gaps": self._identify_skill_gaps()
            }
        }

    def _get_enrollment_distribution(self) -> Dict[str, int]:
        """Get distribution of enrollment statuses"""
        distribution = {status.value: 0 for status in EnrollmentStatus}
        for enrollments in self.enrollments.values():
            for enrollment in enrollments:
                distribution[enrollment["status"].value] += 1
        return distribution

    def _calculate_completion_rates(self) -> Dict[str, float]:
        """Calculate completion rates by course type"""
        rates = {}
        for course_type in CourseType:
            type_courses = [c for c in self.courses.values() 
                          if c.type == course_type]
            if not type_courses:
                continue
                
            completed = 0
            total = 0
            for course in type_courses:
                if course.id in self.enrollments:
                    for enrollment in self.enrollments[course.id]:
                        if enrollment["status"] == EnrollmentStatus.COMPLETED:
                            completed += 1
                        total += 1
            
            rates[course_type.value] = completed / total if total > 0 else 0.0
        return rates

    def _get_participant_distribution(self) -> Dict[str, int]:
        """Get distribution of participants across programs"""
        distribution = {}
        for program in self.training_programs.values():
            distribution[program.name] = len(program.participants)
        return distribution

    def _calculate_program_completion(self) -> Dict[str, float]:
        """Calculate completion rates for programs"""
        completion = {}
        for program in self.training_programs.values():
            total = len(program.participants)
            completed = sum(1 for status in program.completion_status.values() 
                          if status)
            completion[program.name] = completed / total if total > 0 else 0.0
        return completion

    def _calculate_average_progress(self) -> float:
        """Calculate average progress across all enrollments"""
        total_progress = 0
        total_enrollments = 0
        
        for enrollments in self.enrollments.values():
            for enrollment in enrollments:
                total_progress += enrollment["progress"]
                total_enrollments += 1
        
        return total_progress / total_enrollments if total_enrollments > 0 else 0.0

    def _get_course_ratings(self) -> Dict[str, float]:
        """Get average ratings for courses"""
        ratings = {}
        for course in self.courses.values():
            if course.ratings:
                avg_rating = sum(r["rating"] for r in course.ratings) / len(course.ratings)
                ratings[course.title] = avg_rating
        return ratings

    def _get_popular_courses(self) -> List[Dict[str, Any]]:
        """Get most popular courses based on enrollments"""
        course_popularity = []
        for course in self.courses.values():
            enrollments = len(self.enrollments.get(course.id, []))
            course_popularity.append({
                "course_id": course.id,
                "title": course.title,
                "enrollments": enrollments,
                "completion_rate": self._calculate_course_completion_rate(course.id)
            })
        
        return sorted(course_popularity, key=lambda x: x["enrollments"], reverse=True)[:5]

    def _calculate_course_completion_rate(self, course_id: int) -> float:
        """Calculate completion rate for a specific course"""
        if course_id not in self.enrollments:
            return 0.0
        
        enrollments = self.enrollments[course_id]
        total = len(enrollments)
        completed = sum(1 for e in enrollments 
                       if e["status"] == EnrollmentStatus.COMPLETED)
        return completed / total if total > 0 else 0.0

    def _identify_skill_gaps(self) -> List[Dict[str, Any]]:
        """Identify skill gaps based on course completion and assessments"""
        skill_gaps = []
        for course in self.courses.values():
            if course.assessments:
                for assessment in course.assessments:
                    if assessment.get("type") == "skill_assessment":
                        skill_name = assessment.get("skill_name")
                        if skill_name:
                            skill_gaps.append({
                                "skill": skill_name,
                                "course": course.title,
                                "average_score": self._calculate_skill_average(course.id, skill_name),
                                "participants": self._get_skill_participants(course.id, skill_name)
                            })
        return skill_gaps

    def _calculate_skill_average(self, course_id: int, skill_name: str) -> float:
        """Calculate average score for a specific skill"""
        if course_id not in self.enrollments:
            return 0.0
        
        total_score = 0
        count = 0
        
        for enrollment in self.enrollments[course_id]:
            for assessment in enrollment.get("assessments", []):
                if assessment.get("skill_name") == skill_name:
                    total_score += assessment.get("score", 0)
                    count += 1
        
        return total_score / count if count > 0 else 0.0

    def _get_skill_participants(self, course_id: int, skill_name: str) -> int:
        """Get number of participants assessed for a specific skill"""
        if course_id not in self.enrollments:
            return 0
        
        count = 0
        for enrollment in self.enrollments[course_id]:
            for assessment in enrollment.get("assessments", []):
                if assessment.get("skill_name") == skill_name:
                    count += 1
                    break
        return count

    def _notify_employee(self, employee_id: int, event_type: str) -> None:
        """Notify employee about learning and development events"""
        if employee_id not in self.notifications:
            self.notifications[employee_id] = []
            
        self.notifications[employee_id].append({
            "type": event_type,
            "employee_id": employee_id,
            "timestamp": datetime.now(),
            "is_read": False
        }) 