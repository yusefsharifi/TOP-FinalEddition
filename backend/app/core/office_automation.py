import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
import uuid
from pathlib import Path

# Document Types
class DocumentType(Enum):
    LETTER = "letter"
    MEMO = "memo"
    REPORT = "report"
    CONTRACT = "contract"
    FORM = "form"
    NOTICE = "notice"
    CIRCULAR = "circular"
    PROPOSAL = "proposal"
    MINUTES = "minutes"
    OTHER = "other"

# Document Status
class DocumentStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    EXPIRED = "expired"

# Document Priority
class DocumentPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Document Classification
class DocumentClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"

@dataclass
class Document:
    id: str
    type: DocumentType
    title: str
    content: str
    status: DocumentStatus
    priority: DocumentPriority
    classification: DocumentClassification
    sender_id: str
    sender_department: str
    recipients: List[str]
    cc_recipients: List[str]
    bcc_recipients: List[str]
    reference_number: str
    date: datetime
    due_date: Optional[datetime]
    attachments: List[str]
    tags: List[str]
    comments: List[Dict[str, Any]]
    workflow_history: List[Dict[str, Any]]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

# Workflow Types
class WorkflowType(Enum):
    APPROVAL = "approval"
    REVIEW = "review"
    NOTIFICATION = "notification"
    TASK = "task"
    SIGNATURE = "signature"

# Workflow Status
class WorkflowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Workflow:
    id: str
    type: WorkflowType
    document_id: str
    status: WorkflowStatus
    steps: List[Dict[str, Any]]
    current_step: int
    assigned_to: List[str]
    deadline: Optional[datetime]
    comments: List[Dict[str, Any]]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

# Task Types
class TaskType(Enum):
    FOLLOW_UP = "follow_up"
    REMINDER = "reminder"
    DEADLINE = "deadline"
    MEETING = "meeting"
    OTHER = "other"

# Task Status
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

@dataclass
class Task:
    id: str
    type: TaskType
    title: str
    description: str
    status: TaskStatus
    assigned_to: List[str]
    priority: DocumentPriority
    due_date: datetime
    related_document_id: Optional[str]
    attachments: List[str]
    comments: List[Dict[str, Any]]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

# Meeting Types
class MeetingType(Enum):
    REGULAR = "regular"
    EMERGENCY = "emergency"
    PLANNING = "planning"
    REVIEW = "review"
    OTHER = "other"

# Meeting Status
class MeetingStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

