import React from 'react';
import { Button, Space } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { FileTextOutlined } from '@ant-design/icons';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Supplier } from '../../../types/procurement';

interface SuppliersExportButtonsProps {
  suppliers: Supplier[];
}

export const SuppliersExportButtons: React.FC<SuppliersExportButtonsProps> = ({ suppliers }) => {
  const handleExcel = () => {
    const ws = XLSX.utils.json_to_sheet(suppliers);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Suppliers');
    XLSX.writeFile(wb, 'suppliers.xlsx');
  };
  const handlePDF = () => {
    const doc = new jsPDF();
    autoTable(doc, {
      head: [['کد', 'نام', 'شخص تماس', 'تلفن', 'وضعیت', 'امتیاز']],
      body: suppliers.map(s => [s.code, s.name, s.contactPerson, s.phone, s.status, s.rating]),
    });
    doc.save('suppliers.pdf');
  };
  return (
    <Stack direction="row" spacing={1}>
      <Button variant="outlined" startIcon={<FileDownloadIcon />} onClick={handleExcel}>خروجی اکسل</Button>
      <Button variant="outlined" startIcon={<PictureAsPdfIcon />} onClick={handlePDF}>خروجی PDF</Button>
    </Stack>
  );
}; 