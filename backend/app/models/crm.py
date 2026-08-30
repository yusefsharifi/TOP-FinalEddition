from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    criteria = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customers = relationship("Customer", back_populates="segment")

class LoyaltyProgram(Base):
    __tablename__ = "loyalty_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    points_rate = Column(Float)  # Points per currency unit
    minimum_points_redemption = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tiers = relationship("LoyaltyTier", back_populates="program")

class LoyaltyTier(Base):
    __tablename__ = "loyalty_tiers"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("loyalty_programs.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    points_required = Column(Integer)
    benefits = Column(JSON)
    
    program = relationship("LoyaltyProgram", back_populates="tiers")
    customers = relationship("Customer", back_populates="loyalty_tier")

class CustomerFeedback(Base):
    __tablename__ = "customer_feedback"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    rating = Column(Integer)
    comment = Column(Text)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    
    customer = relationship("Customer", back_populates="feedback")

class CustomerInteraction(Base):
    __tablename__ = "customer_interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    interaction_type = Column(String)
    channel = Column(String)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    customer = relationship("Customer", back_populates="interactions")
    creator = relationship("User") 