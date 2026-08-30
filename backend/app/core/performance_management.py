from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship

class GoalStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class PerformanceRating(Enum):
    EXCEPTIONAL = "exceptional"
    EXCEEDS_EXPECTATIONS = "exceeds_expectations"
    MEETS_EXPECTATIONS = "meets_expectations"
    NEEDS_IMPROVEMENT = "needs_improvement"
    UNSATISFACTORY = "unsatisfactory"

class ReviewStatus(Enum):
    DRAFT = "draft"
    PENDING_EMPLOYEE = "pending_employee"
    PENDING_MANAGER = "pending_manager"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Goal(BaseModel):
    id: int
    employee_id: int
    title: str
    description: str
    status: GoalStatus
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime
    category: str
    priority: str
    weight: float
    progress: float = 0.0
    milestones: List[Dict[str, Any]] = []
    achievements: List[Dict[str, Any]] = []
    challenges: List[Dict[str, Any]] = []
    support_needed: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []

class PerformanceReview(BaseModel):
    id: int
    employee_id: int
    reviewer_id: int
    review_period: str
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    start_date: date
    end_date: date
    goals: List[Dict[str, Any]] = []
    competencies: List[Dict[str, Any]] = []
    achievements: List[Dict[str, Any]] = []
    development_areas: List[Dict[str, Any]] = []
    feedback: List[Dict[str, Any]] = []
    overall_rating: Optional[PerformanceRating] = None
    comments: List[Dict[str, Any]] = []
    development_plan: Optional[Dict[str, Any]] = None
    next_review_date: Optional[date] = None
    notes: List[Dict[str, Any]] = []

