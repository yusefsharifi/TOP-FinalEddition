from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"

class AccountType(Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

@dataclass
class Account:
    id: str
    code: str
    name: str
    type: AccountType
    parent_id: Optional[str] = None
    description: str = ""
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Transaction:
    id: str
    date: date
    type: TransactionType
    reference: str
    description: str
    amount: Decimal
    debit_account_id: str
    credit_account_id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class JournalEntry:
    id: str
    date: date
    reference: str
    description: str
    transactions: List[Transaction]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class AccountingSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.accounts: Dict[str, Account] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.journal_entries: Dict[str, JournalEntry] = {}
    
    def add_account(self, account: Account) -> bool:
        """Add new account to the system"""
        try:
            if account.id in self.accounts:
                self.logger.warning(f"Account with ID {account.id} already exists")
                return False
            
            self.accounts[account.id] = account
            self.logger.info(f"Account {account.name} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding account: {str(e)}")
            return False
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        return self.accounts.get(account_id)
    
    def get_account_balance(self, account_id: str, as_of_date: Optional[date] = None) -> Decimal:
        """Calculate account balance as of specific date"""
        try:
            balance = Decimal('0')
            account = self.get_account(account_id)
            if not account:
                return Decimal('0')
            
            for transaction in self.transactions.values():
                if as_of_date and transaction.date > as_of_date:
                    continue
                
                if transaction.debit_account_id == account_id:
                    balance += transaction.amount
                elif transaction.credit_account_id == account_id:
                    balance -= transaction.amount
            
            return balance
        except Exception as e:
            self.logger.error(f"Error calculating account balance: {str(e)}")
            return Decimal('0')
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add new transaction to the system"""
        try:
            if transaction.id in self.transactions:
                self.logger.warning(f"Transaction with ID {transaction.id} already exists")
                return False
            
            # Validate accounts exist
            if not (transaction.debit_account_id in self.accounts and 
                   transaction.credit_account_id in self.accounts):
                self.logger.error("Invalid account IDs in transaction")
                return False
            
            self.transactions[transaction.id] = transaction
            self.logger.info(f"Transaction {transaction.reference} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding transaction: {str(e)}")
            return False
    
    def add_journal_entry(self, journal_entry: JournalEntry) -> bool:
        """Add new journal entry to the system"""
        try:
            if journal_entry.id in self.journal_entries:
                self.logger.warning(f"Journal entry with ID {journal_entry.id} already exists")
                return False
            
            # Validate transactions
            for transaction in journal_entry.transactions:
                if not self.add_transaction(transaction):
                    return False
            
            self.journal_entries[journal_entry.id] = journal_entry
            self.logger.info(f"Journal entry {journal_entry.reference} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding journal entry: {str(e)}")
            return False
    
    def get_trial_balance(self, as_of_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Generate trial balance as of specific date"""
        try:
            trial_balance = []
            for account_id, account in self.accounts.items():
                balance = self.get_account_balance(account_id, as_of_date)
                if balance != Decimal('0'):
                    trial_balance.append({
                        "account_code": account.code,
                        "account_name": account.name,
                        "account_type": account.type.value,
                        "debit": balance if balance > 0 else Decimal('0'),
                        "credit": -balance if balance < 0 else Decimal('0')
                    })
            return trial_balance
        except Exception as e:
            self.logger.error(f"Error generating trial balance: {str(e)}")
            return []
    
    def get_income_statement(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate income statement for the period"""
        try:
            revenue = Decimal('0')
            expenses = Decimal('0')
            
            for account_id, account in self.accounts.items():
                if account.type == AccountType.REVENUE:
                    revenue += self.get_account_balance(account_id, end_date)
                elif account.type == AccountType.EXPENSE:
                    expenses += self.get_account_balance(account_id, end_date)
            
            net_income = revenue - expenses
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "revenue": revenue,
                "expenses": expenses,
                "net_income": net_income
            }
        except Exception as e:
            self.logger.error(f"Error generating income statement: {str(e)}")
            return {}
    
    def get_balance_sheet(self, as_of_date: date) -> Dict[str, Any]:
        """Generate balance sheet as of specific date"""
        try:
            assets = Decimal('0')
            liabilities = Decimal('0')
            equity = Decimal('0')
            
            for account_id, account in self.accounts.items():
                balance = self.get_account_balance(account_id, as_of_date)
                if account.type == AccountType.ASSET:
                    assets += balance
                elif account.type == AccountType.LIABILITY:
                    liabilities += balance
                elif account.type == AccountType.EQUITY:
                    equity += balance
            
            return {
                "date": as_of_date.isoformat(),
                "assets": assets,
                "liabilities": liabilities,
                "equity": equity,
                "total_liabilities_and_equity": liabilities + equity
            }
        except Exception as e:
            self.logger.error(f"Error generating balance sheet: {str(e)}")
            return {}
    
    def get_cash_flow(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate cash flow statement for the period"""
        try:
            operating_activities = Decimal('0')
            investing_activities = Decimal('0')
            financing_activities = Decimal('0')
            
            for transaction in self.transactions.values():
                if start_date <= transaction.date <= end_date:
                    if transaction.type == TransactionType.INCOME:
                        operating_activities += transaction.amount
                    elif transaction.type == TransactionType.EXPENSE:
                        operating_activities -= transaction.amount
                    elif transaction.type == TransactionType.TRANSFER:
                        investing_activities += transaction.amount
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "operating_activities": operating_activities,
                "investing_activities": investing_activities,
                "financing_activities": financing_activities,
                "net_cash_flow": operating_activities + investing_activities + financing_activities
            }
        except Exception as e:
            self.logger.error(f"Error generating cash flow statement: {str(e)}")
            return {}

class TreasurySystem:
    def __init__(self, accounting_system: AccountingSystem):
        self.logger = logging.getLogger(__name__)
        self.accounting_system = accounting_system
        self.cash_accounts: Dict[str, Account] = {}
        self.bank_accounts: Dict[str, Account] = {}
    
    def add_cash_account(self, account: Account) -> bool:
        """Add new cash account"""
        try:
            if account.type != AccountType.ASSET:
                self.logger.error("Cash account must be an asset account")
                return False
            
            self.cash_accounts[account.id] = account
            self.accounting_system.add_account(account)
            self.logger.info(f"Cash account {account.name} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding cash account: {str(e)}")
            return False
    
    def add_bank_account(self, account: Account) -> bool:
        """Add new bank account"""
        try:
            if account.type != AccountType.ASSET:
                self.logger.error("Bank account must be an asset account")
                return False
            
            self.bank_accounts[account.id] = account
            self.accounting_system.add_account(account)
            self.logger.info(f"Bank account {account.name} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding bank account: {str(e)}")
            return False
    
    def get_cash_balance(self, account_id: str, as_of_date: Optional[date] = None) -> Decimal:
        """Get cash balance for specific account"""
        return self.accounting_system.get_account_balance(account_id, as_of_date)
    
    def get_total_cash_balance(self, as_of_date: Optional[date] = None) -> Decimal:
        """Get total cash balance across all cash accounts"""
        total = Decimal('0')
        for account_id in self.cash_accounts:
            total += self.get_cash_balance(account_id, as_of_date)
        return total
    
    def get_total_bank_balance(self, as_of_date: Optional[date] = None) -> Decimal:
        """Get total bank balance across all bank accounts"""
        total = Decimal('0')
        for account_id in self.bank_accounts:
            total += self.get_cash_balance(account_id, as_of_date)
        return total
    
    def transfer_cash(self, 
                     from_account_id: str,
                     to_account_id: str,
                     amount: Decimal,
                     date: date,
                     reference: str,
                     description: str) -> bool:
        """Transfer cash between accounts"""
        try:
            # Create transaction
            transaction = Transaction(
                id=f"TRF_{date.strftime('%Y%m%d')}_{reference}",
                date=date,
                type=TransactionType.TRANSFER,
                reference=reference,
                description=description,
                amount=amount,
                debit_account_id=to_account_id,
                credit_account_id=from_account_id
            )
            
            # Add transaction to accounting system
            return self.accounting_system.add_transaction(transaction)
        except Exception as e:
            self.logger.error(f"Error transferring cash: {str(e)}")
            return False
    
    def get_cash_flow_forecast(self, 
                             start_date: date,
                             end_date: date,
                             include_bank_accounts: bool = True) -> List[Dict[str, Any]]:
        """Generate cash flow forecast for the period"""
        try:
            forecast = []
            current_date = start_date
            
            while current_date <= end_date:
                daily_balance = self.get_total_cash_balance(current_date)
                if include_bank_accounts:
                    daily_balance += self.get_total_bank_balance(current_date)
                
                forecast.append({
                    "date": current_date.isoformat(),
                    "balance": daily_balance
                })
                
                current_date = date(current_date.year, current_date.month, current_date.day + 1)
            
            return forecast
        except Exception as e:
            self.logger.error(f"Error generating cash flow forecast: {str(e)}")
            return [] 