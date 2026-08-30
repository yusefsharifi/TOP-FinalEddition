import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

class SystemMonitor:
    """کلاس نظارت بر یکپارچگی سیستم"""
    
    def __init__(self, db_url: str):
        self.logger = logging.getLogger(__name__)
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def check_accounting_integrity(self) -> List[Dict[str, Any]]:
        """بررسی یکپارچگی اسناد حسابداری با سایر ماژول‌ها"""
        try:
            issues = []
            session = self.Session()
            
            # بررسی اسناد حسابداری بدون معادل در انبار
            warehouse_query = """
            SELECT a.document_number, a.document_date, a.total_amount
            FROM accounting_documents a
            LEFT JOIN warehouse_documents w ON a.document_number = w.document_number
            WHERE w.document_number IS NULL
            AND a.document_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
            """
            warehouse_results = session.execute(text(warehouse_query))
            for row in warehouse_results:
                issues.append({
                    'type': 'accounting_warehouse_mismatch',
                    'document_number': row.document_number,
                    'document_date': row.document_date,
                    'amount': row.total_amount,
                    'message': f'سند حسابداری {row.document_number} در انبار ثبت نشده است',
                    'severity': 'high'
                })
            
            # بررسی اسناد حسابداری بدون معادل در خزانه‌داری
            treasury_query = """
            SELECT a.document_number, a.document_date, a.total_amount
            FROM accounting_documents a
            LEFT JOIN treasury_documents t ON a.document_number = t.document_number
            WHERE t.document_number IS NULL
            AND a.document_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
            """
            treasury_results = session.execute(text(treasury_query))
            for row in treasury_results:
                issues.append({
                    'type': 'accounting_treasury_mismatch',
                    'document_number': row.document_number,
                    'document_date': row.document_date,
                    'amount': row.total_amount,
                    'message': f'سند حسابداری {row.document_number} در خزانه‌داری ثبت نشده است',
                    'severity': 'high'
                })
            
            # بررسی اسناد خرید و فروش بدون معادل در حسابداری
            sales_query = """
            SELECT s.document_number, s.document_date, s.total_amount
            FROM sales_documents s
            LEFT JOIN accounting_documents a ON s.document_number = a.document_number
            WHERE a.document_number IS NULL
            AND s.document_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
            """
            sales_results = session.execute(text(sales_query))
            for row in sales_results:
                issues.append({
                    'type': 'sales_accounting_mismatch',
                    'document_number': row.document_number,
                    'document_date': row.document_date,
                    'amount': row.total_amount,
                    'message': f'سند فروش {row.document_number} در حسابداری ثبت نشده است',
                    'severity': 'high'
                })
            
            session.close()
            return issues
        except Exception as e:
            self.logger.error(f"خطا در بررسی یکپارچگی حسابداری: {str(e)}")
            return []
    
    def check_inventory_integrity(self) -> List[Dict[str, Any]]:
        """بررسی یکپارچگی موجودی انبار"""
        try:
            issues = []
            session = self.Session()
            
            # بررسی موجودی منفی
            negative_inventory_query = """
            SELECT p.product_code, p.product_name, i.quantity
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.quantity < 0
            """
            negative_results = session.execute(text(negative_inventory_query))
            for row in negative_results:
                issues.append({
                    'type': 'negative_inventory',
                    'product_code': row.product_code,
                    'product_name': row.product_name,
                    'quantity': row.quantity,
                    'message': f'موجودی محصول {row.product_name} ({row.product_code}) منفی است',
                    'severity': 'high'
                })
            
            # بررسی موجودی کمتر از حداقل
            low_inventory_query = """
            SELECT p.product_code, p.product_name, i.quantity, p.minimum_quantity
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.quantity < p.minimum_quantity
            """
            low_results = session.execute(text(low_inventory_query))
            for row in low_results:
                issues.append({
                    'type': 'low_inventory',
                    'product_code': row.product_code,
                    'product_name': row.product_name,
                    'quantity': row.quantity,
                    'minimum_quantity': row.minimum_quantity,
                    'message': f'موجودی محصول {row.product_name} ({row.product_code}) کمتر از حداقل است',
                    'severity': 'medium'
                })
            
            session.close()
            return issues
        except Exception as e:
            self.logger.error(f"خطا در بررسی یکپارچگی انبار: {str(e)}")
            return []
    
    def check_treasury_integrity(self) -> List[Dict[str, Any]]:
        """بررسی یکپارچگی خزانه‌داری"""
        try:
            issues = []
            session = self.Session()
            
            # بررسی اسناد خزانه‌داری بدون معادل در حسابداری
            treasury_query = """
            SELECT t.document_number, t.document_date, t.amount
            FROM treasury_documents t
            LEFT JOIN accounting_documents a ON t.document_number = a.document_number
            WHERE a.document_number IS NULL
            AND t.document_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
            """
            treasury_results = session.execute(text(treasury_query))
            for row in treasury_results:
                issues.append({
                    'type': 'treasury_accounting_mismatch',
                    'document_number': row.document_number,
                    'document_date': row.document_date,
                    'amount': row.amount,
                    'message': f'سند خزانه‌داری {row.document_number} در حسابداری ثبت نشده است',
                    'severity': 'high'
                })
            
            # بررسی موجودی نقدی منفی
            negative_cash_query = """
            SELECT account_number, account_name, balance
            FROM cash_accounts
            WHERE balance < 0
            """
            cash_results = session.execute(text(negative_cash_query))
            for row in cash_results:
                issues.append({
                    'type': 'negative_cash_balance',
                    'account_number': row.account_number,
                    'account_name': row.account_name,
                    'balance': row.balance,
                    'message': f'موجودی حساب {row.account_name} ({row.account_number}) منفی است',
                    'severity': 'high'
                })
            
            session.close()
            return issues
        except Exception as e:
            self.logger.error(f"خطا در بررسی یکپارچگی خزانه‌داری: {str(e)}")
            return []
    
    def check_sales_integrity(self) -> List[Dict[str, Any]]:
        """بررسی یکپارچگی فروش"""
        try:
            issues = []
            session = self.Session()
            
            # بررسی اسناد فروش بدون معادل در انبار
            sales_warehouse_query = """
            SELECT s.document_number, s.document_date, s.total_amount
            FROM sales_documents s
            LEFT JOIN warehouse_documents w ON s.document_number = w.document_number
            WHERE w.document_number IS NULL
            AND s.document_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
            """
            sales_results = session.execute(text(sales_warehouse_query))
            for row in sales_results:
                issues.append({
                    'type': 'sales_warehouse_mismatch',
                    'document_number': row.document_number,
                    'document_date': row.document_date,
                    'amount': row.total_amount,
                    'message': f'سند فروش {row.document_number} در انبار ثبت نشده است',
                    'severity': 'high'
                })
            
            # بررسی فروش‌های بدون موجودی
            no_inventory_query = """
            SELECT s.document_number, s.document_date, p.product_code, p.product_name, sd.quantity
            FROM sales_documents s
            JOIN sales_details sd ON s.id = sd.sales_document_id
            JOIN products p ON sd.product_id = p.id
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE i.quantity IS NULL OR i.quantity < sd.quantity
            AND s.document_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
            """
            inventory_results = session.execute(text(no_inventory_query))
            for row in inventory_results:
                issues.append({
                    'type': 'insufficient_inventory',
                    'document_number': row.document_number,
                    'product_code': row.product_code,
                    'product_name': row.product_name,
                    'quantity': row.quantity,
                    'message': f'موجودی کافی برای محصول {row.product_name} ({row.product_code}) در سند فروش {row.document_number} وجود ندارد',
                    'severity': 'high'
                })
            
            session.close()
            return issues
        except Exception as e:
            self.logger.error(f"خطا در بررسی یکپارچگی فروش: {str(e)}")
            return []
    
    def check_all_integrity(self) -> List[Dict[str, Any]]:
        """بررسی یکپارچگی تمام بخش‌های سیستم"""
        try:
            all_issues = []
            
            # بررسی یکپارچگی حسابداری
            accounting_issues = self.check_accounting_integrity()
            all_issues.extend(accounting_issues)
            
            # بررسی یکپارچگی انبار
            inventory_issues = self.check_inventory_integrity()
            all_issues.extend(inventory_issues)
            
            # بررسی یکپارچگی خزانه‌داری
            treasury_issues = self.check_treasury_integrity()
            all_issues.extend(treasury_issues)
            
            # بررسی یکپارچگی فروش
            sales_issues = self.check_sales_integrity()
            all_issues.extend(sales_issues)
            
            # مرتب‌سازی مسائل بر اساس شدت
            all_issues.sort(key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['severity']])
            
            return all_issues
        except Exception as e:
            self.logger.error(f"خطا در بررسی یکپارچگی کلی سیستم: {str(e)}")
            return []
    
    def send_notifications(self, issues: List[Dict[str, Any]]) -> bool:
        """ارسال اعلان‌ها برای مسائل شناسایی شده"""
        try:
            for issue in issues:
                # ارسال اعلان به کاربران مربوطه بر اساس نوع مسئله
                if issue['type'].startswith('accounting'):
                    self._notify_accounting_users(issue)
                elif issue['type'].startswith('inventory'):
                    self._notify_inventory_users(issue)
                elif issue['type'].startswith('treasury'):
                    self._notify_treasury_users(issue)
                elif issue['type'].startswith('sales'):
                    self._notify_sales_users(issue)
            
            return True
        except Exception as e:
            self.logger.error(f"خطا در ارسال اعلان‌ها: {str(e)}")
            return False
    
    def _notify_accounting_users(self, issue: Dict[str, Any]) -> None:
        """ارسال اعلان به کاربران حسابداری"""
        # TODO: پیاده‌سازی ارسال اعلان به کاربران حسابداری
        pass
    
    def _notify_inventory_users(self, issue: Dict[str, Any]) -> None:
        """ارسال اعلان به کاربران انبار"""
        # TODO: پیاده‌سازی ارسال اعلان به کاربران انبار
        pass
    
    def _notify_treasury_users(self, issue: Dict[str, Any]) -> None:
        """ارسال اعلان به کاربران خزانه‌داری"""
        # TODO: پیاده‌سازی ارسال اعلان به کاربران خزانه‌داری
        pass
    
    def _notify_sales_users(self, issue: Dict[str, Any]) -> None:
        """ارسال اعلان به کاربران فروش"""
        # TODO: پیاده‌سازی ارسال اعلان به کاربران فروش
        pass 