class PerformanceManagementSystem:
    def __init__(self):
        self.goals: Dict[int, Goal] = {}
        self.reviews: Dict[int, PerformanceReview] = {}
        self.feedback: Dict[int, List[Dict[str, Any]]] = {}
        self.notifications: Dict[int, List[Dict[str, Any]]] = {}

    def create_goal(self, employee_id: int, title: str, description: str,
                   start_date: date, end_date: date, category: str,
                   priority: str, weight: float) -> int:
        """Create a new performance goal"""
        goal_id = len(self.goals) + 1
        goal = Goal(
            id=goal_id,
            employee_id=employee_id,
            title=title,
            description=description,
            status=GoalStatus.NOT_STARTED,
            start_date=start_date,
            end_date=end_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            category=category,
            priority=priority,
            weight=weight
        )
        self.goals[goal_id] = goal
        self._notify_employee(employee_id, "new_goal")
        return goal_id

    def update_goal_progress(self, goal_id: int, progress: float,
                           achievement: Optional[Dict[str, Any]] = None,
                           challenge: Optional[Dict[str, Any]] = None) -> bool:
        """Update goal progress and add achievements/challenges"""
        if goal_id not in self.goals:
            return False
        
        goal = self.goals[goal_id]
        goal.progress = progress
        goal.updated_at = datetime.now()
        
        if progress >= 100:
            goal.status = GoalStatus.COMPLETED
        elif progress > 0:
            goal.status = GoalStatus.IN_PROGRESS
        
        if achievement:
            goal.achievements.append({
                **achievement,
                "date": datetime.now()
            })
        
        if challenge:
            goal.challenges.append({
                **challenge,
                "date": datetime.now()
            })
        
        return True

    def add_goal_milestone(self, goal_id: int, title: str, description: str,
                          due_date: date) -> bool:
        """Add a milestone to a goal"""
        if goal_id not in self.goals:
            return False
        
        goal = self.goals[goal_id]
        milestone = {
            "id": len(goal.milestones) + 1,
            "title": title,
            "description": description,
            "due_date": due_date,
            "status": "pending",
            "created_at": datetime.now(),
            "completed_at": None
        }
        
        goal.milestones.append(milestone)
        goal.updated_at = datetime.now()
        return True

    def create_performance_review(self, employee_id: int, reviewer_id: int,
                                review_period: str, start_date: date,
                                end_date: date) -> int:
        """Create a new performance review"""
        review_id = len(self.reviews) + 1
        review = PerformanceReview(
            id=review_id,
            employee_id=employee_id,
            reviewer_id=reviewer_id,
            review_period=review_period,
            status=ReviewStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            start_date=start_date,
            end_date=end_date
        )
        self.reviews[review_id] = review
        self._notify_employee(employee_id, "new_review")
        return review_id

    def add_goal_to_review(self, review_id: int, goal_id: int) -> bool:
        """Add a goal to a performance review"""
        if review_id not in self.reviews or goal_id not in self.goals:
            return False
        
        review = self.reviews[review_id]
        goal = self.goals[goal_id]
        
        review.goals.append({
            "goal_id": goal_id,
            "title": goal.title,
            "description": goal.description,
            "status": goal.status,
            "progress": goal.progress,
            "achievements": goal.achievements,
            "challenges": goal.challenges
        })
        
        review.updated_at = datetime.now()
        return True

    def add_competency_assessment(self, review_id: int, competency: str,
                                rating: PerformanceRating, comments: str) -> bool:
        """Add competency assessment to a review"""
        if review_id not in self.reviews:
            return False
        
        review = self.reviews[review_id]
        review.competencies.append({
            "competency": competency,
            "rating": rating,
            "comments": comments,
            "added_at": datetime.now()
        })
        
        review.updated_at = datetime.now()
        return True

    def add_feedback(self, review_id: int, feedback_type: str, content: str,
                    provided_by: int) -> bool:
        """Add feedback to a review"""
        if review_id not in self.reviews:
            return False
        
        review = self.reviews[review_id]
        review.feedback.append({
            "type": feedback_type,
            "content": content,
            "provided_by": provided_by,
            "timestamp": datetime.now()
        })
        
        review.updated_at = datetime.now()
        return True

    def update_review_status(self, review_id: int, new_status: ReviewStatus,
                           updated_by: int, comment: str = "") -> bool:
        """Update review status"""
        if review_id not in self.reviews:
            return False
        
        review = self.reviews[review_id]
        review.status = new_status
        review.updated_at = datetime.now()
        
        review.notes.append({
            "type": "status_update",
            "content": f"Status changed to {new_status.value}: {comment}",
            "updated_by": updated_by,
            "timestamp": datetime.now()
        })
        
        if new_status == ReviewStatus.PENDING_EMPLOYEE:
            self._notify_employee(review.employee_id, "review_pending_employee")
        elif new_status == ReviewStatus.PENDING_MANAGER:
            self._notify_employee(review.reviewer_id, "review_pending_manager")
        elif new_status == ReviewStatus.COMPLETED:
            self._notify_employee(review.employee_id, "review_completed")
        
        return True

    def set_overall_rating(self, review_id: int, rating: PerformanceRating,
                          comments: str, updated_by: int) -> bool:
        """Set overall performance rating"""
        if review_id not in self.reviews:
            return False
        
        review = self.reviews[review_id]
        review.overall_rating = rating
        review.updated_at = datetime.now()
        
        review.comments.append({
            "type": "rating",
            "content": f"Overall rating set to {rating.value}: {comments}",
            "updated_by": updated_by,
            "timestamp": datetime.now()
        })
        
        return True

    def create_development_plan(self, review_id: int, objectives: List[Dict[str, Any]],
                              timeline: List[Dict[str, Any]], resources: List[Dict[str, Any]]) -> bool:
        """Create development plan for a review"""
        if review_id not in self.reviews:
            return False
        
        review = self.reviews[review_id]
        review.development_plan = {
            "objectives": objectives,
            "timeline": timeline,
            "resources": resources,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        review.updated_at = datetime.now()
        return True

    def get_performance_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics for performance management system"""
        return {
            "goal_metrics": {
                "total_goals": len(self.goals),
                "completion_rate": self._calculate_goal_completion_rate(),
                "by_status": self._get_goal_status_distribution(),
                "by_category": self._get_goal_category_distribution()
            },
            "review_metrics": {
                "total_reviews": len(self.reviews),
                "completion_rate": self._calculate_review_completion_rate(),
                "rating_distribution": self._get_rating_distribution(),
                "by_period": self._get_review_period_distribution()
            },
            "performance_insights": {
                "top_performers": self._identify_top_performers(),
                "development_areas": self._identify_development_areas(),
                "competency_gaps": self._identify_competency_gaps(),
                "trends": self._analyze_performance_trends()
            }
        }

    def _calculate_goal_completion_rate(self) -> float:
        """Calculate goal completion rate"""
        total_goals = len(self.goals)
        if total_goals == 0:
            return 0.0
        
        completed_goals = len([g for g in self.goals.values() 
                             if g.status == GoalStatus.COMPLETED])
        return completed_goals / total_goals

    def _get_goal_status_distribution(self) -> Dict[str, int]:
        """Get distribution of goal statuses"""
        distribution = {status.value: 0 for status in GoalStatus}
        for goal in self.goals.values():
            distribution[goal.status.value] += 1
        return distribution

    def _get_goal_category_distribution(self) -> Dict[str, int]:
        """Get distribution of goals by category"""
        distribution = {}
        for goal in self.goals.values():
            if goal.category not in distribution:
                distribution[goal.category] = 0
            distribution[goal.category] += 1
        return distribution

    def _calculate_review_completion_rate(self) -> float:
        """Calculate review completion rate"""
        total_reviews = len(self.reviews)
        if total_reviews == 0:
            return 0.0
        
        completed_reviews = len([r for r in self.reviews.values() 
                               if r.status == ReviewStatus.COMPLETED])
        return completed_reviews / total_reviews

    def _get_rating_distribution(self) -> Dict[str, int]:
        """Get distribution of performance ratings"""
        distribution = {rating.value: 0 for rating in PerformanceRating}
        for review in self.reviews.values():
            if review.overall_rating:
                distribution[review.overall_rating.value] += 1
        return distribution

    def _get_review_period_distribution(self) -> Dict[str, int]:
        """Get distribution of reviews by period"""
        distribution = {}
        for review in self.reviews.values():
            if review.review_period not in distribution:
                distribution[review.review_period] = 0
            distribution[review.review_period] += 1
        return distribution

    def _identify_top_performers(self) -> List[Dict[str, Any]]:
        """Identify top performers based on ratings and goal completion"""
        top_performers = []
        for review in self.reviews.values():
            if review.overall_rating in [PerformanceRating.EXCEPTIONAL,
                                       PerformanceRating.EXCEEDS_EXPECTATIONS]:
                employee_goals = [g for g in self.goals.values() 
                                if g.employee_id == review.employee_id]
                goal_completion = len([g for g in employee_goals 
                                     if g.status == GoalStatus.COMPLETED])
                
                top_performers.append({
                    "employee_id": review.employee_id,
                    "rating": review.overall_rating.value,
                    "goal_completion": goal_completion / len(employee_goals) if employee_goals else 0.0,
                    "review_period": review.review_period
                })
        
        return sorted(top_performers, key=lambda x: x["goal_completion"], reverse=True)[:5]

    def _identify_development_areas(self) -> List[Dict[str, Any]]:
        """Identify common development areas"""
        development_areas = {}
        for review in self.reviews.values():
            for area in review.development_areas:
                area_name = area.get("area")
                if area_name not in development_areas:
                    development_areas[area_name] = {
                        "count": 0,
                        "reviews": []
                    }
                development_areas[area_name]["count"] += 1
                development_areas[area_name]["reviews"].append({
                    "employee_id": review.employee_id,
                    "review_period": review.review_period
                })
        
        return [
            {
                "area": area,
                "frequency": data["count"],
                "affected_reviews": data["reviews"]
            }
            for area, data in development_areas.items()
        ]

    def _identify_competency_gaps(self) -> List[Dict[str, Any]]:
        """Identify competency gaps across the organization"""
        competency_gaps = {}
        for review in self.reviews.values():
            for competency in review.competencies:
                comp_name = competency.get("competency")
                rating = competency.get("rating")
                
                if rating in [PerformanceRating.NEEDS_IMPROVEMENT,
                            PerformanceRating.UNSATISFACTORY]:
                    if comp_name not in competency_gaps:
                        competency_gaps[comp_name] = {
                            "count": 0,
                            "employees": []
                        }
                    competency_gaps[comp_name]["count"] += 1
                    competency_gaps[comp_name]["employees"].append({
                        "employee_id": review.employee_id,
                        "rating": rating.value,
                        "review_period": review.review_period
                    })
        
        return [
            {
                "competency": comp,
                "frequency": data["count"],
                "affected_employees": data["employees"]
            }
            for comp, data in competency_gaps.items()
        ]

    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        trends = {
            "rating_trends": {},
            "goal_completion_trends": {},
            "development_areas_trends": {}
        }
        
        # Analyze rating trends
        for review in self.reviews.values():
            period = review.review_period
            if period not in trends["rating_trends"]:
                trends["rating_trends"][period] = {rating.value: 0 
                                                 for rating in PerformanceRating}
            if review.overall_rating:
                trends["rating_trends"][period][review.overall_rating.value] += 1
        
        # Analyze goal completion trends
        for goal in self.goals.values():
            period = goal.start_date.strftime("%Y-%m")
            if period not in trends["goal_completion_trends"]:
                trends["goal_completion_trends"][period] = {
                    "total": 0,
                    "completed": 0
                }
            trends["goal_completion_trends"][period]["total"] += 1
            if goal.status == GoalStatus.COMPLETED:
                trends["goal_completion_trends"][period]["completed"] += 1
        
        # Analyze development areas trends
        for review in self.reviews.values():
            period = review.review_period
            if period not in trends["development_areas_trends"]:
                trends["development_areas_trends"][period] = {}
            
            for area in review.development_areas:
                area_name = area.get("area")
                if area_name not in trends["development_areas_trends"][period]:
                    trends["development_areas_trends"][period][area_name] = 0
                trends["development_areas_trends"][period][area_name] += 1
        
        return trends

    def _notify_employee(self, employee_id: int, event_type: str) -> None:
        """Notify employee about performance management events"""
        if employee_id not in self.notifications:
            self.notifications[employee_id] = []
            
        self.notifications[employee_id].append({
            "type": event_type,
            "employee_id": employee_id,
            "timestamp": datetime.now(),
            "is_read": False
        }) 