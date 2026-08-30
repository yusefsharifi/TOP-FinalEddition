export type ProductStatus = 'active' | 'inactive' | 'discontinued';
export type StockStatus = 'in_stock' | 'low_stock' | 'out_of_stock' | 'overstocked';
export type TransactionType = 'in' | 'out' | 'adjustment' | 'transfer';
export type UnitType = 'piece' | 'kg' | 'liter' | 'meter' | 'box' | 'pack';

export interface Product {
  id?: number;
  sku: string;
  name: string;
  description?: string;
  category: string;
  brand?: string;
  unit: UnitType;
  price: number;
  cost: number;
  stockQuantity: number;
  minStockLevel: number;
  maxStockLevel: number;
  status: ProductStatus;
  stockStatus: StockStatus;
  barcode?: string;
  weight?: number;
  dimensions?: {
    length: number;
    width: number;
    height: number;
  };
  images?: {
    id: string;
    url: string;
    alt: string;
  }[];
  specifications?: Record<string, any>;
  supplierId?: number;
  supplierName?: string;
  location?: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface Category {
  id?: number;
  name: string;
  code: string;
  parentId?: number;
  description?: string;
  isActive: boolean;
  productCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface Supplier {
  id?: number;
  name: string;
  code: string;
  contactPerson: string;
  email: string;
  phone: string;
  address: string;
  website?: string;
  rating: number;
  isActive: boolean;
  paymentTerms: string;
  leadTime: number;
  minimumOrder: number;
  createdAt: string;
  updatedAt: string;
}

export interface StockTransaction {
  id?: number;
  transactionNumber: string;
  productId: number;
  productName: string;
  productSku: string;
  type: TransactionType;
  quantity: number;
  unitPrice?: number;
  totalAmount?: number;
  referenceNumber?: string;
  notes?: string;
  location?: string;
  performedBy: string;
  performedAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface PurchaseOrder {
  id?: number;
  orderNumber: string;
  supplierId: number;
  supplierName: string;
  orderDate: string;
  expectedDeliveryDate: string;
  status: 'draft' | 'sent' | 'confirmed' | 'received' | 'cancelled';
  subtotal: number;
  taxAmount: number;
  shippingAmount: number;
  totalAmount: number;
  currency: string;
  notes?: string;
  items: PurchaseOrderItem[];
  createdAt: string;
  updatedAt: string;
}

export interface PurchaseOrderItem {
  id?: number;
  productId: number;
  productName: string;
  productSku: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  receivedQuantity: number;
}

export interface InventoryCount {
  id?: number;
  countNumber: string;
  location: string;
  status: 'draft' | 'in_progress' | 'completed' | 'approved';
  startDate: string;
  endDate?: string;
  countedBy: string;
  approvedBy?: string;
  approvedDate?: string;
  notes?: string;
  items: InventoryCountItem[];
  createdAt: string;
  updatedAt: string;
}

export interface InventoryCountItem {
  id?: number;
  productId: number;
  productName: string;
  productSku: string;
  expectedQuantity: number;
  actualQuantity: number;
  difference: number;
  notes?: string;
}

export interface Warehouse {
  id?: number;
  name: string;
  code: string;
  address: string;
  manager: string;
  phone: string;
  email: string;
  isActive: boolean;
  capacity: number;
  usedCapacity: number;
  zones: WarehouseZone[];
  createdAt: string;
  updatedAt: string;
}

export interface WarehouseZone {
  id?: number;
  name: string;
  code: string;
  description?: string;
  capacity: number;
  usedCapacity: number;
  isActive: boolean;
}

export interface InventoryAlert {
  id?: number;
  productId: number;
  productName: string;
  productSku: string;
  type: 'low_stock' | 'overstock' | 'expiry' | 'quality_issue';
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  isRead: boolean;
  createdAt: string;
} 