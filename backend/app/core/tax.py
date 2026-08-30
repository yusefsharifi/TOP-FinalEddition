from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import os

class TaxType(Enum):
    INCOME = "income"
    SALES = "sales"
    PROPERTY = "property"
    CUSTOMS = "customs"
    STAMP = "stamp"
    OTHER = "other"

class TaxStatus(Enum):
    PENDING = "pending"
    CALCULATED = "calculated"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class TaxPeriod(Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"

@dataclass
class TaxRate:
    id: str
    type: TaxType
    name: str
    rate: Decimal
    description: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class TaxExemption:
    id: str
    type: TaxType
    name: str
    description: str
    amount: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class TaxCalculation:
    id: str
    type: TaxType
    period: TaxPeriod
    start_date: date
    end_date: date
    base_amount: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    status: TaxStatus = TaxStatus.PENDING
    calculated_by: Optional[str] = None
    calculated_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class TaxPayment:
    id: str
    calculation_id: str
    amount: Decimal
    payment_date: date
    payment_method: str
    reference_number: str
    status: str = "pending"  # pending, processed, failed
    processed_by: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class TaxDocument:
    id: str
    calculation_id: str
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
class TaxRule:
    id: str
    type: TaxType
    name: str
    description: str
    conditions: Dict[str, Any]  # JSON string of conditions
    actions: Dict[str, Any]  # JSON string of actions
    priority: int
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class RegionalTax:
    id: str
    region: str
    type: TaxType
    rate: Decimal
    additional_rate: Optional[Decimal] = None
    description: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class TaxManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rates: Dict[str, TaxRate] = {}
        self.exemptions: Dict[str, TaxExemption] = {}
        self.calculations: Dict[str, TaxCalculation] = {}
        self.payments: Dict[str, List[TaxPayment]] = {}
        self.documents: Dict[str, List[TaxDocument]] = {}
        self.rules: Dict[str, TaxRule] = {}
        self.regional_taxes: Dict[str, RegionalTax] = {}
        
        # Load tax rules from file
        self.load_tax_rules()
    
    def load_tax_rules(self):
        """Load tax rules from JSON file"""
        try:
            rules_file = os.path.join(os.path.dirname(__file__), 'tax_rules.json')
            if os.path.exists(rules_file):
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    for rule_data in rules_data:
                        rule = TaxRule(
                            id=rule_data['id'],
                            type=TaxType(rule_data['type']),
                            name=rule_data['name'],
                            description=rule_data['description'],
                            conditions=rule_data['conditions'],
                            actions=rule_data['actions'],
                            priority=rule_data['priority']
                        )
                        self.rules[rule.id] = rule
                self.logger.info("Tax rules loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading tax rules: {str(e)}")
    
    def add_rate(self, rate: TaxRate) -> bool:
        """Add tax rate"""
        try:
            if rate.id in self.rates:
                self.logger.warning(f"Rate with ID {rate.id} already exists")
                return False
            
            self.rates[rate.id] = rate
            self.logger.info(f"Tax rate added: {rate.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding tax rate: {str(e)}")
            return False
    
    def add_exemption(self, exemption: TaxExemption) -> bool:
        """Add tax exemption"""
        try:
            if exemption.id in self.exemptions:
                self.logger.warning(f"Exemption with ID {exemption.id} already exists")
                return False
            
            self.exemptions[exemption.id] = exemption
            self.logger.info(f"Tax exemption added: {exemption.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding tax exemption: {str(e)}")
            return False
    
    def add_rule(self, rule: TaxRule) -> bool:
        """Add tax rule"""
        try:
            if rule.id in self.rules:
                self.logger.warning(f"Rule with ID {rule.id} already exists")
                return False
            
            self.rules[rule.id] = rule
            self.logger.info(f"Tax rule added: {rule.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding tax rule: {str(e)}")
            return False
    
    def add_regional_tax(self, regional_tax: RegionalTax) -> bool:
        """Add regional tax"""
        try:
            if regional_tax.id in self.regional_taxes:
                self.logger.warning(f"Regional tax with ID {regional_tax.id} already exists")
                return False
            
            self.regional_taxes[regional_tax.id] = regional_tax
            self.logger.info(f"Regional tax added: {regional_tax.region}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding regional tax: {str(e)}")
            return False
    
    def calculate_tax(self, calculation: TaxCalculation, region: str = None) -> Dict[str, Any]:
        """Calculate tax with complex rules and regional differences"""
        try:
            # Get applicable tax rate
            rate = self.get_applicable_rate(calculation.type, calculation.start_date)
            if not rate:
                return {}
            
            # Apply regional tax if applicable
            if region:
                regional_tax = self.get_regional_tax(region, calculation.type, calculation.start_date)
                if regional_tax:
                    rate = rate + regional_tax.rate
                    if regional_tax.additional_rate:
                        rate = rate + regional_tax.additional_rate
            
            # Apply exemptions
            exemptions = self.get_applicable_exemptions(calculation.type, calculation.start_date)
            exempt_amount = Decimal('0')
            for exemption in exemptions:
                if exemption.amount:
                    exempt_amount += exemption.amount
                elif exemption.percentage:
                    exempt_amount += calculation.base_amount * (exemption.percentage / Decimal('100'))
            
            # Calculate taxable amount
            taxable_amount = calculation.base_amount - exempt_amount
            
            # Apply tax rules
            for rule in sorted(self.rules.values(), key=lambda x: x.priority):
                if self.evaluate_rule_conditions(rule, calculation, taxable_amount):
                    taxable_amount = self.apply_rule_actions(rule, taxable_amount)
            
            # Calculate tax amount
            tax_amount = taxable_amount * (rate / Decimal('100'))
            
            # Update calculation
            calculation.taxable_amount = taxable_amount
            calculation.tax_amount = tax_amount
            calculation.status = TaxStatus.CALCULATED
            calculation.calculated_by = "system"
            calculation.calculated_at = datetime.now()
            calculation.updated_at = datetime.now()
            
            return {
                "id": calculation.id,
                "base_amount": calculation.base_amount,
                "exempt_amount": exempt_amount,
                "taxable_amount": taxable_amount,
                "tax_rate": rate,
                "tax_amount": tax_amount,
                "status": calculation.status.value
            }
        except Exception as e:
            self.logger.error(f"Error calculating tax: {str(e)}")
            return {}
    
    def get_applicable_rate(self, tax_type: TaxType, date: date) -> Optional[Decimal]:
        """Get applicable tax rate for given type and date"""
        try:
            applicable_rates = [
                rate for rate in self.rates.values()
                if rate.type == tax_type
                and rate.is_active
                and (not rate.start_date or rate.start_date <= date)
                and (not rate.end_date or rate.end_date >= date)
            ]
            
            if applicable_rates:
                return applicable_rates[0].rate
            return None
        except Exception as e:
            self.logger.error(f"Error getting applicable rate: {str(e)}")
            return None
    
    def get_regional_tax(self, region: str, tax_type: TaxType, date: date) -> Optional[RegionalTax]:
        """Get applicable regional tax"""
        try:
            applicable_taxes = [
                tax for tax in self.regional_taxes.values()
                if tax.region == region
                and tax.type == tax_type
                and tax.is_active
                and (not tax.start_date or tax.start_date <= date)
                and (not tax.end_date or tax.end_date >= date)
            ]
            
            if applicable_taxes:
                return applicable_taxes[0]
            return None
        except Exception as e:
            self.logger.error(f"Error getting regional tax: {str(e)}")
            return None
    
    def get_applicable_exemptions(self, tax_type: TaxType, date: date) -> List[TaxExemption]:
        """Get applicable tax exemptions"""
        try:
            return [
                exemption for exemption in self.exemptions.values()
                if exemption.type == tax_type
                and exemption.is_active
                and (not exemption.start_date or exemption.start_date <= date)
                and (not exemption.end_date or exemption.end_date >= date)
            ]
        except Exception as e:
            self.logger.error(f"Error getting applicable exemptions: {str(e)}")
            return []
    
    def evaluate_rule_conditions(self, rule: TaxRule, calculation: TaxCalculation, 
                               taxable_amount: Decimal) -> bool:
        """Evaluate tax rule conditions"""
        try:
            conditions = rule.conditions
            
            # Check amount conditions
            if 'min_amount' in conditions and taxable_amount < Decimal(str(conditions['min_amount'])):
                return False
            if 'max_amount' in conditions and taxable_amount > Decimal(str(conditions['max_amount'])):
                return False
            
            # Check date conditions
            if 'start_date' in conditions and calculation.start_date < datetime.strptime(conditions['start_date'], '%Y-%m-%d').date():
                return False
            if 'end_date' in conditions and calculation.end_date > datetime.strptime(conditions['end_date'], '%Y-%m-%d').date():
                return False
            
            # Add more condition types as needed
            
            return True
        except Exception as e:
            self.logger.error(f"Error evaluating rule conditions: {str(e)}")
            return False
    
    def apply_rule_actions(self, rule: TaxRule, taxable_amount: Decimal) -> Decimal:
        """Apply tax rule actions"""
        try:
            actions = rule.actions
            result = taxable_amount
            
            # Apply percentage adjustments
            if 'adjust_percentage' in actions:
                adjustment = Decimal(str(actions['adjust_percentage']))
                result = result * (Decimal('1') + (adjustment / Decimal('100')))
            
            # Apply fixed amount adjustments
            if 'adjust_amount' in actions:
                adjustment = Decimal(str(actions['adjust_amount']))
                result = result + adjustment
            
            # Add more action types as needed
            
            return result
        except Exception as e:
            self.logger.error(f"Error applying rule actions: {str(e)}")
            return taxable_amount
    
    def add_payment(self, payment: TaxPayment) -> bool:
        """Add tax payment"""
        try:
            if payment.calculation_id not in self.calculations:
                self.logger.error(f"Calculation {payment.calculation_id} not found")
                return False
            
            if payment.id in [p.id for p in self.payments.get(payment.calculation_id, [])]:
                self.logger.warning(f"Payment with ID {payment.id} already exists")
                return False
            
            if payment.calculation_id not in self.payments:
                self.payments[payment.calculation_id] = []
            
            self.payments[payment.calculation_id].append(payment)
            self.logger.info(f"Tax payment added for {payment.calculation_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding tax payment: {str(e)}")
            return False
    
    def process_payment(self, payment_id: str, calculation_id: str, 
                       processed_by: str) -> bool:
        """Process tax payment"""
        try:
            payment = next((p for p in self.payments.get(calculation_id, []) 
                          if p.id == payment_id), None)
            if not payment:
                return False
            
            if payment.status != "pending":
                self.logger.warning(f"Payment {payment_id} is not pending")
                return False
            
            payment.status = "paid"
            payment.processed_by = processed_by
            payment.processed_at = datetime.now()
            payment.updated_at = datetime.now()
            
            # Update calculation status
            calculation = self.calculations[calculation_id]
            total_paid = sum(p.amount for p in self.payments[calculation_id] 
                           if p.status == "paid")
            
            if total_paid >= calculation.tax_amount:
                calculation.status = TaxStatus.PAID
                calculation.updated_at = datetime.now()
            
            self.logger.info(f"Tax payment {payment_id} processed")
            return True
        except Exception as e:
            self.logger.error(f"Error processing tax payment: {str(e)}")
            return False
    
    def add_document(self, document: TaxDocument) -> bool:
        """Add tax document"""
        try:
            if document.calculation_id not in self.calculations:
                self.logger.error(f"Calculation {document.calculation_id} not found")
                return False
            
            if document.id in [d.id for d in self.documents.get(document.calculation_id, [])]:
                self.logger.warning(f"Document with ID {document.id} already exists")
                return False
            
            if document.calculation_id not in self.documents:
                self.documents[document.calculation_id] = []
            
            self.documents[document.calculation_id].append(document)
            self.logger.info(f"Tax document added for {document.calculation_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding tax document: {str(e)}")
            return False
    
    def get_calculation_summary(self, calculation_id: str) -> Dict[str, Any]:
        """Get tax calculation summary"""
        try:
            calculation = self.calculations.get(calculation_id)
            if not calculation:
                return {}
            
            payments = self.payments.get(calculation_id, [])
            documents = self.documents.get(calculation_id, [])
            
            total_paid = sum(p.amount for p in payments if p.status == "paid")
            remaining_amount = calculation.tax_amount - total_paid
            
            return {
                "id": calculation.id,
                "type": calculation.type.value,
                "period": calculation.period.value,
                "start_date": calculation.start_date.isoformat(),
                "end_date": calculation.end_date.isoformat(),
                "base_amount": calculation.base_amount,
                "taxable_amount": calculation.taxable_amount,
                "tax_amount": calculation.tax_amount,
                "status": calculation.status.value,
                "total_paid": total_paid,
                "remaining_amount": remaining_amount,
                "document_count": len(documents),
                "created_at": calculation.created_at.isoformat(),
                "updated_at": calculation.updated_at.isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting calculation summary: {str(e)}")
            return {}
    
    def get_tax_report(self, tax_type: TaxType, start_date: date, 
                      end_date: date) -> List[Dict[str, Any]]:
        """Get detailed tax report"""
        try:
            report = []
            for calc in self.calculations.values():
                if (calc.type == tax_type and
                    calc.start_date >= start_date and
                    calc.end_date <= end_date):
                    
                    payments = self.payments.get(calc.id, [])
                    total_paid = sum(p.amount for p in payments if p.status == "processed")
                    
                    report.append({
                        "id": calc.id,
                        "period": calc.period.value,
                        "start_date": calc.start_date.isoformat(),
                        "end_date": calc.end_date.isoformat(),
                        "base_amount": calc.base_amount,
                        "taxable_amount": calc.taxable_amount,
                        "tax_amount": calc.tax_amount,
                        "status": calc.status.value,
                        "total_paid": total_paid,
                        "remaining": calc.tax_amount - total_paid
                    })
            
            return sorted(report, key=lambda x: x["start_date"])
        except Exception as e:
            self.logger.error(f"Error getting tax report: {str(e)}")
            return []
    
    def get_regional_tax_report(self, region: str, tax_type: TaxType, 
                              start_date: date, end_date: date) -> Dict[str, Any]:
        """Get regional tax report"""
        try:
            report = {
                "region": region,
                "tax_type": tax_type.value,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "calculations": [],
                "summary": {
                    "total_base_amount": Decimal('0'),
                    "total_taxable_amount": Decimal('0'),
                    "total_tax_amount": Decimal('0'),
                    "total_paid": Decimal('0')
                }
            }
            
            for calc in self.calculations.values():
                if (calc.type == tax_type and
                    calc.start_date >= start_date and
                    calc.end_date <= end_date):
                    
                    # Apply regional tax
                    regional_tax = self.get_regional_tax(region, tax_type, calc.start_date)
                    if regional_tax:
                        tax_rate = self.get_applicable_rate(tax_type, calc.start_date)
                        if tax_rate:
                            tax_rate += regional_tax.rate
                            if regional_tax.additional_rate:
                                tax_rate += regional_tax.additional_rate
                            
                            tax_amount = calc.taxable_amount * (tax_rate / Decimal('100'))
                            
                            payments = self.payments.get(calc.id, [])
                            total_paid = sum(p.amount for p in payments if p.status == "processed")
                            
                            report["calculations"].append({
                                "id": calc.id,
                                "period": calc.period.value,
                                "start_date": calc.start_date.isoformat(),
                                "end_date": calc.end_date.isoformat(),
                                "base_amount": calc.base_amount,
                                "taxable_amount": calc.taxable_amount,
                                "tax_rate": tax_rate,
                                "tax_amount": tax_amount,
                                "total_paid": total_paid,
                                "remaining": tax_amount - total_paid
                            })
                            
                            report["summary"]["total_base_amount"] += calc.base_amount
                            report["summary"]["total_taxable_amount"] += calc.taxable_amount
                            report["summary"]["total_tax_amount"] += tax_amount
                            report["summary"]["total_paid"] += total_paid
            
            return report
        except Exception as e:
            self.logger.error(f"Error getting regional tax report: {str(e)}")
            return {} 