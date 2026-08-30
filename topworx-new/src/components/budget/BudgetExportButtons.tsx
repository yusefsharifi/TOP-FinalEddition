import { Button, Space } from 'antd';
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";

export const BudgetExportButtons: React.FC<{ data: any[] }> = ({ data }) => {
  const exportExcel = () => {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Budgets");
    XLSX.writeFile(wb, "budgets.xlsx");
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    (doc as any).autoTable({
      head: [Object.keys(data[0] || {})],
      body: data.map(row => Object.values(row)),
    });
    doc.save("budgets.pdf");
  };

  return (
    <Stack direction="row" spacing={2} mb={2}>
      <Button variant="outlined" onClick={exportExcel}>خروجی Excel</Button>
      <Button variant="outlined" onClick={exportPDF}>خروجی PDF</Button>
    </Stack>
  );
};