export type ReportType = 'financial' | 'sales' | 'hr' | 'inventory' | 'project' | 'crm' | 'custom';
export type ReportFormat = 'pdf' | 'excel' | 'csv' | 'json' | 'html';
export type ReportSchedule = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly' | 'custom';
export type ChartType = 'line' | 'bar' | 'pie' | 'doughnut' | 'area' | 'scatter' | 'radar' | 'table' | 'gauge';

export interface Report {
  id?: number;
  name: string;
  description?: string;
  type: ReportType;
  category: string;
  dataSource: string;
  query: string;
  parameters: ReportParameter[];
  charts: Chart[];
  filters: ReportFilter[];
  schedule?: ReportSchedule;
  scheduleConfig?: ScheduleConfig;
  recipients: string[];
  isActive: boolean;
  isPublic: boolean;
  createdBy: number;
  createdByName: string;
  lastRunAt?: string;
  nextRunAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ReportParameter {
  id?: number;
  name: string;
  label: string;
  type: 'string' | 'number' | 'date' | 'boolean' | 'select' | 'multiselect';
  defaultValue?: any;
  required: boolean;
  options?: string[];
  validation?: string;
}

export interface Chart {
  id?: number;
  name: string;
  type: ChartType;
  title: string;
  description?: string;
  dataSource: string;
  query: string;
  config: ChartConfig;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  isVisible: boolean;
}

export interface ChartConfig {
  colors?: string[];
  showLegend?: boolean;
  showGrid?: boolean;
  showLabels?: boolean;
  animate?: boolean;
  responsive?: boolean;
  aspectRatio?: number;
  customOptions?: Record<string, any>;
}

export interface ReportFilter {
  id?: number;
  name: string;
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'between' | 'in' | 'not_in';
  value: any;
  isActive: boolean;
}

export interface ScheduleConfig {
  frequency: ReportSchedule;
  dayOfWeek?: number; // 0-6 for weekly
  dayOfMonth?: number; // 1-31 for monthly
  month?: number; // 1-12 for yearly
  time: string; // HH:MM format
  timezone: string;
  customCron?: string;
}

export interface ReportExecution {
  id?: number;
  reportId: number;
  reportName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: string;
  completedAt?: string;
  duration?: number;
  resultUrl?: string;
  errorMessage?: string;
  parameters: Record<string, any>;
  executedBy: number;
  executedByName: string;
  createdAt: string;
}

export interface Dashboard {
  id?: number;
  name: string;
  description?: string;
  layout: DashboardLayout;
  widgets: DashboardWidget[];
  isPublic: boolean;
  isDefault: boolean;
  createdBy: number;
  createdByName: string;
  createdAt: string;
  updatedAt: string;
}

export interface DashboardLayout {
  columns: number;
  rows: number;
  gap: number;
  padding: number;
}

export interface DashboardWidget {
  id?: number;
  type: 'chart' | 'metric' | 'table' | 'list' | 'iframe' | 'custom';
  title: string;
  description?: string;
  dataSource: string;
  config: WidgetConfig;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  refreshInterval?: number;
  isVisible: boolean;
}

export interface WidgetConfig {
  chartType?: ChartType;
  chartConfig?: ChartConfig;
  metricFormat?: string;
  tableColumns?: string[];
  tableConfig?: Record<string, any>;
  customConfig?: Record<string, any>;
}

export interface KPI {
  id?: number;
  name: string;
  description?: string;
  category: string;
  formula: string;
  unit: string;
  target?: number;
  currentValue: number;
  previousValue: number;
  change: number;
  changePercent: number;
  trend: 'up' | 'down' | 'stable';
  status: 'good' | 'warning' | 'critical';
  dataSource: string;
  refreshInterval: number;
  lastUpdated: string;
  createdAt: string;
  updatedAt: string;
}

export interface DataExport {
  id?: number;
  name: string;
  description?: string;
  dataSource: string;
  query: string;
  format: ReportFormat;
  filters: ReportFilter[];
  schedule?: ReportSchedule;
  scheduleConfig?: ScheduleConfig;
  recipients: string[];
  isActive: boolean;
  lastRunAt?: string;
  nextRunAt?: string;
  createdBy: number;
  createdByName: string;
  createdAt: string;
  updatedAt: string;
}

export interface AnalyticsEvent {
  id?: number;
  eventType: string;
  eventName: string;
  userId?: number;
  userName?: string;
  sessionId?: string;
  pageUrl?: string;
  referrer?: string;
  userAgent?: string;
  ipAddress?: string;
  properties: Record<string, any>;
  timestamp: string;
}

export interface AnalyticsMetric {
  id?: number;
  name: string;
  description?: string;
  eventType: string;
  aggregation: 'count' | 'sum' | 'avg' | 'min' | 'max' | 'unique';
  property?: string;
  filters: ReportFilter[];
  timeRange: string;
  value: number;
  previousValue: number;
  change: number;
  changePercent: number;
  lastUpdated: string;
} 