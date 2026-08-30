// src/hooks/useProcurement.ts
// ============================================================================
// Procurement Hooks
// ============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { procurementApi } from '../services/procurementApi';
import {
  Vendor,
  PurchaseRequest,
  PurchaseOrder,
  GoodsReceipt,
  VendorInvoice,
  CreatePR,
  CreatePO,
  CreateReceipt,
} from '../types';

const KEYS = {
  vendors: (params?: object) => ['procurement', 'vendors', params],
  purchaseRequests: (params?: object) => ['procurement', 'requests', params],
  purchaseOrders: (params?: object) => ['procurement', 'orders', params],
  vendorInvoices: (params?: object) => ['procurement', 'invoices', params],
  payments: (params?: object) => ['procurement', 'payments', params],
};

export function useVendors(params?: Parameters<typeof procurementApi.getVendors>[0]) {
  return useQuery<Vendor[], Error>({
    queryKey: KEYS.vendors(params),
    queryFn: async () => {
      const response = await procurementApi.getVendors(params);
      return response.data;
    },
  });
}

export function usePurchaseRequests(params?: Parameters<typeof procurementApi.getPRs>[0]) {
  return useQuery<PurchaseRequest[], Error>({
    queryKey: KEYS.purchaseRequests(params),
    queryFn: async () => {
      const response = await procurementApi.getPRs(params);
      return response.data;
    },
  });
}

export function usePurchaseOrders(params?: Parameters<typeof procurementApi.getPOs>[0]) {
  return useQuery<PurchaseOrder[], Error>({
    queryKey: KEYS.purchaseOrders(params),
    queryFn: async () => {
      const response = await procurementApi.getPOs(params);
      return response.data;
    },
  });
}

export function useApprovePR() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, notes }: { id: number; notes?: string }) => {
      const response = await procurementApi.approvePR(id, notes);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['procurement', 'requests'] });
    },
  });
}

export function useReceiveGoods() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CreateReceipt) => {
      const response = await procurementApi.receiveGoods(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['procurement', 'orders'] });
      queryClient.invalidateQueries({ queryKey: ['finance', 'reports'] });
      queryClient.invalidateQueries({ queryKey: ['inventory', 'stock'] });
    },
  });
}

export function useVerifyInvoice() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await procurementApi.verifyInvoice(id);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['procurement', 'invoices'] });
    },
  });
}

export function usePayVendor() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: Partial<VendorPayment>) => {
      const response = await procurementApi.payVendor(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['procurement', 'payments'] });
      queryClient.invalidateQueries({ queryKey: ['procurement', 'invoices'] });
      queryClient.invalidateQueries({ queryKey: ['finance', 'reports'] });
    },
  });
}