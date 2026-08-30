// src/hooks/useSales.ts
// ============================================================================
// Sales Hooks
// ============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { salesApi } from '../services/salesApi';
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

const KEYS = {
  customers: (params?: object) => ['sales', 'customers', params],
  customer: (id: number) => ['sales', 'customers', id],
  quotes: (params?: object) => ['sales', 'quotes', params],
  invoices: (params?: object) => ['sales', 'invoices', params],
  invoice: (id: number) => ['sales', 'invoices', id],
  payments: (params?: object) => ['sales', 'payments', params],
  revenueByPeriod: (year?: number) => ['sales', 'reports', 'revenue', year],
  topCustomers: (limit?: number) => ['sales', 'reports', 'top-customers', limit],
};

export function useCustomers(params?: Parameters<typeof salesApi.getCustomers>[0]) {
  return useQuery<Customer[], Error>({
    queryKey: KEYS.customers(params),
    queryFn: async () => {
      const response = await salesApi.getCustomers(params);
      return response.data;
    },
  });
}

export function useCustomer(id: number) {
  return useQuery<Customer, Error>({
    queryKey: KEYS.customer(id),
    queryFn: async () => {
      const response = await salesApi.getCustomer(id);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useInvoices(params?: Parameters<typeof salesApi.getInvoices>[0]) {
  return useQuery<InvoiceListItem[], Error>({
    queryKey: KEYS.invoices(params),
    queryFn: async () => {
      const response = await salesApi.getInvoices(params);
      return response.data;
    },
  });
}

export function useInvoice(id: number) {
  return useQuery<SalesInvoice, Error>({
    queryKey: KEYS.invoice(id),
    queryFn: async () => {
      const response = await salesApi.getInvoice(id);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useQuotes(params?: Parameters<typeof salesApi.getQuotes>[0]) {
  return useQuery<SalesQuote[], Error>({
    queryKey: KEYS.quotes(params),
    queryFn: async () => {
      const response = await salesApi.getQuotes(params);
      return response.data;
    },
  });
}

export function useRevenueByPeriod(year?: number) {
  return useQuery<RevenueByPeriodRow[], Error>({
    queryKey: KEYS.revenueByPeriod(year),
    queryFn: async () => {
      const response = await salesApi.getRevenueByPeriod(year);
      return response.data;
    },
  });
}

export function useTopCustomers(limit?: number) {
  return useQuery<TopCustomerRow[], Error>({
    queryKey: KEYS.topCustomers(limit),
    queryFn: async () => {
      const response = await salesApi.getTopCustomers(limit);
      return response.data;
    },
  });
}

export function useCreateInvoice() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CreateInvoice) => {
      const response = await salesApi.createInvoice(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales', 'invoices'] });
    },
  });
}

export function useIssueInvoice() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await salesApi.issueInvoice(id);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales', 'invoices'] });
      queryClient.invalidateQueries({ queryKey: ['sales', 'customers'] });
      queryClient.invalidateQueries({ queryKey: ['finance', 'reports'] });
      queryClient.invalidateQueries({ queryKey: ['inventory', 'stock'] });
    },
  });
}

export function useReceivePayment() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CreatePayment) => {
      const response = await salesApi.receivePayment(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales', 'payments'] });
      queryClient.invalidateQueries({ queryKey: ['sales', 'invoices'] });
      queryClient.invalidateQueries({ queryKey: ['sales', 'customers'] });
      queryClient.invalidateQueries({ queryKey: ['finance', 'reports'] });
    },
  });
}

export function useConvertQuote() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await salesApi.convertQuote(id);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales', 'quotes'] });
      queryClient.invalidateQueries({ queryKey: ['sales', 'invoices'] });
    },
  });
}