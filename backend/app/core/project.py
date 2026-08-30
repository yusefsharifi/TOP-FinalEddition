from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import os
import uuid

class ProjectStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class ResourceType(Enum):
    HUMAN = "human"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    FINANCIAL = "financial"

@dataclass
class Project:
    id: str
    name: str
    description: str
    start_date: date
    end_date: date
    status: ProjectStatus
    budget: Decimal
    actual_cost: Decimal = Decimal('0')
    progress: Decimal = Decimal('0')
    priority: int = 1
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Task:
    id: str
    project_id: str
    name: str
    description: str
    start_date: date
    end_date: date
    status: TaskStatus
    priority: int = 1
    progress: Decimal = Decimal('0')
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Resource:
    id: str
    project_id: str
    name: str
    type: ResourceType
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    availability: Decimal = Decimal('1')
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Risk:
    id: str
    project_id: str
    name: str
    description: str
    probability: Decimal
    impact: Decimal
    mitigation_plan: str
    status: str = "open"  # open, mitigated, closed
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Milestone:
    id: str
    project_id: str
    name: str
    description: str
    due_date: date
    status: str = "pending"  # pending, completed, delayed
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Document:
    id: str
    project_id: str
    name: str
    description: str
    file_path: str
    file_type: str
    file_size: int
    version: str = "1.0"
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class ProjectManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.projects: Dict[str, Project] = {}
        self.tasks: Dict[str, Task] = {}
        self.resources: Dict[str, Resource] = {}
        self.risks: Dict[str, Risk] = {}
        self.milestones: Dict[str, Milestone] = {}
        self.documents: Dict[str, Document] = {}
        
        # Create necessary directories
        self.create_directories()
    
    def create_directories(self):
        """Create necessary directories for project management"""
        try:
            # Create project documents directory
            docs_dir = os.path.join(os.path.dirname(__file__), 'project_documents')
            if not os.path.exists(docs_dir):
                os.makedirs(docs_dir)
            
            # Create project reports directory
            reports_dir = os.path.join(os.path.dirname(__file__), 'project_reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            self.logger.info("Project management directories created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {str(e)}")
    
    def create_project(self, project: Project) -> bool:
        """Create new project"""
        try:
            if project.id in self.projects:
                self.logger.warning(f"Project with ID {project.id} already exists")
                return False
            
            self.projects[project.id] = project
            self.logger.info(f"Project created: {project.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating project: {str(e)}")
            return False
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update project details"""
        try:
            project = self.projects.get(project_id)
            if not project:
                self.logger.error(f"Project {project_id} not found")
                return False
            
            # Update project attributes
            for key, value in updates.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            project.updated_at = datetime.now()
            self.logger.info(f"Project updated: {project.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating project: {str(e)}")
            return False
    
    def add_task(self, task: Task) -> bool:
        """Add task to project"""
        try:
            if task.id in self.tasks:
                self.logger.warning(f"Task with ID {task.id} already exists")
                return False
            
            if task.project_id not in self.projects:
                self.logger.error(f"Project {task.project_id} not found")
                return False
            
            self.tasks[task.id] = task
            self.logger.info(f"Task added: {task.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding task: {str(e)}")
            return False
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task details"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                self.logger.error(f"Task {task_id} not found")
                return False
            
            # Update task attributes
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            task.updated_at = datetime.now()
            self.logger.info(f"Task updated: {task.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating task: {str(e)}")
            return False
    
    def add_resource(self, resource: Resource) -> bool:
        """Add resource to project"""
        try:
            if resource.id in self.resources:
                self.logger.warning(f"Resource with ID {resource.id} already exists")
                return False
            
            if resource.project_id not in self.projects:
                self.logger.error(f"Project {resource.project_id} not found")
                return False
            
            self.resources[resource.id] = resource
            self.logger.info(f"Resource added: {resource.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding resource: {str(e)}")
            return False
    
    def update_resource(self, resource_id: str, updates: Dict[str, Any]) -> bool:
        """Update resource details"""
        try:
            resource = self.resources.get(resource_id)
            if not resource:
                self.logger.error(f"Resource {resource_id} not found")
                return False
            
            # Update resource attributes
            for key, value in updates.items():
                if hasattr(resource, key):
                    setattr(resource, key, value)
            
            resource.updated_at = datetime.now()
            self.logger.info(f"Resource updated: {resource.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating resource: {str(e)}")
            return False
    
    def add_risk(self, risk: Risk) -> bool:
        """Add risk to project"""
        try:
            if risk.id in self.risks:
                self.logger.warning(f"Risk with ID {risk.id} already exists")
                return False
            
            if risk.project_id not in self.projects:
                self.logger.error(f"Project {risk.project_id} not found")
                return False
            
            self.risks[risk.id] = risk
            self.logger.info(f"Risk added: {risk.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding risk: {str(e)}")
            return False
    
    def update_risk(self, risk_id: str, updates: Dict[str, Any]) -> bool:
        """Update risk details"""
        try:
            risk = self.risks.get(risk_id)
            if not risk:
                self.logger.error(f"Risk {risk_id} not found")
                return False
            
            # Update risk attributes
            for key, value in updates.items():
                if hasattr(risk, key):
                    setattr(risk, key, value)
            
            risk.updated_at = datetime.now()
            self.logger.info(f"Risk updated: {risk.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating risk: {str(e)}")
            return False
    
    def add_milestone(self, milestone: Milestone) -> bool:
        """Add milestone to project"""
        try:
            if milestone.id in self.milestones:
                self.logger.warning(f"Milestone with ID {milestone.id} already exists")
                return False
            
            if milestone.project_id not in self.projects:
                self.logger.error(f"Project {milestone.project_id} not found")
                return False
            
            self.milestones[milestone.id] = milestone
            self.logger.info(f"Milestone added: {milestone.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding milestone: {str(e)}")
            return False
    
    def update_milestone(self, milestone_id: str, updates: Dict[str, Any]) -> bool:
        """Update milestone details"""
        try:
            milestone = self.milestones.get(milestone_id)
            if not milestone:
                self.logger.error(f"Milestone {milestone_id} not found")
                return False
            
            # Update milestone attributes
            for key, value in updates.items():
                if hasattr(milestone, key):
                    setattr(milestone, key, value)
            
            milestone.updated_at = datetime.now()
            self.logger.info(f"Milestone updated: {milestone.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating milestone: {str(e)}")
            return False
    
    def add_document(self, document: Document) -> bool:
        """Add document to project"""
        try:
            if document.id in self.documents:
                self.logger.warning(f"Document with ID {document.id} already exists")
                return False
            
            if document.project_id not in self.projects:
                self.logger.error(f"Project {document.project_id} not found")
                return False
            
            self.documents[document.id] = document
            self.logger.info(f"Document added: {document.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            return False
    
    def update_document(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update document details"""
        try:
            document = self.documents.get(document_id)
            if not document:
                self.logger.error(f"Document {document_id} not found")
                return False
            
            # Update document attributes
            for key, value in updates.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            
            document.updated_at = datetime.now()
            self.logger.info(f"Document updated: {document.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating document: {str(e)}")
            return False
    
    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Get project summary"""
        try:
            project = self.projects.get(project_id)
            if not project:
                self.logger.error(f"Project {project_id} not found")
                return {}
            
            # Get project tasks
            project_tasks = [task for task in self.tasks.values() if task.project_id == project_id]
            
            # Get project resources
            project_resources = [resource for resource in self.resources.values() if resource.project_id == project_id]
            
            # Get project risks
            project_risks = [risk for risk in self.risks.values() if risk.project_id == project_id]
            
            # Get project milestones
            project_milestones = [milestone for milestone in self.milestones.values() if milestone.project_id == project_id]
            
            # Calculate summary metrics
            total_tasks = len(project_tasks)
            completed_tasks = len([task for task in project_tasks if task.status == TaskStatus.DONE])
            total_resources = len(project_resources)
            total_risks = len(project_risks)
            total_milestones = len(project_milestones)
            completed_milestones = len([milestone for milestone in project_milestones if milestone.status == "completed"])
            
            return {
                "project": project,
                "metrics": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "task_completion_rate": Decimal(str(completed_tasks / total_tasks)) if total_tasks > 0 else Decimal('0'),
                    "total_resources": total_resources,
                    "total_risks": total_risks,
                    "total_milestones": total_milestones,
                    "completed_milestones": completed_milestones,
                    "milestone_completion_rate": Decimal(str(completed_milestones / total_milestones)) if total_milestones > 0 else Decimal('0'),
                    "budget_utilization": project.actual_cost / project.budget if project.budget > 0 else Decimal('0')
                },
                "tasks": project_tasks,
                "resources": project_resources,
                "risks": project_risks,
                "milestones": project_milestones
            }
        except Exception as e:
            self.logger.error(f"Error getting project summary: {str(e)}")
            return {}
    
    def get_project_report(self, project_id: str) -> Dict[str, Any]:
        """Generate project report"""
        try:
            summary = self.get_project_summary(project_id)
            if not summary:
                return {}
            
            # Generate report content
            report = {
                "project_id": project_id,
                "generated_at": datetime.now().isoformat(),
                "summary": summary,
                "analysis": {
                    "schedule": self.analyze_schedule(project_id),
                    "cost": self.analyze_cost(project_id),
                    "risks": self.analyze_risks(project_id),
                    "resources": self.analyze_resources(project_id)
                },
                "recommendations": self.generate_recommendations(project_id)
            }
            
            # Save report
            report_file = os.path.join(os.path.dirname(__file__), 
                                     'project_reports', 
                                     f'report_{project_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.json')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating project report: {str(e)}")
            return {}
    
    def analyze_schedule(self, project_id: str) -> Dict[str, Any]:
        """Analyze project schedule"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return {}
            
            # Get project tasks
            tasks = [task for task in self.tasks.values() if task.project_id == project_id]
            
            # Calculate schedule metrics
            total_duration = (project.end_date - project.start_date).days
            elapsed_duration = (date.today() - project.start_date).days
            remaining_duration = (project.end_date - date.today()).days
            
            # Calculate task completion metrics
            completed_tasks = len([task for task in tasks if task.status == TaskStatus.DONE])
            in_progress_tasks = len([task for task in tasks if task.status == TaskStatus.IN_PROGRESS])
            delayed_tasks = len([task for task in tasks if task.end_date < date.today() and task.status != TaskStatus.DONE])
            
            return {
                "total_duration": total_duration,
                "elapsed_duration": elapsed_duration,
                "remaining_duration": remaining_duration,
                "schedule_progress": Decimal(str(elapsed_duration / total_duration)) if total_duration > 0 else Decimal('0'),
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "delayed_tasks": delayed_tasks,
                "task_completion_rate": Decimal(str(completed_tasks / len(tasks))) if tasks else Decimal('0')
            }
        except Exception as e:
            self.logger.error(f"Error analyzing schedule: {str(e)}")
            return {}
    
    def analyze_cost(self, project_id: str) -> Dict[str, Any]:
        """Analyze project costs"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return {}
            
            # Get project resources
            resources = [resource for resource in self.resources.values() if resource.project_id == project_id]
            
            # Calculate cost metrics
            total_budget = project.budget
            actual_cost = project.actual_cost
            remaining_budget = total_budget - actual_cost
            
            # Calculate resource costs
            resource_costs = {
                resource.type.value: resource.total_cost
                for resource in resources
            }
            
            return {
                "total_budget": total_budget,
                "actual_cost": actual_cost,
                "remaining_budget": remaining_budget,
                "budget_utilization": actual_cost / total_budget if total_budget > 0 else Decimal('0'),
                "resource_costs": resource_costs,
                "cost_variance": actual_cost - total_budget
            }
        except Exception as e:
            self.logger.error(f"Error analyzing cost: {str(e)}")
            return {}
    
    def analyze_risks(self, project_id: str) -> Dict[str, Any]:
        """Analyze project risks"""
        try:
            # Get project risks
            risks = [risk for risk in self.risks.values() if risk.project_id == project_id]
            
            # Calculate risk metrics
            total_risks = len(risks)
            open_risks = len([risk for risk in risks if risk.status == "open"])
            mitigated_risks = len([risk for risk in risks if risk.status == "mitigated"])
            closed_risks = len([risk for risk in risks if risk.status == "closed"])
            
            # Calculate risk scores
            risk_scores = {
                "high": len([risk for risk in risks if risk.probability * risk.impact > Decimal('0.7')]),
                "medium": len([risk for risk in risks if Decimal('0.3') <= risk.probability * risk.impact <= Decimal('0.7')]),
                "low": len([risk for risk in risks if risk.probability * risk.impact < Decimal('0.3')])
            }
            
            return {
                "total_risks": total_risks,
                "open_risks": open_risks,
                "mitigated_risks": mitigated_risks,
                "closed_risks": closed_risks,
                "risk_scores": risk_scores,
                "risk_trend": self.calculate_risk_trend(risks)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing risks: {str(e)}")
            return {}
    
    def analyze_resources(self, project_id: str) -> Dict[str, Any]:
        """Analyze project resources"""
        try:
            # Get project resources
            resources = [resource for resource in self.resources.values() if resource.project_id == project_id]
            
            # Calculate resource metrics
            total_resources = len(resources)
            resource_types = {
                resource_type.value: len([r for r in resources if r.type == resource_type])
                for resource_type in ResourceType
            }
            
            # Calculate resource utilization
            resource_utilization = {
                resource.id: resource.availability
                for resource in resources
            }
            
            return {
                "total_resources": total_resources,
                "resource_types": resource_types,
                "resource_utilization": resource_utilization,
                "resource_allocation": self.calculate_resource_allocation(resources)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing resources: {str(e)}")
            return {}
    
    def calculate_risk_trend(self, risks: List[Risk]) -> str:
        """Calculate risk trend"""
        try:
            if not risks:
                return "No risks"
            
            # Calculate average risk score
            avg_score = sum(risk.probability * risk.impact for risk in risks) / len(risks)
            
            if avg_score > Decimal('0.7'):
                return "High risk trend"
            elif avg_score > Decimal('0.3'):
                return "Moderate risk trend"
            else:
                return "Low risk trend"
        except Exception as e:
            self.logger.error(f"Error calculating risk trend: {str(e)}")
            return "Unable to calculate risk trend"
    
    def calculate_resource_allocation(self, resources: List[Resource]) -> Dict[str, Any]:
        """Calculate resource allocation"""
        try:
            allocation = {
                "total_cost": sum(resource.total_cost for resource in resources),
                "by_type": {},
                "utilization": {}
            }
            
            # Calculate allocation by resource type
            for resource_type in ResourceType:
                type_resources = [r for r in resources if r.type == resource_type]
                allocation["by_type"][resource_type.value] = {
                    "count": len(type_resources),
                    "total_cost": sum(r.total_cost for r in type_resources),
                    "average_cost": sum(r.total_cost for r in type_resources) / len(type_resources) if type_resources else Decimal('0')
                }
            
            # Calculate resource utilization
            for resource in resources:
                allocation["utilization"][resource.id] = {
                    "name": resource.name,
                    "type": resource.type.value,
                    "availability": resource.availability,
                    "cost": resource.total_cost
                }
            
            return allocation
        except Exception as e:
            self.logger.error(f"Error calculating resource allocation: {str(e)}")
            return {}
    
    def generate_recommendations(self, project_id: str) -> List[Dict[str, Any]]:
        """Generate project recommendations"""
        try:
            recommendations = []
            
            # Get project analysis
            schedule_analysis = self.analyze_schedule(project_id)
            cost_analysis = self.analyze_cost(project_id)
            risk_analysis = self.analyze_risks(project_id)
            resource_analysis = self.analyze_resources(project_id)
            
            # Schedule recommendations
            if schedule_analysis.get("delayed_tasks", 0) > 0:
                recommendations.append({
                    "type": "schedule",
                    "priority": "high",
                    "message": f"Address {schedule_analysis['delayed_tasks']} delayed tasks",
                    "action": "Review and update task schedules"
                })
            
            # Cost recommendations
            if cost_analysis.get("budget_utilization", Decimal('0')) > Decimal('0.9'):
                recommendations.append({
                    "type": "cost",
                    "priority": "high",
                    "message": "Budget utilization is high",
                    "action": "Review and optimize resource allocation"
                })
            
            # Risk recommendations
            if risk_analysis.get("risk_scores", {}).get("high", 0) > 0:
                recommendations.append({
                    "type": "risk",
                    "priority": "high",
                    "message": "High-risk items identified",
                    "action": "Review and implement risk mitigation plans"
                })
            
            # Resource recommendations
            for resource_id, utilization in resource_analysis.get("resource_utilization", {}).items():
                if utilization < Decimal('0.5'):
                    recommendations.append({
                        "type": "resource",
                        "priority": "medium",
                        "message": f"Low resource utilization for {resource_id}",
                        "action": "Review resource allocation"
                    })
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return [] 