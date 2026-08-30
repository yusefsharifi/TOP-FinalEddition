import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import schedule
import time
from threading import Thread

from .system_monitor import SystemMonitor
from .notification_service import NotificationService

class SystemMonitorScheduler:
    """کلاس زمانبندی نظارت بر سیستم"""
    
    def __init__(self, db_url: str):
        self.logger = logging.getLogger(__name__)
        self.monitor = SystemMonitor(db_url)
        self.notification_service = NotificationService(db_url)
        self.running = False
        self.thread = None
    
    def start(self):
        """شروع زمانبندی نظارت"""
        try:
            if self.running:
                self.logger.warning("زمانبندی نظارت در حال اجراست")
                return
            
            self.running = True
            self.thread = Thread(target=self._run_scheduler)
            self.thread.daemon = True
            self.thread.start()
            
            self.logger.info("زمانبندی نظارت شروع شد")
        except Exception as e:
            self.logger.error(f"خطا در شروع زمانبندی نظارت: {str(e)}")
    
    def stop(self):
        """توقف زمانبندی نظارت"""
        try:
            if not self.running:
                self.logger.warning("زمانبندی نظارت متوقف است")
                return
            
            self.running = False
            if self.thread:
                self.thread.join()
            
            self.logger.info("زمانبندی نظارت متوقف شد")
        except Exception as e:
            self.logger.error(f"خطا در توقف زمانبندی نظارت: {str(e)}")
    
    def _run_scheduler(self):
        """اجرای زمانبندی نظارت"""
        try:
            # تنظیم زمانبندی بررسی‌ها
            schedule.every(1).hours.do(self._check_system_integrity)
            schedule.every(1).days.at("00:00").do(self._daily_report)
            schedule.every(1).weeks.at("00:00").do(self._weekly_report)
            
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # بررسی هر دقیقه
        except Exception as e:
            self.logger.error(f"خطا در اجرای زمانبندی نظارت: {str(e)}")
    
    def _check_system_integrity(self):
        """بررسی یکپارچگی سیستم"""
        try:
            # بررسی یکپارچگی تمام بخش‌ها
            issues = self.monitor.check_all_integrity()
            
            if issues:
                # ارسال اعلان‌ها برای مسائل شناسایی شده
                self._send_notifications_for_issues(issues)
            
            self.logger.info(f"بررسی یکپارچگی سیستم انجام شد. {len(issues)} مسئله شناسایی شد.")
        except Exception as e:
            self.logger.error(f"خطا در بررسی یکپارچگی سیستم: {str(e)}")
    
    def _daily_report(self):
        """گزارش روزانه"""
        try:
            # بررسی یکپارچگی سیستم
            issues = self.monitor.check_all_integrity()
            
            # ایجاد گزارش روزانه
            report = self._create_daily_report(issues)
            
            # ارسال گزارش به مدیران سیستم
            self._send_report_to_managers(report)
            
            self.logger.info("گزارش روزانه ارسال شد")
        except Exception as e:
            self.logger.error(f"خطا در ایجاد گزارش روزانه: {str(e)}")
    
    def _weekly_report(self):
        """گزارش هفتگی"""
        try:
            # بررسی یکپارچگی سیستم
            issues = self.monitor.check_all_integrity()
            
            # ایجاد گزارش هفتگی
            report = self._create_weekly_report(issues)
            
            # ارسال گزارش به مدیران سیستم
            self._send_report_to_managers(report)
            
            self.logger.info("گزارش هفتگی ارسال شد")
        except Exception as e:
            self.logger.error(f"خطا در ایجاد گزارش هفتگی: {str(e)}")
    
    def _send_notifications_for_issues(self, issues: List[Dict[str, Any]]) -> None:
        """ارسال اعلان‌ها برای مسائل شناسایی شده"""
        try:
            notifications = []
            
            for issue in issues:
                # تعیین کاربران مربوطه بر اساس نوع مسئله
                user_ids = self._get_related_users(issue)
                
                # ایجاد اعلان برای هر کاربر
                for user_id in user_ids:
                    notifications.append({
                        'user_id': user_id,
                        'title': f'هشدار سیستم - {issue["type"]}',
                        'message': issue['message'],
                        'severity': issue['severity']
                    })
            
            # ارسال اعلان‌ها
            if notifications:
                self.notification_service.send_batch_notifications(notifications)
        except Exception as e:
            self.logger.error(f"خطا در ارسال اعلان‌ها: {str(e)}")
    
    def _get_related_users(self, issue: Dict[str, Any]) -> List[int]:
        """تعیین کاربران مربوطه بر اساس نوع مسئله"""
        try:
            session = self.monitor.Session()
            
            # تعیین نقش‌های مربوطه بر اساس نوع مسئله
            roles = []
            if issue['type'].startswith('accounting'):
                roles = ['accountant', 'accounting_manager']
            elif issue['type'].startswith('inventory'):
                roles = ['warehouse_keeper', 'inventory_manager']
            elif issue['type'].startswith('treasury'):
                roles = ['treasury_officer', 'treasury_manager']
            elif issue['type'].startswith('sales'):
                roles = ['sales_officer', 'sales_manager']
            
            # دریافت شناسه کاربران با نقش‌های مربوطه
            query = """
            SELECT DISTINCT u.id
            FROM users u
            JOIN user_roles ur ON u.id = ur.user_id
            JOIN roles r ON ur.role_id = r.id
            WHERE r.name IN :roles
            """
            
            results = session.execute(text(query), {'roles': tuple(roles)})
            user_ids = [row.id for row in results]
            
            session.close()
            return user_ids
        except Exception as e:
            self.logger.error(f"خطا در تعیین کاربران مربوطه: {str(e)}")
            return []
    
    def _create_daily_report(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ایجاد گزارش روزانه"""
        try:
            report = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_issues': len(issues),
                'issues_by_type': {},
                'issues_by_severity': {
                    'high': 0,
                    'medium': 0,
                    'low': 0
                }
            }
            
            for issue in issues:
                # شمارش مسائل بر اساس نوع
                issue_type = issue['type'].split('_')[0]
                report['issues_by_type'][issue_type] = report['issues_by_type'].get(issue_type, 0) + 1
                
                # شمارش مسائل بر اساس شدت
                report['issues_by_severity'][issue['severity']] += 1
            
            return report
        except Exception as e:
            self.logger.error(f"خطا در ایجاد گزارش روزانه: {str(e)}")
            return {}
    
    def _create_weekly_report(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ایجاد گزارش هفتگی"""
        try:
            report = {
                'start_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d'),
                'total_issues': len(issues),
                'issues_by_type': {},
                'issues_by_severity': {
                    'high': 0,
                    'medium': 0,
                    'low': 0
                },
                'trends': {}
            }
            
            for issue in issues:
                # شمارش مسائل بر اساس نوع
                issue_type = issue['type'].split('_')[0]
                report['issues_by_type'][issue_type] = report['issues_by_type'].get(issue_type, 0) + 1
                
                # شمارش مسائل بر اساس شدت
                report['issues_by_severity'][issue['severity']] += 1
            
            # محاسبه روندها
            report['trends'] = self._calculate_weekly_trends()
            
            return report
        except Exception as e:
            self.logger.error(f"خطا در ایجاد گزارش هفتگی: {str(e)}")
            return {}
    
    def _calculate_weekly_trends(self) -> Dict[str, Any]:
        """محاسبه روندهای هفتگی"""
        try:
            session = self.monitor.Session()
            
            # دریافت تعداد مسائل در هر روز هفته
            query = """
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM issues
            WHERE created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
            """
            
            results = session.execute(text(query))
            daily_counts = {row.date: row.count for row in results}
            
            # محاسبه روند
            dates = sorted(daily_counts.keys())
            if len(dates) >= 2:
                trend = (daily_counts[dates[-1]] - daily_counts[dates[0]]) / len(dates)
            else:
                trend = 0
            
            session.close()
            return {
                'daily_counts': daily_counts,
                'trend': trend
            }
        except Exception as e:
            self.logger.error(f"خطا در محاسبه روندهای هفتگی: {str(e)}")
            return {}
    
    def _send_report_to_managers(self, report: Dict[str, Any]) -> None:
        """ارسال گزارش به مدیران سیستم"""
        try:
            session = self.monitor.Session()
            
            # دریافت شناسه مدیران سیستم
            query = """
            SELECT DISTINCT u.id
            FROM users u
            JOIN user_roles ur ON u.id = ur.user_id
            JOIN roles r ON ur.role_id = r.id
            WHERE r.name = 'system_manager'
            """
            
            results = session.execute(text(query))
            manager_ids = [row.id for row in results]
            
            session.close()
            
            # ارسال گزارش به هر مدیر
            for manager_id in manager_ids:
                self.notification_service.send_notification(
                    user_id=manager_id,
                    title='گزارش سیستم',
                    message=self._format_report_message(report),
                    severity='medium'
                )
        except Exception as e:
            self.logger.error(f"خطا در ارسال گزارش به مدیران: {str(e)}")
    
    def _format_report_message(self, report: Dict[str, Any]) -> str:
        """فرمت‌بندی پیام گزارش"""
        try:
            date_info = report.get('date')
            if not date_info:
                start_date = report.get('start_date', '')
                end_date = report.get('end_date', '')
                date_info = f"{start_date} تا {end_date}"
            
            message = f"گزارش سیستم برای دوره {date_info}\n\n"
            message += f"تعداد کل مسائل: {report.get('total_issues', 0)}\n\n"
            
            message += "توزیع مسائل بر اساس نوع:\n"
            for issue_type, count in report.get('issues_by_type', {}).items():
                message += f"- {issue_type}: {count}\n"
            
            message += "\nتوزیع مسائل بر اساس شدت:\n"
            for severity, count in report.get('issues_by_severity', {}).items():
                message += f"- {severity}: {count}\n"
            
            if 'trends' in report:
                message += f"\nروند هفتگی: {report['trends'].get('trend', 0):.2f}\n"
            
            return message
        except Exception as e:
            self.logger.error(f"خطا در فرمت‌بندی پیام گزارش: {str(e)}")
            return "" 