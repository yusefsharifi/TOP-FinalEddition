// API Hooks برای ماژول خرید و تدارکات
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Supplier,
  PurchaseRequest,
  PurchaseOrder,
  PurchaseInvoice,
  PurchaseFilter,
  SupplierFilter,
  ProcurementDashboard,
  CreatePurchaseRequestRequest,
  UpdatePurchaseRequestRequest,
  CreatePurchaseOrderRequest,
  UpdatePurchaseOrderRequest,
  CreateSupplierRequest,
  UpdateSupplierRequest,
  SupplierAnalytics,
  ProcurementNotification,
} from '../components/Procurement/types';

// Mock API functions - در آینده با API واقعی جایگزین می‌شود
const API_BASE_URL = '/api/procurement';

// Mock data
const mockSuppliers: Supplier[] = [
  {
    id: 1,
    name: 'شرکت تأمین تجهیزات تهران',
    code: 'SUP001',
    contactPerson: 'احمد محمدی',
    email: 'ahmad@tehran-supply.com',
    phone: '021-12345678',
    address: 'تهران، خیابان ولیعصر، پلاک 123',
    taxNumber: '1234567890',
    bankAccount: 'IR123456789012345678901234',
    creditLimit: 10000000,
    paymentTerms: 30,
    status: 'فعال',
    rating: 4.5,
    notes: 'تأمین‌کننده معتبر با سابقه 10 ساله',
    createdAt: new Date('2023-01-01'),
    updatedAt: new Date('2024-01-01'),
  },
  {
    id: 2,
    name: 'شرکت الکترونیک ایران',
    code: 'SUP002',
    contactPerson: 'فاطمه احمدی',
    email: 'fateme@iran-electronics.com',
    phone: '021-87654321',
    address: 'تهران، خیابان انقلاب، پلاک 456',
    taxNumber: '0987654321',
    bankAccount: 'IR987654321098765432109876',
    creditLimit: 5000000,
    paymentTerms: 15,
    status: 'فعال',
    rating: 4.2,
    notes: 'تخصص در تجهیزات الکترونیک',
    createdAt: new Date('2023-02-01'),
    updatedAt: new Date('2024-01-15'),
  },
];

const mockPurchaseOrders: PurchaseOrder[] = [
  {
    id: 1,
    orderNumber: 'PO-2024-001',
    supplierId: 1,
    supplierName: 'شرکت تأمین تجهیزات تهران',
    orderDate: new Date('2024-01-15'),
    expectedDeliveryDate: new Date('2024-02-15'),
    status: 'تأیید شده',
    totalAmount: 5000000,
    currency: 'تومان',
    taxAmount: 500000,
    discountAmount: 100000,
    finalAmount: 5400000,
    paymentTerms: 30,
    paymentStatus: 'پرداخت نشده',
    items: [
      {
        id: 1,
        itemName: 'لپ‌تاپ Dell Latitude',
        description: 'لپ‌تاپ اداری با مشخصات بالا',
        quantity: 5,
        unit: 'عدد',
        unitPrice: 800000,
        totalPrice: 4000000,
        receivedQuantity: 0,
        specifications: 'Intel i7, 16GB RAM, 512GB SSD',
      },
      {
        id: 2,
        itemName: 'چاپگر HP LaserJet',
        description: 'چاپگر لیزری رنگی',
        quantity: 2,
        unit: 'عدد',
        unitPrice: 500000,
        totalPrice: 1000000,
        receivedQuantity: 0,
        specifications: 'A4, 25ppm, Network Ready',
      },
    ],
    notes: 'تحویل در محل شرکت',
    createdBy: 1,
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-01-15'),
  },
  {
    id: 2,
    orderNumber: 'PO-2024-002',
    supplierId: 2,
    supplierName: 'شرکت الکترونیک ایران',
    orderDate: new Date('2024-01-20'),
    expectedDeliveryDate: new Date('2024-02-10'),
    status: 'ارسال شده',
    totalAmount: 3000000,
    currency: 'تومان',
    taxAmount: 300000,
    discountAmount: 0,
    finalAmount: 3300000,
    paymentTerms: 15,
    paymentStatus: 'نیمه پرداخت',
    items: [
      {
        id: 3,
        itemName: 'مانیتور Samsung 24"',
        description: 'مانیتور LED فول HD',
        quantity: 10,
        unit: 'عدد',
        unitPrice: 300000,
        totalPrice: 3000000,
        receivedQuantity: 8,
        specifications: '1920x1080, HDMI, VGA',
      },
    ],
    notes: 'تحویل تدریجی',
    createdBy: 1,
    createdAt: new Date('2024-01-20'),
    updatedAt: new Date('2024-01-25'),
  },
];

