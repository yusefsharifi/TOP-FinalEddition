from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import networkx as nx
import matplotlib.pyplot as plt
import random

class ControlType(Enum):
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    DIRECTIVE = "directive"

class ControlCategory(Enum):
    AUTHORIZATION = "authorization"
    SEGREGATION = "segregation"
    DOCUMENTATION = "documentation"
    PHYSICAL = "physical"
    IT = "it"
    MONITORING = "monitoring"

class ControlStatus(Enum):
    EFFECTIVE = "effective"
    PARTIALLY_EFFECTIVE = "partially_effective"
    INEFFECTIVE = "ineffective"
    NOT_IMPLEMENTED = "not_implemented"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TestType(Enum):
    PLANNED = "planned"
    RANDOM = "random"
    CONTINUOUS = "continuous"

@dataclass
class Risk:
    id: str
    name: str
    description: str
    category: str
    probability: Decimal  # 0-1
    impact: Decimal  # 0-1
    level: RiskLevel
    controls: List[str]  # List of control IDs
    owner: str
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Control:
    id: str
    name: str
    type: ControlType
    category: ControlCategory
    description: str
    risk_level: RiskLevel
    status: ControlStatus = ControlStatus.NOT_IMPLEMENTED
    owner: str
    frequency: str  # daily, weekly, monthly, quarterly, annually
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ControlTest:
    id: str
    control_id: str
    test_date: date
    tester: str
    result: bool
    findings: str = ""
    evidence: str = ""  # file path or reference
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ControlViolation:
    id: str
    control_id: str
    violation_date: date
    description: str
    impact: str
    reported_by: str
    status: str = "open"  # open, in_progress, resolved, closed
    resolution: str = ""
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ControlDocument:
    id: str
    control_id: str
    title: str
    description: str
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    uploaded_by: str
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ProcessNode:
    id: str
    name: str
    type: str  # process, control, decision
    description: str = ""
    owner: str = ""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ProcessEdge:
    id: str
    source_id: str
    target_id: str
    type: str  # flow, control, data
    description: str = ""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class InternalControlManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.controls: Dict[str, Control] = {}
        self.risks: Dict[str, Risk] = {}
        self.tests: Dict[str, List[ControlTest]] = {}
        self.violations: Dict[str, List[ControlViolation]] = {}
        self.documents: Dict[str, List[ControlDocument]] = {}
        self.process_nodes: Dict[str, ProcessNode] = {}
        self.process_edges: Dict[str, List[ProcessEdge]] = {}
    
    def add_risk(self, risk: Risk) -> bool:
        """Add risk"""
        try:
            if risk.id in self.risks:
                self.logger.warning(f"Risk with ID {risk.id} already exists")
                return False
            
            self.risks[risk.id] = risk
            self.logger.info(f"Risk added: {risk.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding risk: {str(e)}")
            return False
    
    def assess_risk(self, risk_id: str) -> Dict[str, Any]:
        """Assess risk level based on probability and impact"""
        try:
            risk = self.risks.get(risk_id)
            if not risk:
                return {}
            
            # Calculate risk score
            risk_score = risk.probability * risk.impact
            
            # Determine risk level
            if risk_score >= Decimal('0.75'):
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= Decimal('0.5'):
                risk_level = RiskLevel.HIGH
            elif risk_score >= Decimal('0.25'):
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Update risk level
            risk.level = risk_level
            risk.updated_at = datetime.now()
            
            return {
                "id": risk.id,
                "name": risk.name,
                "probability": risk.probability,
                "impact": risk.impact,
                "risk_score": risk_score,
                "risk_level": risk_level.value,
                "controls": risk.controls
            }
        except Exception as e:
            self.logger.error(f"Error assessing risk: {str(e)}")
            return {}
    
    def add_process_node(self, node: ProcessNode) -> bool:
        """Add process node"""
        try:
            if node.id in self.process_nodes:
                self.logger.warning(f"Process node with ID {node.id} already exists")
                return False
            
            self.process_nodes[node.id] = node
            self.process_edges[node.id] = []
            self.logger.info(f"Process node added: {node.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding process node: {str(e)}")
            return False
    
    def add_process_edge(self, edge: ProcessEdge) -> bool:
        """Add process edge"""
        try:
            if edge.source_id not in self.process_nodes:
                self.logger.error(f"Source node {edge.source_id} not found")
                return False
            
            if edge.target_id not in self.process_nodes:
                self.logger.error(f"Target node {edge.target_id} not found")
                return False
            
            if edge.id in [e.id for e in self.process_edges.get(edge.source_id, [])]:
                self.logger.warning(f"Edge with ID {edge.id} already exists")
                return False
            
            self.process_edges[edge.source_id].append(edge)
            self.logger.info(f"Process edge added from {edge.source_id} to {edge.target_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding process edge: {str(e)}")
            return False
    
    def generate_control_map(self, output_path: str) -> bool:
        """Generate control map visualization"""
        try:
            # Create directed graph
            G = nx.DiGraph()
            
            # Add nodes
            for node_id, node in self.process_nodes.items():
                G.add_node(node_id, 
                          name=node.name,
                          type=node.type,
                          description=node.description)
            
            # Add edges
            for source_id, edges in self.process_edges.items():
                for edge in edges:
                    G.add_edge(edge.source_id,
                             edge.target_id,
                             type=edge.type,
                             description=edge.description)
            
            # Create visualization
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos,
                                 node_color='lightblue',
                                 node_size=2000)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos,
                                 edge_color='gray',
                                 arrows=True)
            
            # Add labels
            labels = nx.get_node_attributes(G, 'name')
            nx.draw_networkx_labels(G, pos, labels)
            
            # Save the plot
            plt.savefig(output_path)
            plt.close()
            
            self.logger.info(f"Control map generated: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error generating control map: {str(e)}")
            return False
    
    def schedule_test(self, control_id: str, test_type: TestType, 
                     frequency: str) -> bool:
        """Schedule control test"""
        try:
            if control_id not in self.controls:
                self.logger.error(f"Control {control_id} not found")
                return False
            
            # Create test schedule based on type and frequency
            if test_type == TestType.PLANNED:
                # Schedule specific dates
                test_dates = self.generate_test_dates(frequency)
            elif test_type == TestType.RANDOM:
                # Schedule random dates within the period
                test_dates = self.generate_random_test_dates(frequency)
            else:  # CONTINUOUS
                # Schedule continuous monitoring
                test_dates = self.generate_continuous_test_dates(frequency)
            
            # Create test records
            for test_date in test_dates:
                test = ControlTest(
                    id=f"TEST_{control_id}_{test_date.strftime('%Y%m%d')}",
                    control_id=control_id,
                    test_date=test_date,
                    tester="system",
                    result=False  # To be updated after test
                )
                
                if control_id not in self.tests:
                    self.tests[control_id] = []
                
                self.tests[control_id].append(test)
            
            self.logger.info(f"Tests scheduled for control {control_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error scheduling tests: {str(e)}")
            return False
    
    def generate_test_dates(self, frequency: str) -> List[date]:
        """Generate test dates based on frequency"""
        today = date.today()
        dates = []
        
        if frequency == "daily":
            for i in range(30):
                dates.append(today.replace(day=today.day + i))
        elif frequency == "weekly":
            for i in range(4):
                dates.append(today.replace(day=today.day + i * 7))
        elif frequency == "monthly":
            for i in range(12):
                dates.append(today.replace(month=today.month + i))
        elif frequency == "quarterly":
            for i in range(4):
                dates.append(today.replace(month=today.month + i * 3))
        else:  # annually
            for i in range(5):
                dates.append(today.replace(year=today.year + i))
        
        return dates
    
    def generate_random_test_dates(self, frequency: str) -> List[date]:
        """Generate random test dates within the period"""
        today = date.today()
        dates = []
        
        if frequency == "daily":
            num_tests = 5
            for _ in range(num_tests):
                random_days = random.randint(0, 30)
                dates.append(today.replace(day=today.day + random_days))
        elif frequency == "weekly":
            num_tests = 2
            for _ in range(num_tests):
                random_weeks = random.randint(0, 4)
                dates.append(today.replace(day=today.day + random_weeks * 7))
        elif frequency == "monthly":
            num_tests = 3
            for _ in range(num_tests):
                random_months = random.randint(0, 12)
                dates.append(today.replace(month=today.month + random_months))
        elif frequency == "quarterly":
            num_tests = 2
            for _ in range(num_tests):
                random_quarters = random.randint(0, 4)
                dates.append(today.replace(month=today.month + random_quarters * 3))
        else:  # annually
            num_tests = 2
            for _ in range(num_tests):
                random_years = random.randint(0, 5)
                dates.append(today.replace(year=today.year + random_years))
        
        return sorted(dates)
    
    def generate_continuous_test_dates(self, frequency: str) -> List[date]:
        """Generate continuous test dates"""
        today = date.today()
        dates = []
        
        if frequency == "daily":
            # Test every day
            for i in range(365):
                dates.append(today.replace(day=today.day + i))
        elif frequency == "weekly":
            # Test every week
            for i in range(52):
                dates.append(today.replace(day=today.day + i * 7))
        elif frequency == "monthly":
            # Test every month
            for i in range(12):
                dates.append(today.replace(month=today.month + i))
        elif frequency == "quarterly":
            # Test every quarter
            for i in range(4):
                dates.append(today.replace(month=today.month + i * 3))
        else:  # annually
            # Test every year
            for i in range(5):
                dates.append(today.replace(year=today.year + i))
        
        return dates
    
    def get_risk_report(self) -> List[Dict[str, Any]]:
        """Get risk assessment report"""
        try:
            report = []
            for risk in self.risks.values():
                report.append({
                    "id": risk.id,
                    "name": risk.name,
                    "category": risk.category,
                    "probability": risk.probability,
                    "impact": risk.impact,
                    "level": risk.level.value,
                    "controls": risk.controls,
                    "owner": risk.owner,
                    "is_active": risk.is_active
                })
            
            return sorted(report, key=lambda x: x["level"], reverse=True)
        except Exception as e:
            self.logger.error(f"Error getting risk report: {str(e)}")
            return []
    
    def get_control_map_report(self) -> Dict[str, Any]:
        """Get control map report"""
        try:
            report = {
                "nodes": [],
                "edges": []
            }
            
            # Add nodes
            for node_id, node in self.process_nodes.items():
                report["nodes"].append({
                    "id": node_id,
                    "name": node.name,
                    "type": node.type,
                    "description": node.description,
                    "owner": node.owner
                })
            
            # Add edges
            for source_id, edges in self.process_edges.items():
                for edge in edges:
                    report["edges"].append({
                        "id": edge.id,
                        "source": edge.source_id,
                        "target": edge.target_id,
                        "type": edge.type,
                        "description": edge.description
                    })
            
            return report
        except Exception as e:
            self.logger.error(f"Error getting control map report: {str(e)}")
            return {"nodes": [], "edges": []}
    
    def get_test_schedule_report(self) -> List[Dict[str, Any]]:
        """Get test schedule report"""
        try:
            report = []
            for control_id, tests in self.tests.items():
                control = self.controls[control_id]
                report.append({
                    "control_id": control_id,
                    "control_name": control.name,
                    "control_type": control.type.value,
                    "test_count": len(tests),
                    "upcoming_tests": [{
                        "id": t.id,
                        "date": t.test_date.isoformat(),
                        "tester": t.tester,
                        "result": t.result
                    } for t in sorted(tests, key=lambda x: x.test_date)[:5]]
                })
            
            return sorted(report, key=lambda x: x["control_name"])
        except Exception as e:
            self.logger.error(f"Error getting test schedule report: {str(e)}")
            return []
    
    def add_control(self, control: Control) -> bool:
        """Add internal control"""
        try:
            if control.id in self.controls:
                self.logger.warning(f"Control with ID {control.id} already exists")
                return False
            
            self.controls[control.id] = control
            self.logger.info(f"Internal control added: {control.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding internal control: {str(e)}")
            return False
    
    def add_test(self, test: ControlTest) -> bool:
        """Add control test"""
        try:
            if test.control_id not in self.controls:
                self.logger.error(f"Control {test.control_id} not found")
                return False
            
            if test.id in [t.id for t in self.tests.get(test.control_id, [])]:
                self.logger.warning(f"Test with ID {test.id} already exists")
                return False
            
            if test.control_id not in self.tests:
                self.tests[test.control_id] = []
            
            self.tests[test.control_id].append(test)
            self.logger.info(f"Control test added for {test.control_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding control test: {str(e)}")
            return False
    
    def add_violation(self, violation: ControlViolation) -> bool:
        """Add control violation"""
        try:
            if violation.control_id not in self.controls:
                self.logger.error(f"Control {violation.control_id} not found")
                return False
            
            if violation.id in [v.id for v in self.violations.get(violation.control_id, [])]:
                self.logger.warning(f"Violation with ID {violation.id} already exists")
                return False
            
            if violation.control_id not in self.violations:
                self.violations[violation.control_id] = []
            
            self.violations[violation.control_id].append(violation)
            self.logger.info(f"Control violation added for {violation.control_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding control violation: {str(e)}")
            return False
    
    def resolve_violation(self, violation_id: str, control_id: str, 
                         resolution: str, resolved_by: str) -> bool:
        """Resolve control violation"""
        try:
            violation = next((v for v in self.violations.get(control_id, []) 
                            if v.id == violation_id), None)
            if not violation:
                return False
            
            if violation.status == "closed":
                self.logger.warning(f"Violation {violation_id} is already closed")
                return False
            
            violation.status = "resolved"
            violation.resolution = resolution
            violation.resolved_by = resolved_by
            violation.resolved_at = datetime.now()
            violation.updated_at = datetime.now()
            
            self.logger.info(f"Control violation {violation_id} resolved")
            return True
        except Exception as e:
            self.logger.error(f"Error resolving control violation: {str(e)}")
            return False
    
    def add_document(self, document: ControlDocument) -> bool:
        """Add control document"""
        try:
            if document.control_id not in self.controls:
                self.logger.error(f"Control {document.control_id} not found")
                return False
            
            if document.id in [d.id for d in self.documents.get(document.control_id, [])]:
                self.logger.warning(f"Document with ID {document.id} already exists")
                return False
            
            if document.control_id not in self.documents:
                self.documents[document.control_id] = []
            
            self.documents[document.control_id].append(document)
            self.logger.info(f"Control document added for {document.control_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding control document: {str(e)}")
            return False
    
    def get_control_summary(self, control_id: str) -> Dict[str, Any]:
        """Get control summary"""
        try:
            control = self.controls.get(control_id)
            if not control:
                return {}
            
            tests = self.tests.get(control_id, [])
            violations = self.violations.get(control_id, [])
            documents = self.documents.get(control_id, [])
            
            recent_tests = sorted(tests, key=lambda x: x.test_date, reverse=True)[:3]
            open_violations = [v for v in violations if v.status != "closed"]
            
            return {
                "id": control.id,
                "name": control.name,
                "type": control.type.value,
                "category": control.category.value,
                "description": control.description,
                "risk_level": control.risk_level.value,
                "status": control.status.value,
                "owner": control.owner,
                "frequency": control.frequency,
                "is_active": control.is_active,
                "test_count": len(tests),
                "violation_count": len(violations),
                "open_violation_count": len(open_violations),
                "document_count": len(documents),
                "recent_tests": [{
                    "date": t.test_date.isoformat(),
                    "tester": t.tester,
                    "result": t.result
                } for t in recent_tests],
                "created_at": control.created_at.isoformat(),
                "updated_at": control.updated_at.isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting control summary: {str(e)}")
            return {}
    
    def get_violation_report(self, start_date: date, 
                           end_date: date) -> List[Dict[str, Any]]:
        """Get control violation report"""
        try:
            report = []
            for control_id, violations in self.violations.items():
                control = self.controls[control_id]
                for violation in violations:
                    if violation.violation_date < start_date or violation.violation_date > end_date:
                        continue
                    
                    report.append({
                        "id": violation.id,
                        "control_id": violation.control_id,
                        "control_name": control.name,
                        "control_type": control.type.value,
                        "violation_date": violation.violation_date.isoformat(),
                        "description": violation.description,
                        "impact": violation.impact,
                        "reported_by": violation.reported_by,
                        "status": violation.status,
                        "resolution": violation.resolution,
                        "resolved_by": violation.resolved_by,
                        "resolved_at": violation.resolved_at.isoformat() if violation.resolved_at else None
                    })
            
            return sorted(report, key=lambda x: x["violation_date"], reverse=True)
        except Exception as e:
            self.logger.error(f"Error getting violation report: {str(e)}")
            return [] 