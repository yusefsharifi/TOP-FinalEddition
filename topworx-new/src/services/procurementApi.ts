// src/services/procurementApi.ts
// ============================================================================
// Procurement API
// ============================================================================

import { apiClient } from './api';
import {
  Vendor,
  PurchaseRequest,
  PurchaseOrder,
  GoodsReceipt,
  VendorInvoice,
  ThreeWayMatchResult,
  VendorPayment,
  CreatePR,
  CreatePO,
  CreateReceipt,
} from '../types';

const BASE = '/procurement';

export const procurementApi = {
  // Vendors
  getVendors: (params?: { is_active?: boolean; is_approved?: boolean; search?: string }) =>
    apiClient.get<Vendor[]>(`${BASE}/vendors`, { params }),
  
  getVendor: (id: number) =>
    apiClient.get<Vendor>(`${BASE}/vendors/${id}`),
  
  createVendor: (data: Partial<Vendor>) =>
    apiClient.post<Vendor>(`${BASE}/vendors`, data),
  
  updateVendor: (id: number, data: Partial<Vendor>) =>
    apiClient.put<Vendor>(`${BASE}/vendors/${id}`, data),
  
  getVendorStatement: (id: number, asOfDate?: string) =>
    apiClient.get(`${BASE}/vendors/${id}/statement`, { params: { as_of_date: asOfDate } }),

  // Purchase Requests
  getPRs: (params?: { status?: string; department?: string }) =>
    apiClient.get<PurchaseRequest[]>(`${BASE}/requests`, { params }),
  
  createPR: (data: CreatePR) =>
    apiClient.post<PurchaseRequest>(`${BASE}/requests`, data),
  
  submitPR: (id: number) =>
    apiClient.post<PurchaseRequest>(`${BASE}/requests/${id}/submit`),
  
  approvePR: (id: number, notes?: string) =>
    apiClient.post<PurchaseRequest>(`${BASE}/requests/${id}/approve`, { notes }),
  
  rejectPR: (id: number, reason: string) =>
    apiClient.post<PurchaseRequest>(`${BASE}/requests/${id}/reject`, { reason }),
  
  convertPR: (id: number, vendorId: number, expectedDelivery?: string) =>
    apiClient.post<PurchaseOrder>(`${BASE}/requests/${id}/convert`, null, { 
      params: { vendor_id: vendorId, expected_delivery: expectedDelivery } 
    }),

  // Purchase Orders
  getPOs: (params?: { vendor_id?: number; status?: string }) =>
    apiClient.get<PurchaseOrder[]>(`${BASE}/orders`, { params }),
  
  getPO: (id: number) =>
    apiClient.get<PurchaseOrder>(`${BASE}/orders/${id}`),
  
  createPO: (data: CreatePO) =>
    apiClient.post<PurchaseOrder>(`${BASE}/orders`, data),
  
  sendPO: (id: number) =>
    apiClient.post<PurchaseOrder>(`${BASE}/orders/${id}/send`),
  
  receiveGoods: (data: CreateReceipt) =>
    apiClient.post<GoodsReceipt>(`${BASE}/orders/${data.poId}/receive`, data),

  // Vendor Invoices
  getVendorInvoices: (params?: { vendor_id?: number; pending_only?: boolean }) =>
    apiClient.get<VendorInvoice[]>(`${BASE}/invoices`, { params }),
  
  recordVendorInvoice: (data: Partial<VendorInvoice>) =>
    apiClient.post<VendorInvoice>(`${BASE}/invoices`, data),
  
  verifyInvoice: (id: number) =>
    apiClient.post<ThreeWayMatchResult>(`${BASE}/invoices/${id}/verify`),

  // Payments
  getPayments: (params?: { vendor_id?: number }) =>
    apiClient.get<VendorPayment[]>(`${BASE}/payments`, { params }),
  
  payVendor: (data: Partial<VendorPayment>) =>
    apiClient.post<VendorPayment>(`${BASE}/payments`, data),

  // Reports
  getSpendByVendor: () =>
    apiClient.get(`${BASE}/reports/spend-by-vendor`),
  
  getPendingApprovals: () =>
    apiClient.get(`${BASE}/reports/pending-approvals`),
  
  getDeliveryPerformance: () =>
    apiClient.get(`${BASE}/reports/delivery-performance`),
  
  getApAging: (asOfDate?: string) =>
    apiClient.get(`${BASE}/reports/ap-aging`, { params: { as_of_date: asOfDate } }),
};