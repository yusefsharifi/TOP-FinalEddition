from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text, Table
from sqlalchemy.orm import relationship
from app.database import Base

class OrderStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"

class Order(Base):
    """مدل سفارش"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_rep_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), nullable=False, default=OrderStatus.DRAFT.value)
    payment_status = Column(String(50), nullable=False, default=PaymentStatus.PENDING.value)
    
    # اطلاعات قیمت
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # اطلاعات پرداخت
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    payment_date = Column(DateTime)
    
    # اطلاعات ارسال
    shipping_method = Column(String(50))
    shipping_address = Column(JSON)
    tracking_number = Column(String(100))
    estimated_delivery = Column(DateTime)
    actual_delivery = Column(DateTime)
    
    # اطلاعات مالی
    currency = Column(String(10), default="IRR")
    exchange_rate = Column(Float, default=1.0)
    commission_rate = Column(Float, default=0.0)
    commission_amount = Column(Float, default=0.0)
    
    # اطلاعات اضافی
    notes = Column(Text)
    internal_notes = Column(Text)
    tags = Column(JSON)
    custom_fields = Column(JSON)
    
    # اطلاعات سیستم
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime)
    cancelled_by = Column(Integer, ForeignKey("users.id"))
    cancelled_reason = Column(Text)
    
    # روابط
    customer = relationship("Customer", back_populates="orders")
    sales_rep = relationship("User", foreign_keys=[sales_rep_id])
    creator = relationship("User", foreign_keys=[created_by])
    canceller = relationship("User", foreign_keys=[cancelled_by])
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("OrderPayment", back_populates="order")
    shipments = relationship("OrderShipment", back_populates="order")

class OrderItem(Base):
    """مدل آیتم‌های سفارش"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"))
    
    # اطلاعات محصول
    product_name = Column(String(200), nullable=False)
    product_code = Column(String(50), nullable=False)
    variant_name = Column(String(200))
    variant_code = Column(String(50))
    sku = Column(String(50))
    
    # قیمت و مقدار
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # اطلاعات اضافی
    notes = Column(Text)
    custom_fields = Column(JSON)
    
    # روابط
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")

class OrderPayment(Base):
    """مدل پرداخت‌های سفارش"""
    __tablename__ = "order_payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_reference = Column(String(100))
    status = Column(String(50), nullable=False, default=PaymentStatus.PENDING.value)
    payment_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    order = relationship("Order", back_populates="payments")

class OrderShipment(Base):
    """مدل ارسال‌های سفارش"""
    __tablename__ = "order_shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    shipment_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    shipping_method = Column(String(50), nullable=False)
    tracking_number = Column(String(100))
    estimated_delivery = Column(DateTime)
    actual_delivery = Column(DateTime)
    shipping_address = Column(JSON, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    order = relationship("Order", back_populates="shipments") 