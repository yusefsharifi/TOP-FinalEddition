from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Table, Text, Interval
from sqlalchemy.orm import relationship
from app.database import Base

class ReportType(Enum):
    SALES_SUMMARY = "sales_summary"
    PRODUCT_PERFORMANCE = "product_performance"
    CUSTOMER_ANALYSIS = "customer_analysis"
    SALES_REP_PERFORMANCE = "sales_rep_performance"
    REGIONAL_ANALYSIS = "regional_analysis"
    TREND_ANALYSIS = "trend_analysis"
    INVENTORY_ANALYSIS = "inventory_analysis"
    CUSTOM = "custom"

class ReportStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Report(Base):
    """مدل گزارش"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(50), unique=True, nullable=False)
    report_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default=ReportStatus.PENDING.value)
    parameters = Column(JSON)  # پارامترهای گزارش
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    is_scheduled = Column(Boolean, default=False)
    schedule_interval = Column(String(50))  # مثلاً "1 day", "1 week", "1 month"
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)

    # روابط
    creator = relationship("User", back_populates="reports")
    data = relationship("ReportData", back_populates="report")

class ReportData(Base):
    """مدل داده‌های گزارش"""
    __tablename__ = "report_data"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    data_type = Column(String(50), nullable=False)  # مثلاً "chart", "table", "metric"
    title = Column(String(200))
    description = Column(Text)
    data = Column(JSON)  # داده‌های گزارش
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    report = relationship("Report", back_populates="data")

class ReportTemplate(Base):
    """مدل قالب گزارش"""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    report_type = Column(String(50), nullable=False)
    parameters = Column(JSON)  # پارامترهای پیش‌فرض قالب
    layout = Column(JSON)  # ساختار و چیدمان گزارش
    created_by = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    creator = relationship("User", back_populates="report_templates")

class ReportSchedule(Base):
    """مدل زمانبندی گزارش"""
    __tablename__ = "report_schedules"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    schedule_type = Column(String(50), nullable=False)  # مثلاً "daily", "weekly", "monthly"
    schedule_time = Column(String(50))  # زمان اجرا (مثلاً "09:00")
    days_of_week = Column(JSON)  # روزهای هفته برای گزارش هفتگی
    days_of_month = Column(JSON)  # روزهای ماه برای گزارش ماهانه
    recipients = Column(JSON)  # لیست گیرندگان گزارش
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    report = relationship("Report") 