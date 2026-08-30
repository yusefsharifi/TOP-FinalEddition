import React from 'react';
import { Button, Space } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { FileTextOutlined } from '@ant-design/icons';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { PurchaseRequest } from '../../../types/procurement';

interface PurchaseRequestsExportButtonsProps {
  requests: PurchaseRequest[];
}

export const PurchaseRequestsExportButtons: React.FC<PurchaseRequestsExportButtonsProps> = ({ requests }) => {
  const handleExcel = () => {
    const ws = XLSX.utils.json_to_sheet(requests);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Requests');
    XLSX.writeFile(wb, 'purchase_requests.xlsx');
  };
  const handlePDF = () => {
    const doc = new jsPDF();
    autoTable(doc, {
      head: [['شماره درخواست', 'دپارتمان', 'تاریخ درخواست', 'تاریخ مورد نیاز', 'اولویت', 'وضعیت']],
      body: requests.map(r => [r.requestNumber, r.department, new Date(r.requestDate).toLocaleDateString(), new Date(r.requiredDate).toLocaleDateString(), r.priority, r.status]),
    });
    doc.save('purchase_requests.pdf');
  };
  return (
    <Stack direction="row" spacing={1}>
      <Button variant="outlined" startIcon={<FileDownloadIcon />} onClick={handleExcel}>خروجی اکسل</Button>
      <Button variant="outlined" startIcon={<PictureAsPdfIcon />} onClick={handlePDF}>خروجی PDF</Button>
    </Stack>
  );
}; 