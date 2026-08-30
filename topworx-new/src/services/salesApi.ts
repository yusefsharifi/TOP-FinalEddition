// src/services/salesApi.ts
// ============================================================================
// Sales API
// ============================================================================

import { apiClient } from './api';
import {
  Customer,
  SalesQuote,
  SalesInvoice,
  InvoiceListItem,
  SalesPayment,
  CreateQuote,
  CreateInvoice,
  CreatePayment,
  RevenueByPeriodRow,
  TopCustomerRow,
  ProductMarginRow,
} from '../types';

const BASE = '/sales';

export const salesApi = {
  // Customers
  getCustomers: (params?: { search?: string; category?: string; is_active?: boolean }) =>
    apiClient.get<Customer[]>(`${BASE}/customers`, { params }),
  
  getCustomer: (id: number) =>
    apiClient.get<Customer>(`${BASE}/customers/${id}`),
  
  createCustomer: (data: Partial<Customer>) =>
    apiClient.post<Customer>(`${BASE}/customers`, data),
  
  updateCustomer: (id: number, data: Partial<Customer>) =>
    apiClient.put<Customer>(`${BASE}/customers/${id}`, data),
  
  getCustomerStatement: (id: number, asOfDate?: string) =>
    apiClient.get(`${BASE}/customers/${id}/statement`, { params: { as_of_date: asOfDate } }),

  // Quotes
  getQuotes: (params?: { customer_id?: number; status?: string }) =>
    apiClient.get<SalesQuote[]>(`${BASE}/quotes`, { params }),
  
  getQuote: (id: number) =>
    apiClient.get<SalesQuote>(`${BASE}/quotes/${id}`),
  
  createQuote: (data: CreateQuote) =>
    apiClient.post<SalesQuote>(`${BASE}/quotes`, data),
  
  sendQuote: (id: number) =>
    apiClient.post<SalesQuote>(`${BASE}/quotes/${id}/send`),
  
  convertQuote: (id: number) =>
    apiClient.post<SalesInvoice>(`${BASE}/quotes/${id}/convert`),

  // Invoices
  getInvoices: (params?: { customer_id?: number; status?: string; overdue_only?: boolean }) =>
    apiClient.get<InvoiceListItem[]>(`${BASE}/invoices`, { params }),
  
  getInvoice: (id: number) =>
    apiClient.get<SalesInvoice>(`${BASE}/invoices/${id}`),
  
  createInvoice: (data: CreateInvoice) =>
    apiClient.post<SalesInvoice>(`${BASE}/invoices`, data),
  
  issueInvoice: (id: number) =>
    apiClient.post<SalesInvoice>(`${BASE}/invoices/${id}/issue`),
  
  cancelInvoice: (id: number) =>
    apiClient.post<SalesInvoice>(`${BASE}/invoices/${id}/cancel`),
  
  downloadPdf: (id: number) =>
    apiClient.get(`${BASE}/invoices/${id}/pdf`, { responseType: 'blob' }),
  
  getTaxExport: (id: number) =>
    apiClient.get(`${BASE}/invoices/${id}/tax-export`),

  // Payments
  getPayments: (params?: { customer_id?: number; status?: string }) =>
    apiClient.get<SalesPayment[]>(`${BASE}/payments`, { params }),
  
  receivePayment: (data: CreatePayment) =>
    apiClient.post<SalesPayment>(`${BASE}/payments`, data),
  
  allocatePayment: (paymentId: number, invoiceId: number, amount: string) =>
    apiClient.post<SalesPayment>(`${BASE}/payments/${paymentId}/allocate`, { 
      invoice_id: invoiceId, 
      amount 
    }),

  // Reports
  getRevenueByPeriod: (year?: number) =>
    apiClient.get<RevenueByPeriodRow[]>(`${BASE}/reports/revenue-by-period`, { params: { year } }),
  
  getTopCustomers: (limit?: number) =>
    apiClient.get<TopCustomerRow[]>(`${BASE}/reports/top-customers`, { params: { limit } }),
  
  getProductMargin: (params?: { date_from?: string; date_to?: string }) =>
    apiClient.get<ProductMarginRow[]>(`${BASE}/reports/product-margin`, { params }),
  
  getArAging: (asOfDate?: string) =>
    apiClient.get(`${BASE}/reports/ar-aging`, { params: { as_of_date: asOfDate } }),
};