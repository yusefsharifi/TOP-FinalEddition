from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import enum

class VisualizationType(enum.Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEAT_MAP = "heat_map"
    GAUGE = "gauge"
    KPI = "kpi"
    TABLE = "table"
    CUSTOM = "custom"

class BIDashboard(Base):
    __tablename__ = "bi_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    layout = Column(JSON)
    theme = Column(String)
    is_public = Column(Boolean, default=False)
    refresh_interval = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("User")
    widgets = relationship("BIWidget", back_populates="dashboard")
    filters = relationship("BIFilter", back_populates="dashboard")
    subscriptions = relationship("BISubscription", back_populates="dashboard")

class BIWidget(Base):
    __tablename__ = "bi_widgets"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("bi_dashboards.id"))
    name = Column(String, nullable=False)
    type = Column(Enum(VisualizationType))
    query = Column(Text)
    config = Column(JSON)
    position = Column(JSON)
    refresh_interval = Column(Integer)  # in minutes
    last_refresh = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dashboard = relationship("BIDashboard", back_populates="widgets")
    alerts = relationship("BIAlert", back_populates="widget")

class BIFilter(Base):
    __tablename__ = "bi_filters"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("bi_dashboards.id"))
    name = Column(String, nullable=False)
    type = Column(String)  # date, category, numeric, etc.
    field = Column(String)
    default_value = Column(JSON)
    options = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dashboard = relationship("BIDashboard", back_populates="filters")

class BIAlert(Base):
    __tablename__ = "bi_alerts"

    id = Column(Integer, primary_key=True, index=True)
    widget_id = Column(Integer, ForeignKey("bi_widgets.id"))
    name = Column(String, nullable=False)
    condition = Column(JSON)  # Alert condition definition
    threshold = Column(Float)
    frequency = Column(String)  # real-time, daily, weekly
    notification_channels = Column(JSON)  # email, push, sms
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    widget = relationship("BIWidget", back_populates="alerts")
    notifications = relationship("BIAlertNotification", back_populates="alert")

class BIAlertNotification(Base):
    __tablename__ = "bi_alert_notifications"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("bi_alerts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    channel = Column(String)
    status = Column(String)  # sent, failed, pending
    sent_at = Column(DateTime)
    error_message = Column(Text)
    
    alert = relationship("BIAlert", back_populates="notifications")
    user = relationship("User")

class BISubscription(Base):
    __tablename__ = "bi_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("bi_dashboards.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    frequency = Column(String)  # daily, weekly, monthly
    format = Column(String)  # pdf, excel, html
    schedule = Column(JSON)  # Cron expression
    last_sent = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dashboard = relationship("BIDashboard", back_populates="subscriptions")
    user = relationship("User")

class BIDataSource(Base):
    __tablename__ = "bi_data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)  # database, api, file
    connection_string = Column(String)
    credentials = Column(JSON)
    schema = Column(JSON)
    refresh_interval = Column(Integer)  # in minutes
    last_refresh = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    queries = relationship("BIQuery", back_populates="data_source")

class BIQuery(Base):
    __tablename__ = "bi_queries"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("bi_data_sources.id"))
    name = Column(String, nullable=False)
    query = Column(Text)
    parameters = Column(JSON)
    cache_duration = Column(Integer)  # in minutes
    last_execution = Column(DateTime)
    execution_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    data_source = relationship("BIDataSource", back_populates="queries") 