import React from 'react';
import { Button, Space } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { FileTextOutlined } from '@ant-design/icons';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { QualityInspection } from '../../../types/quality';

interface QualityInspectionsExportButtonsProps {
  inspections: QualityInspection[];
}

export const QualityInspectionsExportButtons: React.FC<QualityInspectionsExportButtonsProps> = ({ inspections }) => {
  const handleExcel = () => {
    const ws = XLSX.utils.json_to_sheet(inspections.map(inspection => ({
      'شماره بازرسی': inspection.inspectionNumber,
      'نوع بازرسی': inspection.type,
      'محصول': inspection.productName || '-',
      'شماره دسته': inspection.batchNumber || inspection.lotNumber || '-',
      'تعداد کل': inspection.quantity,
      'تعداد بازرسی شده': inspection.inspectedQuantity,
      'تعداد قبول': inspection.passedQuantity,
      'تعداد رد': inspection.failedQuantity,
      'نرخ قبولی': `${Math.round((inspection.passedQuantity / inspection.inspectedQuantity) * 100)}%`,
      'وضعیت': inspection.status,
      'بازرس': inspection.inspectorName,
      'تاریخ بازرسی': new Date(inspection.inspectionDate).toLocaleDateString(),
      'تعداد نقص‌ها': inspection.defects.length
    })));
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Quality Inspections');
    XLSX.writeFile(wb, 'quality_inspections.xlsx');
  };
  
  const handlePDF = () => {
    const doc = new jsPDF();
    autoTable(doc, {
      head: [['شماره بازرسی', 'نوع', 'محصول', 'وضعیت', 'نرخ قبولی', 'بازرس']],
      body: inspections.map(inspection => [
        inspection.inspectionNumber,
        inspection.type,
        inspection.productName || '-',
        inspection.status,
        `${Math.round((inspection.passedQuantity / inspection.inspectedQuantity) * 100)}%`,
        inspection.inspectorName
      ]),
    });
    doc.save('quality_inspections.pdf');
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