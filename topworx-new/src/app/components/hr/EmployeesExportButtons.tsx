import React from 'react';
import { Button, Space } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { FileTextOutlined } from '@ant-design/icons';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Employee } from '../../../types/hr';

interface EmployeesExportButtonsProps {
  employees: Employee[];
}

export const EmployeesExportButtons: React.FC<EmployeesExportButtonsProps> = ({ employees }) => {
  const handleExcel = () => {
    const ws = XLSX.utils.json_to_sheet(employees);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Employees');
    XLSX.writeFile(wb, 'employees.xlsx');
  };
  
  const handlePDF = () => {
    const doc = new jsPDF();
    autoTable(doc, {
      head: [['کد پرسنلی', 'نام', 'دپارتمان', 'سمت', 'وضعیت', 'حقوق']],
      body: employees.map(e => [
        e.employeeCode,
        `${e.firstName} ${e.lastName}`,
        e.department,
        e.position,
        e.status,
        e.salary.toLocaleString()
      ]),
    });
    doc.save('employees.pdf');
  };
  
  return (
    <Stack direction="row" spacing={1}>
      <Button variant="outlined" startIcon={<FileDownloadIcon />} onClick={handleExcel}>
        خروجی اکسل
      </Button>
      <Button variant="outlined" startIcon={<PictureAsPdfIcon />} onClick={handlePDF}>
        خروجی PDF
      </Button>
    </Stack>
  );
}; 