import React from "react";
import { Button, Table, Tag, Tooltip } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { Asset } from "../../api/assets/types";
import { Button } from 'antd';
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";

const exportExcel = (assets) => {
  const ws = XLSX.utils.json_to_sheet(assets);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Assets");
  XLSX.writeFile(wb, "assets.xlsx");
};

const exportPDF = (assets) => {
  const doc = new jsPDF();
  (doc as any).autoTable({
    head: [Object.keys(assets[0] || {})],
    body: assets.map(row => Object.values(row)),
  });
  doc.save("assets.pdf");
};

<Button onClick={() => exportExcel(data)}>خروجی Excel</Button>
<Button onClick={() => exportPDF(data)}>خروجی PDF</Button>

const statusLabels: Record<string, string> = {
  active: "فعال",
  inactive: "غیرفعال",
  maintenance: "در تعمیر",
  disposed: "خارج شده",
};

export const AssetTable: React.FC<{
  data: Asset[];
  onDetails: (id: string) => void;
}> = ({ data, onDetails }) => (
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>کد</TableCell>
        <TableCell>نام دارایی</TableCell>
        <TableCell>دسته‌بندی</TableCell>
        <TableCell>محل نگهداری</TableCell>
        <TableCell>مسئول</TableCell>
        <TableCell>ارزش</TableCell>
        <TableCell>وضعیت</TableCell>
        <TableCell>عملیات</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((a) => (
        <TableRow key={a.id}>
          <TableCell>{a.code}</TableCell>
          <TableCell>{a.name}</TableCell>
          <TableCell>{a.category}</TableCell>
          <TableCell>{a.location}</TableCell>
          <TableCell>{a.manager.name}</TableCell>
          <TableCell>{a.value.toLocaleString()}</TableCell>
          <TableCell>
            <Tag label={statusLabels[a.status]} color={
              a.status === "active" ? "success" :
              a.status === "maintenance" ? "warning" :
              a.status === "disposed" ? "error" : "default"
            } />
          </TableCell>
          <TableCell>
            <Tooltip title="مشاهده جزئیات">
              <Button type="text" onClick={() => onDetails(a.id)}><VisibilityIcon /></Button>
            </Tooltip>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);