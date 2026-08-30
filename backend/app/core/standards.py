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

class StandardType(Enum):
    ISO = "iso"
    GAAP = "gaap"
    IFRS = "ifrs"
    SOX = "sox"
    PCI = "pci"
    GDPR = "gdpr"
    CUSTOM = "custom"

class ComplianceStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    EXEMPT = "exempt"

@dataclass
class Standard:
    id: str
    name: str
    description: str
    type: StandardType
    version: str
    effective_date: date
    expiry_date: Optional[date]
    requirements: List[Dict[str, Any]]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ComplianceRequirement:
    id: str
    standard_id: str
    requirement_id: str
    description: str
    status: ComplianceStatus
    evidence: List[Dict[str, Any]]
    notes: str = ""
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ComplianceEvidence:
    id: str
    requirement_id: str
    name: str
    description: str
    file_path: str
    file_type: str
    file_size: int
    uploaded_by: str
    uploaded_at: datetime = datetime.now()

@dataclass
class ComplianceAudit:
    id: str
    standard_id: str
    name: str
    description: str
    start_date: date
    end_date: date
    status: str = "planned"  # planned, in_progress, completed
    findings: List[Dict[str, Any]] = None
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ComplianceReport:
    id: str
    standard_id: str
    name: str
    description: str
    period_start: date
    period_end: date
    status: str = "draft"  # draft, final
    content: Dict[str, Any] = None
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class StandardsManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.standards: Dict[str, Standard] = {}
        self.requirements: Dict[str, ComplianceRequirement] = {}
        self.evidence: Dict[str, ComplianceEvidence] = {}
        self.audits: Dict[str, ComplianceAudit] = {}
        self.reports: Dict[str, ComplianceReport] = {}
        
        # Create necessary directories
        self.create_directories()
        
        # Load standards from file
        self.load_standards()
    
    def create_directories(self):
        """Create necessary directories for standards management"""
        try:
            # Create standards documents directory
            docs_dir = os.path.join(os.path.dirname(__file__), 'standards_documents')
            if not os.path.exists(docs_dir):
                os.makedirs(docs_dir)
            
            # Create compliance evidence directory
            evidence_dir = os.path.join(os.path.dirname(__file__), 'compliance_evidence')
            if not os.path.exists(evidence_dir):
                os.makedirs(evidence_dir)
            
            # Create compliance reports directory
            reports_dir = os.path.join(os.path.dirname(__file__), 'compliance_reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            self.logger.info("Standards management directories created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {str(e)}")
    
    def load_standards(self):
        """Load standards from JSON file"""
        try:
            standards_file = os.path.join(os.path.dirname(__file__), 'standards.json')
            if os.path.exists(standards_file):
                with open(standards_file, 'r', encoding='utf-8') as f:
                    standards_data = json.load(f)
                    for standard_data in standards_data:
                        standard = Standard(
                            id=standard_data['id'],
                            name=standard_data['name'],
                            description=standard_data['description'],
                            type=StandardType(standard_data['type']),
                            version=standard_data['version'],
                            effective_date=datetime.strptime(standard_data['effective_date'], '%Y-%m-%d').date(),
                            expiry_date=datetime.strptime(standard_data['expiry_date'], '%Y-%m-%d').date() if standard_data.get('expiry_date') else None,
                            requirements=standard_data['requirements'],
                            created_by=standard_data['created_by']
                        )
                        self.standards[standard.id] = standard
                self.logger.info("Standards loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading standards: {str(e)}")
    
    def add_standard(self, standard: Standard) -> bool:
        """Add new standard"""
        try:
            if standard.id in self.standards:
                self.logger.warning(f"Standard with ID {standard.id} already exists")
                return False
            
            self.standards[standard.id] = standard
            self.logger.info(f"Standard added: {standard.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding standard: {str(e)}")
            return False
    
    def update_standard(self, standard_id: str, updates: Dict[str, Any]) -> bool:
        """Update standard details"""
        try:
            standard = self.standards.get(standard_id)
            if not standard:
                self.logger.error(f"Standard {standard_id} not found")
                return False
            
            # Update standard attributes
            for key, value in updates.items():
                if hasattr(standard, key):
                    setattr(standard, key, value)
            
            standard.updated_at = datetime.now()
            self.logger.info(f"Standard updated: {standard.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating standard: {str(e)}")
            return False
    
    def add_requirement(self, requirement: ComplianceRequirement) -> bool:
        """Add compliance requirement"""
        try:
            if requirement.id in self.requirements:
                self.logger.warning(f"Requirement with ID {requirement.id} already exists")
                return False
            
            if requirement.standard_id not in self.standards:
                self.logger.error(f"Standard {requirement.standard_id} not found")
                return False
            
            self.requirements[requirement.id] = requirement
            self.logger.info(f"Requirement added: {requirement.description}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding requirement: {str(e)}")
            return False
    
    def update_requirement(self, requirement_id: str, updates: Dict[str, Any]) -> bool:
        """Update compliance requirement"""
        try:
            requirement = self.requirements.get(requirement_id)
            if not requirement:
                self.logger.error(f"Requirement {requirement_id} not found")
                return False
            
            # Update requirement attributes
            for key, value in updates.items():
                if hasattr(requirement, key):
                    setattr(requirement, key, value)
            
            requirement.updated_at = datetime.now()
            self.logger.info(f"Requirement updated: {requirement.description}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating requirement: {str(e)}")
            return False
    
    def add_evidence(self, evidence: ComplianceEvidence) -> bool:
        """Add compliance evidence"""
        try:
            if evidence.id in self.evidence:
                self.logger.warning(f"Evidence with ID {evidence.id} already exists")
                return False
            
            if evidence.requirement_id not in self.requirements:
                self.logger.error(f"Requirement {evidence.requirement_id} not found")
                return False
            
            self.evidence[evidence.id] = evidence
            self.logger.info(f"Evidence added: {evidence.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding evidence: {str(e)}")
            return False
    
    def update_evidence(self, evidence_id: str, updates: Dict[str, Any]) -> bool:
        """Update compliance evidence"""
        try:
            evidence = self.evidence.get(evidence_id)
            if not evidence:
                self.logger.error(f"Evidence {evidence_id} not found")
                return False
            
            # Update evidence attributes
            for key, value in updates.items():
                if hasattr(evidence, key):
                    setattr(evidence, key, value)
            
            evidence.uploaded_at = datetime.now()
            self.logger.info(f"Evidence updated: {evidence.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating evidence: {str(e)}")
            return False
    
    def add_audit(self, audit: ComplianceAudit) -> bool:
        """Add compliance audit"""
        try:
            if audit.id in self.audits:
                self.logger.warning(f"Audit with ID {audit.id} already exists")
                return False
            
            if audit.standard_id not in self.standards:
                self.logger.error(f"Standard {audit.standard_id} not found")
                return False
            
            self.audits[audit.id] = audit
            self.logger.info(f"Audit added: {audit.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding audit: {str(e)}")
            return False
    
    def update_audit(self, audit_id: str, updates: Dict[str, Any]) -> bool:
        """Update compliance audit"""
        try:
            audit = self.audits.get(audit_id)
            if not audit:
                self.logger.error(f"Audit {audit_id} not found")
                return False
            
            # Update audit attributes
            for key, value in updates.items():
                if hasattr(audit, key):
                    setattr(audit, key, value)
            
            audit.updated_at = datetime.now()
            self.logger.info(f"Audit updated: {audit.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating audit: {str(e)}")
            return False
    
    def add_report(self, report: ComplianceReport) -> bool:
        """Add compliance report"""
        try:
            if report.id in self.reports:
                self.logger.warning(f"Report with ID {report.id} already exists")
                return False
            
            if report.standard_id not in self.standards:
                self.logger.error(f"Standard {report.standard_id} not found")
                return False
            
            self.reports[report.id] = report
            self.logger.info(f"Report added: {report.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding report: {str(e)}")
            return False
    
    def update_report(self, report_id: str, updates: Dict[str, Any]) -> bool:
        """Update compliance report"""
        try:
            report = self.reports.get(report_id)
            if not report:
                self.logger.error(f"Report {report_id} not found")
                return False
            
            # Update report attributes
            for key, value in updates.items():
                if hasattr(report, key):
                    setattr(report, key, value)
            
            report.updated_at = datetime.now()
            self.logger.info(f"Report updated: {report.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating report: {str(e)}")
            return False
    
    def get_standard_summary(self, standard_id: str) -> Dict[str, Any]:
        """Get standard compliance summary"""
        try:
            standard = self.standards.get(standard_id)
            if not standard:
                self.logger.error(f"Standard {standard_id} not found")
                return {}
            
            # Get standard requirements
            requirements = [req for req in self.requirements.values() if req.standard_id == standard_id]
            
            # Calculate compliance metrics
            total_requirements = len(requirements)
            compliant_requirements = len([req for req in requirements if req.status == ComplianceStatus.COMPLIANT])
            non_compliant_requirements = len([req for req in requirements if req.status == ComplianceStatus.NON_COMPLIANT])
            in_progress_requirements = len([req for req in requirements if req.status == ComplianceStatus.IN_PROGRESS])
            exempt_requirements = len([req for req in requirements if req.status == ComplianceStatus.EXEMPT])
            
            return {
                "standard": standard,
                "metrics": {
                    "total_requirements": total_requirements,
                    "compliant_requirements": compliant_requirements,
                    "non_compliant_requirements": non_compliant_requirements,
                    "in_progress_requirements": in_progress_requirements,
                    "exempt_requirements": exempt_requirements,
                    "compliance_rate": Decimal(str(compliant_requirements / total_requirements)) if total_requirements > 0 else Decimal('0')
                },
                "requirements": requirements,
                "recent_audits": self.get_recent_audits(standard_id),
                "recent_reports": self.get_recent_reports(standard_id)
            }
        except Exception as e:
            self.logger.error(f"Error getting standard summary: {str(e)}")
            return {}
    
    def get_recent_audits(self, standard_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent audits for standard"""
        try:
            audits = [audit for audit in self.audits.values() if audit.standard_id == standard_id]
            audits.sort(key=lambda x: x.end_date, reverse=True)
            return [{
                "id": audit.id,
                "name": audit.name,
                "start_date": audit.start_date.isoformat(),
                "end_date": audit.end_date.isoformat(),
                "status": audit.status,
                "findings_count": len(audit.findings) if audit.findings else 0
            } for audit in audits[:limit]]
        except Exception as e:
            self.logger.error(f"Error getting recent audits: {str(e)}")
            return []
    
    def get_recent_reports(self, standard_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent reports for standard"""
        try:
            reports = [report for report in self.reports.values() if report.standard_id == standard_id]
            reports.sort(key=lambda x: x.period_end, reverse=True)
            return [{
                "id": report.id,
                "name": report.name,
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "status": report.status
            } for report in reports[:limit]]
        except Exception as e:
            self.logger.error(f"Error getting recent reports: {str(e)}")
            return []
    
    def generate_compliance_report(self, standard_id: str, period_start: date, period_end: date) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            summary = self.get_standard_summary(standard_id)
            if not summary:
                return {}
            
            # Generate report content
            report = {
                "standard_id": standard_id,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "generated_at": datetime.now().isoformat(),
                "summary": summary,
                "requirements": self.get_requirements_details(standard_id),
                "audits": self.get_audits_details(standard_id, period_start, period_end),
                "findings": self.get_findings_summary(standard_id, period_start, period_end),
                "recommendations": self.generate_recommendations(standard_id)
            }
            
            # Save report
            report_file = os.path.join(os.path.dirname(__file__), 
                                     'compliance_reports', 
                                     f'report_{standard_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.json')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {str(e)}")
            return {}
    
    def get_requirements_details(self, standard_id: str) -> List[Dict[str, Any]]:
        """Get detailed requirements information"""
        try:
            requirements = [req for req in self.requirements.values() if req.standard_id == standard_id]
            return [{
                "id": req.id,
                "requirement_id": req.requirement_id,
                "description": req.description,
                "status": req.status.value,
                "evidence_count": len(req.evidence),
                "notes": req.notes
            } for req in requirements]
        except Exception as e:
            self.logger.error(f"Error getting requirements details: {str(e)}")
            return []
    
    def get_audits_details(self, standard_id: str, period_start: date, period_end: date) -> List[Dict[str, Any]]:
        """Get detailed audits information"""
        try:
            audits = [audit for audit in self.audits.values() 
                     if audit.standard_id == standard_id 
                     and period_start <= audit.start_date <= period_end]
            return [{
                "id": audit.id,
                "name": audit.name,
                "start_date": audit.start_date.isoformat(),
                "end_date": audit.end_date.isoformat(),
                "status": audit.status,
                "findings": audit.findings
            } for audit in audits]
        except Exception as e:
            self.logger.error(f"Error getting audits details: {str(e)}")
            return []
    
    def get_findings_summary(self, standard_id: str, period_start: date, period_end: date) -> Dict[str, Any]:
        """Get summary of findings"""
        try:
            audits = [audit for audit in self.audits.values() 
                     if audit.standard_id == standard_id 
                     and period_start <= audit.start_date <= period_end]
            
            findings = []
            for audit in audits:
                if audit.findings:
                    findings.extend(audit.findings)
            
            # Categorize findings by severity
            findings_by_severity = {
                "critical": len([f for f in findings if f.get("severity") == "critical"]),
                "high": len([f for f in findings if f.get("severity") == "high"]),
                "medium": len([f for f in findings if f.get("severity") == "medium"]),
                "low": len([f for f in findings if f.get("severity") == "low"])
            }
            
            return {
                "total_findings": len(findings),
                "findings_by_severity": findings_by_severity,
                "findings": findings
            }
        except Exception as e:
            self.logger.error(f"Error getting findings summary: {str(e)}")
            return {}
    
    def generate_recommendations(self, standard_id: str) -> List[Dict[str, Any]]:
        """Generate compliance recommendations"""
        try:
            recommendations = []
            summary = self.get_standard_summary(standard_id)
            
            if not summary:
                return recommendations
            
            metrics = summary.get("metrics", {})
            
            # Compliance rate recommendations
            if metrics.get("compliance_rate", Decimal('0')) < Decimal('0.8'):
                recommendations.append({
                    "type": "compliance",
                    "priority": "high",
                    "message": "Overall compliance rate is below 80%",
                    "action": "Review and address non-compliant requirements"
                })
            
            # Non-compliant requirements recommendations
            if metrics.get("non_compliant_requirements", 0) > 0:
                recommendations.append({
                    "type": "requirements",
                    "priority": "high",
                    "message": f"Found {metrics['non_compliant_requirements']} non-compliant requirements",
                    "action": "Review and implement corrective actions"
                })
            
            # In-progress requirements recommendations
            if metrics.get("in_progress_requirements", 0) > 0:
                recommendations.append({
                    "type": "progress",
                    "priority": "medium",
                    "message": f"Found {metrics['in_progress_requirements']} requirements in progress",
                    "action": "Monitor and support completion of in-progress requirements"
                })
            
            # Evidence recommendations
            requirements = summary.get("requirements", [])
            for req in requirements:
                if len(req.evidence) == 0:
                    recommendations.append({
                        "type": "evidence",
                        "priority": "medium",
                        "message": f"No evidence provided for requirement {req.requirement_id}",
                        "action": "Gather and upload required evidence"
                    })
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return [] 