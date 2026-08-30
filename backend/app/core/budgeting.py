from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

class BudgetType(Enum):
    OPERATIONAL = "operational"
    CAPITAL = "capital"
    CASH = "cash"
    PROJECT = "project"

class BudgetStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    CLOSED = "closed"

class BudgetPeriod(Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"

@dataclass
class BudgetAccount:
    id: str
    code: str
    name: str
    type: str  # income, expense, asset, liability
    parent_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class BudgetLine:
    id: str
    budget_id: str
    account_id: str
    amount: Decimal
    description: str = ""
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Budget:
    id: str
    name: str
    type: BudgetType
    period: BudgetPeriod
    fiscal_year: str
    start_date: date
    end_date: date
    status: BudgetStatus = BudgetStatus.DRAFT
    description: str = ""
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class BudgetRevision:
    id: str
    budget_id: str
    revision_number: int
    revision_date: date
    description: str
    status: BudgetStatus = BudgetStatus.DRAFT
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class BudgetPerformance:
    id: str
    budget_id: str
    account_id: str
    period: str  # YYYY-MM format
    budget_amount: Decimal
    actual_amount: Decimal
    variance_amount: Decimal
    variance_percentage: Decimal
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class BudgetManager:
    def __init__(self, accounting_system):
        self.logger = logging.getLogger(__name__)
        self.accounting_system = accounting_system
        self.accounts: Dict[str, BudgetAccount] = {}
        self.budgets: Dict[str, Budget] = {}
        self.budget_lines: Dict[str, List[BudgetLine]] = {}
        self.revisions: Dict[str, List[BudgetRevision]] = {}
        self.performance: Dict[str, List[BudgetPerformance]] = {}
    
    def add_account(self, account: BudgetAccount) -> bool:
        """Add budget account"""
        try:
            if account.id in self.accounts:
                self.logger.warning(f"Account with ID {account.id} already exists")
                return False
            
            self.accounts[account.id] = account
            self.logger.info(f"Budget account added: {account.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding budget account: {str(e)}")
            return False
    
    def create_budget(self, budget: Budget) -> bool:
        """Create new budget"""
        try:
            if budget.id in self.budgets:
                self.logger.warning(f"Budget with ID {budget.id} already exists")
                return False
            
            self.budgets[budget.id] = budget
            self.budget_lines[budget.id] = []
            self.logger.info(f"Budget created: {budget.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating budget: {str(e)}")
            return False
    
    def add_budget_line(self, line: BudgetLine) -> bool:
        """Add line to budget"""
        try:
            if line.budget_id not in self.budgets:
                self.logger.error(f"Budget {line.budget_id} not found")
                return False
            
            if line.account_id not in self.accounts:
                self.logger.error(f"Account {line.account_id} not found")
                return False
            
            if line.id in [l.id for l in self.budget_lines.get(line.budget_id, [])]:
                self.logger.warning(f"Line with ID {line.id} already exists")
                return False
            
            self.budget_lines[line.budget_id].append(line)
            self.logger.info(f"Budget line added to {line.budget_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding budget line: {str(e)}")
            return False
    
    def submit_budget(self, budget_id: str) -> bool:
        """Submit budget for approval"""
        try:
            budget = self.budgets.get(budget_id)
            if not budget:
                return False
            
            if budget.status != BudgetStatus.DRAFT:
                self.logger.warning(f"Budget {budget_id} is not in draft status")
                return False
            
            budget.status = BudgetStatus.PENDING
            budget.updated_at = datetime.now()
            
            self.logger.info(f"Budget {budget_id} submitted for approval")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting budget: {str(e)}")
            return False
    
    def approve_budget(self, budget_id: str, approved_by: str) -> bool:
        """Approve budget"""
        try:
            budget = self.budgets.get(budget_id)
            if not budget:
                return False
            
            if budget.status != BudgetStatus.PENDING:
                self.logger.warning(f"Budget {budget_id} is not pending")
                return False
            
            budget.status = BudgetStatus.APPROVED
            budget.approved_by = approved_by
            budget.approved_at = datetime.now()
            budget.updated_at = datetime.now()
            
            self.logger.info(f"Budget {budget_id} approved")
            return True
        except Exception as e:
            self.logger.error(f"Error approving budget: {str(e)}")
            return False
    
    def create_revision(self, revision: BudgetRevision) -> bool:
        """Create budget revision"""
        try:
            if revision.budget_id not in self.budgets:
                self.logger.error(f"Budget {revision.budget_id} not found")
                return False
            
            if revision.id in [r.id for r in self.revisions.get(revision.budget_id, [])]:
                self.logger.warning(f"Revision with ID {revision.id} already exists")
                return False
            
            if revision.budget_id not in self.revisions:
                self.revisions[revision.budget_id] = []
            
            self.revisions[revision.budget_id].append(revision)
            self.logger.info(f"Budget revision created for {revision.budget_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating budget revision: {str(e)}")
            return False
    
    def calculate_performance(self, budget_id: str, period: str) -> bool:
        """Calculate budget performance for period"""
        try:
            budget = self.budgets.get(budget_id)
            if not budget:
                return False
            
            if budget.status != BudgetStatus.APPROVED:
                self.logger.warning(f"Budget {budget_id} is not approved")
                return False
            
            # Get actual amounts from accounting system
            actual_amounts = self.accounting_system.get_account_balances(
                [line.account_id for line in self.budget_lines.get(budget_id, [])],
                period
            )
            
            # Calculate performance for each line
            for line in self.budget_lines.get(budget_id, []):
                actual_amount = actual_amounts.get(line.account_id, Decimal('0'))
                variance_amount = actual_amount - line.amount
                variance_percentage = (variance_amount / line.amount * 100) if line.amount != 0 else 0
                
                performance = BudgetPerformance(
                    id=f"PERF_{budget_id}_{line.account_id}_{period}",
                    budget_id=budget_id,
                    account_id=line.account_id,
                    period=period,
                    budget_amount=line.amount,
                    actual_amount=actual_amount,
                    variance_amount=variance_amount,
                    variance_percentage=variance_percentage
                )
                
                if budget_id not in self.performance:
                    self.performance[budget_id] = []
                
                self.performance[budget_id].append(performance)
            
            self.logger.info(f"Budget performance calculated for {budget_id} - {period}")
            return True
        except Exception as e:
            self.logger.error(f"Error calculating budget performance: {str(e)}")
            return False
    
    def get_budget_summary(self, budget_id: str) -> Dict[str, Any]:
        """Get budget summary"""
        try:
            budget = self.budgets.get(budget_id)
            if not budget:
                return {}
            
            lines = self.budget_lines.get(budget_id, [])
            total_income = sum(line.amount for line in lines 
                             if self.accounts[line.account_id].type == "income")
            total_expense = sum(line.amount for line in lines 
                              if self.accounts[line.account_id].type == "expense")
            
            return {
                "id": budget.id,
                "name": budget.name,
                "type": budget.type.value,
                "period": budget.period.value,
                "fiscal_year": budget.fiscal_year,
                "start_date": budget.start_date.isoformat(),
                "end_date": budget.end_date.isoformat(),
                "status": budget.status.value,
                "total_income": total_income,
                "total_expense": total_expense,
                "net_amount": total_income - total_expense,
                "line_count": len(lines),
                "revision_count": len(self.revisions.get(budget_id, [])),
                "created_at": budget.created_at.isoformat(),
                "updated_at": budget.updated_at.isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting budget summary: {str(e)}")
            return {}
    
    def get_performance_report(self, budget_id: str, 
                             start_period: str, 
                             end_period: str) -> List[Dict[str, Any]]:
        """Get budget performance report"""
        try:
            report = []
            for performance in self.performance.get(budget_id, []):
                if performance.period < start_period or performance.period > end_period:
                    continue
                
                account = self.accounts[performance.account_id]
                report.append({
                    "period": performance.period,
                    "account_code": account.code,
                    "account_name": account.name,
                    "account_type": account.type,
                    "budget_amount": performance.budget_amount,
                    "actual_amount": performance.actual_amount,
                    "variance_amount": performance.variance_amount,
                    "variance_percentage": performance.variance_percentage
                })
            
            return sorted(report, key=lambda x: (x["period"], x["account_code"]))
        except Exception as e:
            self.logger.error(f"Error getting performance report: {str(e)}")
            return [] 