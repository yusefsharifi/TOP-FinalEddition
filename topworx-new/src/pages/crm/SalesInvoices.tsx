import React, { useState } from "react";
import { Alert, Button, Typography } from 'antd';
import { SalesInvoice } from "../../../types/crm";
import { SalesInvoicesTable } from "../../app/components/crm/SalesInvoicesTable";
import { SalesInvoiceForm } from "../../app/components/crm/SalesInvoiceForm";

const mockInvoices: SalesInvoice[] = [
  { id: 1, invoiceNumber: "INV-1001", orderId: 1, customerId: 1, customerName: "شرکت الف", invoiceDate: new Date(), dueDate: new Date(), amount: 1200000, taxAmount: 120000, totalAmount: 1320000, currency: "تومان", status: "پرداخت نشده", notes: "" },
  { id: 2, invoiceNumber: "INV-1002", orderId: 2, customerId: 2, customerName: "شرکت ب", invoiceDate: new Date(), dueDate: new Date(), amount: 850000, taxAmount: 85000, totalAmount: 935000, currency: "تومان", status: "نیمه پرداخت", notes: "" },
  { id: 3, invoiceNumber: "INV-1003", orderId: 3, customerId: 3, customerName: "شرکت ج", invoiceDate: new Date(), dueDate: new Date(), amount: 500000, taxAmount: 50000, totalAmount: 550000, currency: "تومان", status: "پرداخت شده", notes: "" },
];

export const SalesInvoices: React.FC = () => {
  const [invoices, setInvoices] = useState<SalesInvoice[]>(mockInvoices);
  const [formOpen, setFormOpen] = useState(false);
  const [editInvoice, setEditInvoice] = useState<SalesInvoice | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const handleAdd = () => {
    setEditInvoice(null);
    setFormOpen(true);
  };
  const handleEdit = (invoice: SalesInvoice) => {
    setEditInvoice(invoice);
    setFormOpen(true);
  };
  const handleDelete = (id: number) => {
    setInvoices(inv => inv.filter(i => i.id !== id));
    setSnackbar({ open: true, message: "فاکتور حذف شد.", severity: "success" });
  };
  const handleSave = (data: SalesInvoice) => {
    if (editInvoice) {
      setInvoices(inv => inv.map(i => i.id === editInvoice.id ? { ...data, id: editInvoice.id } : i));
      setSnackbar({ open: true, message: "فاکتور ویرایش شد.", severity: "success" });
    } else {
      setInvoices(inv => [...inv, { ...data, id: Math.max(...inv.map(i => i.id || 0)) + 1 }]);
      setSnackbar({ open: true, message: "فاکتور جدید اضافه شد.", severity: "success" });
    }
    setFormOpen(false);
  };
  const handleView = (invoice: SalesInvoice) => {
    setEditInvoice(invoice);
    setFormOpen(true);
  };

  return (
    <div>
      <div>
        <Typography.Title level={3}>فاکتورهای فروش</Typography.Title>
        <Button variant="contained" color="primary" onClick={handleAdd}>افزودن فاکتور</Button>
      </div>
      <SalesInvoicesTable
        invoices={invoices}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={handleView}
      />
      <SalesInvoiceForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        invoice={editInvoice}
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