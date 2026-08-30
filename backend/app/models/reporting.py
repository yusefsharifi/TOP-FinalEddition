from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import enum

class ReportType(enum.Enum):
    SALES = "sales"
    INVENTORY = "inventory"
    CUSTOMER = "customer"
    FINANCIAL = "financial"
    CUSTOM = "custom"

class ReportFormat(enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    JSON = "json"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    report_type = Column(Enum(ReportType))
    query = Column(Text)
    parameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_template = Column(Boolean, default=False)
    
    creator = relationship("User")
    schedules = relationship("ReportSchedule", back_populates="report")
    executions = relationship("ReportExecution", back_populates="report")

class ReportSchedule(Base):
    __tablename__ = "report_schedules"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    name = Column(String, nullable=False)
    cron_expression = Column(String)
    format = Column(Enum(ReportFormat))
    recipients = Column(JSON)  # List of email addresses
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    report = relationship("Report", back_populates="schedules")

class ReportExecution(Base):
    __tablename__ = "report_executions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    status = Column(String)  # pending, running, completed, failed
    format = Column(Enum(ReportFormat))
    parameters = Column(JSON)
    file_path = Column(String)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    report = relationship("Report", back_populates="executions")
    creator = relationship("User")

class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    template_type = Column(Enum(ReportType))
    layout = Column(JSON)
    styles = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    creator = relationship("User") 