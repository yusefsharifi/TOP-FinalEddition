from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship

class FeedbackStatus(Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class FeedbackType(Enum):
    SELF = "self"
    PEER = "peer"
    MANAGER = "manager"
    SUBORDINATE = "subordinate"
    CUSTOMER = "customer"

class CompetencyLevel(Enum):
    EXPERT = "expert"
    ADVANCED = "advanced"
    PROFICIENT = "proficient"
    INTERMEDIATE = "intermediate"
    BEGINNER = "beginner"

class FeedbackTemplate(BaseModel):
    id: int
    name: str
    description: str
    competencies: List[Dict[str, Any]]
    questions: List[Dict[str, Any]]
    rating_scale: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    department: Optional[str] = None

class FeedbackRequest(BaseModel):
    id: int
    employee_id: int
    template_id: int
    status: FeedbackStatus
    created_at: datetime
    due_date: datetime
    reviewers: List[Dict[str, Any]]
    feedback_types: List[FeedbackType]
    competencies: List[Dict[str, Any]]
    questions: List[Dict[str, Any]]
    responses: Dict[int, Dict[str, Any]]
    comments: Dict[int, List[Dict[str, Any]]]
    overall_rating: Optional[float] = None
    summary: Optional[str] = None
    action_items: List[Dict[str, Any]] = []
    development_plan: Optional[Dict[str, Any]] = None

class Feedback360System:
    def __init__(self):
        self.templates: Dict[int, FeedbackTemplate] = {}
        self.feedback_requests: Dict[int, FeedbackRequest] = {}
        self.competency_framework: Dict[str, Dict[str, Any]] = {}
        self.notifications: Dict[int, List[Dict[str, Any]]] = {}

    def create_template(self, name: str, description: str, competencies: List[Dict[str, Any]], 
                       questions: List[Dict[str, Any]], rating_scale: Dict[str, Any]) -> int:
        """Create a new feedback template"""
        template_id = len(self.templates) + 1
        template = FeedbackTemplate(
            id=template_id,
            name=name,
            description=description,
            competencies=competencies,
            questions=questions,
            rating_scale=rating_scale,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.templates[template_id] = template
        return template_id

    def create_feedback_request(self, employee_id: int, template_id: int, 
                              reviewers: List[Dict[str, Any]], due_date: datetime) -> int:
        """Create a new feedback request"""
        if template_id not in self.templates:
            return -1

        template = self.templates[template_id]
        request_id = len(self.feedback_requests) + 1
        request = FeedbackRequest(
            id=request_id,
            employee_id=employee_id,
            template_id=template_id,
            status=FeedbackStatus.IN_PROGRESS,
            created_at=datetime.now(),
            due_date=due_date,
            reviewers=reviewers,
            feedback_types=[FeedbackType.SELF],  # Always include self-feedback
            competencies=template.competencies,
            questions=template.questions,
            responses={},
            comments={}
        )
        self.feedback_requests[request_id] = request
        self._create_notifications(reviewers, "new_feedback_request", request_id)
        return request_id

    def submit_feedback(self, request_id: int, reviewer_id: int, 
                       responses: Dict[str, Any], comments: List[Dict[str, Any]]) -> bool:
        """Submit feedback for a request"""
        if request_id not in self.feedback_requests:
            return False
        request = self.feedback_requests[request_id]
        
        request.responses[reviewer_id] = responses
        request.comments[reviewer_id] = comments
        
        # Check if all reviewers have submitted feedback
        if len(request.responses) == len(request.reviewers):
            self._calculate_overall_rating(request_id)
            request.status = FeedbackStatus.COMPLETED
            self._create_summary(request_id)
            self._generate_development_plan(request_id)
        
        return True

    def get_feedback_summary(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Get the summary of a feedback request"""
        if request_id not in self.feedback_requests:
            return None
        request = self.feedback_requests[request_id]
        
        if not request.summary:
            return None
            
        return {
            "overall_rating": request.overall_rating,
            "summary": request.summary,
            "action_items": request.action_items,
            "development_plan": request.development_plan,
            "competency_ratings": self._get_competency_ratings(request_id),
            "feedback_by_type": self._get_feedback_by_type(request_id)
        }

    def get_employee_feedback_history(self, employee_id: int) -> List[Dict[str, Any]]:
        """Get feedback history for an employee"""
        return [
            {
                "request_id": req.id,
                "date": req.created_at,
                "status": req.status,
                "overall_rating": req.overall_rating,
                "reviewers": len(req.reviewers)
            }
            for req in self.feedback_requests.values()
            if req.employee_id == employee_id
        ]

    def get_pending_feedback(self, reviewer_id: int) -> List[Dict[str, Any]]:
        """Get all pending feedback requests for a reviewer"""
        return [
            {
                "request_id": req.id,
                "employee_id": req.employee_id,
                "due_date": req.due_date,
                "template_name": self.templates[req.template_id].name
            }
            for req in self.feedback_requests.values()
            if req.status == FeedbackStatus.IN_PROGRESS
            and any(r["id"] == reviewer_id for r in req.reviewers)
            and reviewer_id not in req.responses
        ]

    def _calculate_overall_rating(self, request_id: int) -> None:
        """Calculate overall rating from all feedback"""
        request = self.feedback_requests[request_id]
        ratings = []
        
        for responses in request.responses.values():
            for competency in responses.values():
                if isinstance(competency, (int, float)):
                    ratings.append(competency)
        
        if ratings:
            request.overall_rating = sum(ratings) / len(ratings)

    def _create_summary(self, request_id: int) -> None:
        """Create a summary of the feedback"""
        request = self.feedback_requests[request_id]
        
        # Analyze strengths and areas for improvement
        strengths = []
        improvements = []
        
        for competency in request.competencies:
            competency_ratings = []
            for responses in request.responses.values():
                if competency["id"] in responses:
                    competency_ratings.append(responses[competency["id"]])
            
            if competency_ratings:
                avg_rating = sum(competency_ratings) / len(competency_ratings)
                if avg_rating >= 4.0:
                    strengths.append(competency["name"])
                elif avg_rating <= 2.0:
                    improvements.append(competency["name"])
        
        # Create action items
        action_items = []
        for improvement in improvements:
            action_items.append({
                "area": improvement,
                "action": f"Develop {improvement} through training and practice",
                "priority": "high"
            })
        
        request.summary = {
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "key_findings": self._analyze_key_findings(request_id)
        }
        request.action_items = action_items

    def _generate_development_plan(self, request_id: int) -> None:
        """Generate a development plan based on feedback"""
        request = self.feedback_requests[request_id]
        
        development_plan = {
            "short_term_goals": [],
            "long_term_goals": [],
            "training_recommendations": [],
            "mentoring_opportunities": []
        }
        
        # Add goals based on areas for improvement
        for improvement in request.summary["areas_for_improvement"]:
            development_plan["short_term_goals"].append({
                "goal": f"Improve {improvement}",
                "timeline": "3 months",
                "success_metrics": f"Demonstrate improved {improvement} in next review"
            })
        
        # Add training recommendations
        for improvement in request.summary["areas_for_improvement"]:
            development_plan["training_recommendations"].append({
                "topic": improvement,
                "type": "workshop",
                "duration": "2 days",
                "provider": "Internal Training"
            })
        
        request.development_plan = development_plan

    def _analyze_key_findings(self, request_id: int) -> List[str]:
        """Analyze feedback to identify key findings"""
        request = self.feedback_requests[request_id]
        findings = []
        
        # Analyze patterns in comments
        comment_patterns = {}
        for comments in request.comments.values():
            for comment in comments:
                for competency in comment.get("competencies", []):
                    if competency not in comment_patterns:
                        comment_patterns[competency] = []
                    comment_patterns[competency].append(comment["content"])
        
        # Identify recurring themes
        for competency, comments in comment_patterns.items():
            if len(comments) >= 3:  # If multiple reviewers mention the same thing
                findings.append(f"Strong consensus on {competency}: {comments[0]}")
        
        return findings

    def _get_competency_ratings(self, request_id: int) -> Dict[str, float]:
        """Get average ratings for each competency"""
        request = self.feedback_requests[request_id]
        ratings = {}
        
        for competency in request.competencies:
            competency_ratings = []
            for responses in request.responses.values():
                if competency["id"] in responses:
                    competency_ratings.append(responses[competency["id"]])
            
            if competency_ratings:
                ratings[competency["name"]] = sum(competency_ratings) / len(competency_ratings)
        
        return ratings

    def _get_feedback_by_type(self, request_id: int) -> Dict[str, Dict[str, Any]]:
        """Get feedback organized by feedback type"""
        request = self.feedback_requests[request_id]
        feedback_by_type = {}
        
        for feedback_type in request.feedback_types:
            feedback_by_type[feedback_type.value] = {
                "ratings": [],
                "comments": []
            }
            
            for reviewer in request.reviewers:
                if reviewer["type"] == feedback_type and reviewer["id"] in request.responses:
                    feedback_by_type[feedback_type.value]["ratings"].append(
                        request.responses[reviewer["id"]]
                    )
                    feedback_by_type[feedback_type.value]["comments"].extend(
                        request.comments.get(reviewer["id"], [])
                    )
        
        return feedback_by_type

    def _create_notifications(self, reviewers: List[Dict[str, Any]], 
                            notification_type: str, reference_id: int) -> None:
        """Create notifications for reviewers"""
        for reviewer in reviewers:
            reviewer_id = reviewer["id"]
            if reviewer_id not in self.notifications:
                self.notifications[reviewer_id] = []
            self.notifications[reviewer_id].append({
                "type": notification_type,
                "reference_id": reference_id,
                "created_at": datetime.now(),
                "is_read": False
            })

    def get_feedback_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics for feedback system"""
        return {
            "request_statistics": {
                "total_requests": len(self.feedback_requests),
                "completed_requests": len([r for r in self.feedback_requests.values() 
                                        if r.status == FeedbackStatus.COMPLETED]),
                "completion_rate": self._calculate_completion_rate()
            },
            "feedback_quality": {
                "average_rating": self._calculate_average_rating(),
                "response_rate": self._calculate_response_rate(),
                "feedback_distribution": self._get_feedback_distribution()
            },
            "competency_analysis": {
                "top_competencies": self._get_top_competencies(),
                "improvement_areas": self._get_improvement_areas()
            }
        }

    def _calculate_completion_rate(self) -> float:
        """Calculate the rate of completed feedback requests"""
        total = len(self.feedback_requests)
        completed = len([r for r in self.feedback_requests.values() 
                        if r.status == FeedbackStatus.COMPLETED])
        return completed / total if total > 0 else 0.0

    def _calculate_average_rating(self) -> float:
        """Calculate average rating across all completed feedback"""
        ratings = [r.overall_rating for r in self.feedback_requests.values() 
                  if r.overall_rating is not None]
        return sum(ratings) / len(ratings) if ratings else 0.0

    def _calculate_response_rate(self) -> float:
        """Calculate average response rate for feedback requests"""
        total_responses = sum(len(r.responses) for r in self.feedback_requests.values())
        total_expected = sum(len(r.reviewers) for r in self.feedback_requests.values())
        return total_responses / total_expected if total_expected > 0 else 0.0

    def _get_feedback_distribution(self) -> Dict[str, int]:
        """Get distribution of feedback types"""
        distribution = {ft.value: 0 for ft in FeedbackType}
        for request in self.feedback_requests.values():
            for ft in request.feedback_types:
                distribution[ft.value] += 1
        return distribution

    def _get_top_competencies(self) -> List[Dict[str, Any]]:
        """Get top performing competencies"""
        competency_ratings = {}
        for request in self.feedback_requests.values():
            if request.overall_rating:
                for competency, rating in self._get_competency_ratings(request.id).items():
                    if competency not in competency_ratings:
                        competency_ratings[competency] = []
                    competency_ratings[competency].append(rating)
        
        return [
            {"competency": comp, "average_rating": sum(ratings) / len(ratings)}
            for comp, ratings in competency_ratings.items()
        ]

    def _get_improvement_areas(self) -> List[Dict[str, Any]]:
        """Get areas needing improvement"""
        improvement_areas = {}
        for request in self.feedback_requests.values():
            if request.summary:
                for area in request.summary["areas_for_improvement"]:
                    if area not in improvement_areas:
                        improvement_areas[area] = 0
                    improvement_areas[area] += 1
        
        return [
            {"area": area, "frequency": count}
            for area, count in improvement_areas.items()
        ] 