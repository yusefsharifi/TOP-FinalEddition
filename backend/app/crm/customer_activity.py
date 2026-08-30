from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base

class ActivityType(enum.Enum):
    MEETING = "meeting"
    CALL = "call"
    EMAIL = "email"
    VISIT = "visit"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    OTHER = "other"

class ActivityStatus(enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CustomerActivity(Base):
    """مدل فعالیت‌های مشتری"""
    
    __tablename__ = "customer_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    type = Column(Enum(ActivityType), nullable=False)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.PLANNED)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration = Column(Integer)  # مدت زمان به دقیقه
    priority = Column(Integer, default=0)  # اولویت (0: پایین، 1: متوسط، 2: بالا)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    metadata = Column(JSON)  # برای ذخیره اطلاعات اضافی
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ارتباطات
    customer = relationship("Customer", back_populates="activities")
    
    def __repr__(self):
        return f"<CustomerActivity {self.title}>" 