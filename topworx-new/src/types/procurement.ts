// تعریف انواع داده‌ای ماژول خرید و تدارکات

export interface Supplier {
  id?: number;
  name: string;
  code: string;
  contactPerson: string;
  email: string;
  phone: string;
  address: string;
  taxNumber: string;
  bankAccount: string;
  creditLimit: number;
  paymentTerms: number; // روزهای اعتبار
  status: "فعال" | "غیرفعال" | "معلق";
  rating: number; // امتیاز 1-5
  notes?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface PurchaseRequest {
  id?: number;
  requestNumber: string;
  requesterId: number;
  requesterName: string;
  department: string;
  requestDate: Date;
  requiredDate: Date;
  priority: "کم" | "متوسط" | "زیاد" | "فوری";
  status: "در انتظار" | "تأیید شده" | "رد شده" | "لغو شده";
  totalAmount: number;
  currency: "تومان" | "دلار" | "یورو";
  description: string;
  items: PurchaseRequestItem[];
  attachments?: string[]; // مسیر فایل‌های پیوست
  approvedBy?: number;
  approvedAt?: Date;
  rejectionReason?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface PurchaseRequestItem {
  id?: number;
  itemName: string;
  description: string;
  quantity: number;
  unit: string;
  estimatedPrice: number;
  totalPrice: number;
  specifications?: string;
}

export interface PurchaseOrder {
  id?: number;
  orderNumber: string;
  requestId?: number;
  supplierId: number;
  supplierName: string;
  orderDate: Date;
  expectedDeliveryDate: Date;
  actualDeliveryDate?: Date;
  status: "در انتظار" | "تأیید شده" | "ارسال شده" | "دریافت شده" | "لغو شده";
  totalAmount: number;
  currency: "تومان" | "دلار" | "یورو";
  taxAmount: number;
  discountAmount: number;
  finalAmount: number;
  paymentTerms: number;
  paymentStatus: "پرداخت نشده" | "نیمه پرداخت" | "پرداخت شده";
  items: PurchaseOrderItem[];
  notes?: string;
  attachments?: string[];
  createdBy: number;
  approvedBy?: number;
  approvedAt?: Date;
  createdAt?: Date;
  updatedAt?: Date;
  isArchived?: boolean;
}

export interface PurchaseOrderItem {
  id?: number;
  itemName: string;
  description: string;
  quantity: number;
  unit: string;
  unitPrice: number;
  totalPrice: number;
  receivedQuantity: number;
  specifications?: string;
}

export interface PurchaseInvoice {
  id?: number;
  invoiceNumber: string;
  orderId: number;
  supplierId: number;
  supplierName: string;
  invoiceDate: Date;
  dueDate: Date;
  amount: number;
  taxAmount: number;
  totalAmount: number;
  currency: "تومان" | "دلار" | "یورو";
  status: "پرداخت نشده" | "نیمه پرداخت" | "پرداخت شده" | "تأخیر";
  paymentMethod?: "نقدی" | "چک" | "کارت" | "انتقال";
  paymentDate?: Date;
  attachment?: string; // مسیر فایل فاکتور
  notes?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface PurchaseOrderStatus {
  id?: number;
  orderId: number;
  status: PurchaseOrder["status"];
  changedBy: number;
  changedByName: string;
  changedAt: Date;
  notes?: string;
}

export interface SupplierRating {
  id?: number;
  supplierId: number;
  orderId: number;
  rating: number; // 1-5
  criteria: {
    quality: number;
    delivery: number;
    communication: number;
    price: number;
  };
  comments?: string;
  ratedBy: number;
  ratedAt: Date;
}

export interface ProcurementDashboard {
  totalOrders: number;
  pendingOrders: number;
  deliveredOrders: number;
  totalSpent: number;
  overdueOrders: number;
  topSuppliers: Array<{
    supplierId: number;
    supplierName: string;
    totalOrders: number;
    totalAmount: number;
  }>;
  recentOrders: PurchaseOrder[];
  overdueInvoices: PurchaseInvoice[];
}

export interface PurchaseFilter {
  search?: string;
  status?: PurchaseOrder["status"];
  supplierId?: number;
  dateFrom?: Date;
  dateTo?: Date;
  amountFrom?: number;
  amountTo?: number;
  includeArchived?: boolean;
}

export interface SupplierFilter {
  search?: string;
  status?: Supplier["status"];
  rating?: number;
  hasOverdueInvoices?: boolean;
}

// انواع برای API
export interface CreatePurchaseRequestRequest {
  requesterId: number;
  department: string;
  requiredDate: Date;
  priority: PurchaseRequest["priority"];
  description: string;
  items: Omit<PurchaseRequestItem, "id" | "totalPrice">[];
}

export interface UpdatePurchaseRequestRequest {
  id: number;
  requiredDate?: Date;
  priority?: PurchaseRequest["priority"];
  description?: string;
  items?: Omit<PurchaseRequestItem, "id" | "totalPrice">[];
}

export interface CreatePurchaseOrderRequest {
  requestId?: number;
  supplierId: number;
  expectedDeliveryDate: Date;
  items: Omit<PurchaseOrderItem, "id" | "totalPrice" | "receivedQuantity">[];
  notes?: string;
}

export interface UpdatePurchaseOrderRequest {
  id: number;
  expectedDeliveryDate?: Date;
  items?: Omit<PurchaseOrderItem, "id" | "totalPrice" | "receivedQuantity">[];
  notes?: string;
}

export interface CreateSupplierRequest {
  name: string;
  code: string;
  contactPerson: string;
  email: string;
  phone: string;
  address: string;
  taxNumber: string;
  bankAccount: string;
  creditLimit: number;
  paymentTerms: number;
  notes?: string;
}

export interface UpdateSupplierRequest {
  id: number;
  name?: string;
  contactPerson?: string;
  email?: string;
  phone?: string;
  address?: string;
  creditLimit?: number;
  paymentTerms?: number;
  status?: Supplier["status"];
  notes?: string;
}

// انواع برای فیلترها و جستجو
export interface AdvancedPurchaseFilter extends PurchaseFilter {
  createdBy?: number;
  approvedBy?: number;
  paymentStatus?: PurchaseOrder["paymentStatus"];
  deliveryStatus?: "در موعد" | "تأخیر" | "زودتر از موعد";
}

export interface SupplierAnalytics {
  supplierId: number;
  supplierName: string;
  totalOrders: number;
  totalAmount: number;
  averageRating: number;
  onTimeDeliveryRate: number;
  qualityRating: number;
  lastOrderDate?: Date;
  overdueInvoicesCount: number;
  overdueInvoicesAmount: number;
}

// انواع برای اعلان‌ها
export interface ProcurementNotification {
  id: number;
  type: "overdue_order" | "overdue_invoice" | "delivery_reminder" | "approval_required";
  title: string;
  message: string;
  relatedId: number; // ID سفارش یا فاکتور
  relatedType: "order" | "invoice" | "request";
  isRead: boolean;
  createdAt: Date;
} 