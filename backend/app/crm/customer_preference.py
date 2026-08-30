from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class CustomerPreference(Base):
    """مدل ترجیحات مشتری"""
    
    __tablename__ = "customer_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, unique=True)
    preferred_contact_method = Column(String(50))  # روش ترجیحی ارتباط
    preferred_contact_time = Column(String(100))  # زمان ترجیحی ارتباط
    language = Column(String(10), default="fa")  # زبان ترجیحی
    timezone = Column(String(50))
    notification_preferences = Column(JSON)  # تنظیمات اعلان‌ها
    marketing_preferences = Column(JSON)  # تنظیمات بازاریابی
    communication_preferences = Column(JSON)  # تنظیمات ارتباطی
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ارتباطات
    customer = relationship("Customer", back_populates="preferences")
    
    def __repr__(self):
        return f"<CustomerPreference {self.customer_id}>" 