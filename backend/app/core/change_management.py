from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship

class ChangeStatus(Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    FAILED = "failed"

class ChangeType(Enum):
    ORGANIZATIONAL = "organizational"
    PROCESS = "process"
    TECHNOLOGICAL = "technological"
    CULTURAL = "cultural"
    STRUCTURAL = "structural"
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"

class ImpactLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ChangeRequest(BaseModel):
    id: int
    title: str
    description: str
    type: ChangeType
    status: ChangeStatus
    impact_level: ImpactLevel
    priority: int
    requested_by: int
    approved_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    budget: Optional[float] = None
    actual_cost: Optional[float] = None
    stakeholders: List[Dict[str, Any]] = []
    affected_departments: List[str] = []
    affected_employees: List[int] = []
    objectives: List[str] = []
    success_criteria: List[str] = []
    risks: List[Dict[str, Any]] = []
    mitigation_plans: List[Dict[str, Any]] = []
    tasks: List[Dict[str, Any]] = []
    resources: List[Dict[str, Any]] = []
    communications: List[Dict[str, Any]] = []
    training_plans: List[Dict[str, Any]] = []
    feedback: List[Dict[str, Any]] = []
    documents: List[Dict[str, Any]] = []
    milestones: List[Dict[str, Any]] = []
    dependencies: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []

class ChangeManagementSystem:
    def __init__(self):
        self.change_requests: Dict[int, ChangeRequest] = {}
        self.notifications: Dict[int, List[Dict[str, Any]]] = {}
        self.risk_register: Dict[str, Dict[str, Any]] = {}
        self.resource_pool: Dict[str, List[Dict[str, Any]]] = {}

    def create_change_request(self, title: str, description: str, 
                            change_type: ChangeType, impact_level: ImpactLevel,
                            priority: int, requested_by: int,
                            stakeholders: List[Dict[str, Any]],
                            affected_departments: List[str],
                            affected_employees: List[int],
                            objectives: List[str],
                            success_criteria: List[str]) -> int:
        """Create a new change request"""
        request_id = len(self.change_requests) + 1
        request = ChangeRequest(
            id=request_id,
            title=title,
            description=description,
            type=change_type,
            status=ChangeStatus.PLANNED,
            impact_level=impact_level,
            priority=priority,
            requested_by=requested_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            stakeholders=stakeholders,
            affected_departments=affected_departments,
            affected_employees=affected_employees,
            objectives=objectives,
            success_criteria=success_criteria
        )
        self.change_requests[request_id] = request
        self._notify_stakeholders(request_id, "change_request_created")
        return request_id

    def approve_change_request(self, request_id: int, approved_by: int) -> bool:
        """Approve a change request"""
        if request_id not in self.change_requests:
            return False
        
        request = self.change_requests[request_id]
        if request.status != ChangeStatus.PLANNED:
            return False
        
        request.status = ChangeStatus.IN_PROGRESS
        request.approved_by = approved_by
        request.updated_at = datetime.now()
        
        self._notify_stakeholders(request_id, "change_request_approved")
        return True

    def update_change_status(self, request_id: int, new_status: ChangeStatus,
                           updated_by: int, reason: str = "") -> bool:
        """Update the status of a change request"""
        if request_id not in self.change_requests:
            return False
        
        request = self.change_requests[request_id]
        request.status = new_status
        request.updated_at = datetime.now()
        
        if new_status == ChangeStatus.COMPLETED:
            request.actual_end_date = datetime.now()
        elif new_status == ChangeStatus.IN_PROGRESS and not request.actual_start_date:
            request.actual_start_date = datetime.now()
        
        request.notes.append({
            "type": "status_update",
            "content": f"Status changed to {new_status.value}: {reason}",
            "updated_by": updated_by,
            "timestamp": datetime.now()
        })
        
        self._notify_stakeholders(request_id, "status_updated")
        return True

    def add_task(self, request_id: int, title: str, description: str,
                 assigned_to: int, due_date: datetime,
                 priority: int = 1) -> bool:
        """Add a task to a change request"""
        if request_id not in self.change_requests:
            return False
        
        request = self.change_requests[request_id]
        task = {
            "id": len(request.tasks) + 1,
            "title": title,
            "description": description,
            "assigned_to": assigned_to,
            "due_date": due_date,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "completion_date": None,
            "notes": []
        }
        
        request.tasks.append(task)
        self._notify_stakeholders(request_id, "new_task")
        return True

    def update_task_status(self, request_id: int, task_id: int,
                          new_status: str, updated_by: int,
                          comment: str = "") -> bool:
        """Update the status of a task"""
        if request_id not in self.change_requests:
            return False
        
        request = self.change_requests[request_id]
        task = next((t for t in request.tasks if t["id"] == task_id), None)
        if not task:
            return False
        
        task["status"] = new_status
        task["updated_at"] = datetime.now()
        if new_status == "completed":
            task["completion_date"] = datetime.now()
        
        task["notes"].append({
            "type": "status_update",
            "content": f"Status changed to {new_status}: {comment}",
            "updated_by": updated_by,
            "timestamp": datetime.now()
        })
        
        self._notify_stakeholders(request_id, "task_status_updated")
        return True

    def add_risk(self, request_id: int, title: str, description: str,
                 probability: float, impact: str,
                 mitigation_plan: str) -> bool:
        """Add a risk to a change request"""
        if request_id not in self.change_requests:
            return False
        
        request = self.change_requests[request_id]
        risk = {
            "id": len(request.risks) + 1,
            "title": title,
            "description": description,
            "probability": probability,
            "impact": impact,
            "mitigation_plan": mitigation_plan,
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "resolved_at": None,
            "notes": []
        }
        
        request.risks.append(risk)
        self._notify_stakeholders(request_id, "new_risk")
        return True

    def update_risk_status(self, request_id: int, risk_id: int,
                          new_status: str, updated_by: int,
                          comment: str = "") -> bool:
        """Update the status of a risk"""
        if request_id not in self.change_requests:
            return False
        
        request = self.change_requests[request_id]
        risk = next((r for r in request.risks if r["id"] == risk_id), None)
        if not risk:
            return False
        
        risk["status"] = new_status
        risk["updated_at"] = datetime.now()
        if new_status == "resolved":
            risk["resolved_at"] = datetime.now()
        
        risk["notes"].append({
            "type": "status_update",
            "content": f"Status changed to {new_status}: {comment}",
            "updated_by": updated_by,
            "timestamp": datetime.now()
        })
        
        self._notify_stakeholders(request_id, "risk_status_updated")
        return True

    def add_communication(self, request_id: int, title: str, content: str,
                         audience: List[str], channel: str,
                         scheduled_date: datetime) -> bool:
        """Add a communication plan to a change request"""
        if request_id not in self.change_requests:
            return False
        
        request = self.change_requests[request_id]
        communication = {
            "id": len(request.communications) + 1,
            "title": title,
            "content": content,
            "audience": audience,
            "channel": channel,
            "scheduled_date": scheduled_date,
            "status": "scheduled",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "sent_at": None,
            "feedback": []
        }
        
        request.communications.append(communication)
        self._notify_stakeholders(request_id, "new_communication")
        return True

    def add_training_plan(self, request_id: int, title: str, description: str,
                         target_audience: List[str], trainer: str,
                         scheduled_date: datetime, duration: str) -> bool:
        """Add a training plan to a change request"""
        if request_id not in self.change_requests:
            return False
        
        request = self.change_requests[request_id]
        training = {
            "id": len(request.training_plans) + 1,
            "title": title,
            "description": description,
            "target_audience": target_audience,
            "trainer": trainer,
            "scheduled_date": scheduled_date,
            "duration": duration,
            "status": "scheduled",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "completed_at": None,
            "feedback": []
        }
        
        request.training_plans.append(training)
        self._notify_stakeholders(request_id, "new_training")
        return True

    def add_feedback(self, request_id: int, user_id: int, content: str,
                     category: str) -> bool:
        """Add feedback to a change request"""
        if request_id not in self.change_requests:
            return False
        
        request = self.change_requests[request_id]
        feedback = {
            "id": len(request.feedback) + 1,
            "user_id": user_id,
            "content": content,
            "category": category,
            "created_at": datetime.now(),
            "status": "active"
        }
        
        request.feedback.append(feedback)
        self._notify_stakeholders(request_id, "new_feedback")
        return True

    def get_change_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics for change management system"""
        return {
            "change_statistics": {
                "total_changes": len(self.change_requests),
                "completed_changes": len([c for c in self.change_requests.values() 
                                       if c.status == ChangeStatus.COMPLETED]),
                "in_progress_changes": len([c for c in self.change_requests.values() 
                                         if c.status == ChangeStatus.IN_PROGRESS]),
                "planned_changes": len([c for c in self.change_requests.values() 
                                     if c.status == ChangeStatus.PLANNED])
            },
            "performance_metrics": {
                "average_completion_time": self._calculate_average_completion_time(),
                "success_rate": self._calculate_success_rate(),
                "risk_management": self._get_risk_management_metrics(),
                "resource_utilization": self._get_resource_utilization()
            },
            "impact_analysis": {
                "change_types": self._get_change_type_distribution(),
                "impact_levels": self._get_impact_level_distribution(),
                "department_impact": self._get_department_impact(),
                "cost_analysis": self._get_cost_analysis()
            }
        }

    def _calculate_average_completion_time(self) -> float:
        """Calculate average time to complete changes"""
        completed_changes = [c for c in self.change_requests.values() 
                           if c.status == ChangeStatus.COMPLETED 
                           and c.actual_start_date and c.actual_end_date]
        
        if not completed_changes:
            return 0.0
            
        total_days = sum((c.actual_end_date - c.actual_start_date).days 
                        for c in completed_changes)
        return total_days / len(completed_changes)

    def _calculate_success_rate(self) -> float:
        """Calculate success rate of changes"""
        total_changes = len(self.change_requests)
        if total_changes == 0:
            return 0.0
            
        successful_changes = len([c for c in self.change_requests.values() 
                                if c.status == ChangeStatus.COMPLETED])
        return successful_changes / total_changes

    def _get_risk_management_metrics(self) -> Dict[str, Any]:
        """Get risk management metrics"""
        total_risks = sum(len(c.risks) for c in self.change_requests.values())
        resolved_risks = sum(len([r for r in c.risks if r["status"] == "resolved"]) 
                           for c in self.change_requests.values())
        
        return {
            "total_risks": total_risks,
            "resolved_risks": resolved_risks,
            "resolution_rate": resolved_risks / total_risks if total_risks > 0 else 0.0,
            "risk_distribution": self._get_risk_distribution()
        }

    def _get_resource_utilization(self) -> Dict[str, Any]:
        """Get resource utilization metrics"""
        return {
            "total_tasks": sum(len(c.tasks) for c in self.change_requests.values()),
            "completed_tasks": sum(len([t for t in c.tasks if t["status"] == "completed"]) 
                                 for c in self.change_requests.values()),
            "resource_allocation": self._get_resource_allocation(),
            "training_completion": self._get_training_completion()
        }

    def _get_change_type_distribution(self) -> Dict[str, int]:
        """Get distribution of change types"""
        distribution = {ct.value: 0 for ct in ChangeType}
        for request in self.change_requests.values():
            distribution[request.type.value] += 1
        return distribution

    def _get_impact_level_distribution(self) -> Dict[str, int]:
        """Get distribution of impact levels"""
        distribution = {il.value: 0 for il in ImpactLevel}
        for request in self.change_requests.values():
            distribution[request.impact_level.value] += 1
        return distribution

    def _get_department_impact(self) -> Dict[str, int]:
        """Get impact distribution across departments"""
        department_impact = {}
        for request in self.change_requests.values():
            for department in request.affected_departments:
                if department not in department_impact:
                    department_impact[department] = 0
                department_impact[department] += 1
        return department_impact

    def _get_cost_analysis(self) -> Dict[str, Any]:
        """Get cost analysis of changes"""
        total_budget = sum(c.budget for c in self.change_requests.values() 
                         if c.budget is not None)
        total_actual = sum(c.actual_cost for c in self.change_requests.values() 
                         if c.actual_cost is not None)
        
        return {
            "total_budget": total_budget,
            "total_actual": total_actual,
            "budget_variance": total_actual - total_budget if total_budget else 0.0,
            "average_cost": total_actual / len(self.change_requests) 
                          if self.change_requests else 0.0
        }

    def _get_risk_distribution(self) -> Dict[str, int]:
        """Get distribution of risk statuses"""
        distribution = {"active": 0, "resolved": 0, "mitigated": 0}
        for request in self.change_requests.values():
            for risk in request.risks:
                distribution[risk["status"]] += 1
        return distribution

    def _get_resource_allocation(self) -> Dict[str, Any]:
        """Get resource allocation metrics"""
        return {
            "total_resources": sum(len(c.resources) for c in self.change_requests.values()),
            "resource_types": self._get_resource_type_distribution(),
            "resource_utilization": self._calculate_resource_utilization()
        }

    def _get_training_completion(self) -> Dict[str, Any]:
        """Get training completion metrics"""
        total_training = sum(len(c.training_plans) for c in self.change_requests.values())
        completed_training = sum(len([t for t in c.training_plans if t["status"] == "completed"]) 
                               for c in self.change_requests.values())
        
        return {
            "total_sessions": total_training,
            "completed_sessions": completed_training,
            "completion_rate": completed_training / total_training if total_training > 0 else 0.0
        }

    def _get_resource_type_distribution(self) -> Dict[str, int]:
        """Get distribution of resource types"""
        distribution = {}
        for request in self.change_requests.values():
            for resource in request.resources:
                resource_type = resource.get("type", "other")
                if resource_type not in distribution:
                    distribution[resource_type] = 0
                distribution[resource_type] += 1
        return distribution

    def _calculate_resource_utilization(self) -> float:
        """Calculate overall resource utilization"""
        total_capacity = sum(r.get("capacity", 0) for request in self.change_requests.values() 
                           for r in request.resources)
        total_allocated = sum(r.get("allocated", 0) for request in self.change_requests.values() 
                            for r in request.resources)
        
        return total_allocated / total_capacity if total_capacity > 0 else 0.0

    def _notify_stakeholders(self, request_id: int, event_type: str) -> None:
        """Notify stakeholders about change events"""
        if request_id not in self.change_requests:
            return
            
        request = self.change_requests[request_id]
        for stakeholder in request.stakeholders:
            user_id = stakeholder["user_id"]
            if user_id not in self.notifications:
                self.notifications[user_id] = []
            self.notifications[user_id].append({
                "type": event_type,
                "request_id": request_id,
                "title": request.title,
                "timestamp": datetime.now(),
                "is_read": False
            }) 