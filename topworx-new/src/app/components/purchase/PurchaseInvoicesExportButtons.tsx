import React from 'react';
import { Button, Space } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { FileTextOutlined } from '@ant-design/icons';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { PurchaseInvoice } from '../../../types/procurement';

interface PurchaseInvoicesExportButtonsProps {
  invoices: PurchaseInvoice[];
}

export const PurchaseInvoicesExportButtons: React.FC<PurchaseInvoicesExportButtonsProps> = ({ invoices }) => {
  const handleExcel = () => {
    const ws = XLSX.utils.json_to_sheet(invoices);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Invoices');
    XLSX.writeFile(wb, 'purchase_invoices.xlsx');
  };
  const handlePDF = () => {
    const doc = new jsPDF();
    autoTable(doc, {
      head: [['شماره فاکتور', 'تأمین‌کننده', 'تاریخ سررسید', 'مبلغ کل', 'وضعیت']],
      body: invoices.map(i => [i.invoiceNumber, i.supplierName, new Date(i.dueDate).toLocaleDateString(), i.totalAmount, i.status]),
    });
    doc.save('purchase_invoices.pdf');
  };
  return (
    <Stack direction="row" spacing={1}>
      <Button variant="outlined" startIcon={<FileDownloadIcon />} onClick={handleExcel}>خروجی اکسل</Button>
      <Button variant="outlined" startIcon={<PictureAsPdfIcon />} onClick={handlePDF}>خروجی PDF</Button>
    </Stack>
  );
}; 