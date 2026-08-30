from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class AnalyticsDashboard(Base):
    __tablename__ = "analytics_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    layout = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="dashboards")
    widgets = relationship("DashboardWidget", back_populates="dashboard")

class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("analytics_dashboards.id"))
    widget_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    config = Column(JSON)
    position = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dashboard = relationship("AnalyticsDashboard", back_populates="widgets")

class SalesAnalytics(Base):
    __tablename__ = "sales_analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    total_sales = Column(Float)
    total_orders = Column(Integer)
    average_order_value = Column(Float)
    conversion_rate = Column(Float)
    customer_count = Column(Integer)
    product_category = Column(String)
    
    class Config:
        indexes = [
            ("date", "product_category")
        ]

class CustomerAnalytics(Base):
    __tablename__ = "customer_analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    purchase_frequency = Column(Integer)
    total_spent = Column(Float)
    last_purchase_date = Column(DateTime)
    customer_segment = Column(String)
    
    customer = relationship("Customer", back_populates="analytics")
    
    class Config:
        indexes = [
            ("date", "customer_segment")
        ] 