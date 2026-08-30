from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

class DocumentType(Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    EXPENSE = "expense"
    SALARY = "salary"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    OPENING = "opening"
    CLOSING = "closing"
    REVERSING = "reversing"

class DocumentStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    POSTED = "posted"
    REVERSED = "reversed"

class ApprovalLevel(Enum):
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    LEVEL_4 = "level_4"
    LEVEL_5 = "level_5"

@dataclass
class DocumentAttachment:
    id: str
    document_id: str
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    uploaded_by: str
    uploaded_at: datetime = datetime.now()

@dataclass
class DocumentApproval:
    id: str
    document_id: str
    level: ApprovalLevel
    approver_id: str
    status: DocumentStatus
    comments: str = ""
    approved_at: Optional[datetime] = None
    created_at: datetime = datetime.now()

@dataclass
class DocumentLine:
    id: str
    document_id: str
    account_id: str
    debit_amount: Decimal = Decimal('0')
    credit_amount: Decimal = Decimal('0')
    description: str = ""
    cost_center_id: Optional[str] = None
    department_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None
    location_id: Optional[str] = None
    customer_id: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class FinancialDocument:
    id: str
    number: str
    type: DocumentType
    date: date
    reference: str
    description: str
    total_amount: Decimal
    status: DocumentStatus = DocumentStatus.DRAFT
    fiscal_year_id: str
    created_by: str
    approved_by: Optional[str] = None
    posted_by: Optional[str] = None
    posted_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class FinancialDocumentManager:
    def __init__(self, accounting_system):
        self.logger = logging.getLogger(__name__)
        self.accounting_system = accounting_system
        self.documents: Dict[str, FinancialDocument] = {}
        self.document_lines: Dict[str, List[DocumentLine]] = {}
        self.document_approvals: Dict[str, List[DocumentApproval]] = {}
        self.document_attachments: Dict[str, List[DocumentAttachment]] = {}
    
    def create_document(self, document: FinancialDocument, lines: List[DocumentLine]) -> bool:
        """Create new financial document"""
        try:
            if document.id in self.documents:
                self.logger.warning(f"Document with ID {document.id} already exists")
                return False
            
            # Validate document lines
            if not self._validate_document_lines(lines):
                self.logger.error("Invalid document lines")
                return False
            
            # Save document
            self.documents[document.id] = document
            self.document_lines[document.id] = lines
            
            # Create initial approval record
            approval = DocumentApproval(
                id=f"APP_{document.id}_1",
                document_id=document.id,
                level=ApprovalLevel.LEVEL_1,
                approver_id=document.created_by,
                status=DocumentStatus.DRAFT
            )
            self.document_approvals[document.id] = [approval]
            
            self.logger.info(f"Document {document.number} created successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error creating document: {str(e)}")
            return False
    
    def _validate_document_lines(self, lines: List[DocumentLine]) -> bool:
        """Validate document lines"""
        try:
            total_debit = Decimal('0')
            total_credit = Decimal('0')
            
            for line in lines:
                total_debit += line.debit_amount
                total_credit += line.credit_amount
            
            return total_debit == total_credit
        except Exception:
            return False
    
    def add_attachment(self, attachment: DocumentAttachment) -> bool:
        """Add attachment to document"""
        try:
            if attachment.document_id not in self.documents:
                self.logger.error(f"Document {attachment.document_id} not found")
                return False
            
            if attachment.document_id not in self.document_attachments:
                self.document_attachments[attachment.document_id] = []
            
            self.document_attachments[attachment.document_id].append(attachment)
            self.logger.info(f"Attachment added to document {attachment.document_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding attachment: {str(e)}")
            return False
    
    def submit_for_approval(self, document_id: str, approver_id: str) -> bool:
        """Submit document for approval"""
        try:
            document = self.documents.get(document_id)
            if not document:
                return False
            
            if document.status != DocumentStatus.DRAFT:
                self.logger.warning(f"Document {document_id} is not in draft status")
                return False
            
            # Create new approval record
            current_approvals = self.document_approvals.get(document_id, [])
            next_level = self._get_next_approval_level(current_approvals)
            
            approval = DocumentApproval(
                id=f"APP_{document_id}_{len(current_approvals) + 1}",
                document_id=document_id,
                level=next_level,
                approver_id=approver_id,
                status=DocumentStatus.PENDING
            )
            
            current_approvals.append(approval)
            self.document_approvals[document_id] = current_approvals
            document.status = DocumentStatus.PENDING
            document.updated_at = datetime.now()
            
            self.logger.info(f"Document {document_id} submitted for approval")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting document for approval: {str(e)}")
            return False
    
    def _get_next_approval_level(self, current_approvals: List[DocumentApproval]) -> ApprovalLevel:
        """Get next approval level"""
        if not current_approvals:
            return ApprovalLevel.LEVEL_1
        
        last_approval = current_approvals[-1]
        if last_approval.level == ApprovalLevel.LEVEL_5:
            return ApprovalLevel.LEVEL_5
        
        return ApprovalLevel(f"level_{int(last_approval.level.value.split('_')[1]) + 1}")
    
    def approve_document(self, document_id: str, approver_id: str, comments: str = "") -> bool:
        """Approve document"""
        try:
            document = self.documents.get(document_id)
            if not document:
                return False
            
            if document.status != DocumentStatus.PENDING:
                self.logger.warning(f"Document {document_id} is not pending approval")
                return False
            
            # Update approval record
            current_approvals = self.document_approvals.get(document_id, [])
            last_approval = current_approvals[-1]
            
            if last_approval.approver_id != approver_id:
                self.logger.warning(f"User {approver_id} is not authorized to approve")
                return False
            
            last_approval.status = DocumentStatus.APPROVED
            last_approval.comments = comments
            last_approval.approved_at = datetime.now()
            
            # Check if document needs more approvals
            if last_approval.level == ApprovalLevel.LEVEL_5:
                document.status = DocumentStatus.APPROVED
                document.approved_by = approver_id
                document.updated_at = datetime.now()
            
            self.logger.info(f"Document {document_id} approved")
            return True
        except Exception as e:
            self.logger.error(f"Error approving document: {str(e)}")
            return False
    
    def reject_document(self, document_id: str, approver_id: str, comments: str) -> bool:
        """Reject document"""
        try:
            document = self.documents.get(document_id)
            if not document:
                return False
            
            if document.status != DocumentStatus.PENDING:
                self.logger.warning(f"Document {document_id} is not pending approval")
                return False
            
            # Update approval record
            current_approvals = self.document_approvals.get(document_id, [])
            last_approval = current_approvals[-1]
            
            if last_approval.approver_id != approver_id:
                self.logger.warning(f"User {approver_id} is not authorized to reject")
                return False
            
            last_approval.status = DocumentStatus.REJECTED
            last_approval.comments = comments
            last_approval.approved_at = datetime.now()
            
            document.status = DocumentStatus.REJECTED
            document.updated_at = datetime.now()
            
            self.logger.info(f"Document {document_id} rejected")
            return True
        except Exception as e:
            self.logger.error(f"Error rejecting document: {str(e)}")
            return False
    
    def post_document(self, document_id: str, posted_by: str) -> bool:
        """Post document to accounting system"""
        try:
            document = self.documents.get(document_id)
            if not document:
                return False
            
            if document.status != DocumentStatus.APPROVED:
                self.logger.warning(f"Document {document_id} is not approved")
                return False
            
            # Create journal entry
            lines = self.document_lines.get(document_id, [])
            journal_entry = JournalEntry(
                id=f"JE_{document_id}",
                date=document.date,
                reference=document.reference,
                description=document.description,
                transactions=[]
            )
            
            for line in lines:
                transaction = Transaction(
                    id=f"TR_{document_id}_{line.id}",
                    date=document.date,
                    type=document.type,
                    reference=document.reference,
                    description=line.description,
                    amount=line.debit_amount if line.debit_amount > 0 else line.credit_amount,
                    debit_account_id=line.account_id if line.debit_amount > 0 else "999999",
                    credit_account_id="999999" if line.debit_amount > 0 else line.account_id
                )
                journal_entry.transactions.append(transaction)
            
            # Add journal entry to accounting system
            if not self.accounting_system.add_journal_entry(journal_entry):
                return False
            
            # Update document status
            document.status = DocumentStatus.POSTED
            document.posted_by = posted_by
            document.posted_at = datetime.now()
            document.updated_at = datetime.now()
            
            self.logger.info(f"Document {document_id} posted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error posting document: {str(e)}")
            return False
    
    def reverse_document(self, document_id: str, reversed_by: str) -> bool:
        """Reverse posted document"""
        try:
            document = self.documents.get(document_id)
            if not document:
                return False
            
            if document.status != DocumentStatus.POSTED:
                self.logger.warning(f"Document {document_id} is not posted")
                return False
            
            # Create reversing document
            reversing_doc = FinancialDocument(
                id=f"REV_{document_id}",
                number=f"REV_{document.number}",
                type=DocumentType.REVERSING,
                date=date.today(),
                reference=f"Reversing {document.reference}",
                description=f"Reversing document {document.number}",
                total_amount=document.total_amount,
                status=DocumentStatus.DRAFT,
                fiscal_year_id=document.fiscal_year_id,
                created_by=reversed_by
            )
            
            # Create reversing lines
            lines = self.document_lines.get(document_id, [])
            reversing_lines = []
            
            for line in lines:
                reversing_line = DocumentLine(
                    id=f"REV_{line.id}",
                    document_id=reversing_doc.id,
                    account_id=line.account_id,
                    debit_amount=line.credit_amount,
                    credit_amount=line.debit_amount,
                    description=f"Reversing {line.description}",
                    cost_center_id=line.cost_center_id,
                    department_id=line.department_id,
                    project_id=line.project_id,
                    product_id=line.product_id,
                    location_id=line.location_id,
                    customer_id=line.customer_id
                )
                reversing_lines.append(reversing_line)
            
            # Create reversing document
            if not self.create_document(reversing_doc, reversing_lines):
                return False
            
            # Update original document
            document.status = DocumentStatus.REVERSED
            document.updated_at = datetime.now()
            
            self.logger.info(f"Document {document_id} reversed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error reversing document: {str(e)}")
            return False
    
    def get_document_details(self, document_id: str) -> Dict[str, Any]:
        """Get document details including lines, approvals and attachments"""
        try:
            document = self.documents.get(document_id)
            if not document:
                return {}
            
            return {
                "document": {
                    "id": document.id,
                    "number": document.number,
                    "type": document.type.value,
                    "date": document.date.isoformat(),
                    "reference": document.reference,
                    "description": document.description,
                    "total_amount": document.total_amount,
                    "status": document.status.value,
                    "created_by": document.created_by,
                    "approved_by": document.approved_by,
                    "posted_by": document.posted_by,
                    "posted_at": document.posted_at.isoformat() if document.posted_at else None,
                    "created_at": document.created_at.isoformat(),
                    "updated_at": document.updated_at.isoformat()
                },
                "lines": [
                    {
                        "id": line.id,
                        "account_id": line.account_id,
                        "debit_amount": line.debit_amount,
                        "credit_amount": line.credit_amount,
                        "description": line.description,
                        "cost_center_id": line.cost_center_id,
                        "department_id": line.department_id,
                        "project_id": line.project_id,
                        "product_id": line.product_id,
                        "location_id": line.location_id,
                        "customer_id": line.customer_id
                    }
                    for line in self.document_lines.get(document_id, [])
                ],
                "approvals": [
                    {
                        "id": approval.id,
                        "level": approval.level.value,
                        "approver_id": approval.approver_id,
                        "status": approval.status.value,
                        "comments": approval.comments,
                        "approved_at": approval.approved_at.isoformat() if approval.approved_at else None,
                        "created_at": approval.created_at.isoformat()
                    }
                    for approval in self.document_approvals.get(document_id, [])
                ],
                "attachments": [
                    {
                        "id": attachment.id,
                        "file_name": attachment.file_name,
                        "file_type": attachment.file_type,
                        "file_size": attachment.file_size,
                        "uploaded_by": attachment.uploaded_by,
                        "uploaded_at": attachment.uploaded_at.isoformat()
                    }
                    for attachment in self.document_attachments.get(document_id, [])
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting document details: {str(e)}")
            return {}
    
    def get_document_list(self, 
                         document_type: Optional[DocumentType] = None,
                         status: Optional[DocumentStatus] = None,
                         start_date: Optional[date] = None,
                         end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get list of documents with optional filters"""
        try:
            documents = []
            for document in self.documents.values():
                if (document_type and document.type != document_type) or \
                   (status and document.status != status) or \
                   (start_date and document.date < start_date) or \
                   (end_date and document.date > end_date):
                    continue
                
                documents.append({
                    "id": document.id,
                    "number": document.number,
                    "type": document.type.value,
                    "date": document.date.isoformat(),
                    "reference": document.reference,
                    "description": document.description,
                    "total_amount": document.total_amount,
                    "status": document.status.value,
                    "created_by": document.created_by,
                    "created_at": document.created_at.isoformat()
                })
            
            return sorted(documents, key=lambda x: x["date"], reverse=True)
        except Exception as e:
            self.logger.error(f"Error getting document list: {str(e)}")
            return [] 