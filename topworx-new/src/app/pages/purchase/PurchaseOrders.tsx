import React, { useState } from 'react';
import { Alert, Button, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { PurchaseOrder } from '../../../types/procurement';
import { PurchaseOrdersTable } from '../../components/purchase/PurchaseOrdersTable';
import { PurchaseOrderForm } from '../../components/purchase/PurchaseOrderForm';
import { PurchaseOrderStatusHistory } from '../../components/purchase/PurchaseOrderStatusHistory';
import { PurchaseOrderExportButtons } from '../../components/purchase/PurchaseOrderExportButtons';
import { useCreatePurchaseOrder, useUpdatePurchaseOrder } from '../../../api/procurement';

export const PurchaseOrders: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [editOrder, setEditOrder] = useState<PurchaseOrder | null>(null);
  const [statusHistoryOpen, setStatusHistoryOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<PurchaseOrder | null>(null);
  const [exportData, setExportData] = useState<PurchaseOrder[]>([]);
  const [snackbar, setSnackbar] = useState<{ 
    open: boolean; 
    message: string; 
    severity: 'success' | 'error' 
  }>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  const createOrder = useCreatePurchaseOrder();
  const updateOrder = useUpdatePurchaseOrder();

  const handleEdit = (order: PurchaseOrder | null) => {
    setEditOrder(order);
    setFormOpen(true);
  };

  const handleViewStatusHistory = (order: PurchaseOrder) => {
    setSelectedOrder(order);
    setStatusHistoryOpen(true);
  };

  const handleExport = (orders: PurchaseOrder[]) => {
    setExportData(orders);
  };

  const handleSave = async (data: any) => {
    try {
      if (editOrder) {
        await updateOrder.mutateAsync({ id: editOrder.id, ...data });
        setSnackbar({ 
          open: true, 
          message: 'سفارش با موفقیت ویرایش شد.', 
          severity: 'success' 
        });
      } else {
        await createOrder.mutateAsync(data);
        setSnackbar({ 
          open: true, 
          message: 'سفارش جدید با موفقیت ایجاد شد.', 
          severity: 'success' 
        });
      }
      setFormOpen(false);
      setEditOrder(null);
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'خطا در ذخیره سفارش.', 
        severity: 'error' 
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  return (
    <div style={{  p: 3  }}>
      <div style={{  mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center'  }}>
        <Typography.Title level={2}>مدیریت سفارشات خرید</Typography.Title>
        <div style={{  display: 'flex', gap: 2  }}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={() => handleEdit(null)}
          >
            افزودن سفارش جدید
          </Button>
          {exportData.length > 0 && (
            <PurchaseOrderExportButtons orders={exportData} />
          )}
        </div>
      </div>

      <PurchaseOrdersTable
        onEdit={handleEdit}
        onViewStatusHistory={handleViewStatusHistory}
        onExport={handleExport}
        userRole="admin"
      />

      <PurchaseOrderForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditOrder(null);
        }}
        order={editOrder}
        onSave={handleSave}
      />

      <PurchaseOrderStatusHistory
        open={statusHistoryOpen}
        onClose={() => setStatusHistoryOpen(false)}
        order={selectedOrder}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </div>
    </div>
  );
}; 