import React from 'react';
import { Button, Space } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { FileTextOutlined } from '@ant-design/icons';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { PurchaseOrder } from '../../../types/procurement';

interface PurchaseOrderExportButtonsProps {
  orders: PurchaseOrder[];
}

export const PurchaseOrderExportButtons: React.FC<PurchaseOrderExportButtonsProps> = ({ orders }) => {
  const handleExcel = () => {
    const ws = XLSX.utils.json_to_sheet(orders);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Orders');
    XLSX.writeFile(wb, 'purchase_orders.xlsx');
  };
  const handlePDF = () => {
    const doc = new jsPDF();
    autoTable(doc, {
      head: [['شماره سفارش', 'تأمین‌کننده', 'تاریخ سفارش', 'تاریخ تحویل', 'مبلغ نهایی', 'وضعیت']],
      body: orders.map(o => [o.orderNumber, o.supplierName, new Date(o.orderDate).toLocaleDateString(), new Date(o.expectedDeliveryDate).toLocaleDateString(), o.finalAmount, o.status]),
    });
    doc.save('purchase_orders.pdf');
  };
  return (
    <Stack direction="row" spacing={1}>
      <Button variant="outlined" startIcon={<FileDownloadIcon />} onClick={handleExcel}>خروجی اکسل</Button>
      <Button variant="outlined" startIcon={<PictureAsPdfIcon />} onClick={handlePDF}>خروجی PDF</Button>
    </Stack>
  );
}; 