// topworx-new/src/api/inventory/index.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import {
  Product,
  Category,
  Supplier,
  StockTransaction,
  PurchaseOrder,
  InventoryCount,
  Warehouse,
  InventoryAlert,
  InventoryItem,
} from './types';

// --- Products ---
export const useProducts = (filter?: any) =>
  useQuery<Product[]>(['products', filter], async () => {
    const { data } = await axios.get('/api/inventory/products', { params: filter });
    return data;
  });

export const useInventoryItems = (filter?: any) =>
  useQuery<InventoryItem[]>(['inventoryItems', filter], async () => {
    const { data } = await axios.get('/api/inventory/items', { params: filter });
    return data;
  });

export const useCreateProduct = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Product>) => axios.post('/api/inventory/products', payload),
    { onSuccess: () => queryClient.invalidateQueries(['products']) }
  );
};

export const useUpdateProduct = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Product>) =>
      axios.put(`/api/inventory/products/${payload.id}`, payload),
    { onSuccess: () => queryClient.invalidateQueries(['products']) }
  );
};

export const useDeleteProduct = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/inventory/products/${id}`),
    { onSuccess: () => queryClient.invalidateQueries(['products']) }
  );
};

// --- Categories ---
export const useCategories = (filter?: any) =>
  useQuery<Category[]>(['categories', filter], async () => {
    const { data } = await axios.get('/api/inventory/categories', { params: filter });
    return data;
  });

export const useCreateCategory = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Category>) => axios.post('/api/inventory/categories', payload),
    { onSuccess: () => queryClient.invalidateQueries(['categories']) }
  );
};

export const useUpdateCategory = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Category>) =>
      axios.put(`/api/inventory/categories/${payload.id}`, payload),
    { onSuccess: () => queryClient.invalidateQueries(['categories']) }
  );
};

export const useDeleteCategory = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/inventory/categories/${id}`),
    { onSuccess: () => queryClient.invalidateQueries(['categories']) }
  );
};

// --- Suppliers ---
export const useSuppliers = (filter?: any) =>
  useQuery<Supplier[]>(['suppliers', filter], async () => {
    const { data } = await axios.get('/api/inventory/suppliers', { params: filter });
    return data;
  });

export const useCreateSupplier = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Supplier>) => axios.post('/api/inventory/suppliers', payload),
    { onSuccess: () => queryClient.invalidateQueries(['suppliers']) }
  );
};

export const useUpdateSupplier = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Supplier>) =>
      axios.put(`/api/inventory/suppliers/${payload.id}`, payload),
    { onSuccess: () => queryClient.invalidateQueries(['suppliers']) }
  );
};

export const useDeleteSupplier = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/inventory/suppliers/${id}`),
    { onSuccess: () => queryClient.invalidateQueries(['suppliers']) }
  );
};

// --- Stock Transactions ---
export const useStockTransactions = (filter?: any) =>
  useQuery<StockTransaction[]>(['stockTransactions', filter], async () => {
    const { data } = await axios.get('/api/inventory/stock-transactions', { params: filter });
    return data;
  });

export const useCreateStockTransaction = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<StockTransaction>) =>
      axios.post('/api/inventory/stock-transactions', payload),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['stockTransactions']);
        queryClient.invalidateQueries(['inventoryItems']);
      },
    }
  );
};

// --- Purchase Orders ---
export const usePurchaseOrders = (filter?: any) =>
  useQuery<PurchaseOrder[]>(['purchaseOrders', filter], async () => {
    const { data } = await axios.get('/api/inventory/purchase-orders', { params: filter });
    return data;
  });

export const useCreatePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<PurchaseOrder>) =>
      axios.post('/api/inventory/purchase-orders', payload),
    { onSuccess: () => queryClient.invalidateQueries(['purchaseOrders']) }
  );
};

export const useUpdatePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<PurchaseOrder>) =>
      axios.put(`/api/inventory/purchase-orders/${payload.id}`, payload),
    { onSuccess: () => queryClient.invalidateQueries(['purchaseOrders']) }
  );
};

// --- Inventory Count ---
export const useInventoryCounts = (filter?: any) =>
  useQuery<InventoryCount[]>(['inventoryCounts', filter], async () => {
    const { data } = await axios.get('/api/inventory/counts', { params: filter });
    return data;
  });

export const useCreateInventoryCount = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<InventoryCount>) =>
      axios.post('/api/inventory/counts', payload),
    { onSuccess: () => queryClient.invalidateQueries(['inventoryCounts']) }
  );
};

// --- Warehouses ---
export const useWarehouses = (filter?: any) =>
  useQuery<Warehouse[]>(['warehouses', filter], async () => {
    const { data } = await axios.get('/api/inventory/warehouses', { params: filter });
    return data;
  });

// --- Alerts ---
export const useInventoryAlerts = () =>
  useQuery<InventoryAlert[]>(['inventoryAlerts'], async () => {
    const { data } = await axios.get('/api/inventory/alerts');
    return data;
  });

export const useMarkAlertRead = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.patch(`/api/inventory/alerts/${id}/read`),
    { onSuccess: () => queryClient.invalidateQueries(['inventoryAlerts']) }
  );
};
