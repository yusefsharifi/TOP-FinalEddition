from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import enum

class DeviceType(enum.Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"

class PushNotification(Base):
    __tablename__ = "push_notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(Text)
    data = Column(JSON)
    priority = Column(String)  # high, normal, low
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    
    recipients = relationship("PushNotificationRecipient", back_populates="notification")

class PushNotificationRecipient(Base):
    __tablename__ = "push_notification_recipients"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("push_notifications.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    device_token = Column(String)
    status = Column(String)  # pending, sent, failed
    error_message = Column(Text)
    delivered_at = Column(DateTime)
    
    notification = relationship("PushNotification", back_populates="recipients")
    user = relationship("User")

class MobileDevice(Base):
    __tablename__ = "mobile_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_type = Column(Enum(DeviceType))
    device_token = Column(String, unique=True)
    device_name = Column(String)
    os_version = Column(String)
    app_version = Column(String)
    last_active = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="devices")

class OfflineSync(Base):
    __tablename__ = "offline_syncs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("mobile_devices.id"))
    sync_type = Column(String)  # full, incremental
    status = Column(String)  # pending, in_progress, completed, failed
    data = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    user = relationship("User")
    device = relationship("MobileDevice")

class MobileAppConfig(Base):
    __tablename__ = "mobile_app_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, nullable=False, unique=True)
    value = Column(JSON)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    versions = relationship("MobileAppVersion", back_populates="config")

class MobileAppVersion(Base):
    __tablename__ = "mobile_app_versions"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("mobile_app_configs.id"))
    version = Column(String, nullable=False)
    platform = Column(Enum(DeviceType))
    is_required = Column(Boolean, default=False)
    release_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    config = relationship("MobileAppConfig", back_populates="versions") 