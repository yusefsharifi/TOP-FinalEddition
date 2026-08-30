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
import requests
from datetime import datetime, timedelta

class CurrencyType(Enum):
    FIAT = "fiat"
    CRYPTO = "crypto"
    COMMODITY = "commodity"

class ExchangeRateType(Enum):
    SPOT = "spot"
    FORWARD = "forward"
    HISTORICAL = "historical"
    CUSTOM = "custom"

@dataclass
class Currency:
    id: str
    code: str
    name: str
    type: CurrencyType
    symbol: str
    decimals: int
    is_active: bool = True
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ExchangeRate:
    id: str
    base_currency: str
    target_currency: str
    rate: Decimal
    type: ExchangeRateType
    effective_date: date
    expiry_date: Optional[date]
    source: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class CurrencyTransaction:
    id: str
    transaction_id: str
    currency: str
    amount: Decimal
    exchange_rate: Decimal
    base_amount: Decimal
    transaction_date: datetime
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class CurrencyBalance:
    id: str
    account_id: str
    currency: str
    balance: Decimal
    last_updated: datetime
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class CurrencyReport:
    id: str
    name: str
    description: str
    period_start: date
    period_end: date
    currencies: List[str]
    content: Dict[str, Any]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class CurrencyManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.currencies: Dict[str, Currency] = {}
        self.exchange_rates: Dict[str, ExchangeRate] = {}
        self.transactions: Dict[str, CurrencyTransaction] = {}
        self.balances: Dict[str, CurrencyBalance] = {}
        self.reports: Dict[str, CurrencyReport] = {}
        
        # Create necessary directories
        self.create_directories()
        
        # Load currencies from file
        self.load_currencies()
        
        # Initialize exchange rate sources
        self.exchange_rate_sources = {
            "fiat": "https://api.exchangerate-api.com/v4/latest/",
            "crypto": "https://api.coingecko.com/api/v3/simple/price",
            "commodity": "https://api.metals.live/v1/spot"
        }
    
    def create_directories(self):
        """Create necessary directories for currency management"""
        try:
            # Create currency data directory
            data_dir = os.path.join(os.path.dirname(__file__), 'currency_data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Create currency reports directory
            reports_dir = os.path.join(os.path.dirname(__file__), 'currency_reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            self.logger.info("Currency management directories created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {str(e)}")
    
    def load_currencies(self):
        """Load currencies from JSON file"""
        try:
            currencies_file = os.path.join(os.path.dirname(__file__), 'currencies.json')
            if os.path.exists(currencies_file):
                with open(currencies_file, 'r', encoding='utf-8') as f:
                    currencies_data = json.load(f)
                    for currency_data in currencies_data:
                        currency = Currency(
                            id=currency_data['id'],
                            code=currency_data['code'],
                            name=currency_data['name'],
                            type=CurrencyType(currency_data['type']),
                            symbol=currency_data['symbol'],
                            decimals=currency_data['decimals'],
                            is_active=currency_data['is_active'],
                            created_by=currency_data['created_by']
                        )
                        self.currencies[currency.id] = currency
                self.logger.info("Currencies loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading currencies: {str(e)}")
    
    def add_currency(self, currency: Currency) -> bool:
        """Add new currency"""
        try:
            if currency.id in self.currencies:
                self.logger.warning(f"Currency with ID {currency.id} already exists")
                return False
            
            self.currencies[currency.id] = currency
            self.logger.info(f"Currency added: {currency.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding currency: {str(e)}")
            return False
    
    def update_currency(self, currency_id: str, updates: Dict[str, Any]) -> bool:
        """Update currency details"""
        try:
            currency = self.currencies.get(currency_id)
            if not currency:
                self.logger.error(f"Currency {currency_id} not found")
                return False
            
            # Update currency attributes
            for key, value in updates.items():
                if hasattr(currency, key):
                    setattr(currency, key, value)
            
            currency.updated_at = datetime.now()
            self.logger.info(f"Currency updated: {currency.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating currency: {str(e)}")
            return False
    
    def add_exchange_rate(self, rate: ExchangeRate) -> bool:
        """Add exchange rate"""
        try:
            if rate.id in self.exchange_rates:
                self.logger.warning(f"Exchange rate with ID {rate.id} already exists")
                return False
            
            if rate.base_currency not in self.currencies:
                self.logger.error(f"Base currency {rate.base_currency} not found")
                return False
            
            if rate.target_currency not in self.currencies:
                self.logger.error(f"Target currency {rate.target_currency} not found")
                return False
            
            self.exchange_rates[rate.id] = rate
            self.logger.info(f"Exchange rate added: {rate.base_currency}/{rate.target_currency}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding exchange rate: {str(e)}")
            return False
    
    def update_exchange_rate(self, rate_id: str, updates: Dict[str, Any]) -> bool:
        """Update exchange rate"""
        try:
            rate = self.exchange_rates.get(rate_id)
            if not rate:
                self.logger.error(f"Exchange rate {rate_id} not found")
                return False
            
            # Update rate attributes
            for key, value in updates.items():
                if hasattr(rate, key):
                    setattr(rate, key, value)
            
            rate.updated_at = datetime.now()
            self.logger.info(f"Exchange rate updated: {rate.base_currency}/{rate.target_currency}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating exchange rate: {str(e)}")
            return False
    
    def get_exchange_rate(self, base_currency: str, target_currency: str, 
                         rate_type: ExchangeRateType = ExchangeRateType.SPOT) -> Optional[Decimal]:
        """Get exchange rate"""
        try:
            # First try to get from stored rates
            applicable_rates = [
                rate for rate in self.exchange_rates.values()
                if rate.base_currency == base_currency
                and rate.target_currency == target_currency
                and rate.type == rate_type
                and rate.effective_date <= date.today()
                and (not rate.expiry_date or rate.expiry_date >= date.today())
            ]
            
            if applicable_rates:
                return applicable_rates[-1].rate
            
            # If no stored rate, try to fetch from external source
            return self.fetch_exchange_rate(base_currency, target_currency, rate_type)
        except Exception as e:
            self.logger.error(f"Error getting exchange rate: {str(e)}")
            return None
    
    def fetch_exchange_rate(self, base_currency: str, target_currency: str, 
                          rate_type: ExchangeRateType) -> Optional[Decimal]:
        """Fetch exchange rate from external source"""
        try:
            base = self.currencies.get(base_currency)
            target = self.currencies.get(target_currency)
            
            if not base or not target:
                return None
            
            # Get appropriate API endpoint based on currency type
            if base.type == CurrencyType.FIAT:
                response = requests.get(f"{self.exchange_rate_sources['fiat']}{base.code}")
                if response.status_code == 200:
                    data = response.json()
                    return Decimal(str(data['rates'][target.code]))
            
            elif base.type == CurrencyType.CRYPTO:
                response = requests.get(
                    self.exchange_rate_sources['crypto'],
                    params={
                        'ids': base.code.lower(),
                        'vs_currencies': target.code.lower()
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return Decimal(str(data[base.code.lower()][target.code.lower()]))
            
            elif base.type == CurrencyType.COMMODITY:
                response = requests.get(self.exchange_rate_sources['commodity'])
                if response.status_code == 200:
                    data = response.json()
                    # Find commodity rate and convert to target currency
                    commodity_rate = next(
                        (item['price'] for item in data if item['symbol'] == base.code),
                        None
                    )
                    if commodity_rate:
                        # Convert commodity rate to target currency
                        usd_rate = self.get_exchange_rate("USD", target_currency)
                        if usd_rate:
                            return Decimal(str(commodity_rate)) * usd_rate
            
            return None
        except Exception as e:
            self.logger.error(f"Error fetching exchange rate: {str(e)}")
            return None
    
    def convert_amount(self, amount: Decimal, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """Convert amount between currencies"""
        try:
            if from_currency == to_currency:
                return amount
            
            rate = self.get_exchange_rate(from_currency, to_currency)
            if rate:
                return amount * rate
            
            return None
        except Exception as e:
            self.logger.error(f"Error converting amount: {str(e)}")
            return None
    
    def add_transaction(self, transaction: CurrencyTransaction) -> bool:
        """Add currency transaction"""
        try:
            if transaction.id in self.transactions:
                self.logger.warning(f"Transaction with ID {transaction.id} already exists")
                return False
            
            if transaction.currency not in self.currencies:
                self.logger.error(f"Currency {transaction.currency} not found")
                return False
            
            self.transactions[transaction.id] = transaction
            self.logger.info(f"Transaction added: {transaction.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding transaction: {str(e)}")
            return False
    
    def update_transaction(self, transaction_id: str, updates: Dict[str, Any]) -> bool:
        """Update currency transaction"""
        try:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                self.logger.error(f"Transaction {transaction_id} not found")
                return False
            
            # Update transaction attributes
            for key, value in updates.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            
            transaction.updated_at = datetime.now()
            self.logger.info(f"Transaction updated: {transaction.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating transaction: {str(e)}")
            return False
    
    def add_balance(self, balance: CurrencyBalance) -> bool:
        """Add currency balance"""
        try:
            if balance.id in self.balances:
                self.logger.warning(f"Balance with ID {balance.id} already exists")
                return False
            
            if balance.currency not in self.currencies:
                self.logger.error(f"Currency {balance.currency} not found")
                return False
            
            self.balances[balance.id] = balance
            self.logger.info(f"Balance added: {balance.currency}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding balance: {str(e)}")
            return False
    
    def update_balance(self, balance_id: str, updates: Dict[str, Any]) -> bool:
        """Update currency balance"""
        try:
            balance = self.balances.get(balance_id)
            if not balance:
                self.logger.error(f"Balance {balance_id} not found")
                return False
            
            # Update balance attributes
            for key, value in updates.items():
                if hasattr(balance, key):
                    setattr(balance, key, value)
            
            balance.updated_at = datetime.now()
            self.logger.info(f"Balance updated: {balance.currency}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating balance: {str(e)}")
            return False
    
    def get_balance_summary(self, account_id: str) -> Dict[str, Any]:
        """Get currency balance summary"""
        try:
            # Get all balances for account
            account_balances = [
                balance for balance in self.balances.values()
                if balance.account_id == account_id
            ]
            
            # Calculate total value in base currency
            total_value = Decimal('0')
            for balance in account_balances:
                if balance.currency != "USD":  # Assuming USD is base currency
                    rate = self.get_exchange_rate(balance.currency, "USD")
                    if rate:
                        total_value += balance.balance * rate
                else:
                    total_value += balance.balance
            
            return {
                "account_id": account_id,
                "balances": account_balances,
                "total_value": total_value,
                "last_updated": datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error getting balance summary: {str(e)}")
            return {}
    
    def generate_currency_report(self, report: CurrencyReport) -> bool:
        """Generate currency report"""
        try:
            # Get transactions for period
            period_transactions = [
                t for t in self.transactions.values()
                if report.period_start <= t.transaction_date.date() <= report.period_end
                and t.currency in report.currencies
            ]
            
            # Calculate report metrics
            report.content = {
                "period": {
                    "start": report.period_start.isoformat(),
                    "end": report.period_end.isoformat()
                },
                "currencies": report.currencies,
                "transactions": {
                    "total": len(period_transactions),
                    "by_currency": self.calculate_transactions_by_currency(period_transactions),
                    "by_date": self.calculate_transactions_by_date(period_transactions)
                },
                "exchange_rates": self.get_exchange_rate_summary(report.currencies),
                "balances": self.get_balance_summary_for_currencies(report.currencies)
            }
            
            # Save report
            report_file = os.path.join(os.path.dirname(__file__), 
                                     'currency_reports', 
                                     f'report_{report.id}.json')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report.content, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error generating currency report: {str(e)}")
            return False
    
    def calculate_transactions_by_currency(self, transactions: List[CurrencyTransaction]) -> Dict[str, Any]:
        """Calculate transaction metrics by currency"""
        try:
            metrics = {}
            for currency in set(t.currency for t in transactions):
                currency_transactions = [t for t in transactions if t.currency == currency]
                metrics[currency] = {
                    "count": len(currency_transactions),
                    "total_amount": sum(t.amount for t in currency_transactions),
                    "total_base_amount": sum(t.base_amount for t in currency_transactions)
                }
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating transactions by currency: {str(e)}")
            return {}
    
    def calculate_transactions_by_date(self, transactions: List[CurrencyTransaction]) -> Dict[str, Any]:
        """Calculate transaction metrics by date"""
        try:
            metrics = {}
            for transaction in transactions:
                date_key = transaction.transaction_date.date().isoformat()
                if date_key not in metrics:
                    metrics[date_key] = {
                        "count": 0,
                        "currencies": {}
                    }
                
                metrics[date_key]["count"] += 1
                if transaction.currency not in metrics[date_key]["currencies"]:
                    metrics[date_key]["currencies"][transaction.currency] = {
                        "count": 0,
                        "total_amount": Decimal('0'),
                        "total_base_amount": Decimal('0')
                    }
                
                metrics[date_key]["currencies"][transaction.currency]["count"] += 1
                metrics[date_key]["currencies"][transaction.currency]["total_amount"] += transaction.amount
                metrics[date_key]["currencies"][transaction.currency]["total_base_amount"] += transaction.base_amount
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating transactions by date: {str(e)}")
            return {}
    
    def get_exchange_rate_summary(self, currencies: List[str]) -> Dict[str, Any]:
        """Get exchange rate summary for currencies"""
        try:
            summary = {}
            for currency in currencies:
                if currency != "USD":  # Assuming USD is base currency
                    rate = self.get_exchange_rate("USD", currency)
                    if rate:
                        summary[currency] = {
                            "rate": rate,
                            "last_updated": datetime.now().isoformat()
                        }
            return summary
        except Exception as e:
            self.logger.error(f"Error getting exchange rate summary: {str(e)}")
            return {}
    
    def get_balance_summary_for_currencies(self, currencies: List[str]) -> Dict[str, Any]:
        """Get balance summary for currencies"""
        try:
            summary = {}
            for currency in currencies:
                currency_balances = [
                    b for b in self.balances.values()
                    if b.currency == currency
                ]
                if currency_balances:
                    summary[currency] = {
                        "total_balance": sum(b.balance for b in currency_balances),
                        "account_count": len(currency_balances),
                        "last_updated": max(b.last_updated for b in currency_balances).isoformat()
                    }
            return summary
        except Exception as e:
            self.logger.error(f"Error getting balance summary for currencies: {str(e)}")
            return {} 