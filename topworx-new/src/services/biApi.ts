// src/services/biApi.ts
// ============================================================================
// BI Dashboard API
// ============================================================================

import { apiClient } from './api';
import {
  CEODashboardData,
  KPIData,
  AlertEvent,
  AlertRule,
  ReportConfig,
  ReportTemplate,
} from '../types';

const BASE = '/bi';

export const biApi = {
  // Dashboards
  getCEODashboard: (year: number, month: number) =>
    apiClient.get<CEODashboardData>(`${BASE}/dashboard/ceo`, { params: { year, month } }),
  
  getCFODashboard: (year: number, month: number) =>
    apiClient.get(`${BASE}/dashboard/cfo`, { params: { year, month } }),
  
  getSalesDashboard: (year: number, month: number) =>
    apiClient.get(`${BASE}/dashboard/sales`, { params: { year, month } }),
  
  getInventoryDashboard: () =>
    apiClient.get(`${BASE}/dashboard/inventory`),
  
  getHRDashboard: (year: number, month: number) =>
    apiClient.get(`${BASE}/dashboard/hr`, { params: { year, month } }),

  // KPIs
  getAllKPIs: (year: number, month: number) =>
    apiClient.get<Record<string, KPIData>>(`${BASE}/kpis`, { params: { year, month } }),
  
  getKPIHistory: (kpiName: string, days?: number) =>
    apiClient.get(`${BASE}/kpis/${kpiName}/history`, { params: { days } }),

  // Alerts
  getAlerts: (unacknowledgedOnly?: boolean) =>
    apiClient.get<AlertEvent[]>(`${BASE}/alerts`, { params: { unacknowledged_only: unacknowledgedOnly } }),
  
  createAlertRule: (data: Partial<AlertRule>) =>
    apiClient.post<AlertRule>(`${BASE}/alerts/rules`, data),
  
  updateAlertRule: (id: number, data: Partial<AlertRule>) =>
    apiClient.put<AlertRule>(`${BASE}/alerts/rules/${id}`, data),
  
  acknowledgeAlert: (eventId: number) =>
    apiClient.post(`${BASE}/alerts/${eventId}/acknowledge`),

  // Reports
  buildReport: (config: ReportConfig) =>
    apiClient.post(`${BASE}/reports/build`, config),
  
  getTemplates: () =>
    apiClient.get<ReportTemplate[]>(`${BASE}/reports/templates`),
  
  saveTemplate: (name: string, config: ReportConfig, isPublic?: boolean) =>
    apiClient.post(`${BASE}/reports/save`, { name, config, is_public: isPublic }),

  // Export
  exportExcel: (report: string, year: number, month: number) =>
    apiClient.get(`${BASE}/export/excel`, { 
      params: { report, year, month }, 
      responseType: 'blob' 
    }),

  // ETL
  triggerETL: (full?: boolean) =>
    apiClient.post(`${BASE}/etl/run`, null, { params: { full } }),
  
  initDates: () =>
    apiClient.post(`${BASE}/etl/init-dates`),
};