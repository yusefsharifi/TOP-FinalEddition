import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.sales.models.report import (
    Report, ReportData, ReportTemplate, ReportSchedule,
    ReportType, ReportStatus
)
from app.sales.services.report_service import ReportService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class TestReportService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی تست"""
        # ایجاد دیتابیس تست
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # ایجاد سرویس
        self.service = ReportService(self.session)
        
        # ایجاد داده‌های تست
        self._create_test_data()
    
    def tearDown(self):
        """پاکسازی تست"""
        self.session.close()
    
    def _create_test_data(self):
        """ایجاد داده‌های تست"""
        # ایجاد گزارش تست
        self.test_report = Report(
            report_number="REP-001",
            report_type=ReportType.SALES_SUMMARY.value,
            title="گزارش خلاصه فروش",
            description="گزارش خلاصه فروش ماهانه",
            status=ReportStatus.PENDING.value,
            parameters={"start_date": datetime.now(), "end_date": datetime.now() + timedelta(days=30)},
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            created_by=1
        )
        self.session.add(self.test_report)
        self.session.commit()
        
        # ایجاد داده گزارش تست
        self.test_report_data = ReportData(
            report_id=self.test_report.id,
            data_type="chart",
            title="نمودار فروش",
            description="نمودار فروش روزانه",
            data={"labels": [], "values": []}
        )
        self.session.add(self.test_report_data)
        self.session.commit()
    
    def test_create_report(self):
        """تست ایجاد گزارش"""
        data = {
            "report_number": "REP-002",
            "report_type": ReportType.PRODUCT_PERFORMANCE.value,
            "title": "گزارش عملکرد محصولات",
            "description": "گزارش عملکرد محصولات ماهانه",
            "status": ReportStatus.PENDING.value,
            "parameters": {"start_date": datetime.now(), "end_date": datetime.now() + timedelta(days=30)},
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=30),
            "created_by": 1
        }
        report = self.service.create_report(data)
        self.assertIsNotNone(report)
        self.assertEqual(report.report_number, "REP-002")
    
    def test_get_report(self):
        """تست دریافت گزارش"""
        report = self.service.get_report(self.test_report.id)
        self.assertIsNotNone(report)
        self.assertEqual(report.id, self.test_report.id)
    
    def test_update_report_status(self):
        """تست به‌روزرسانی وضعیت گزارش"""
        report = self.service.update_report_status(
            self.test_report.id, ReportStatus.COMPLETED.value
        )
        self.assertIsNotNone(report)
        self.assertEqual(report.status, ReportStatus.COMPLETED.value)
    
    def test_add_report_data(self):
        """تست افزودن داده به گزارش"""
        data = {
            "report_id": self.test_report.id,
            "data_type": "table",
            "title": "جدول فروش",
            "description": "جدول فروش روزانه",
            "data": {"headers": [], "rows": []}
        }
        report_data = self.service.add_report_data(data)
        self.assertIsNotNone(report_data)
        self.assertEqual(report_data.data_type, "table")
    
    def test_create_report_template(self):
        """تست ایجاد قالب گزارش"""
        data = {
            "name": "قالب خلاصه فروش",
            "description": "قالب پیش‌فرض گزارش خلاصه فروش",
            "report_type": ReportType.SALES_SUMMARY.value,
            "parameters": {"start_date": None, "end_date": None},
            "layout": {"sections": []},
            "created_by": 1,
            "is_public": True
        }
        template = self.service.create_report_template(data)
        self.assertIsNotNone(template)
        self.assertEqual(template.name, "قالب خلاصه فروش")
    
    def test_get_report_template(self):
        """تست دریافت قالب گزارش"""
        # ابتدا یک قالب ایجاد می‌کنیم
        template_data = {
            "name": "قالب خلاصه فروش",
            "description": "قالب پیش‌فرض گزارش خلاصه فروش",
            "report_type": ReportType.SALES_SUMMARY.value,
            "parameters": {"start_date": None, "end_date": None},
            "layout": {"sections": []},
            "created_by": 1,
            "is_public": True
        }
        template = self.service.create_report_template(template_data)
        
        # سپس قالب را دریافت می‌کنیم
        retrieved_template = self.service.get_report_template(template.id)
        self.assertIsNotNone(retrieved_template)
        self.assertEqual(retrieved_template.id, template.id)
    
    def test_create_report_schedule(self):
        """تست ایجاد زمانبندی گزارش"""
        data = {
            "report_id": self.test_report.id,
            "schedule_type": "daily",
            "schedule_time": "09:00",
            "days_of_week": [1, 2, 3, 4, 5],
            "days_of_month": None,
            "recipients": [1, 2],
            "is_active": True
        }
        schedule = self.service.create_report_schedule(data)
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule.schedule_type, "daily")
    
    def test_get_report_schedule(self):
        """تست دریافت زمانبندی گزارش"""
        # ابتدا یک زمانبندی ایجاد می‌کنیم
        schedule_data = {
            "report_id": self.test_report.id,
            "schedule_type": "daily",
            "schedule_time": "09:00",
            "days_of_week": [1, 2, 3, 4, 5],
            "days_of_month": None,
            "recipients": [1, 2],
            "is_active": True
        }
        schedule = self.service.create_report_schedule(schedule_data)
        
        # سپس زمانبندی را دریافت می‌کنیم
        retrieved_schedule = self.service.get_report_schedule(schedule.id)
        self.assertIsNotNone(retrieved_schedule)
        self.assertEqual(retrieved_schedule.id, schedule.id)
    
    def test_get_user_reports(self):
        """تست دریافت گزارش‌های کاربر"""
        reports = self.service.get_user_reports(1)
        self.assertIsNotNone(reports)
        self.assertIsInstance(reports, list)
    
    def test_get_public_templates(self):
        """تست دریافت قالب‌های عمومی"""
        # ابتدا یک قالب عمومی ایجاد می‌کنیم
        template_data = {
            "name": "قالب خلاصه فروش",
            "description": "قالب پیش‌فرض گزارش خلاصه فروش",
            "report_type": ReportType.SALES_SUMMARY.value,
            "parameters": {"start_date": None, "end_date": None},
            "layout": {"sections": []},
            "created_by": 1,
            "is_public": True
        }
        self.service.create_report_template(template_data)
        
        # سپس قالب‌های عمومی را دریافت می‌کنیم
        templates = self.service.get_public_templates()
        self.assertIsNotNone(templates)
        self.assertIsInstance(templates, list)
    
    def test_get_scheduled_reports(self):
        """تست دریافت گزارش‌های زمانبندی شده"""
        # ابتدا یک گزارش زمانبندی شده ایجاد می‌کنیم
        report_data = {
            "report_number": "REP-003",
            "report_type": ReportType.SALES_SUMMARY.value,
            "title": "گزارش خلاصه فروش",
            "description": "گزارش خلاصه فروش ماهانه",
            "status": ReportStatus.PENDING.value,
            "parameters": {"start_date": datetime.now(), "end_date": datetime.now() + timedelta(days=30)},
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=30),
            "created_by": 1,
            "is_scheduled": True,
            "next_run_at": datetime.now() + timedelta(days=1)
        }
        self.service.create_report(report_data)
        
        # سپس گزارش‌های زمانبندی شده را دریافت می‌کنیم
        reports = self.service.get_scheduled_reports()
        self.assertIsNotNone(reports)
        self.assertIsInstance(reports, list)
    
    def test_generate_sales_summary(self):
        """تست تولید گزارش خلاصه فروش"""
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=30)
        data = self.service.generate_sales_summary(start_date, end_date)
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
    
    def test_generate_product_performance(self):
        """تست تولید گزارش عملکرد محصولات"""
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=30)
        data = self.service.generate_product_performance(start_date, end_date)
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
    
    def test_generate_customer_analysis(self):
        """تست تولید گزارش تحلیل مشتریان"""
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=30)
        data = self.service.generate_customer_analysis(start_date, end_date)
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
    
    def test_generate_sales_rep_performance(self):
        """تست تولید گزارش عملکرد نمایندگان فروش"""
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=30)
        data = self.service.generate_sales_rep_performance(start_date, end_date)
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
    
    def test_generate_regional_analysis(self):
        """تست تولید گزارش تحلیل منطقه‌ای"""
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=30)
        data = self.service.generate_regional_analysis(start_date, end_date)
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
    
    def test_generate_trend_analysis(self):
        """تست تولید گزارش تحلیل روند"""
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=30)
        data = self.service.generate_trend_analysis(start_date, end_date)
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
    
    def test_generate_inventory_analysis(self):
        """تست تولید گزارش تحلیل موجودی"""
        data = self.service.generate_inventory_analysis()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict) 