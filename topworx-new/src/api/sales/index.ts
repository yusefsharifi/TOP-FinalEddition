// Sales & CRM API
import { apiClient } from '../../services/api';
import {
  Customer,
  Lead,
  Opportunity,
  Quote,
  QuoteItem,
  SalesOrder,
  SalesOrderItem,
  Invoice,
  InvoiceItem,
  SalesActivity,
  SalesPipeline,
  SalesTarget,
  SalesReport,
  CustomerFormData,
  LeadFormData,
  OpportunityFormData,
  QuoteFormData,
  QuoteItemFormData,
  SalesFilters,
  CustomerFilters,
  LeadFilters,
  SalesResponse,
  SalesStats
} from '../../types/sales';

// Customers API
export const customersApi = {
  getAll: (filters?: CustomerFilters) =>
    apiClient.get<SalesResponse<Customer>>('/sales/customers', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Customer>(`/sales/customers/${id}`),
  
  create: (data: CustomerFormData) =>
    apiClient.post<Customer>('/sales/customers', data),
  
  update: (id: string, data: Partial<CustomerFormData>) =>
    apiClient.put<Customer>(`/sales/customers/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/customers/${id}`),
  
  getByType: (type: string) =>
    apiClient.get<Customer[]>(`/sales/customers/type/${type}`),
  
  getBySegment: (segmentId: string) =>
    apiClient.get<Customer[]>(`/sales/customers/segment/${segmentId}`),
  
  getBalance: (id: string) =>
    apiClient.get<{ balance: number }>(`/sales/customers/${id}/balance`),
  
  export: (filters?: CustomerFilters) =>
    apiClient.get('/sales/customers/export', { params: filters, responseType: 'blob' }),
};

// Leads API
export const leadsApi = {
  getAll: (filters?: LeadFilters) =>
    apiClient.get<SalesResponse<Lead>>('/sales/leads', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Lead>(`/sales/leads/${id}`),
  
  create: (data: LeadFormData) =>
    apiClient.post<Lead>('/sales/leads', data),
  
  update: (id: string, data: Partial<LeadFormData>) =>
    apiClient.put<Lead>(`/sales/leads/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/leads/${id}`),
  
  convert: (id: string, data: { customer_id: string; opportunity_id?: string }) =>
    apiClient.post<Lead>(`/sales/leads/${id}/convert`, data),
  
  getByStatus: (status: string) =>
    apiClient.get<Lead[]>(`/sales/leads/status/${status}`),
  
  getBySource: (source: string) =>
    apiClient.get<Lead[]>(`/sales/leads/source/${source}`),
  
  export: (filters?: LeadFilters) =>
    apiClient.get('/sales/leads/export', { params: filters, responseType: 'blob' }),
};

// Opportunities API
export const opportunitiesApi = {
  getAll: (filters?: SalesFilters) =>
    apiClient.get<SalesResponse<Opportunity>>('/sales/opportunities', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Opportunity>(`/sales/opportunities/${id}`),
  
  create: (data: OpportunityFormData) =>
    apiClient.post<Opportunity>('/sales/opportunities', data),
  
  update: (id: string, data: Partial<OpportunityFormData>) =>
    apiClient.put<Opportunity>(`/sales/opportunities/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/opportunities/${id}`),
  
  close: (id: string, data: { stage: string; actual_revenue?: number; actual_close_date?: string }) =>
    apiClient.post<Opportunity>(`/sales/opportunities/${id}/close`, data),
  
  getByStage: (stage: string) =>
    apiClient.get<Opportunity[]>(`/sales/opportunities/stage/${stage}`),
  
  getByCustomer: (customerId: string) =>
    apiClient.get<Opportunity[]>(`/sales/opportunities/customer/${customerId}`),
  
  export: (filters?: SalesFilters) =>
    apiClient.get('/sales/opportunities/export', { params: filters, responseType: 'blob' }),
};

// Quotes API
export const quotesApi = {
  getAll: (filters?: SalesFilters) =>
    apiClient.get<SalesResponse<Quote>>('/sales/quotes', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Quote>(`/sales/quotes/${id}`),
  
  create: (data: QuoteFormData) =>
    apiClient.post<Quote>('/sales/quotes', data),
  
  update: (id: string, data: Partial<QuoteFormData>) =>
    apiClient.put<Quote>(`/sales/quotes/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/quotes/${id}`),
  
  send: (id: string) =>
    apiClient.post<Quote>(`/sales/quotes/${id}/send`),
  
  accept: (id: string) =>
    apiClient.post<Quote>(`/sales/quotes/${id}/accept`),
  
  reject: (id: string, reason: string) =>
    apiClient.post<Quote>(`/sales/quotes/${id}/reject`, { reason }),
  
  getItems: (id: string) =>
    apiClient.get<QuoteItem[]>(`/sales/quotes/${id}/items`),
  
  updateItems: (id: string, items: QuoteItemFormData[]) =>
    apiClient.put<QuoteItem[]>(`/sales/quotes/${id}/items`, { items }),
  
  getNextNumber: () =>
    apiClient.get<{ next_number: string }>('/sales/quotes/next-number'),
  
  export: (id: string, format: 'pdf' | 'excel') =>
    apiClient.get(`/sales/quotes/${id}/export`, { params: { format }, responseType: 'blob' }),
};

// Sales Orders API
export const salesOrdersApi = {
  getAll: (filters?: SalesFilters) =>
    apiClient.get<SalesResponse<SalesOrder>>('/sales/orders', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<SalesOrder>(`/sales/orders/${id}`),
  
  create: (data: any) =>
    apiClient.post<SalesOrder>('/sales/orders', data),
  
  update: (id: string, data: Partial<SalesOrder>) =>
    apiClient.put<SalesOrder>(`/sales/orders/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/orders/${id}`),
  
  confirm: (id: string) =>
    apiClient.post<SalesOrder>(`/sales/orders/${id}/confirm`),
  
  deliver: (id: string) =>
    apiClient.post<SalesOrder>(`/sales/orders/${id}/deliver`),
  
  cancel: (id: string, reason: string) =>
    apiClient.post<SalesOrder>(`/sales/orders/${id}/cancel`, { reason }),
  
  getItems: (id: string) =>
    apiClient.get<SalesOrderItem[]>(`/sales/orders/${id}/items`),
  
  getNextNumber: () =>
    apiClient.get<{ next_number: string }>('/sales/orders/next-number'),
  
  export: (id: string, format: 'pdf' | 'excel') =>
    apiClient.get(`/sales/orders/${id}/export`, { params: { format }, responseType: 'blob' }),
};

// Invoices API
export const invoicesApi = {
  getAll: (filters?: SalesFilters) =>
    apiClient.get<SalesResponse<Invoice>>('/sales/invoices', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Invoice>(`/sales/invoices/${id}`),
  
  create: (data: any) =>
    apiClient.post<Invoice>('/sales/invoices', data),
  
  update: (id: string, data: Partial<Invoice>) =>
    apiClient.put<Invoice>(`/sales/invoices/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/invoices/${id}`),
  
  send: (id: string) =>
    apiClient.post<Invoice>(`/sales/invoices/${id}/send`),
  
  markAsPaid: (id: string, paidAmount: number) =>
    apiClient.post<Invoice>(`/sales/invoices/${id}/mark-paid`, { paid_amount: paidAmount }),
  
  getItems: (id: string) =>
    apiClient.get<InvoiceItem[]>(`/sales/invoices/${id}/items`),
  
  getNextNumber: () =>
    apiClient.get<{ next_number: string }>('/sales/invoices/next-number'),
  
  export: (id: string, format: 'pdf' | 'excel') =>
    apiClient.get(`/sales/invoices/${id}/export`, { params: { format }, responseType: 'blob' }),
};

// Sales Activities API
export const salesActivitiesApi = {
  getAll: (filters?: SalesFilters) =>
    apiClient.get<SalesResponse<SalesActivity>>('/sales/activities', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<SalesActivity>(`/sales/activities/${id}`),
  
  create: (data: any) =>
    apiClient.post<SalesActivity>('/sales/activities', data),
  
  update: (id: string, data: Partial<SalesActivity>) =>
    apiClient.put<SalesActivity>(`/sales/activities/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/activities/${id}`),
  
  getByCustomer: (customerId: string) =>
    apiClient.get<SalesActivity[]>(`/sales/activities/customer/${customerId}`),
  
  getByLead: (leadId: string) =>
    apiClient.get<SalesActivity[]>(`/sales/activities/lead/${leadId}`),
  
  getByOpportunity: (opportunityId: string) =>
    apiClient.get<SalesActivity[]>(`/sales/activities/opportunity/${opportunityId}`),
  
  getByUser: (userId: string) =>
    apiClient.get<SalesActivity[]>(`/sales/activities/user/${userId}`),
};

// Sales Pipeline API
export const salesPipelineApi = {
  getAll: () =>
    apiClient.get<SalesPipeline[]>('/sales/pipelines'),
  
  getById: (id: string) =>
    apiClient.get<SalesPipeline>(`/sales/pipelines/${id}`),
  
  create: (data: any) =>
    apiClient.post<SalesPipeline>('/sales/pipelines', data),
  
  update: (id: string, data: Partial<SalesPipeline>) =>
    apiClient.put<SalesPipeline>(`/sales/pipelines/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/pipelines/${id}`),
  
  getStages: (id: string) =>
    apiClient.get<SalesPipelineStage[]>(`/sales/pipelines/${id}/stages`),
  
  updateStages: (id: string, stages: any[]) =>
    apiClient.put<SalesPipelineStage[]>(`/sales/pipelines/${id}/stages`, { stages }),
};

// Sales Targets API
export const salesTargetsApi = {
  getAll: (filters?: SalesFilters) =>
    apiClient.get<SalesResponse<SalesTarget>>('/sales/targets', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<SalesTarget>(`/sales/targets/${id}`),
  
  create: (data: any) =>
    apiClient.post<SalesTarget>('/sales/targets', data),
  
  update: (id: string, data: Partial<SalesTarget>) =>
    apiClient.put<SalesTarget>(`/sales/targets/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/targets/${id}`),
  
  getByUser: (userId: string) =>
    apiClient.get<SalesTarget[]>(`/sales/targets/user/${userId}`),
  
  getProgress: (id: string) =>
    apiClient.get<{ progress: number; remaining: number }>(`/sales/targets/${id}/progress`),
};

// Sales Reports API
export const salesReportsApi = {
  getAll: () =>
    apiClient.get<SalesReport[]>('/sales/reports'),
  
  getById: (id: string) =>
    apiClient.get<SalesReport>(`/sales/reports/${id}`),
  
  create: (data: any) =>
    apiClient.post<SalesReport>('/sales/reports', data),
  
  update: (id: string, data: Partial<SalesReport>) =>
    apiClient.put<SalesReport>(`/sales/reports/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sales/reports/${id}`),
  
  generate: (id: string) =>
    apiClient.post<SalesReport>(`/sales/reports/${id}/generate`),
  
  export: (id: string, format: 'pdf' | 'excel') =>
    apiClient.get(`/sales/reports/${id}/export`, { params: { format }, responseType: 'blob' }),
};

// Sales Statistics API
export const salesStatsApi = {
  getDashboard: () =>
    apiClient.get<SalesStats>('/sales/stats/dashboard'),
  
  getPipeline: () =>
    apiClient.get<any[]>('/sales/stats/pipeline'),
  
  getRevenue: (period: string) =>
    apiClient.get<any[]>('/sales/stats/revenue', { params: { period } }),
  
  getConversion: () =>
    apiClient.get<any[]>('/sales/stats/conversion'),
  
  getPerformance: (userId?: string) =>
    apiClient.get<any[]>('/sales/stats/performance', { params: { user_id: userId } }),
  
  getCustomerAnalysis: () =>
    apiClient.get<any[]>('/sales/stats/customer-analysis'),
  
  getProductPerformance: () =>
    apiClient.get<any[]>('/sales/stats/product-performance'),
};

// Export all APIs
export const salesApi = {
  customers: customersApi,
  leads: leadsApi,
  opportunities: opportunitiesApi,
  quotes: quotesApi,
  salesOrders: salesOrdersApi,
  invoices: invoicesApi,
  activities: salesActivitiesApi,
  pipeline: salesPipelineApi,
  targets: salesTargetsApi,
  reports: salesReportsApi,
  stats: salesStatsApi,
}; 