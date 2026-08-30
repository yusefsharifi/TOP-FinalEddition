from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship

class CompensationType(Enum):
    BASE_SALARY = "base_salary"
    BONUS = "bonus"
    COMMISSION = "commission"
    STOCK_OPTIONS = "stock_options"
    PROFIT_SHARING = "profit_sharing"
    ALLOWANCE = "allowance"
    REIMBURSEMENT = "reimbursement"

class BenefitType(Enum):
    HEALTH_INSURANCE = "health_insurance"
    DENTAL_INSURANCE = "dental_insurance"
    VISION_INSURANCE = "vision_insurance"
    LIFE_INSURANCE = "life_insurance"
    DISABILITY_INSURANCE = "disability_insurance"
    RETIREMENT_PLAN = "retirement_plan"
    PAID_TIME_OFF = "paid_time_off"
    FLEXIBLE_SPENDING = "flexible_spending"
    EMPLOYEE_ASSISTANCE = "employee_assistance"
    WELLNESS_PROGRAM = "wellness_program"
    OTHER = "other"

class IncentiveType(Enum):
    PERFORMANCE_BONUS = "performance_bonus"
    REFERRAL_BONUS = "referral_bonus"
    RETENTION_BONUS = "retention_bonus"
    SIGN_ON_BONUS = "sign_on_bonus"
    RECOGNITION_AWARD = "recognition_award"
    SPOT_BONUS = "spot_bonus"
    PROJECT_BONUS = "project_bonus"
    OTHER = "other"

class Compensation(BaseModel):
    id: int
    employee_id: int
    type: CompensationType
    amount: float
    currency: str
    effective_date: date
    end_date: Optional[date] = None
    frequency: str
    created_at: datetime
    updated_at: datetime
    notes: List[Dict[str, Any]] = []
    adjustments: List[Dict[str, Any]] = []
    deductions: List[Dict[str, Any]] = []
    tax_info: Dict[str, Any] = {}
    documents: List[Dict[str, Any]] = []

class Benefit(BaseModel):
    id: int
    employee_id: int
    type: BenefitType
    provider: str
    plan_name: str
    coverage_level: str
    start_date: date
    end_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    cost: float
    employee_contribution: float
    employer_contribution: float
    dependents: List[Dict[str, Any]] = []
    documents: List[Dict[str, Any]] = []
    claims: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []

class Incentive(BaseModel):
    id: int
    employee_id: int
    type: IncentiveType
    amount: float
    currency: str
    awarded_date: date
    effective_date: date
    created_at: datetime
    updated_at: datetime
    reason: str
    performance_period: Optional[str] = None
    approval_status: str
    approved_by: Optional[int] = None
    approval_date: Optional[datetime] = None
    documents: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []

