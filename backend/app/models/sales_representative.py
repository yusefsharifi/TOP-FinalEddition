from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class SalesRepStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"

class SalesRepLevel(Enum):
    JUNIOR = "junior"
    SENIOR = "senior"
    MANAGER = "manager"
    DIRECTOR = "director"

class SalesRepresentative(Base):
    """مدل فروشنده"""
    __tablename__ = "sales_representatives"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default=SalesRepStatus.ACTIVE.value)
    level = Column(String(20), default=SalesRepLevel.JUNIOR.value)
    region_id = Column(Integer, ForeignKey("sales_regions.id"))
    manager_id = Column(Integer, ForeignKey("sales_representatives.id"))
    target_amount = Column(Float, default=0.0)
    commission_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    user = relationship("User", back_populates="sales_representative")
    region = relationship("SalesRegion", back_populates="sales_representatives")
    manager = relationship("SalesRepresentative", remote_side=[id], backref="subordinates")
    visits = relationship("SalesVisit", back_populates="sales_rep")
    performance_records = relationship("SalesPerformance", back_populates="sales_rep")

class SalesRegion(Base):
    """مدل منطقه فروش"""
    __tablename__ = "sales_regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    territory = Column(JSON)  # محدوده جغرافیایی منطقه
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    sales_representatives = relationship("SalesRepresentative", back_populates="region")
    customers = relationship("Customer", back_populates="sales_region")

class SalesVisit(Base):
    """مدل بازدید فروش"""
    __tablename__ = "sales_visits"

    id = Column(Integer, primary_key=True, index=True)
    sales_rep_id = Column(Integer, ForeignKey("sales_representatives.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    visit_date = Column(DateTime, nullable=False)
    visit_type = Column(String(50))  # نوع بازدید (مشاوره، پیگیری، فروش و...)
    notes = Column(String(1000))
    outcome = Column(String(500))  # نتیجه بازدید
    next_follow_up = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    sales_rep = relationship("SalesRepresentative", back_populates="visits")
    customer = relationship("Customer", back_populates="visits")

class SalesPerformance(Base):
    """مدل عملکرد فروش"""
    __tablename__ = "sales_performance"

    id = Column(Integer, primary_key=True, index=True)
    sales_rep_id = Column(Integer, ForeignKey("sales_representatives.id"), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    total_sales = Column(Float, default=0.0)
    target_achievement = Column(Float, default=0.0)  # درصد تحقق هدف
    new_customers = Column(Integer, default=0)
    customer_retention = Column(Float, default=0.0)  # درصد حفظ مشتریان
    average_order_value = Column(Float, default=0.0)
    metrics = Column(JSON)  # سایر شاخص‌های عملکرد
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    sales_rep = relationship("SalesRepresentative", back_populates="performance_records") 