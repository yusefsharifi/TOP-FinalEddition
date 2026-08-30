from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean, Float, JSON, Date, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
from app.crm.models.loyalty import MembershipTier
import enum

class PointMultiplierType(str, enum.Enum):
    TIER = "tier"  # ضریب بر اساس سطح عضویت
    SPECIAL_DAY = "special_day"  # ضریب برای روزهای خاص
    BEHAVIOR = "behavior"  # ضریب بر اساس رفتار مشتری

class PointMultiplier(Base):
    """مدل ضریب امتیازدهی"""
    __tablename__ = "point_multipliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    multiplier_type = Column(Enum(PointMultiplierType))
    multiplier_value = Column(Float)  # مقدار ضریب (مثلاً 1.5 برای 50% بیشتر)
    tier = Column(Enum(MembershipTier), nullable=True)  # برای ضریب بر اساس سطح
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SpecialDay(Base):
    """مدل روزهای خاص برای امتیازدهی مضاعف"""
    __tablename__ = "special_days"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    date = Column(Date)  # تاریخ روز خاص
    point_multiplier = Column(Float)  # ضریب امتیازدهی برای این روز
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PointRule(Base):
    """مدل قوانین امتیازدهی هوشمند"""
    __tablename__ = "point_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    condition_type = Column(String(50))  # نوع شرط (مثلاً: purchase_amount, visit_count, etc.)
    condition_value = Column(JSON)  # مقدار شرط
    points = Column(Integer)  # امتیاز تعلق گرفته
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CustomerBehavior(Base):
    """مدل رفتار مشتری برای امتیازدهی هوشمند"""
    __tablename__ = "customer_behaviors"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    behavior_type = Column(String(50))  # نوع رفتار (مثلاً: purchase_frequency, visit_frequency, etc.)
    behavior_value = Column(JSON)  # مقدار رفتار
    last_updated = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="behaviors")

class RewardType(str, enum.Enum):
    EXPERIENTIAL = "experiential"  # پاداش‌های تجربه‌ای
    PERSONALIZED = "personalized"  # پاداش‌های شخصی‌سازی شده
    PARTNER = "partner"  # پاداش‌های مشارکتی
    STANDARD = "standard"  # پاداش‌های استاندارد

class ExperientialReward(Base):
    """مدل پاداش‌های تجربه‌ای"""
    __tablename__ = "experiential_rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    points_cost = Column(Integer)
    experience_type = Column(String(50))  # نوع تجربه (مثلاً: سفر، دوره آموزشی، رویداد)
    experience_details = Column(JSON)  # جزئیات تجربه
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    quantity_available = Column(Integer)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PersonalizedReward(Base):
    """مدل پاداش‌های شخصی‌سازی شده"""
    __tablename__ = "personalized_rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    points_cost = Column(Integer)
    personalization_options = Column(JSON)  # گزینه‌های شخصی‌سازی
    validity_days = Column(Integer)  # مدت اعتبار به روز
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PartnerReward(Base):
    """مدل پاداش‌های مشارکتی با برندهای دیگر"""
    __tablename__ = "partner_rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    points_cost = Column(Integer)
    partner_name = Column(String(255))
    partner_reward_details = Column(JSON)  # جزئیات پاداش شریک
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    quantity_available = Column(Integer)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CustomerRewardPreference(Base):
    """مدل ترجیحات پاداش مشتری"""
    __tablename__ = "customer_reward_preferences"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    preferred_reward_types = Column(JSON)  # لیست انواع پاداش‌های ترجیحی
    preferred_partners = Column(JSON, nullable=True)  # لیست شرکای ترجیحی
    preferred_experiences = Column(JSON, nullable=True)  # لیست تجربیات ترجیحی
    last_updated = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="reward_preferences")

class RewardRedemptionHistory(Base):
    """مدل تاریخچه استفاده از پاداش‌ها"""
    __tablename__ = "reward_redemption_histories"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    reward_type = Column(Enum(RewardType))
    reward_id = Column(Integer)  # ID پاداش استفاده شده
    points_cost = Column(Integer)
    redemption_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50))  # وضعیت استفاده (مثلاً: completed, cancelled, expired)
    feedback = Column(Text, nullable=True)  # بازخورد مشتری
    metadata = Column(JSON, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="redemption_history") 