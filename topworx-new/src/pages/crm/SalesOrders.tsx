import React, { useState } from "react";
import { Alert, Button, Typography } from 'antd';
import { SalesOrder, SalesOrderStatus } from "../../../types/crm";
import { SalesOrdersTable } from "../../app/components/crm/SalesOrdersTable";
import { SalesOrderForm } from "../../app/components/crm/SalesOrderForm";
import { SalesOrdersKanban } from "../../app/components/crm/SalesOrdersKanban";

const mockOrders: SalesOrder[] = [
  { id: 1, orderNumber: "SO-1001", customerId: 1, customerName: "شرکت الف", opportunityId: 1, status: "در انتظار", orderDate: new Date(), deliveryDate: undefined, totalAmount: 1200000, currency: "تومان", paymentStatus: "پرداخت نشده", items: [], createdBy: 1, notes: "" },
  { id: 2, orderNumber: "SO-1002", customerId: 2, customerName: "شرکت ب", opportunityId: 2, status: "ارسال شده", orderDate: new Date(), deliveryDate: undefined, totalAmount: 850000, currency: "تومان", paymentStatus: "نیمه پرداخت", items: [], createdBy: 2, notes: "" },
  { id: 3, orderNumber: "SO-1003", customerId: 3, customerName: "شرکت ج", opportunityId: 3, status: "پرداخت شده", orderDate: new Date(), deliveryDate: undefined, totalAmount: 500000, currency: "تومان", paymentStatus: "پرداخت شده", items: [], createdBy: 1, notes: "" },
];

export const SalesOrders: React.FC = () => {
  const [orders, setOrders] = useState<SalesOrder[]>(mockOrders);
  const [formOpen, setFormOpen] = useState(false);
  const [editOrder, setEditOrder] = useState<SalesOrder | null>(null);
  const [kanbanView, setKanbanView] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const handleAdd = () => {
    setEditOrder(null);
    setFormOpen(true);
  };
  const handleEdit = (order: SalesOrder) => {
    setEditOrder(order);
    setFormOpen(true);
  };
  const handleDelete = (id: number) => {
    setOrders(ords => ords.filter(o => o.id !== id));
    setSnackbar({ open: true, message: "سفارش حذف شد.", severity: "success" });
  };
  const handleSave = (data: SalesOrder) => {
    if (editOrder) {
      setOrders(ords => ords.map(o => o.id === editOrder.id ? { ...data, id: editOrder.id } : o));
      setSnackbar({ open: true, message: "سفارش ویرایش شد.", severity: "success" });
    } else {
      setOrders(ords => [...ords, { ...data, id: Math.max(...ords.map(o => o.id || 0)) + 1 }]);
      setSnackbar({ open: true, message: "سفارش جدید اضافه شد.", severity: "success" });
    }
    setFormOpen(false);
  };
  const handleView = (order: SalesOrder) => {
    setEditOrder(order);
    setFormOpen(true);
  };
  const handleStatusChange = (id: number, newStatus: SalesOrderStatus) => {
    setOrders(ords => ords.map(o => o.id === id ? { ...o, status: newStatus } : o));
    setSnackbar({ open: true, message: "وضعیت سفارش تغییر کرد.", severity: "success" });
  };

  return (
    <div>
      <div>
        <Typography.Title level={3}>سفارش‌های فروش</Typography.Title>
        <div>
          <Button variant={kanbanView ? "outlined" : "contained"} onClick={() => setKanbanView(false)}>جدول</Button>
          <Button variant={kanbanView ? "contained" : "outlined"} onClick={() => setKanbanView(true)}>Kanban</Button>
          <Button variant="contained" color="primary" onClick={handleAdd}>افزودن سفارش</Button>
        </div>
      </div>
      {kanbanView ? (
        <SalesOrdersKanban
          orders={orders}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={handleView}
          onStatusChange={handleStatusChange}
        />
      ) : (
        <SalesOrdersTable
          orders={orders}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={handleView}
        />
      )}
      <SalesOrderForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        order={editOrder}
        onSave={handleSave}
      />
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar(s => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </div>
    </div>
  );
}; 