const mockPurchaseRequests: PurchaseRequest[] = [
  {
    id: 1,
    requestNumber: 'PR-2024-001',
    requesterId: 1,
    requesterName: 'علی رضایی',
    department: 'فناوری اطلاعات',
    requestDate: new Date('2024-01-10'),
    requiredDate: new Date('2024-02-10'),
    priority: 'زیاد',
    status: 'تأیید شده',
    totalAmount: 5000000,
    currency: 'تومان',
    description: 'خرید تجهیزات کامپیوتری برای بخش IT',
    items: [
      {
        id: 1,
        itemName: 'لپ‌تاپ',
        description: 'لپ‌تاپ اداری',
        quantity: 5,
        unit: 'عدد',
        estimatedPrice: 800000,
        totalPrice: 4000000,
        specifications: 'Intel i7, 16GB RAM',
      },
      {
        id: 2,
        itemName: 'چاپگر',
        description: 'چاپگر لیزری',
        quantity: 2,
        unit: 'عدد',
        estimatedPrice: 500000,
        totalPrice: 1000000,
        specifications: 'A4, Network Ready',
      },
    ],
    approvedBy: 2,
    approvedAt: new Date('2024-01-12'),
    createdAt: new Date('2024-01-10'),
    updatedAt: new Date('2024-01-12'),
  },
];

const mockPurchaseInvoices: PurchaseInvoice[] = [
  {
    id: 1,
    invoiceNumber: 'INV-2024-001',
    orderId: 1,
    supplierId: 1,
    supplierName: 'شرکت تأمین تجهیزات تهران',
    invoiceDate: new Date('2024-01-25'),
    dueDate: new Date('2024-02-24'),
    amount: 5000000,
    taxAmount: 500000,
    totalAmount: 5500000,
    currency: 'تومان',
    status: 'پرداخت نشده',
    notes: 'فاکتور مربوط به سفارش PO-2024-001',
    createdAt: new Date('2024-01-25'),
    updatedAt: new Date('2024-01-25'),
  },
];