class RewardsManagementSystem:
    def __init__(self):
        self.compensations: Dict[int, Compensation] = {}
        self.benefits: Dict[int, Benefit] = {}
        self.incentives: Dict[int, Incentive] = {}
        self.notifications: Dict[int, List[Dict[str, Any]]] = {}

    def create_compensation(self, employee_id: int, comp_type: CompensationType,
                          amount: float, currency: str, effective_date: date,
                          frequency: str) -> int:
        """Create a new compensation record"""
        comp_id = len(self.compensations) + 1
        compensation = Compensation(
            id=comp_id,
            employee_id=employee_id,
            type=comp_type,
            amount=amount,
            currency=currency,
            effective_date=effective_date,
            frequency=frequency,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.compensations[comp_id] = compensation
        self._notify_employee(employee_id, "new_compensation")
        return comp_id

    def update_compensation(self, comp_id: int, updates: Dict[str, Any]) -> bool:
        """Update compensation details"""
        if comp_id not in self.compensations:
            return False
        
        compensation = self.compensations[comp_id]
        for key, value in updates.items():
            if hasattr(compensation, key):
                setattr(compensation, key, value)
        
        compensation.updated_at = datetime.now()
        return True

    def add_compensation_adjustment(self, comp_id: int, amount: float,
                                  reason: str, effective_date: date) -> bool:
        """Add a compensation adjustment"""
        if comp_id not in self.compensations:
            return False
        
        compensation = self.compensations[comp_id]
        adjustment = {
            "amount": amount,
            "reason": reason,
            "effective_date": effective_date,
            "added_at": datetime.now()
        }
        
        compensation.adjustments.append(adjustment)
        compensation.updated_at = datetime.now()
        return True

    def create_benefit(self, employee_id: int, benefit_type: BenefitType,
                      provider: str, plan_name: str, coverage_level: str,
                      start_date: date, cost: float,
                      employee_contribution: float) -> int:
        """Create a new benefit record"""
        benefit_id = len(self.benefits) + 1
        benefit = Benefit(
            id=benefit_id,
            employee_id=employee_id,
            type=benefit_type,
            provider=provider,
            plan_name=plan_name,
            coverage_level=coverage_level,
            start_date=start_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            cost=cost,
            employee_contribution=employee_contribution,
            employer_contribution=cost - employee_contribution
        )
        self.benefits[benefit_id] = benefit
        self._notify_employee(employee_id, "new_benefit")
        return benefit_id

    def add_benefit_dependent(self, benefit_id: int, name: str,
                            relationship: str, date_of_birth: date) -> bool:
        """Add a dependent to a benefit"""
        if benefit_id not in self.benefits:
            return False
        
        benefit = self.benefits[benefit_id]
        dependent = {
            "name": name,
            "relationship": relationship,
            "date_of_birth": date_of_birth,
            "added_at": datetime.now()
        }
        
        benefit.dependents.append(dependent)
        benefit.updated_at = datetime.now()
        return True

    def create_incentive(self, employee_id: int, incentive_type: IncentiveType,
                        amount: float, currency: str, awarded_date: date,
                        effective_date: date, reason: str) -> int:
        """Create a new incentive record"""
        incentive_id = len(self.incentives) + 1
        incentive = Incentive(
            id=incentive_id,
            employee_id=employee_id,
            type=incentive_type,
            amount=amount,
            currency=currency,
            awarded_date=awarded_date,
            effective_date=effective_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            reason=reason,
            approval_status="pending"
        )
        self.incentives[incentive_id] = incentive
        self._notify_employee(employee_id, "new_incentive")
        return incentive_id

    def approve_incentive(self, incentive_id: int, approved_by: int) -> bool:
        """Approve an incentive"""
        if incentive_id not in self.incentives:
            return False
        
        incentive = self.incentives[incentive_id]
        incentive.approval_status = "approved"
        incentive.approved_by = approved_by
        incentive.approval_date = datetime.now()
        incentive.updated_at = datetime.now()
        
        self._notify_employee(incentive.employee_id, "incentive_approved")
        return True

    def get_rewards_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics for rewards management system"""
        return {
            "compensation_metrics": {
                "total_compensation": self._calculate_total_compensation(),
                "by_type": self._get_compensation_type_distribution(),
                "adjustments": self._get_compensation_adjustments(),
                "market_comparison": self._get_market_comparison()
            },
            "benefits_metrics": {
                "total_benefits": self._calculate_total_benefits(),
                "enrollment_distribution": self._get_benefit_enrollment_distribution(),
                "cost_analysis": self._get_benefit_cost_analysis(),
                "utilization": self._get_benefit_utilization()
            },
            "incentives_metrics": {
                "total_incentives": self._calculate_total_incentives(),
                "by_type": self._get_incentive_type_distribution(),
                "approval_rate": self._calculate_incentive_approval_rate(),
                "cost_impact": self._get_incentive_cost_impact()
            }
        }

    def _calculate_total_compensation(self) -> Dict[str, float]:
        """Calculate total compensation by type"""
        totals = {comp_type.value: 0.0 for comp_type in CompensationType}
        
        for compensation in self.compensations.values():
            if compensation.end_date is None or compensation.end_date >= date.today():
                totals[compensation.type.value] += compensation.amount
        
        return totals

    def _get_compensation_type_distribution(self) -> Dict[str, Dict[str, Any]]:
        """Get distribution of compensation types"""
        distribution = {}
        for comp_type in CompensationType:
            comps = [c for c in self.compensations.values() 
                    if c.type == comp_type]
            if comps:
                distribution[comp_type.value] = {
                    "count": len(comps),
                    "total_amount": sum(c.amount for c in comps),
                    "average_amount": sum(c.amount for c in comps) / len(comps)
                }
        return distribution

    def _get_compensation_adjustments(self) -> List[Dict[str, Any]]:
        """Get compensation adjustments"""
        adjustments = []
        for compensation in self.compensations.values():
            for adjustment in compensation.adjustments:
                adjustments.append({
                    "employee_id": compensation.employee_id,
                    "compensation_type": compensation.type.value,
                    "amount": adjustment["amount"],
                    "reason": adjustment["reason"],
                    "effective_date": adjustment["effective_date"]
                })
        return sorted(adjustments, key=lambda x: x["effective_date"], reverse=True)

    def _get_market_comparison(self) -> Dict[str, Any]:
        """Get market comparison data"""
        # This would typically integrate with external market data
        return {
            "base_salary": {
                "market_median": 0.0,
                "market_75th_percentile": 0.0,
                "company_median": 0.0,
                "comparison": "neutral"
            },
            "total_compensation": {
                "market_median": 0.0,
                "market_75th_percentile": 0.0,
                "company_median": 0.0,
                "comparison": "neutral"
            }
        }

    def _calculate_total_benefits(self) -> Dict[str, float]:
        """Calculate total benefits cost"""
        return {
            "total_cost": sum(b.cost for b in self.benefits.values()),
            "employee_contribution": sum(b.employee_contribution for b in self.benefits.values()),
            "employer_contribution": sum(b.employer_contribution for b in self.benefits.values())
        }

    def _get_benefit_enrollment_distribution(self) -> Dict[str, int]:
        """Get distribution of benefit enrollments"""
        distribution = {benefit_type.value: 0 for benefit_type in BenefitType}
        for benefit in self.benefits.values():
            distribution[benefit.type.value] += 1
        return distribution

    def _get_benefit_cost_analysis(self) -> Dict[str, Dict[str, float]]:
        """Get benefit cost analysis"""
        analysis = {}
        for benefit_type in BenefitType:
            benefits = [b for b in self.benefits.values() 
                       if b.type == benefit_type]
            if benefits:
                analysis[benefit_type.value] = {
                    "total_cost": sum(b.cost for b in benefits),
                    "employee_contribution": sum(b.employee_contribution for b in benefits),
                    "employer_contribution": sum(b.employer_contribution for b in benefits),
                    "average_cost": sum(b.cost for b in benefits) / len(benefits)
                }
        return analysis

    def _get_benefit_utilization(self) -> Dict[str, Dict[str, Any]]:
        """Get benefit utilization data"""
        utilization = {}
        for benefit_type in BenefitType:
            benefits = [b for b in self.benefits.values() 
                       if b.type == benefit_type]
            if benefits:
                utilization[benefit_type.value] = {
                    "total_enrolled": len(benefits),
                    "total_claims": sum(len(b.claims) for b in benefits),
                    "average_claims_per_enrollee": sum(len(b.claims) for b in benefits) / len(benefits)
                }
        return utilization

    def _calculate_total_incentives(self) -> Dict[str, float]:
        """Calculate total incentives"""
        return {
            "total_awarded": sum(i.amount for i in self.incentives.values()),
            "total_approved": sum(i.amount for i in self.incentives.values() 
                                if i.approval_status == "approved"),
            "total_pending": sum(i.amount for i in self.incentives.values() 
                               if i.approval_status == "pending")
        }

    def _get_incentive_type_distribution(self) -> Dict[str, Dict[str, Any]]:
        """Get distribution of incentive types"""
        distribution = {}
        for incentive_type in IncentiveType:
            incentives = [i for i in self.incentives.values() 
                         if i.type == incentive_type]
            if incentives:
                distribution[incentive_type.value] = {
                    "count": len(incentives),
                    "total_amount": sum(i.amount for i in incentives),
                    "average_amount": sum(i.amount for i in incentives) / len(incentives)
                }
        return distribution

    def _calculate_incentive_approval_rate(self) -> float:
        """Calculate incentive approval rate"""
        total_incentives = len(self.incentives)
        if total_incentives == 0:
            return 0.0
        
        approved_incentives = len([i for i in self.incentives.values() 
                                 if i.approval_status == "approved"])
        return approved_incentives / total_incentives

    def _get_incentive_cost_impact(self) -> Dict[str, Any]:
        """Get incentive cost impact analysis"""
        return {
            "total_budget": 0.0,  # Would be set based on company budget
            "total_awarded": sum(i.amount for i in self.incentives.values()),
            "budget_utilization": 0.0,  # Would be calculated based on budget
            "by_department": {},  # Would be populated based on department data
            "by_performance_level": {}  # Would be populated based on performance data
        }

    def _notify_employee(self, employee_id: int, event_type: str) -> None:
        """Notify employee about rewards management events"""
        if employee_id not in self.notifications:
            self.notifications[employee_id] = []
            
        self.notifications[employee_id].append({
            "type": event_type,
            "employee_id": employee_id,
            "timestamp": datetime.now(),
            "is_read": False
        }) 