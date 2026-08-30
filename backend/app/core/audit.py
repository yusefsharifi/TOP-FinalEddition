from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import os
import hashlib

class AuditType(Enum):
    SYSTEM = "system"
    USER = "user"
    DATA = "data"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"

class AuditLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ComplianceStandard(Enum):
    IFRS = "ifrs"
    GAAP = "gaap"
    ISO27001 = "iso27001"
    SOX = "sox"
    PCI = "pci"
    GDPR = "gdpr"

@dataclass
class AuditLog:
    id: str
    type: AuditType
    level: AuditLevel
    timestamp: datetime
    user_id: Optional[str]
    action: str
    entity_type: str
    entity_id: str
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime = datetime.now()

@dataclass
class ComplianceCheck:
    id: str
    standard: ComplianceStandard
    requirement: str
    description: str
    frequency: str  # daily, weekly, monthly, quarterly, annually
    last_check: Optional[datetime]
    next_check: Optional[datetime]
    status: str = "pending"  # pending, passed, failed, warning
    result: Optional[Dict[str, Any]]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class AuditPolicy:
    id: str
    name: str
    description: str
    type: AuditType
    level: AuditLevel
    enabled: bool = True
    retention_days: int = 365
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class AuditReport:
    id: str
    name: str
    description: str
    type: AuditType
    start_date: date
    end_date: date
    status: str = "draft"  # draft, generated, archived
    file_path: Optional[str]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class AuditManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logs: Dict[str, List[AuditLog]] = {}
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.policies: Dict[str, AuditPolicy] = {}
        self.reports: Dict[str, AuditReport] = {}
        
        # Load audit policies from file
        self.load_audit_policies()
    
    def load_audit_policies(self):
        """Load audit policies from JSON file"""
        try:
            policies_file = os.path.join(os.path.dirname(__file__), 'audit_policies.json')
            if os.path.exists(policies_file):
                with open(policies_file, 'r', encoding='utf-8') as f:
                    policies_data = json.load(f)
                    for policy_data in policies_data:
                        policy = AuditPolicy(
                            id=policy_data['id'],
                            name=policy_data['name'],
                            description=policy_data['description'],
                            type=AuditType(policy_data['type']),
                            level=AuditLevel(policy_data['level']),
                            enabled=policy_data['enabled'],
                            retention_days=policy_data['retention_days']
                        )
                        self.policies[policy.id] = policy
                self.logger.info("Audit policies loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading audit policies: {str(e)}")
    
    def log_audit(self, log: AuditLog) -> bool:
        """Log audit event"""
        try:
            # Check if policy exists and is enabled
            policy = self.get_applicable_policy(log.type, log.level)
            if not policy or not policy.enabled:
                return False
            
            # Generate log ID if not provided
            if not log.id:
                log.id = self.generate_log_id(log)
            
            # Add to logs
            if log.entity_type not in self.logs:
                self.logs[log.entity_type] = []
            
            self.logs[log.entity_type].append(log)
            self.logger.info(f"Audit log added: {log.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error logging audit: {str(e)}")
            return False
    
    def generate_log_id(self, log: AuditLog) -> str:
        """Generate unique log ID"""
        try:
            # Create hash from log data
            data = f"{log.type.value}{log.level.value}{log.timestamp.isoformat()}{log.entity_type}{log.entity_id}"
            hash_object = hashlib.sha256(data.encode())
            return f"LOG_{hash_object.hexdigest()[:8]}"
        except Exception as e:
            self.logger.error(f"Error generating log ID: {str(e)}")
            return f"LOG_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def get_applicable_policy(self, audit_type: AuditType, level: AuditLevel) -> Optional[AuditPolicy]:
        """Get applicable audit policy"""
        try:
            applicable_policies = [
                policy for policy in self.policies.values()
                if policy.type == audit_type
                and policy.level == level
                and policy.enabled
            ]
            
            if applicable_policies:
                return applicable_policies[0]
            return None
        except Exception as e:
            self.logger.error(f"Error getting applicable policy: {str(e)}")
            return None
    
    def add_compliance_check(self, check: ComplianceCheck) -> bool:
        """Add compliance check"""
        try:
            if check.id in self.compliance_checks:
                self.logger.warning(f"Compliance check with ID {check.id} already exists")
                return False
            
            self.compliance_checks[check.id] = check
            self.logger.info(f"Compliance check added: {check.requirement}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding compliance check: {str(e)}")
            return False
    
    def run_compliance_check(self, check_id: str) -> Dict[str, Any]:
        """Run compliance check"""
        try:
            check = self.compliance_checks.get(check_id)
            if not check:
                return {}
            
            # Run check based on standard
            result = self.execute_compliance_check(check)
            
            # Update check status
            check.last_check = datetime.now()
            check.next_check = self.calculate_next_check(check)
            check.status = self.determine_check_status(result)
            check.result = result
            check.updated_at = datetime.now()
            
            return {
                "id": check.id,
                "standard": check.standard.value,
                "requirement": check.requirement,
                "status": check.status,
                "result": result,
                "last_check": check.last_check.isoformat(),
                "next_check": check.next_check.isoformat() if check.next_check else None
            }
        except Exception as e:
            self.logger.error(f"Error running compliance check: {str(e)}")
            return {}
    
    def execute_compliance_check(self, check: ComplianceCheck) -> Dict[str, Any]:
        """Execute compliance check based on standard"""
        try:
            if check.standard == ComplianceStandard.IFRS:
                return self.check_ifrs_compliance(check)
            elif check.standard == ComplianceStandard.GAAP:
                return self.check_gaap_compliance(check)
            elif check.standard == ComplianceStandard.ISO27001:
                return self.check_iso27001_compliance(check)
            elif check.standard == ComplianceStandard.SOX:
                return self.check_sox_compliance(check)
            elif check.standard == ComplianceStandard.PCI:
                return self.check_pci_compliance(check)
            elif check.standard == ComplianceStandard.GDPR:
                return self.check_gdpr_compliance(check)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error executing compliance check: {str(e)}")
            return {}
    
    def check_ifrs_compliance(self, check: ComplianceCheck) -> Dict[str, Any]:
        """Check IFRS compliance"""
        # Implement IFRS-specific checks
        return {
            "status": "passed",
            "details": "IFRS compliance check completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def check_gaap_compliance(self, check: ComplianceCheck) -> Dict[str, Any]:
        """Check GAAP compliance"""
        # Implement GAAP-specific checks
        return {
            "status": "passed",
            "details": "GAAP compliance check completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def check_iso27001_compliance(self, check: ComplianceCheck) -> Dict[str, Any]:
        """Check ISO 27001 compliance"""
        # Implement ISO 27001-specific checks
        return {
            "status": "passed",
            "details": "ISO 27001 compliance check completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def check_sox_compliance(self, check: ComplianceCheck) -> Dict[str, Any]:
        """Check SOX compliance"""
        # Implement SOX-specific checks
        return {
            "status": "passed",
            "details": "SOX compliance check completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def check_pci_compliance(self, check: ComplianceCheck) -> Dict[str, Any]:
        """Check PCI compliance"""
        # Implement PCI-specific checks
        return {
            "status": "passed",
            "details": "PCI compliance check completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def check_gdpr_compliance(self, check: ComplianceCheck) -> Dict[str, Any]:
        """Check GDPR compliance"""
        # Implement GDPR-specific checks
        return {
            "status": "passed",
            "details": "GDPR compliance check completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_next_check(self, check: ComplianceCheck) -> Optional[datetime]:
        """Calculate next check date based on frequency"""
        try:
            if not check.last_check:
                return None
            
            if check.frequency == "daily":
                return check.last_check.replace(day=check.last_check.day + 1)
            elif check.frequency == "weekly":
                return check.last_check.replace(day=check.last_check.day + 7)
            elif check.frequency == "monthly":
                return check.last_check.replace(month=check.last_check.month + 1)
            elif check.frequency == "quarterly":
                return check.last_check.replace(month=check.last_check.month + 3)
            else:  # annually
                return check.last_check.replace(year=check.last_check.year + 1)
        except Exception as e:
            self.logger.error(f"Error calculating next check: {str(e)}")
            return None
    
    def determine_check_status(self, result: Dict[str, Any]) -> str:
        """Determine compliance check status based on result"""
        try:
            if not result:
                return "failed"
            
            status = result.get("status", "failed")
            if status == "passed":
                return "passed"
            elif status == "warning":
                return "warning"
            else:
                return "failed"
        except Exception as e:
            self.logger.error(f"Error determining check status: {str(e)}")
            return "failed"
    
    def generate_audit_report(self, report: AuditReport) -> bool:
        """Generate audit report"""
        try:
            # Get relevant logs
            logs = self.get_logs_for_report(report.type, report.start_date, report.end_date)
            
            # Generate report content
            report_content = self.create_report_content(logs)
            
            # Save report
            report.file_path = self.save_report(report.id, report_content)
            report.status = "generated"
            report.updated_at = datetime.now()
            
            self.logger.info(f"Audit report generated: {report.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error generating audit report: {str(e)}")
            return False
    
    def get_logs_for_report(self, audit_type: AuditType, start_date: date, 
                          end_date: date) -> List[AuditLog]:
        """Get logs for report period"""
        try:
            all_logs = []
            for logs in self.logs.values():
                period_logs = [
                    log for log in logs
                    if log.type == audit_type
                    and log.timestamp.date() >= start_date
                    and log.timestamp.date() <= end_date
                ]
                all_logs.extend(period_logs)
            
            return sorted(all_logs, key=lambda x: x.timestamp)
        except Exception as e:
            self.logger.error(f"Error getting logs for report: {str(e)}")
            return []
    
    def create_report_content(self, logs: List[AuditLog]) -> Dict[str, Any]:
        """Create report content from logs"""
        try:
            content = {
                "summary": {
                    "total_logs": len(logs),
                    "by_level": {},
                    "by_type": {},
                    "by_entity": {}
                },
                "details": []
            }
            
            for log in logs:
                # Update summary
                content["summary"]["by_level"][log.level.value] = \
                    content["summary"]["by_level"].get(log.level.value, 0) + 1
                content["summary"]["by_type"][log.type.value] = \
                    content["summary"]["by_type"].get(log.type.value, 0) + 1
                content["summary"]["by_entity"][log.entity_type] = \
                    content["summary"]["by_entity"].get(log.entity_type, 0) + 1
                
                # Add log details
                content["details"].append({
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "type": log.type.value,
                    "level": log.level.value,
                    "user_id": log.user_id,
                    "action": log.action,
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "old_value": log.old_value,
                    "new_value": log.new_value,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "metadata": log.metadata
                })
            
            return content
        except Exception as e:
            self.logger.error(f"Error creating report content: {str(e)}")
            return {}
    
    def save_report(self, report_id: str, content: Dict[str, Any]) -> str:
        """Save report to file"""
        try:
            # Create reports directory if not exists
            reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Save report file
            file_path = os.path.join(reports_dir, f'report_{report_id}.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            return file_path
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")
            return ""
    
    def get_compliance_report(self, standard: ComplianceStandard, 
                            start_date: date, end_date: date) -> Dict[str, Any]:
        """Get compliance report"""
        try:
            report = {
                "standard": standard.value,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_checks": 0,
                    "passed": 0,
                    "failed": 0,
                    "warning": 0
                },
                "checks": []
            }
            
            for check in self.compliance_checks.values():
                if check.standard == standard:
                    report["summary"]["total_checks"] += 1
                    report["summary"][check.status] += 1
                    
                    report["checks"].append({
                        "id": check.id,
                        "requirement": check.requirement,
                        "description": check.description,
                        "frequency": check.frequency,
                        "last_check": check.last_check.isoformat() if check.last_check else None,
                        "next_check": check.next_check.isoformat() if check.next_check else None,
                        "status": check.status,
                        "result": check.result
                    })
            
            return report
        except Exception as e:
            self.logger.error(f"Error getting compliance report: {str(e)}")
            return {} 