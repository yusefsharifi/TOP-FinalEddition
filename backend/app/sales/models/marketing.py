from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean, Float, JSON, Date, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    DIGITAL_ADS = "digital_ads"
    OFFLINE = "offline"

class MarketingCampaign(Base):
    """مدل کمپین‌های بازاریابی"""
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    campaign_type = Column(Enum(CampaignType))
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    budget = Column(Float, nullable=True)
    target_audience = Column(JSON)  # مشخصات مخاطبان هدف
    content = Column(JSON)  # محتوای کمپین
    metrics = Column(JSON)  # شاخص‌های عملکرد
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DiscountType(str, enum.Enum):
    PERCENTAGE = "percentage"  # تخفیف درصدی
    FIXED = "fixed"  # تخفیف مبلغی
    BUY_X_GET_Y = "buy_x_get_y"  # خرید X و دریافت Y
    BULK = "bulk"  # تخفیف عمده

class Discount(Base):
    """مدل تخفیفات"""
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    discount_type = Column(Enum(DiscountType))
    value = Column(Float)  # مقدار تخفیف (درصد یا مبلغ)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    min_purchase_amount = Column(Float, nullable=True)
    max_discount_amount = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    applicable_products = Column(JSON, nullable=True)  # لیست محصولات قابل تخفیف
    applicable_categories = Column(JSON, nullable=True)  # لیست دسته‌بندی‌های قابل تخفیف
    applicable_customers = Column(JSON, nullable=True)  # لیست مشتریان قابل تخفیف
    usage_limit = Column(Integer, nullable=True)  # محدودیت تعداد استفاده
    used_count = Column(Integer, default=0)  # تعداد استفاده شده
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MarketerRewardType(str, enum.Enum):
    COMMISSION = "commission"  # کمیسیون فروش
    NEW_CUSTOMER = "new_customer"  # پاداش جذب مشتری جدید
    CUSTOMER_RETENTION = "customer_retention"  # پاداش حفظ مشتری
    SPECIAL_PRODUCT = "special_product"  # پاداش فروش محصول خاص
    TARGET_ACHIEVEMENT = "target_achievement"  # پاداش دستیابی به هدف

class MarketerReward(Base):
    """مدل پاداش‌های بازاریاب"""
    __tablename__ = "marketer_rewards"

    id = Column(Integer, primary_key=True, index=True)
    marketer_id = Column(Integer, ForeignKey("users.id"))
    reward_type = Column(Enum(MarketerRewardType))
    amount = Column(Float)
    description = Column(Text)
    reference_id = Column(Integer, nullable=True)  # شناسه مرجع (مثلاً شناسه فروش یا مشتری)
    status = Column(String(50))  # وضعیت پرداخت
    payment_date = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    marketer = relationship("User", back_populates="rewards")

class MarketerPerformance(Base):
    """مدل عملکرد بازاریاب"""
    __tablename__ = "marketer_performance"

    id = Column(Integer, primary_key=True, index=True)
    marketer_id = Column(Integer, ForeignKey("users.id"))
    period_start = Column(Date)
    period_end = Column(Date)
    total_sales = Column(Float)
    total_commission = Column(Float)
    new_customers = Column(Integer)
    retained_customers = Column(Integer)
    special_product_sales = Column(Float)
    target_achievement_rate = Column(Float)
    metrics = Column(JSON)  # سایر شاخص‌های عملکرد
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    marketer = relationship("User", back_populates="performance") 