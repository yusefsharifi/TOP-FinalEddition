import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import {
  PurchaseOrder,
  PurchaseRequest,
  Supplier,
  PurchaseFilter,
  AdvancedPurchaseFilter,
  CreatePurchaseOrderRequest,
  UpdatePurchaseOrderRequest,
  CreatePurchaseRequestRequest,
  UpdatePurchaseRequestRequest,
  CreateSupplierRequest,
  UpdateSupplierRequest,
  PurchaseInvoice
} from '../../types/procurement';

// --- Purchase Orders ---
export const usePurchaseOrders = (filter?: AdvancedPurchaseFilter) =>
  useQuery<PurchaseOrder[]>(['purchaseOrders', filter], async () => {
    const { data } = await axios.get('/api/purchase/orders', { params: filter });
    return data;
  });

export const usePurchaseOrder = (id: number) =>
  useQuery<PurchaseOrder>(['purchaseOrder', id], async () => {
    const { data } = await axios.get(`/api/purchase/orders/${id}`);
    return data;
  });

export const useCreatePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: CreatePurchaseOrderRequest) => axios.post('/api/purchase/orders', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['purchaseOrders'])
    }
  );
};

export const useUpdatePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: UpdatePurchaseOrderRequest) => axios.put(`/api/purchase/orders/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['purchaseOrders'])
    }
  );
};

export const useDeletePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/purchase/orders/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['purchaseOrders'])
    }
  );
};

export const useArchivePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.post(`/api/purchase/orders/${id}/archive`),
    {
      onSuccess: () => queryClient.invalidateQueries(['purchaseOrders'])
    }
  );
};

export const useUnarchivePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.post(`/api/purchase/orders/${id}/unarchive`),
    {
      onSuccess: () => queryClient.invalidateQueries(['purchaseOrders'])
    }
  );
};

// --- Purchase Requests ---
export const usePurchaseRequests = (filter?: PurchaseFilter) =>
  useQuery<PurchaseRequest[]>(['purchaseRequests', filter], async () => {
    const { data } = await axios.get('/api/purchase/requests', { params: filter });
    return data;
  });

// --- Suppliers ---
export const useSuppliers = (filter?: any) =>
  useQuery<Supplier[]>(['suppliers', filter], async () => {
    const { data } = await axios.get('/api/purchase/suppliers', { params: filter });
    return data;
  });

// --- Purchase Invoices ---
export const usePurchaseInvoices = (filter?: any) =>
  useQuery<PurchaseInvoice[]>(['purchaseInvoices', filter], async () => {
    const { data } = await axios.get('/api/purchase/invoices', { params: filter });
    return data;
  });

export const useCreatePurchaseInvoice = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: any) => axios.post('/api/purchase/invoices', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['purchaseInvoices'])
    }
  );
};

export const useUpdatePurchaseInvoice = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: any) => axios.put(`/api/purchase/invoices/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['purchaseInvoices'])
    }
  );
};

export const useDeletePurchaseInvoice = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/purchase/invoices/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['purchaseInvoices'])
    }
  );
};

export const useOrderStatusHistory = (orderId: number) =>
  useQuery(['orderStatusHistory', orderId], async () => {
    const { data } = await axios.get(`/api/purchase/orders/${orderId}/status-history`);
    return data;
  }); 