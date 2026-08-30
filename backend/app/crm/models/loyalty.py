from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum

class MembershipTier(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class PointTransactionType(str, enum.Enum):
    EARN = "earn"
    REDEEM = "redeem"
    EXPIRE = "expire"
    ADJUST = "adjust"

class RewardStatus(str, enum.Enum):
    AVAILABLE = "available"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class CustomerMembership(Base):
    __tablename__ = "customer_memberships"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    tier = Column(Enum(MembershipTier), default=MembershipTier.BRONZE)
    points_balance = Column(Integer, default=0)
    total_points_earned = Column(Integer, default=0)
    total_points_redeemed = Column(Integer, default=0)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="membership")
    point_transactions = relationship("PointTransaction", back_populates="membership")
    rewards = relationship("CustomerReward", back_populates="membership")

class PointTransaction(Base):
    __tablename__ = "point_transactions"

    id = Column(Integer, primary_key=True, index=True)
    membership_id = Column(Integer, ForeignKey("customer_memberships.id"))
    transaction_type = Column(Enum(PointTransactionType))
    points = Column(Integer)
    description = Column(Text)
    reference_id = Column(String(255), nullable=True)  # برای ارتباط با تراکنش اصلی
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    membership = relationship("CustomerMembership", back_populates="point_transactions")

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    points_cost = Column(Integer)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    quantity_available = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer_rewards = relationship("CustomerReward", back_populates="reward")

class CustomerReward(Base):
    __tablename__ = "customer_rewards"

    id = Column(Integer, primary_key=True, index=True)
    membership_id = Column(Integer, ForeignKey("customer_memberships.id"))
    reward_id = Column(Integer, ForeignKey("rewards.id"))
    status = Column(Enum(RewardStatus), default=RewardStatus.AVAILABLE)
    points_spent = Column(Integer)
    redeemed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    membership = relationship("CustomerMembership", back_populates="rewards")
    reward = relationship("Reward", back_populates="customer_rewards") 