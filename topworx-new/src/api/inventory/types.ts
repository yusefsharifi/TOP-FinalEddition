// topworx-new/src/api/inventory/types.ts

export interface Warehouse {
  id: string;
  name: string;
  location: string;
  manager: { id: string; name: string };
}

export interface Product {
  id: string;
  code: string;
  name: string;
  category: string;
  unit: string;
  minStock: number;
  maxStock: number;
  createdAt: string;
  updatedAt: string;
}

export interface InventoryItem {
  id: string;
  product: Product;
  warehouse: Warehouse;
  quantity: number;
  lastMovement: string;
  status: 'ok' | 'low' | 'over';
  history?: {
    date: string;
    user: string;
    action: string;
    quantity: number;
    description?: string;
  }[];
}

export interface Category {
  id: number;
  name: string;
  description?: string;
}

export interface Supplier {
  id: number;
  name: string;
  contactPerson?: string;
  phone?: string;
  email?: string;
  address?: string;
}

export type TransactionType = 'in' | 'out' | 'transfer' | 'adjustment';

export interface StockTransaction {
  id: number;
  product: Product;
  warehouse: Warehouse;
  type: TransactionType;
  quantity: number;
  date: string;
  note?: string;
  createdBy?: string;
}

export interface PurchaseOrder {
  id: number;
  supplier: Supplier;
  status: 'draft' | 'pending' | 'approved' | 'received' | 'cancelled';
  items: {
    product: Product;
    quantity: number;
    unitPrice: number;
  }[];
  totalAmount: number;
  orderDate: string;
  expectedDate?: string;
  note?: string;
}

export interface InventoryCount {
  id: number;
  warehouse: Warehouse;
  status: 'draft' | 'in_progress' | 'completed';
  items: {
    product: Product;
    expectedQty: number;
    actualQty: number;
    difference: number;
  }[];
  startedAt: string;
  completedAt?: string;
}

export interface InventoryAlert {
  id: number;
  product: Product;
  warehouse: Warehouse;
  type: 'low_stock' | 'overstock' | 'expiry';
  message: string;
  createdAt: string;
  isRead: boolean;
}
