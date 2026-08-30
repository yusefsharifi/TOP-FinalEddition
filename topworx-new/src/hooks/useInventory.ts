// src/hooks/useInventory.ts
// ============================================================================
// Inventory Hooks
// ============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryApi } from '../services/inventoryApi';
import {
  InventoryItem,
  InventoryItemDetail,
  StockLevel,
  InventoryMovement,
  LowStockItem,
  InventoryLocation,
  InventoryCategory,
  Supplier,
  CreateItemRequest,
  InboundMovementRequest,
  OutboundMovementRequest,
  StockTransferRequest,
  StockAdjustRequest,
} from '../types';

const KEYS = {
  items: (params?: object) => ['inventory', 'items', params],
  item: (id: number) => ['inventory', 'items', id],
  stock: (params?: object) => ['inventory', 'stock', params],
  movements: (params?: object) => ['inventory', 'movements', params],
  lowStock: ['inventory', 'reports', 'low-stock'],
  locations: ['inventory', 'locations'],
  suppliers: ['inventory', 'suppliers'],
  categories: ['inventory', 'categories'],
};

export function useInventoryItems(params?: Parameters<typeof inventoryApi.getItems>[0]) {
  return useQuery<InventoryItem[], Error>({
    queryKey: KEYS.items(params),
    queryFn: async () => {
      const response = await inventoryApi.getItems(params);
      return response.data;
    },
  });
}

export function useInventoryItem(id: number) {
  return useQuery<InventoryItemDetail, Error>({
    queryKey: KEYS.item(id),
    queryFn: async () => {
      const response = await inventoryApi.getItem(id);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useStockLevels(params?: Parameters<typeof inventoryApi.getStock>[0]) {
  return useQuery<StockLevel[], Error>({
    queryKey: KEYS.stock(params),
    queryFn: async () => {
      const response = await inventoryApi.getStock(params);
      return response.data;
    },
  });
}

export function useLowStockReport() {
  return useQuery<LowStockItem[], Error>({
    queryKey: KEYS.lowStock,
    queryFn: async () => {
      const response = await inventoryApi.getLowStock();
      return response.data;
    },
  });
}

export function useLocations() {
  return useQuery<InventoryLocation[], Error>({
    queryKey: KEYS.locations,
    queryFn: async () => {
      const response = await inventoryApi.getLocations();
      return response.data;
    },
  });
}

export function useSuppliers() {
  return useQuery<Supplier[], Error>({
    queryKey: KEYS.suppliers,
    queryFn: async () => {
      const response = await inventoryApi.getSuppliers();
      return response.data;
    },
  });
}

export function useCategories() {
  return useQuery<InventoryCategory[], Error>({
    queryKey: KEYS.categories,
    queryFn: async () => {
      const response = await inventoryApi.getCategories();
      return response.data;
    },
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CreateItemRequest) => {
      const response = await inventoryApi.createItem(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'items'] });
    },
  });
}

export function useReceiveGoods() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: InboundMovementRequest) => {
      const response = await inventoryApi.receiveGoods(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'stock'] });
      queryClient.invalidateQueries({ queryKey: ['inventory', 'movements'] });
    },
  });
}

export function useIssueGoods() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: OutboundMovementRequest) => {
      const response = await inventoryApi.issueGoods(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'stock'] });
      queryClient.invalidateQueries({ queryKey: ['inventory', 'movements'] });
    },
  });
}

export function useTransferStock() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: StockTransferRequest) => {
      const response = await inventoryApi.transferStock(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'stock'] });
      queryClient.invalidateQueries({ queryKey: ['inventory', 'movements'] });
    },
  });
}

export function useAdjustStock() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: StockAdjustRequest) => {
      const response = await inventoryApi.adjustStock(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'stock'] });
      queryClient.invalidateQueries({ queryKey: ['inventory', 'movements'] });
    },
  });
}