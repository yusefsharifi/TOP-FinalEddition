from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Table, Text, Interval
from sqlalchemy.orm import relationship
from app.database import Base

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"

class SubscriptionType(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class Subscription(Base):
    """مدل اشتراک"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    subscription_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_rep_id = Column(Integer, ForeignKey("sales_representatives.id"))
    subscription_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default=SubscriptionStatus.PENDING.value)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    next_delivery_date = Column(DateTime)
    delivery_interval = Column(String(50))  # مثلاً "1 month"
    total_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    final_amount = Column(Float, default=0.0)
    payment_method = Column(String(50))
    shipping_address = Column(JSON)
    billing_address = Column(JSON)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    customer = relationship("Customer", back_populates="subscriptions")
    sales_rep = relationship("SalesRepresentative", back_populates="subscriptions")
    items = relationship("SubscriptionItem", back_populates="subscription")
    deliveries = relationship("SubscriptionDelivery", back_populates="subscription")
    payments = relationship("SubscriptionPayment", back_populates="subscription")

class SubscriptionItem(Base):
    """مدل آیتم‌های اشتراک"""
    __tablename__ = "subscription_items"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    subscription = relationship("Subscription", back_populates="items")
    product = relationship("Product", back_populates="subscription_items")

class SubscriptionDelivery(Base):
    """مدل تحویل‌های اشتراک"""
    __tablename__ = "subscription_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    delivery_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50))
    scheduled_date = Column(DateTime, nullable=False)
    actual_delivery_date = Column(DateTime)
    shipping_method = Column(String(50))
    tracking_number = Column(String(100))
    shipping_address = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    subscription = relationship("Subscription", back_populates="deliveries")
    items = relationship("SubscriptionDeliveryItem", back_populates="delivery")

class SubscriptionDeliveryItem(Base):
    """مدل آیتم‌های تحویل اشتراک"""
    __tablename__ = "subscription_delivery_items"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("subscription_deliveries.id"), nullable=False)
    subscription_item_id = Column(Integer, ForeignKey("subscription_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    delivery = relationship("SubscriptionDelivery", back_populates="items")
    subscription_item = relationship("SubscriptionItem")

class SubscriptionPayment(Base):
    """مدل پرداخت‌های اشتراک"""
    __tablename__ = "subscription_payments"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    payment_number = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    transaction_id = Column(String(100))
    status = Column(String(50))
    payment_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    subscription = relationship("Subscription", back_populates="payments") 