// API Functions
const api = {
  // Suppliers
  getSuppliers: async (filter?: SupplierFilter): Promise<Supplier[]> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    return mockSuppliers.filter(supplier => {
      if (filter?.search) {
        return supplier.name.includes(filter.search) || 
               supplier.code.includes(filter.search) ||
               supplier.contactPerson.includes(filter.search);
      }
      if (filter?.status) {
        return supplier.status === filter.status;
      }
      if (filter?.rating) {
        return supplier.rating >= filter.rating;
      }
      return true;
    });
  },

  getSupplier: async (id: number): Promise<Supplier> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const supplier = mockSuppliers.find(s => s.id === id);
    if (!supplier) throw new Error('تأمین‌کننده یافت نشد');
    return supplier;
  },

  createSupplier: async (data: CreateSupplierRequest): Promise<Supplier> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const newSupplier: Supplier = {
      id: Math.max(...mockSuppliers.map(s => s.id || 0)) + 1,
      ...data,
      status: 'فعال',
      rating: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    mockSuppliers.push(newSupplier);
    return newSupplier;
  },

  updateSupplier: async (id: number, data: UpdateSupplierRequest): Promise<Supplier> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const index = mockSuppliers.findIndex(s => s.id === id);
    if (index === -1) throw new Error('تأمین‌کننده یافت نشد');
    mockSuppliers[index] = { ...mockSuppliers[index], ...data, updatedAt: new Date() };
    return mockSuppliers[index];
  },

  deleteSupplier: async (id: number): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const index = mockSuppliers.findIndex(s => s.id === id);
    if (index === -1) throw new Error('تأمین‌کننده یافت نشد');
    mockSuppliers.splice(index, 1);
  },

  // Purchase Requests
  getPurchaseRequests: async (): Promise<PurchaseRequest[]> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return mockPurchaseRequests;
  },

  getPurchaseRequest: async (id: number): Promise<PurchaseRequest> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const request = mockPurchaseRequests.find(r => r.id === id);
    if (!request) throw new Error('درخواست خرید یافت نشد');
    return request;
  },

  createPurchaseRequest: async (data: CreatePurchaseRequestRequest): Promise<PurchaseRequest> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const newRequest: PurchaseRequest = {
      id: Math.max(...mockPurchaseRequests.map(r => r.id || 0)) + 1,
      requestNumber: `PR-${new Date().getFullYear()}-${String(mockPurchaseRequests.length + 1).padStart(3, '0')}`,
      ...data,
      requesterName: 'کاربر سیستم', // در آینده از context کاربر گرفته می‌شود
      requestDate: new Date(),
      status: 'در انتظار',
      totalAmount: data.items.reduce((sum, item) => sum + (item.estimatedPrice * item.quantity), 0),
      items: data.items.map((item, index) => ({
        ...item,
        id: index + 1,
        totalPrice: item.estimatedPrice * item.quantity,
      })),
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    mockPurchaseRequests.push(newRequest);
    return newRequest;
  },

  updatePurchaseRequest: async (id: number, data: UpdatePurchaseRequestRequest): Promise<PurchaseRequest> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const index = mockPurchaseRequests.findIndex(r => r.id === id);
    if (index === -1) throw new Error('درخواست خرید یافت نشد');
    const updatedRequest = { ...mockPurchaseRequests[index], ...data, updatedAt: new Date() };
    if (data.items) {
      updatedRequest.totalAmount = data.items.reduce((sum, item) => sum + (item.estimatedPrice * item.quantity), 0);
      updatedRequest.items = data.items.map((item, idx) => ({
        ...item,
        id: idx + 1,
        totalPrice: item.estimatedPrice * item.quantity,
      }));
    }
    mockPurchaseRequests[index] = updatedRequest;
    return updatedRequest;
  },

  // Purchase Orders
  getPurchaseOrders: async (filter?: PurchaseFilter): Promise<PurchaseOrder[]> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return mockPurchaseOrders.filter(order => {
      if (filter?.search) {
        return order.orderNumber.includes(filter.search) || 
               order.supplierName.includes(filter.search);
      }
      if (filter?.status) {
        return order.status === filter.status;
      }
      if (filter?.supplierId) {
        return order.supplierId === filter.supplierId;
      }
      if (filter?.dateFrom) {
        return order.orderDate >= filter.dateFrom;
      }
      if (filter?.dateTo) {
        return order.orderDate <= filter.dateTo;
      }
      if (filter?.amountFrom) {
        return order.totalAmount >= filter.amountFrom;
      }
      if (filter?.amountTo) {
        return order.totalAmount <= filter.amountTo;
      }
      if (!filter?.includeArchived) {
        return !order.isArchived;
      }
      return true;
    });
  },

  getPurchaseOrder: async (id: number): Promise<PurchaseOrder> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const order = mockPurchaseOrders.find(o => o.id === id);
    if (!order) throw new Error('سفارش خرید یافت نشد');
    return order;
  },

  createPurchaseOrder: async (data: CreatePurchaseOrderRequest): Promise<PurchaseOrder> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const supplier = mockSuppliers.find(s => s.id === data.supplierId);
    if (!supplier) throw new Error('تأمین‌کننده یافت نشد');
    
    const newOrder: PurchaseOrder = {
      id: Math.max(...mockPurchaseOrders.map(o => o.id || 0)) + 1,
      orderNumber: `PO-${new Date().getFullYear()}-${String(mockPurchaseOrders.length + 1).padStart(3, '0')}`,
      ...data,
      supplierName: supplier.name,
      orderDate: new Date(),
      status: 'در انتظار',
      totalAmount: data.items.reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0),
      currency: 'تومان',
      taxAmount: 0,
      discountAmount: 0,
      finalAmount: data.items.reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0),
      paymentTerms: supplier.paymentTerms,
      paymentStatus: 'پرداخت نشده',
      items: data.items.map((item, index) => ({
        ...item,
        id: index + 1,
        totalPrice: item.unitPrice * item.quantity,
        receivedQuantity: 0,
      })),
      createdBy: 1, // در آینده از context کاربر گرفته می‌شود
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    mockPurchaseOrders.push(newOrder);
    return newOrder;
  },

  updatePurchaseOrder: async (id: number, data: UpdatePurchaseOrderRequest): Promise<PurchaseOrder> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const index = mockPurchaseOrders.findIndex(o => o.id === id);
    if (index === -1) throw new Error('سفارش خرید یافت نشد');
    const updatedOrder = { ...mockPurchaseOrders[index], ...data, updatedAt: new Date() };
    if (data.items) {
      updatedOrder.totalAmount = data.items.reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0);
      updatedOrder.finalAmount = updatedOrder.totalAmount + updatedOrder.taxAmount - updatedOrder.discountAmount;
      updatedOrder.items = data.items.map((item, idx) => ({
        ...item,
        id: idx + 1,
        totalPrice: item.unitPrice * item.quantity,
        receivedQuantity: 0,
      }));
    }
    mockPurchaseOrders[index] = updatedOrder;
    return updatedOrder;
  },

  deletePurchaseOrder: async (id: number): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const index = mockPurchaseOrders.findIndex(o => o.id === id);
    if (index === -1) throw new Error('سفارش خرید یافت نشد');
    mockPurchaseOrders.splice(index, 1);
  },

  // Purchase Invoices
  getPurchaseInvoices: async (): Promise<PurchaseInvoice[]> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return mockPurchaseInvoices;
  },

  getPurchaseInvoice: async (id: number): Promise<PurchaseInvoice> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const invoice = mockPurchaseInvoices.find(i => i.id === id);
    if (!invoice) throw new Error('فاکتور خرید یافت نشد');
    return invoice;
  },

  // Dashboard
  getProcurementDashboard: async (): Promise<ProcurementDashboard> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const totalOrders = mockPurchaseOrders.length;
    const pendingOrders = mockPurchaseOrders.filter(o => o.status === 'در انتظار').length;
    const deliveredOrders = mockPurchaseOrders.filter(o => o.status === 'دریافت شده').length;
    const totalSpent = mockPurchaseOrders.reduce((sum, o) => sum + o.finalAmount, 0);
    const overdueOrders = mockPurchaseOrders.filter(o => 
      o.status !== 'دریافت شده' && o.status !== 'لغو شده' && 
      o.expectedDeliveryDate < new Date()
    ).length;

    const supplierStats = mockSuppliers.map(supplier => {
      const supplierOrders = mockPurchaseOrders.filter(o => o.supplierId === supplier.id);
      return {
        supplierId: supplier.id!,
        supplierName: supplier.name,
        totalOrders: supplierOrders.length,
        totalAmount: supplierOrders.reduce((sum, o) => sum + o.finalAmount, 0),
      };
    }).sort((a, b) => b.totalAmount - a.totalAmount).slice(0, 5);

    return {
      totalOrders,
      pendingOrders,
      deliveredOrders,
      totalSpent,
      overdueOrders,
      topSuppliers: supplierStats,
      recentOrders: mockPurchaseOrders.slice(-5),
      overdueInvoices: mockPurchaseInvoices.filter(i => i.dueDate < new Date() && i.status !== 'پرداخت شده'),
    };
  },

  // Analytics
  getSupplierAnalytics: async (supplierId: number): Promise<SupplierAnalytics> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const supplier = mockSuppliers.find(s => s.id === supplierId);
    if (!supplier) throw new Error('تأمین‌کننده یافت نشد');
    
    const supplierOrders = mockPurchaseOrders.filter(o => o.supplierId === supplierId);
    const totalOrders = supplierOrders.length;
    const totalAmount = supplierOrders.reduce((sum, o) => sum + o.finalAmount, 0);
    const onTimeDeliveries = supplierOrders.filter(o => 
      o.status === 'دریافت شده' && o.actualDeliveryDate && 
      o.actualDeliveryDate <= o.expectedDeliveryDate
    ).length;
    const overdueInvoices = mockPurchaseInvoices.filter(i => 
      i.supplierId === supplierId && i.dueDate < new Date() && i.status !== 'پرداخت شده'
    );

    return {
      supplierId,
      supplierName: supplier.name,
      totalOrders,
      totalAmount,
      averageRating: supplier.rating,
      onTimeDeliveryRate: totalOrders > 0 ? (onTimeDeliveries / totalOrders) * 100 : 0,
      qualityRating: supplier.rating,
      lastOrderDate: supplierOrders.length > 0 ? 
        supplierOrders.sort((a, b) => new Date(b.orderDate).getTime() - new Date(a.orderDate).getTime())[0].orderDate : 
        undefined,
      overdueInvoicesCount: overdueInvoices.length,
      overdueInvoicesAmount: overdueInvoices.reduce((sum, i) => sum + i.totalAmount, 0),
    };
  },

  // Notifications
  getProcurementNotifications: async (): Promise<ProcurementNotification[]> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const notifications: ProcurementNotification[] = [];
    
    // Overdue orders
    mockPurchaseOrders.forEach(order => {
      if (order.status !== 'دریافت شده' && order.status !== 'لغو شده' && 
          order.expectedDeliveryDate < new Date()) {
        notifications.push({
          id: notifications.length + 1,
          type: 'overdue_order',
          title: 'سفارش تأخیر در تحویل',
          message: `سفارش ${order.orderNumber} از تأمین‌کننده ${order.supplierName} تأخیر در تحویل دارد`,
          relatedId: order.id!,
          relatedType: 'order',
          isRead: false,
          createdAt: new Date(),
        });
      }
    });

    // Overdue invoices
    mockPurchaseInvoices.forEach(invoice => {
      if (invoice.dueDate < new Date() && invoice.status !== 'پرداخت شده') {
        notifications.push({
          id: notifications.length + 1,
          type: 'overdue_invoice',
          title: 'فاکتور معوق',
          message: `فاکتور ${invoice.invoiceNumber} از تأمین‌کننده ${invoice.supplierName} معوق است`,
          relatedId: invoice.id!,
          relatedType: 'invoice',
          isRead: false,
          createdAt: new Date(),
        });
      }
    });

    return notifications;
  },
};

