from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

class PartyType(Enum):
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    EMPLOYEE = "employee"
    BANK = "bank"
    OTHER = "other"

class PaymentType(Enum):
    CASH = "cash"
    CHECK = "check"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    PROMISSORY_NOTE = "promissory_note"
    OTHER = "other"

class PaymentStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

@dataclass
class Party:
    id: str
    code: str
    name: str
    type: PartyType
    tax_id: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    credit_limit: Decimal = Decimal('0')
    payment_terms: int = 0  # تعداد روزهای اعتبار
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Payment:
    id: str
    party_id: str
    document_id: str
    type: PaymentType
    amount: Decimal
    payment_date: date
    due_date: Optional[date] = None
    reference: str = ""
    description: str = ""
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Check:
    id: str
    payment_id: str
    check_number: str
    bank_name: str
    amount: Decimal
    issue_date: date
    due_date: date
    status: PaymentStatus = PaymentStatus.PENDING
    cleared_date: Optional[date] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PromissoryNote:
    id: str
    payment_id: str
    note_number: str
    amount: Decimal
    issue_date: date
    due_date: date
    status: PaymentStatus = PaymentStatus.PENDING
    cleared_date: Optional[date] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class ReceivablesPayablesManager:
    def __init__(self, accounting_system):
        self.logger = logging.getLogger(__name__)
        self.accounting_system = accounting_system
        self.parties: Dict[str, Party] = {}
        self.payments: Dict[str, Payment] = {}
        self.checks: Dict[str, Check] = {}
        self.promissory_notes: Dict[str, PromissoryNote] = {}
    
    def add_party(self, party: Party) -> bool:
        """Add new party"""
        try:
            if party.id in self.parties:
                self.logger.warning(f"Party with ID {party.id} already exists")
                return False
            
            self.parties[party.id] = party
            self.logger.info(f"Party {party.name} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding party: {str(e)}")
            return False
    
    def add_payment(self, payment: Payment) -> bool:
        """Add new payment"""
        try:
            if payment.id in self.payments:
                self.logger.warning(f"Payment with ID {payment.id} already exists")
                return False
            
            if payment.party_id not in self.parties:
                self.logger.error(f"Party {payment.party_id} not found")
                return False
            
            self.payments[payment.id] = payment
            self.logger.info(f"Payment {payment.id} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding payment: {str(e)}")
            return False
    
    def add_check(self, check: Check) -> bool:
        """Add new check"""
        try:
            if check.id in self.checks:
                self.logger.warning(f"Check with ID {check.id} already exists")
                return False
            
            if check.payment_id not in self.payments:
                self.logger.error(f"Payment {check.payment_id} not found")
                return False
            
            self.checks[check.id] = check
            self.logger.info(f"Check {check.check_number} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding check: {str(e)}")
            return False
    
    def add_promissory_note(self, note: PromissoryNote) -> bool:
        """Add new promissory note"""
        try:
            if note.id in self.promissory_notes:
                self.logger.warning(f"Promissory note with ID {note.id} already exists")
                return False
            
            if note.payment_id not in self.payments:
                self.logger.error(f"Payment {note.payment_id} not found")
                return False
            
            self.promissory_notes[note.id] = note
            self.logger.info(f"Promissory note {note.note_number} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding promissory note: {str(e)}")
            return False
    
    def clear_check(self, check_id: str, cleared_date: date) -> bool:
        """Clear check"""
        try:
            check = self.checks.get(check_id)
            if not check:
                return False
            
            if check.status != PaymentStatus.PENDING:
                self.logger.warning(f"Check {check_id} is not pending")
                return False
            
            check.status = PaymentStatus.PAID
            check.cleared_date = cleared_date
            check.updated_at = datetime.now()
            
            # Update payment status
            payment = self.payments.get(check.payment_id)
            if payment:
                self._update_payment_status(payment)
            
            self.logger.info(f"Check {check.check_number} cleared successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing check: {str(e)}")
            return False
    
    def clear_promissory_note(self, note_id: str, cleared_date: date) -> bool:
        """Clear promissory note"""
        try:
            note = self.promissory_notes.get(note_id)
            if not note:
                return False
            
            if note.status != PaymentStatus.PENDING:
                self.logger.warning(f"Promissory note {note_id} is not pending")
                return False
            
            note.status = PaymentStatus.PAID
            note.cleared_date = cleared_date
            note.updated_at = datetime.now()
            
            # Update payment status
            payment = self.payments.get(note.payment_id)
            if payment:
                self._update_payment_status(payment)
            
            self.logger.info(f"Promissory note {note.note_number} cleared successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing promissory note: {str(e)}")
            return False
    
    def _update_payment_status(self, payment: Payment) -> None:
        """Update payment status based on related items"""
        try:
            # Get all checks and promissory notes for this payment
            checks = [c for c in self.checks.values() if c.payment_id == payment.id]
            notes = [n for n in self.promissory_notes.values() if n.payment_id == payment.id]
            
            # Calculate total paid amount
            total_paid = sum(c.amount for c in checks if c.status == PaymentStatus.PAID)
            total_paid += sum(n.amount for n in notes if n.status == PaymentStatus.PAID)
            
            # Update payment status
            if total_paid == Decimal('0'):
                payment.status = PaymentStatus.PENDING
            elif total_paid < payment.amount:
                payment.status = PaymentStatus.PARTIAL
            else:
                payment.status = PaymentStatus.PAID
            
            payment.updated_at = datetime.now()
        except Exception as e:
            self.logger.error(f"Error updating payment status: {str(e)}")
    
    def get_party_balance(self, party_id: str, as_of_date: Optional[date] = None) -> Decimal:
        """Calculate party balance as of specific date"""
        try:
            party = self.parties.get(party_id)
            if not party:
                return Decimal('0')
            
            balance = Decimal('0')
            for payment in self.payments.values():
                if payment.party_id == party_id:
                    if as_of_date and payment.payment_date > as_of_date:
                        continue
                    
                    if party.type == PartyType.CUSTOMER:
                        balance += payment.amount
                    elif party.type == PartyType.SUPPLIER:
                        balance -= payment.amount
            
            return balance
        except Exception as e:
            self.logger.error(f"Error calculating party balance: {str(e)}")
            return Decimal('0')
    
    def get_party_statement(self, party_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate statement for specific party"""
        try:
            party = self.parties.get(party_id)
            if not party:
                return {}
            
            transactions = []
            balance = Decimal('0')
            
            for payment in self.payments.values():
                if payment.party_id == party_id and start_date <= payment.payment_date <= end_date:
                    if party.type == PartyType.CUSTOMER:
                        balance += payment.amount
                    elif party.type == PartyType.SUPPLIER:
                        balance -= payment.amount
                    
                    transactions.append({
                        "date": payment.payment_date.isoformat(),
                        "reference": payment.reference,
                        "description": payment.description,
                        "amount": payment.amount,
                        "type": payment.type.value,
                        "status": payment.status.value
                    })
            
            return {
                "party": {
                    "id": party.id,
                    "code": party.code,
                    "name": party.name,
                    "type": party.type.value
                },
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "opening_balance": self.get_party_balance(party_id, start_date),
                "closing_balance": balance,
                "transactions": sorted(transactions, key=lambda x: x["date"])
            }
        except Exception as e:
            self.logger.error(f"Error generating party statement: {str(e)}")
            return {}
    
    def get_overdue_payments(self, as_of_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get list of overdue payments"""
        try:
            if not as_of_date:
                as_of_date = date.today()
            
            overdue = []
            for payment in self.payments.values():
                if payment.status in [PaymentStatus.PENDING, PaymentStatus.PARTIAL]:
                    due_date = payment.due_date or payment.payment_date
                    if due_date < as_of_date:
                        party = self.parties.get(payment.party_id)
                        if party:
                            overdue.append({
                                "payment_id": payment.id,
                                "party_id": party.id,
                                "party_name": party.name,
                                "party_type": party.type.value,
                                "amount": payment.amount,
                                "due_date": due_date.isoformat(),
                                "status": payment.status.value,
                                "days_overdue": (as_of_date - due_date).days
                            })
            
            return sorted(overdue, key=lambda x: x["days_overdue"], reverse=True)
        except Exception as e:
            self.logger.error(f"Error getting overdue payments: {str(e)}")
            return []
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get payment details including checks and promissory notes"""
        try:
            payment = self.payments.get(payment_id)
            if not payment:
                return {}
            
            party = self.parties.get(payment.party_id)
            if not party:
                return {}
            
            return {
                "payment": {
                    "id": payment.id,
                    "party_id": party.id,
                    "party_name": party.name,
                    "party_type": party.type.value,
                    "type": payment.type.value,
                    "amount": payment.amount,
                    "payment_date": payment.payment_date.isoformat(),
                    "due_date": payment.due_date.isoformat() if payment.due_date else None,
                    "reference": payment.reference,
                    "description": payment.description,
                    "status": payment.status.value,
                    "created_at": payment.created_at.isoformat(),
                    "updated_at": payment.updated_at.isoformat()
                },
                "checks": [
                    {
                        "id": check.id,
                        "check_number": check.check_number,
                        "bank_name": check.bank_name,
                        "amount": check.amount,
                        "issue_date": check.issue_date.isoformat(),
                        "due_date": check.due_date.isoformat(),
                        "status": check.status.value,
                        "cleared_date": check.cleared_date.isoformat() if check.cleared_date else None
                    }
                    for check in self.checks.values()
                    if check.payment_id == payment_id
                ],
                "promissory_notes": [
                    {
                        "id": note.id,
                        "note_number": note.note_number,
                        "amount": note.amount,
                        "issue_date": note.issue_date.isoformat(),
                        "due_date": note.due_date.isoformat(),
                        "status": note.status.value,
                        "cleared_date": note.cleared_date.isoformat() if note.cleared_date else None
                    }
                    for note in self.promissory_notes.values()
                    if note.payment_id == payment_id
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting payment details: {str(e)}")
            return {}
    
    def get_party_list(self, party_type: Optional[PartyType] = None) -> List[Dict[str, Any]]:
        """Get list of parties with optional filter"""
        try:
            parties = []
            for party in self.parties.values():
                if party_type and party.type != party_type:
                    continue
                
                balance = self.get_party_balance(party.id)
                parties.append({
                    "id": party.id,
                    "code": party.code,
                    "name": party.name,
                    "type": party.type.value,
                    "tax_id": party.tax_id,
                    "address": party.address,
                    "phone": party.phone,
                    "email": party.email,
                    "credit_limit": party.credit_limit,
                    "payment_terms": party.payment_terms,
                    "balance": balance,
                    "is_active": party.is_active
                })
            
            return sorted(parties, key=lambda x: x["name"])
        except Exception as e:
            self.logger.error(f"Error getting party list: {str(e)}")
            return [] 