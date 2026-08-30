from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    RADAR = "radar"
    CANDLESTICK = "candlestick"

class TimeRange(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class FilterOptions(BaseModel):
    time_range: TimeRange
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    departments: Optional[List[str]] = None
    products: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    custom_filters: Optional[Dict[str, Any]] = None

class KPIResponse(BaseModel):
    name: str
    value: float
    unit: str
    trend: float
    target: Optional[float] = None
    status: str
    last_updated: datetime
    details: Optional[Dict[str, Any]] = None

class ChartData(BaseModel):
    chart_type: ChartType
    title: str
    data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None
    filters: Optional[FilterOptions] = None

class DashboardConfig(BaseModel):
    title: str
    description: Optional[str] = None
    layout: Dict[str, Any]
    widgets: List[Dict[str, Any]]
    filters: Optional[FilterOptions] = None
    refresh_rate: Optional[int] = None
    export_options: Optional[Dict[str, Any]] = None

class DashboardData(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    config: DashboardConfig
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_public: bool = False
    tags: Optional[List[str]] = None
    permissions: Optional[Dict[str, List[str]]] = None

class PredictiveAnalytics(BaseModel):
    metric: str
    historical_data: List[Dict[str, Any]]
    forecast: List[Dict[str, Any]]
    confidence_intervals: Dict[str, List[Dict[str, Any]]]
    model_info: Optional[Dict[str, Any]] = None

class DrillDownData(BaseModel):
    metric: str
    dimensions: List[str]
    data: Dict[str, Any]
    ratios: Optional[Dict[str, Any]] = None
    trends: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class CustomReport(BaseModel):
    id: str
    name: str
    config: DashboardConfig
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str
    format: str
    schedule: Optional[Dict[str, Any]] = None
    recipients: Optional[List[str]] = None 