// React Query Hooks
export const useSuppliers = (filter?: SupplierFilter) => {
  return useQuery({
    queryKey: ['suppliers', filter],
    queryFn: () => api.getSuppliers(filter),
  });
};

export const useSupplier = (id: number) => {
  return useQuery({
    queryKey: ['supplier', id],
    queryFn: () => api.getSupplier(id),
    enabled: !!id,
  });
};

export const useCreateSupplier = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.createSupplier,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
    },
  });
};

export const useUpdateSupplier = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateSupplierRequest }) => 
      api.updateSupplier(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      queryClient.invalidateQueries({ queryKey: ['supplier', id] });
    },
  });
};

export const useDeleteSupplier = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteSupplier,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
    },
  });
};

export const usePurchaseRequests = () => {
  return useQuery({
    queryKey: ['purchase-requests'],
    queryFn: api.getPurchaseRequests,
  });
};

export const usePurchaseRequest = (id: number) => {
  return useQuery({
    queryKey: ['purchase-request', id],
    queryFn: () => api.getPurchaseRequest(id),
    enabled: !!id,
  });
};

export const useCreatePurchaseRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.createPurchaseRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-requests'] });
    },
  });
};

export const useUpdatePurchaseRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdatePurchaseRequestRequest }) => 
      api.updatePurchaseRequest(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['purchase-requests'] });
      queryClient.invalidateQueries({ queryKey: ['purchase-request', id] });
    },
  });
};

