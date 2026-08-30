/**
 * AI Module API Client
 * TOP WorX ERP System
 * 
 * Provides API functions for AI integration across all modules.
 */

import apiClient from '../../core/api/client';

// ══════════════════════════════════════════════════════════════════════════════
// Types
// ══════════════════════════════════════════════════════════════════════════════

export interface AIInsight {
  type: string;
  data: Record<string, any>;
}

export interface StockoutPrediction {
  item_id: number;
  item_name: string;
  sku: string;
  current_stock: number;
  reorder_point: number;
  avg_daily_usage: number;
  days_remaining: number;
  severity: string;
}

export interface ReorderSuggestion {
  item_id: number;
  item_name: string;
  sku: string;
  current_stock: number;
  suggested_reorder_point: number;
  suggested_order_qty: number;
  estimated_stockout_days: number;
}

export interface CashflowPrediction {
  account_id: number;
  account_name: string;
  avg_daily_flow: number;
  trend: number;
  projected_30_days: number;
}

export interface RevenueForecast {
  month_offset: number;
  projected_revenue: number;
}

export interface LeadScore {
  lead_id: number;
  lead_name: string;
  score: number;
  factors: Record<string, number>;
}

export interface SupplierRisk {
  vendor_id: number;
  vendor_name: string;
  total_orders: number;
  on_time_rate: number;
  risk_score: number;
  risk_level: string;
}

export interface SafetyScore {
  overall_score: number;
  incident_score: number;
  checklist_score: number;
  total_incidents: number;
  resolved_incidents: number;
}

export interface ProjectRiskAssessment {
  project_id: number;
  project_name: string;
  overall_risk_score: number;
  open_risks_count: number;
  schedule_risk: string;
  budget_risk: string;
  risks: Array<{
    id: number;
    name: string;
    probability: number;
    impact: number;
    score: number;
  }>;
}

export interface SentimentAnalysis {
  ticket_id: number;
  sentiment: string;
  confidence: number;
  positive_signals: number;
  negative_signals: number;
}

// ══════════════════════════════════════════════════════════════════════════════
// AI API Functions
// ══════════════════════════════════════════════════════════════════════════════

/**
 * AI Chat - Send message to AI assistant
 */
export const aiChat = async (params: {
  message: string;
  conversation_id?: number;
  module?: string;
  system_prompt?: string;
  model?: string;
  temperature?: number;
}) => {
  const response = await apiClient.post('/ai/chat', params);
  return response.data;
};

/**
 * Get AI conversations
 */
export const getAIConversations = async (params?: {
  module?: string;
  offset?: number;
  limit?: number;
}) => {
  const response = await apiClient.get('/ai/conversations', { params });
  return response.data;
};

/**
 * Create AI conversation
 */
export const createAIConversation = async (params: {
  title: string;
  module?: string;
  model?: string;
}) => {
  const response = await apiClient.post('/ai/conversations', params);
  return response.data;
};

/**
 * Get AI insights
 */
export const getAIInsights = async (params?: {
  module?: string;
  unread_only?: boolean;
  offset?: number;
  limit?: number;
}) => {
  const response = await apiClient.get('/ai/insights', { params });
  return response.data;
};

/**
 * Get AI usage statistics
 */
export const getAIUsage = async (days: number = 30) => {
  const response = await apiClient.get('/ai/usage', { params: { days } });
  return response.data;
};

// ══════════════════════════════════════════════════════════════════════════════
// Module-Specific AI Endpoints
// ══════════════════════════════════════════════════════════════════════════════

// --- Inventory AI ---
export const getInventoryStockoutPrediction = async () => {
  const response = await apiClient.get('/ai/inventory/stockout-prediction');
  return response.data;
};

export const getInventorySmartReorder = async () => {
  const response = await apiClient.get('/ai/inventory/smart-reorder');
  return response.data;
};

export const getInventoryAnomalyDetection = async () => {
  const response = await apiClient.get('/ai/inventory/anomaly-detection');
  return response.data;
};

// --- Finance AI ---
export const getFinanceCashflowPrediction = async () => {
  const response = await apiClient.get('/ai/finance/cashflow-prediction');
  return response.data;
};

export const getFinanceExpenseAnomaly = async () => {
  const response = await apiClient.get('/ai/finance/expense-anomaly');
  return response.data;
};

// --- HR AI ---
export const getHRAttritionPrediction = async () => {
  const response = await apiClient.get('/ai/hr/attrition-prediction');
  return response.data;
};

// --- Sales AI ---
export const getSalesRevenueForecast = async () => {
  const response = await apiClient.get('/ai/sales/revenue-forecast');
  return response.data;
};

export const getSalesChurnPrediction = async () => {
  const response = await apiClient.get('/ai/sales/churn-prediction');
  return response.data;
};

// --- CRM AI ---
export const getCRMLeadScore = async (leadId: number) => {
  const response = await apiClient.get(`/ai/crm/lead-scoring/${leadId}`);
  return response.data;
};

// --- Procurement AI ---
export const getProcurementSupplierRisk = async () => {
  const response = await apiClient.get('/ai/procurement/supplier-risk');
  return response.data;
};

// --- Quality AI ---
export const getQualityDefectPrediction = async () => {
  const response = await apiClient.get('/ai/quality/defect-prediction');
  return response.data;
};

// --- HSE AI ---
export const getHSEIncidentPrediction = async () => {
  const response = await apiClient.get('/ai/hse/incident-prediction');
  return response.data;
};

export const getHSESafetyScore = async () => {
  const response = await apiClient.get('/ai/hse/safety-score');
  return response.data;
};

// --- Projects AI ---
export const getProjectsRiskAssessment = async (projectId: number) => {
  const response = await apiClient.get(`/ai/projects/${projectId}/risk-assessment`);
  return response.data;
};

// --- Support AI ---
export const getSupportTicketSentiment = async (ticketId: number) => {
  const response = await apiClient.get(`/ai/support/ticket-sentiment/${ticketId}`);
  return response.data;
};

// --- All Insights ---
export const getAllAIInsights = async (modules?: string[]) => {
  const params = modules ? { modules: modules.join(',') } : {};
  const response = await apiClient.get('/ai/dashboard/all-insights', { params });
  return response.data;
};

// --- AI Dashboard ---
export const getAIDashboard = async () => {
  const response = await apiClient.get('/ai/dashboard');
  return response.data;
};

export default {
  // Chat
  aiChat,
  getAIConversations,
  createAIConversation,
  getAIInsights,
  getAIUsage,
  
  // Inventory
  getInventoryStockoutPrediction,
  getInventorySmartReorder,
  getInventoryAnomalyDetection,
  
  // Finance
  getFinanceCashflowPrediction,
  getFinanceExpenseAnomaly,
  
  // HR
  getHRAttritionPrediction,
  
  // Sales
  getSalesRevenueForecast,
  getSalesChurnPrediction,
  
  // CRM
  getCRMLeadScore,
  
  // Procurement
  getProcurementSupplierRisk,
  
  // Quality
  getQualityDefectPrediction,
  
  // HSE
  getHSEIncidentPrediction,
  getHSESafetyScore,
  
  // Projects
  getProjectsRiskAssessment,
  
  // Support
  getSupportTicketSentiment,
  
  // All
  getAllAIInsights,
  getAIDashboard,
};
