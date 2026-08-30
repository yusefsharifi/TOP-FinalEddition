from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Table
from sqlalchemy.orm import relationship
from app.database import Base

class PricingType(Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    DYNAMIC = "dynamic"
    VOLUME_BASED = "volume_based"
    CUSTOMER_BASED = "customer_based"

class PricingRuleType(Enum):
    TIME_BASED = "time_based"
    QUANTITY_BASED = "quantity_based"
    CUSTOMER_SEGMENT = "customer_segment"
    REGION_BASED = "region_based"
    SEASONAL = "seasonal"
    SPECIAL_EVENT = "special_event"

class PricingRule(Base):
    """مدل قوانین قیمت‌گذاری"""
    __tablename__ = "pricing_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    rule_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    priority = Column(Integer, default=0)  # اولویت اعمال قانون
    conditions = Column(JSON)  # شرایط اعمال قانون
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    price_adjustments = relationship("PriceAdjustment", back_populates="pricing_rule")

class PriceAdjustment(Base):
    """مدل تنظیمات قیمت"""
    __tablename__ = "price_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    pricing_rule_id = Column(Integer, ForeignKey("pricing_rules.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    customer_segment_id = Column(Integer, ForeignKey("customer_segments.id"))
    adjustment_type = Column(String(50), nullable=False)  # نوع تنظیم (افزایش، کاهش، درصدی و...)
    adjustment_value = Column(Float, nullable=False)  # مقدار تنظیم
    min_price = Column(Float)  # حداقل قیمت
    max_price = Column(Float)  # حداکثر قیمت
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    pricing_rule = relationship("PricingRule", back_populates="price_adjustments")
    product = relationship("Product", back_populates="price_adjustments")
    category = relationship("Category", back_populates="price_adjustments")
    customer_segment = relationship("CustomerSegment", back_populates="price_adjustments")

class DynamicPricing(Base):
    """مدل قیمت‌گذاری پویا"""
    __tablename__ = "dynamic_pricing"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    base_price = Column(Float, nullable=False)
    min_price = Column(Float)
    max_price = Column(Float)
    demand_factor = Column(Float, default=1.0)  # ضریب تقاضا
    supply_factor = Column(Float, default=1.0)  # ضریب عرضه
    competitor_prices = Column(JSON)  # قیمت‌های رقبا
    market_conditions = Column(JSON)  # شرایط بازار
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    product = relationship("Product", back_populates="dynamic_pricing")
    price_history = relationship("PriceHistory", back_populates="dynamic_pricing")

class PriceHistory(Base):
    """مدل تاریخچه قیمت"""
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    dynamic_pricing_id = Column(Integer, ForeignKey("dynamic_pricing.id"), nullable=False)
    price = Column(Float, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    reason = Column(String(500))  # دلیل تغییر قیمت
    created_at = Column(DateTime, default=datetime.utcnow)

    # روابط
    dynamic_pricing = relationship("DynamicPricing", back_populates="price_history")

class VolumeDiscount(Base):
    """مدل تخفیف حجمی"""
    __tablename__ = "volume_discounts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    min_quantity = Column(Integer, nullable=False)
    max_quantity = Column(Integer)
    discount_type = Column(String(50), nullable=False)  # نوع تخفیف (درصدی یا مبلغی)
    discount_value = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    product = relationship("Product", back_populates="volume_discounts")
    category = relationship("Category", back_populates="volume_discounts") 