export const usePurchaseOrders = (filter?: PurchaseFilter) => {
  return useQuery({
    queryKey: ['purchase-orders', filter],
    queryFn: () => api.getPurchaseOrders(filter),
  });
};

export const usePurchaseOrder = (id: number) => {
  return useQuery({
    queryKey: ['purchase-order', id],
    queryFn: () => api.getPurchaseOrder(id),
    enabled: !!id,
  });
};

export const useCreatePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.createPurchaseOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['procurement-dashboard'] });
    },
  });
};

export const useUpdatePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdatePurchaseOrderRequest }) => 
      api.updatePurchaseOrder(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['purchase-order', id] });
      queryClient.invalidateQueries({ queryKey: ['procurement-dashboard'] });
    },
  });
};

export const useDeletePurchaseOrder = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deletePurchaseOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['procurement-dashboard'] });
    },
  });
};

export const usePurchaseInvoices = () => {
  return useQuery({
    queryKey: ['purchase-invoices'],
    queryFn: api.getPurchaseInvoices,
  });
};

export const usePurchaseInvoice = (id: number) => {
  return useQuery({
    queryKey: ['purchase-invoice', id],
    queryFn: () => api.getPurchaseInvoice(id),
    enabled: !!id,
  });
};

export const useProcurementDashboard = () => {
  return useQuery({
    queryKey: ['procurement-dashboard'],
    queryFn: api.getProcurementDashboard,
    refetchInterval: 30000, // هر 30 ثانیه بروزرسانی
  });
};

export const useSupplierAnalytics = (supplierId: number) => {
  return useQuery({
    queryKey: ['supplier-analytics', supplierId],
    queryFn: () => api.getSupplierAnalytics(supplierId),
    enabled: !!supplierId,
  });
};

export const useProcurementNotifications = () => {
  return useQuery({
    queryKey: ['procurement-notifications'],
    queryFn: api.getProcurementNotifications,
    refetchInterval: 60000, // هر 1 دقیقه بروزرسانی
  });
}; 