@dataclass
class Meeting:
    id: str
    type: MeetingType
    title: str
    description: str
    status: MeetingStatus
    organizer_id: str
    participants: List[str]
    start_time: datetime
    end_time: datetime
    location: str
    agenda: List[str]
    minutes: Optional[str]
    attachments: List[str]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class OfficeAutomationManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize data structures
        self.documents: Dict[str, Document] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.tasks: Dict[str, Task] = {}
        self.meetings: Dict[str, Meeting] = {}
        
        # Create necessary directories
        self.create_directories()
        
        # Load saved data
        self.load_data()
    
    def create_directories(self):
        """Create necessary directories for office automation"""
        try:
            # Create main data directory
            data_dir = os.path.join(os.path.dirname(__file__), 'office_automation_data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Create subdirectories for each system
            subdirs = [
                'documents', 'workflows', 'tasks', 'meetings',
                'attachments', 'templates', 'archives'
            ]
            
            for subdir in subdirs:
                path = os.path.join(data_dir, subdir)
                if not os.path.exists(path):
                    os.makedirs(path)
            
            self.logger.info("Office automation directories created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {str(e)}")
    
    def load_data(self):
        """Load saved data from files"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), 'office_automation_data')
            
            # Load document data
            document_file = os.path.join(data_dir, 'documents', 'documents.json')
            if os.path.exists(document_file):
                with open(document_file, 'r', encoding='utf-8') as f:
                    document_data = json.load(f)
                    for item in document_data:
                        document = Document(**item)
                        self.documents[document.id] = document
            
            # Load workflow data
            workflow_file = os.path.join(data_dir, 'workflows', 'workflows.json')
            if os.path.exists(workflow_file):
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                    for item in workflow_data:
                        workflow = Workflow(**item)
                        self.workflows[workflow.id] = workflow
            
            # Load task data
            task_file = os.path.join(data_dir, 'tasks', 'tasks.json')
            if os.path.exists(task_file):
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                    for item in task_data:
                        task = Task(**item)
                        self.tasks[task.id] = task
            
            # Load meeting data
            meeting_file = os.path.join(data_dir, 'meetings', 'meetings.json')
            if os.path.exists(meeting_file):
                with open(meeting_file, 'r', encoding='utf-8') as f:
                    meeting_data = json.load(f)
                    for item in meeting_data:
                        meeting = Meeting(**item)
                        self.meetings[meeting.id] = meeting
            
            self.logger.info("Office automation data loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
    
    def save_data(self):
        """Save data to files"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), 'office_automation_data')
            
            # Save document data
            document_file = os.path.join(data_dir, 'documents', 'documents.json')
            with open(document_file, 'w', encoding='utf-8') as f:
                json.dump([vars(document) for document in self.documents.values()], f, indent=4)
            
            # Save workflow data
            workflow_file = os.path.join(data_dir, 'workflows', 'workflows.json')
            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump([vars(workflow) for workflow in self.workflows.values()], f, indent=4)
            
            # Save task data
            task_file = os.path.join(data_dir, 'tasks', 'tasks.json')
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump([vars(task) for task in self.tasks.values()], f, indent=4)
            
            # Save meeting data
            meeting_file = os.path.join(data_dir, 'meetings', 'meetings.json')
            with open(meeting_file, 'w', encoding='utf-8') as f:
                json.dump([vars(meeting) for meeting in self.meetings.values()], f, indent=4)
            
            self.logger.info("Office automation data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
    
    # Document Management Methods
    def create_document(self, document: Document) -> bool:
        """Create new document"""
        try:
            if document.id in self.documents:
                self.logger.warning(f"Document with ID {document.id} already exists")
                return False
            
            self.documents[document.id] = document
            self.save_data()
            self.logger.info(f"Document created: {document.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating document: {str(e)}")
            return False
    
    def update_document_status(self, document_id: str, status: DocumentStatus) -> bool:
        """Update document status"""
        try:
            document = self.documents.get(document_id)
            if not document:
                self.logger.error(f"Document {document_id} not found")
                return False
            
            document.status = status
            document.updated_at = datetime.now()
            self.save_data()
            self.logger.info(f"Document status updated: {document.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating document status: {str(e)}")
            return False
    
    def add_document_comment(self, document_id: str, user_id: str, comment: str) -> bool:
        """Add comment to document"""
        try:
            document = self.documents.get(document_id)
            if not document:
                self.logger.error(f"Document {document_id} not found")
                return False
            
            comment_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "comment": comment,
                "timestamp": datetime.now().isoformat()
            }
            document.comments.append(comment_data)
            document.updated_at = datetime.now()
            self.save_data()
            self.logger.info(f"Comment added to document: {document.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding document comment: {str(e)}")
            return False
    
    # Workflow Management Methods
    def create_workflow(self, workflow: Workflow) -> bool:
        """Create new workflow"""
        try:
            if workflow.id in self.workflows:
                self.logger.warning(f"Workflow with ID {workflow.id} already exists")
                return False
            
            self.workflows[workflow.id] = workflow
            self.save_data()
            self.logger.info(f"Workflow created: {workflow.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating workflow: {str(e)}")
            return False
    
    def update_workflow_status(self, workflow_id: str, status: WorkflowStatus) -> bool:
        """Update workflow status"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                self.logger.error(f"Workflow {workflow_id} not found")
                return False
            
            workflow.status = status
            workflow.updated_at = datetime.now()
            self.save_data()
            self.logger.info(f"Workflow status updated: {workflow.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating workflow status: {str(e)}")
            return False
    
    def advance_workflow_step(self, workflow_id: str) -> bool:
        """Advance workflow to next step"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                self.logger.error(f"Workflow {workflow_id} not found")
                return False
            
            if workflow.current_step < len(workflow.steps) - 1:
                workflow.current_step += 1
                workflow.updated_at = datetime.now()
                self.save_data()
                self.logger.info(f"Workflow advanced to step {workflow.current_step + 1}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error advancing workflow step: {str(e)}")
            return False
    
    # Task Management Methods
    def create_task(self, task: Task) -> bool:
        """Create new task"""
        try:
            if task.id in self.tasks:
                self.logger.warning(f"Task with ID {task.id} already exists")
                return False
            
            self.tasks[task.id] = task
            self.save_data()
            self.logger.info(f"Task created: {task.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating task: {str(e)}")
            return False
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                self.logger.error(f"Task {task_id} not found")
                return False
            
            task.status = status
            task.updated_at = datetime.now()
            self.save_data()
            self.logger.info(f"Task status updated: {task.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating task status: {str(e)}")
            return False
    
    def assign_task(self, task_id: str, user_ids: List[str]) -> bool:
        """Assign task to users"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                self.logger.error(f"Task {task_id} not found")
                return False
            
            task.assigned_to = user_ids
            task.updated_at = datetime.now()
            self.save_data()
            self.logger.info(f"Task assigned to users: {task.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error assigning task: {str(e)}")
            return False
    
    # Meeting Management Methods
    def schedule_meeting(self, meeting: Meeting) -> bool:
        """Schedule new meeting"""
        try:
            if meeting.id in self.meetings:
                self.logger.warning(f"Meeting with ID {meeting.id} already exists")
                return False
            
            self.meetings[meeting.id] = meeting
            self.save_data()
            self.logger.info(f"Meeting scheduled: {meeting.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error scheduling meeting: {str(e)}")
            return False
    
    def update_meeting_status(self, meeting_id: str, status: MeetingStatus) -> bool:
        """Update meeting status"""
        try:
            meeting = self.meetings.get(meeting_id)
            if not meeting:
                self.logger.error(f"Meeting {meeting_id} not found")
                return False
            
            meeting.status = status
            meeting.updated_at = datetime.now()
            self.save_data()
            self.logger.info(f"Meeting status updated: {meeting.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating meeting status: {str(e)}")
            return False
    
    def add_meeting_minutes(self, meeting_id: str, minutes: str) -> bool:
        """Add minutes to meeting"""
        try:
            meeting = self.meetings.get(meeting_id)
            if not meeting:
                self.logger.error(f"Meeting {meeting_id} not found")
                return False
            
            meeting.minutes = minutes
            meeting.updated_at = datetime.now()
            self.save_data()
            self.logger.info(f"Minutes added to meeting: {meeting.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding meeting minutes: {str(e)}")
            return False
    
    # Analytics Methods
    def generate_document_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate document analytics"""
        try:
            period_documents = [
                document for document in self.documents.values()
                if start_date <= document.created_at.date() <= end_date
            ]
            
            analytics = {
                "total_documents": len(period_documents),
                "by_type": {},
                "by_status": {},
                "by_priority": {},
                "by_classification": {},
                "average_processing_time": 0
            }
            
            # Calculate metrics by type
            for doc_type in DocumentType:
                analytics["by_type"][doc_type.value] = len([
                    doc for doc in period_documents
                    if doc.type == doc_type
                ])
            
            # Calculate metrics by status
            for status in DocumentStatus:
                analytics["by_status"][status.value] = len([
                    doc for doc in period_documents
                    if doc.status == status
                ])
            
            # Calculate metrics by priority
            for priority in DocumentPriority:
                analytics["by_priority"][priority.value] = len([
                    doc for doc in period_documents
                    if doc.priority == priority
                ])
            
            # Calculate metrics by classification
            for classification in DocumentClassification:
                analytics["by_classification"][classification.value] = len([
                    doc for doc in period_documents
                    if doc.classification == classification
                ])
            
            # Calculate average processing time
            completed_docs = [
                doc for doc in period_documents
                if doc.status == DocumentStatus.APPROVED
            ]
            if completed_docs:
                total_time = sum(
                    (doc.updated_at - doc.created_at).total_seconds()
                    for doc in completed_docs
                )
                analytics["average_processing_time"] = total_time / len(completed_docs)
            
            return analytics
        except Exception as e:
            self.logger.error(f"Error generating document analytics: {str(e)}")
            return {}
    
    def generate_workflow_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate workflow analytics"""
        try:
            period_workflows = [
                workflow for workflow in self.workflows.values()
                if start_date <= workflow.created_at.date() <= end_date
            ]
            
            analytics = {
                "total_workflows": len(period_workflows),
                "by_type": {},
                "by_status": {},
                "average_completion_time": 0,
                "completion_rate": 0
            }
            
            # Calculate metrics by type
            for workflow_type in WorkflowType:
                analytics["by_type"][workflow_type.value] = len([
                    wf for wf in period_workflows
                    if wf.type == workflow_type
                ])
            
            # Calculate metrics by status
            for status in WorkflowStatus:
                analytics["by_status"][status.value] = len([
                    wf for wf in period_workflows
                    if wf.status == status
                ])
            
            # Calculate average completion time
            completed_workflows = [
                wf for wf in period_workflows
                if wf.status == WorkflowStatus.COMPLETED
            ]
            if completed_workflows:
                total_time = sum(
                    (wf.updated_at - wf.created_at).total_seconds()
                    for wf in completed_workflows
                )
                analytics["average_completion_time"] = total_time / len(completed_workflows)
            
            # Calculate completion rate
            if period_workflows:
                analytics["completion_rate"] = len(completed_workflows) / len(period_workflows)
            
            return analytics
        except Exception as e:
            self.logger.error(f"Error generating workflow analytics: {str(e)}")
            return {}
    
    def generate_task_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate task analytics"""
        try:
            period_tasks = [
                task for task in self.tasks.values()
                if start_date <= task.created_at.date() <= end_date
            ]
            
            analytics = {
                "total_tasks": len(period_tasks),
                "by_type": {},
                "by_status": {},
                "by_priority": {},
                "completion_rate": 0,
                "overdue_rate": 0
            }
            
            # Calculate metrics by type
            for task_type in TaskType:
                analytics["by_type"][task_type.value] = len([
                    task for task in period_tasks
                    if task.type == task_type
                ])
            
            # Calculate metrics by status
            for status in TaskStatus:
                analytics["by_status"][status.value] = len([
                    task for task in period_tasks
                    if task.status == status
                ])
            
            # Calculate metrics by priority
            for priority in DocumentPriority:
                analytics["by_priority"][priority.value] = len([
                    task for task in period_tasks
                    if task.priority == priority
                ])
            
            # Calculate completion rate
            completed_tasks = [
                task for task in period_tasks
                if task.status == TaskStatus.COMPLETED
            ]
            if period_tasks:
                analytics["completion_rate"] = len(completed_tasks) / len(period_tasks)
            
            # Calculate overdue rate
            overdue_tasks = [
                task for task in period_tasks
                if task.status == TaskStatus.OVERDUE
            ]
            if period_tasks:
                analytics["overdue_rate"] = len(overdue_tasks) / len(period_tasks)
            
            return analytics
        except Exception as e:
            self.logger.error(f"Error generating task analytics: {str(e)}")
            return {}
    
    def generate_meeting_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate meeting analytics"""
        try:
            period_meetings = [
                meeting for meeting in self.meetings.values()
                if start_date <= meeting.created_at.date() <= end_date
            ]
            
            analytics = {
                "total_meetings": len(period_meetings),
                "by_type": {},
                "by_status": {},
                "average_participants": 0,
                "completion_rate": 0
            }
            
            # Calculate metrics by type
            for meeting_type in MeetingType:
                analytics["by_type"][meeting_type.value] = len([
                    meeting for meeting in period_meetings
                    if meeting.type == meeting_type
                ])
            
            # Calculate metrics by status
            for status in MeetingStatus:
                analytics["by_status"][status.value] = len([
                    meeting for meeting in period_meetings
                    if meeting.status == status
                ])
            
            # Calculate average participants
            if period_meetings:
                total_participants = sum(
                    len(meeting.participants)
                    for meeting in period_meetings
                )
                analytics["average_participants"] = total_participants / len(period_meetings)
            
            # Calculate completion rate
            completed_meetings = [
                meeting for meeting in period_meetings
                if meeting.status == MeetingStatus.COMPLETED
            ]
            if period_meetings:
                analytics["completion_rate"] = len(completed_meetings) / len(period_meetings)
            
            return analytics
        except Exception as e:
            self.logger.error(f"Error generating meeting analytics: {str(e)}")
            return {}
    
    def generate_comprehensive_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate comprehensive analytics for all systems"""
        try:
            analytics = {
                "documents": self.generate_document_analytics(start_date, end_date),
                "workflows": self.generate_workflow_analytics(start_date, end_date),
                "tasks": self.generate_task_analytics(start_date, end_date),
                "meetings": self.generate_meeting_analytics(start_date, end_date)
            }
            
            # Calculate overall performance metrics
            analytics["overall"] = {
                "total_documents": analytics["documents"]["total_documents"],
                "total_workflows": analytics["workflows"]["total_workflows"],
                "total_tasks": analytics["tasks"]["total_tasks"],
                "total_meetings": analytics["meetings"]["total_meetings"],
                "average_completion_rate": (
                    analytics["workflows"]["completion_rate"] +
                    analytics["tasks"]["completion_rate"] +
                    analytics["meetings"]["completion_rate"]
                ) / 3
            }
            
            return analytics
        except Exception as e:
            self.logger.error(f"Error generating comprehensive analytics: {str(e)}")
            return {} 