import React from "react";
import { Button, Space } from 'antd';
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { Report } from "../../api/reports/types";

export const ReportExportButtons: React.FC<{ data: Report[] }> = ({ data }) => {
  const exportExcel = () => {
    const ws = XLSX.utils.json_to_sheet(data.flatMap(r => r.rows.map(row => Object.fromEntries(r.columns.map((col, i) => [col, row[i]])))));
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Reports");
    XLSX.writeFile(wb, "reports.xlsx");
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    data.forEach((r, idx) => {
      doc.text(r.title, 10, 10 + idx * 80);
      (doc as any).autoTable({
        head: [r.columns],
        body: r.rows,
        startY: 15 + idx * 80,
      });
    });
    doc.save("reports.pdf");
  };

  return (
    <Stack direction="row" spacing={2} mb={2}>
      <Button variant="outlined" onClick={exportExcel}>خروجی Excel</Button>
      <Button variant="outlined" onClick={exportPDF}>خروجی PDF</Button>
    </Stack>
  );
};