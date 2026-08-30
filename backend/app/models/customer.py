from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text, Table
from sqlalchemy.orm import relationship
from app.database import Base

class CustomerType(Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    VIP = "vip"
    WHOLESALE = "wholesale"

class CustomerStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING = "pending"

class Customer(Base):
    """مدل مشتری"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_number = Column(String(50), unique=True, nullable=False)
    customer_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default=CustomerStatus.ACTIVE.value)
    
    # اطلاعات شخصی/شرکتی
    first_name = Column(String(100))
    last_name = Column(String(100))
    company_name = Column(String(200))
    tax_id = Column(String(50))
    national_id = Column(String(50))
    
    # اطلاعات تماس
    email = Column(String(200), unique=True)
    phone = Column(String(50))
    mobile = Column(String(50))
    fax = Column(String(50))
    
    # آدرس‌ها
    billing_address = Column(JSON)  # آدرس صورتحساب
    shipping_address = Column(JSON)  # آدرس ارسال
    additional_addresses = Column(JSON)  # آدرس‌های اضافی
    
    # اطلاعات مالی
    credit_limit = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    payment_terms = Column(String(50))
    preferred_payment_method = Column(String(50))
    
    # اطلاعات فروش
    sales_rep_id = Column(Integer, ForeignKey("users.id"))
    assigned_territory = Column(String(100))
    customer_group = Column(String(100))
    
    # اطلاعات اضافی
    notes = Column(Text)
    tags = Column(JSON)  # برچسب‌های مشتری
    custom_fields = Column(JSON)  # فیلدهای سفارشی
    
    # اطلاعات سیستم
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact_at = Column(DateTime)
    last_order_at = Column(DateTime)
    
    # روابط
    sales_rep = relationship("User", foreign_keys=[sales_rep_id], back_populates="customers")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_customers")
    contacts = relationship("CustomerContact", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    subscriptions = relationship("Subscription", back_populates="customer")

class CustomerContact(Base):
    """مدل مخاطبین مشتری"""
    __tablename__ = "customer_contacts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    position = Column(String(100))
    email = Column(String(200))
    phone = Column(String(50))
    mobile = Column(String(50))
    is_primary = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    customer = relationship("Customer", back_populates="contacts")

class CustomerNote(Base):
    """مدل یادداشت‌های مشتری"""
    __tablename__ = "customer_notes"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    note_type = Column(String(50))  # مثلاً "general", "support", "sales"
    content = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    customer = relationship("Customer")
    creator = relationship("User")

class CustomerActivity(Base):
    """مدل فعالیت‌های مشتری"""
    __tablename__ = "customer_activities"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # مثلاً "order", "payment", "contact"
    description = Column(Text, nullable=False)
    metadata = Column(JSON)  # اطلاعات اضافی فعالیت
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # روابط
    customer = relationship("Customer")
    creator = relationship("User")

class CustomerSegment(Base):
    """مدل بخش‌بندی مشتریان"""
    __tablename__ = "customer_segments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    criteria = Column(JSON)  # معیارهای بخش‌بندی
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    creator = relationship("User") 