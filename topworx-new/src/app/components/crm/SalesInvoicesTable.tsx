import React, { useMemo, useState } from "react";
import { Alert, Button, Card, Input, InputNumber, Table, Tag, Tooltip } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { SalesInvoice } from "../../../types/crm";

export interface SalesInvoicesTableProps {
  invoices: SalesInvoice[];
  onEdit: (invoice: SalesInvoice) => void;
  onDelete: (id: number) => void;
  onView: (invoice: SalesInvoice) => void;
}

export const SalesInvoicesTable: React.FC<SalesInvoicesTableProps> = ({ invoices, onEdit, onDelete, onView }) => {
  const [search, setSearch] = useState("");
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const filtered = useMemo(() =>
    invoices.filter(i =>
      i.invoiceNumber.toLowerCase().includes(search.toLowerCase()) ||
      i.customerName.toLowerCase().includes(search.toLowerCase())
    ), [invoices, search]);

  const exportExcel = () => {
    const ws = XLSX.utils.json_to_sheet(filtered);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "SalesInvoices");
    XLSX.writeFile(wb, "sales_invoices.xlsx");
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    (doc as any).autoTable({
      head: [Object.keys(filtered[0] || {})],
      body: filtered.map(row => Object.values(row)),
    });
    doc.save("sales_invoices.pdf");
  };

  return (
    <Card style={{  mt: 2  }}>
      <div style={{  justifyContent: "space-between", flexDirection: "row-reverse"  }}>
        <Button variant="outlined" onClick={exportExcel}>خروجی Excel</Button>
        <Button variant="outlined" onClick={exportPDF}>خروجی PDF</Button>
        <Input
          label="جستجو"
          value={search}
          onChange={e => setSearch(e.target.value)}
          size="small"
          style={{  width: 200  }}
        />
      </div>
      <div>
        <Table size="small">
          <thead>
            <tr>
              <td align="right">شماره فاکتور</td>
              <td align="right">مشتری</td>
              <td align="right">تاریخ فاکتور</td>
              <td align="right">تاریخ سررسید</td>
              <td align="right">جمع کل</td>
              <td align="right">وضعیت پرداخت</td>
              <td align="right">عملیات</td>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={7} align="center">هیچ فاکتوری یافت نشد.</td></tr>
            ) : (
              filtered.map((invoice) => (
                <tr key={invoice.id} hover>
                  <td align="right">{invoice.invoiceNumber}</td>
                  <td align="right">{invoice.customerName}</td>
                  <td align="right">{invoice.invoiceDate ? new Date(invoice.invoiceDate).toLocaleDateString() : ""}</td>
                  <td align="right">{invoice.dueDate ? new Date(invoice.dueDate).toLocaleDateString() : ""}</td>
                  <td align="right">{invoice.totalAmount.toLocaleString()} {invoice.currency}</td>
                  <td align="right">
                    <Tag label={invoice.status} color={invoice.status === "پرداخت شده" ? "success" : invoice.status === "نیمه پرداخت" ? "warning" : "default"} size="small" />
                  </td>
                  <td align="right">
                    <Tooltip title="مشاهده جزئیات">
                      <Button type="text" onClick={() => onView(invoice)}><EyeOutlined /></Button>
                    </Tooltip>
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(invoice)}><EditOutlined /></Button>
                    </Tooltip>
                    <Tooltip title="حذف">
                      <Button type="text" onClick={() => onDelete(invoice.id!)}><DeleteOutlined color="error" /></Button>
                    </Tooltip>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </Table>
      </div>
      <div
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar(s => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </div>
    </Card>
  );
}; 