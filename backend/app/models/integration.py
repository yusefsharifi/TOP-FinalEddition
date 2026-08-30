from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import enum

class IntegrationType(enum.Enum):
    PAYMENT = "payment"
    SHIPPING = "shipping"
    ACCOUNTING = "accounting"
    ECOMMERCE = "ecommerce"
    EMAIL = "email"
    SMS = "sms"

class IntegrationStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(IntegrationType))
    provider = Column(String)
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.INACTIVE)
    config = Column(JSON)
    credentials = Column(JSON)
    last_sync = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sync_logs = relationship("IntegrationSyncLog", back_populates="integration")

class IntegrationSyncLog(Base):
    __tablename__ = "integration_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"))
    sync_type = Column(String)  # full, incremental
    status = Column(String)  # success, failed, partial
    records_processed = Column(Integer)
    records_failed = Column(Integer)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    integration = relationship("Integration", back_populates="sync_logs")

class PaymentGateway(Base):
    __tablename__ = "payment_gateways"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    provider = Column(String)
    is_active = Column(Boolean, default=True)
    config = Column(JSON)
    credentials = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transactions = relationship("PaymentTransaction", back_populates="gateway")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    gateway_id = Column(Integer, ForeignKey("payment_gateways.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    transaction_id = Column(String, unique=True)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    payment_method = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    gateway = relationship("PaymentGateway", back_populates="transactions")
    order = relationship("Order")

class ShippingProvider(Base):
    __tablename__ = "shipping_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    provider = Column(String)
    is_active = Column(Boolean, default=True)
    config = Column(JSON)
    credentials = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    shipments = relationship("Shipment", back_populates="provider")

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("shipping_providers.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    tracking_number = Column(String, unique=True)
    status = Column(String)
    shipping_method = Column(String)
    cost = Column(Float)
    estimated_delivery = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    provider = relationship("ShippingProvider", back_populates="shipments")
    order = relationship("Order") 