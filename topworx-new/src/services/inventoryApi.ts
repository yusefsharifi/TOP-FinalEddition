// src/services/inventoryApi.ts
// ============================================================================
// Inventory API
// ============================================================================

import { apiClient } from './api';
import {
  InventoryItem,
  InventoryItemDetail,
  InventoryLocation,
  StockLevel,
  InventoryMovement,
  LowStockItem,
  InventoryCategory,
  Supplier,
  CreateItemRequest,
  InboundMovementRequest,
  OutboundMovementRequest,
  StockTransferRequest,
  StockAdjustRequest,
} from '../types';

const BASE = '/inventory';

export const inventoryApi = {
  // Items
  getItems: (params?: {
    category_id?: number;
    search?: string;
    low_stock?: boolean;
    is_active?: boolean;
    offset?: number;
    limit?: number;
  }) => apiClient.get<InventoryItem[]>(`${BASE}/items`, { params }),

  getItem: (id: number) =>
    apiClient.get<InventoryItemDetail>(`${BASE}/items/${id}`),

  createItem: (data: CreateItemRequest) =>
    apiClient.post<InventoryItem>(`${BASE}/items`, data),

  updateItem: (id: number, data: Partial<CreateItemRequest>) =>
    apiClient.put<InventoryItem>(`${BASE}/items/${id}`, data),

  deleteItem: (id: number) =>
    apiClient.delete(`${BASE}/items/${id}`),

  // Stock
  getStock: (params?: { item_id?: number; location_id?: number }) =>
    apiClient.get<StockLevel[]>(`${BASE}/stock`, { params }),

  adjustStock: (data: StockAdjustRequest) =>
    apiClient.post<InventoryMovement>(`${BASE}/stock/adjust`, data),

  transferStock: (data: StockTransferRequest) =>
    apiClient.post<InventoryMovement[]>(`${BASE}/stock/transfer`, data),

  // Movements
  getMovements: (params?: {
    item_id?: number;
    location_id?: number;
    movement_type?: string;
    date_from?: string;
    date_to?: string;
    offset?: number;
    limit?: number;
  }) => apiClient.get<InventoryMovement[]>(`${BASE}/movements`, { params }),

  receiveGoods: (data: InboundMovementRequest) =>
    apiClient.post<InventoryMovement>(`${BASE}/movements/inbound`, data),

  issueGoods: (data: OutboundMovementRequest) =>
    apiClient.post<InventoryMovement>(`${BASE}/movements/outbound`, data),

  // Reports
  getLowStock: (location_id?: number) =>
    apiClient.get<LowStockItem[]>(`${BASE}/reports/low-stock`, {
      params: location_id ? { location_id } : undefined,
    }),

  getMovementSummary: (date_from: string, date_to: string, item_id?: number) =>
    apiClient.get(`${BASE}/reports/movement-summary`, {
      params: { date_from, date_to, item_id },
    }),

  // Locations
  getLocations: () =>
    apiClient.get<InventoryLocation[]>(`${BASE}/locations`),

  // Suppliers
  getSuppliers: () =>
    apiClient.get<Supplier[]>(`${BASE}/suppliers`),

  // Categories
  getCategories: () =>
    apiClient.get<InventoryCategory[]>(`${BASE}/categories`),
};