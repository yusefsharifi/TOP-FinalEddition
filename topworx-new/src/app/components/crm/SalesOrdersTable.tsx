import React, { useMemo, useState } from "react";
import { Alert, Button, Card, Input, InputNumber, Table, Tag, Tooltip } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { SalesOrder } from "../../../types/crm";

export interface SalesOrdersTableProps {
  orders: SalesOrder[];
  onEdit: (order: SalesOrder) => void;
  onDelete: (id: number) => void;
  onView: (order: SalesOrder) => void;
}

export const SalesOrdersTable: React.FC<SalesOrdersTableProps> = ({ orders, onEdit, onDelete, onView }) => {
  const [search, setSearch] = useState("");
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const filtered = useMemo(() =>
    orders.filter(o =>
      o.orderNumber.toLowerCase().includes(search.toLowerCase()) ||
      o.customerName.toLowerCase().includes(search.toLowerCase())
    ), [orders, search]);

  const exportExcel = () => {
    const ws = XLSX.utils.json_to_sheet(filtered);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "SalesOrders");
    XLSX.writeFile(wb, "sales_orders.xlsx");
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    (doc as any).autoTable({
      head: [Object.keys(filtered[0] || {})],
      body: filtered.map(row => Object.values(row)),
    });
    doc.save("sales_orders.pdf");
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
              <td align="right">شماره سفارش</td>
              <td align="right">مشتری</td>
              <td align="right">تاریخ سفارش</td>
              <td align="right">مبلغ کل</td>
              <td align="right">وضعیت سفارش</td>
              <td align="right">وضعیت پرداخت</td>
              <td align="right">عملیات</td>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={7} align="center">هیچ سفارشی یافت نشد.</td></tr>
            ) : (
              filtered.map((order) => (
                <tr key={order.id} hover>
                  <td align="right">{order.orderNumber}</td>
                  <td align="right">{order.customerName}</td>
                  <td align="right">{order.orderDate ? new Date(order.orderDate).toLocaleDateString() : ""}</td>
                  <td align="right">{order.totalAmount.toLocaleString()} {order.currency}</td>
                  <td align="right">
                    <Tag label={order.status} color={order.status === "پرداخت شده" ? "success" : order.status === "لغو شده" ? "error" : "default"} size="small" />
                  </td>
                  <td align="right">
                    <Tag label={order.paymentStatus} color={order.paymentStatus === "پرداخت شده" ? "success" : order.paymentStatus === "نیمه پرداخت" ? "warning" : "default"} size="small" />
                  </td>
                  <td align="right">
                    <Tooltip title="مشاهده جزئیات">
                      <Button type="text" onClick={() => onView(order)}><EyeOutlined /></Button>
                    </Tooltip>
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(order)}><EditOutlined /></Button>
                    </Tooltip>
                    <Tooltip title="حذف">
                      <Button type="text" onClick={() => onDelete(order.id!)}><DeleteOutlined color="error" /></Button>
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