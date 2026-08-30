import React, { useMemo, useState } from "react";
import { Alert, Button, Card, Input, InputNumber, Table, Tag, Tooltip } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { Opportunity } from "../../../types/crm";

export interface OpportunitiesTableProps {
  opportunities: Opportunity[];
  onEdit: (op: Opportunity) => void;
  onDelete: (id: number) => void;
  onView: (op: Opportunity) => void;
  renderActions?: (op: Opportunity) => React.ReactNode;
}

export const OpportunitiesTable: React.FC<OpportunitiesTableProps> = ({ opportunities, onEdit, onDelete, onView }) => {
  const [search, setSearch] = useState("");
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const filtered = useMemo(() =>
    opportunities.filter(o =>
      o.title.toLowerCase().includes(search.toLowerCase()) ||
      o.customerName.toLowerCase().includes(search.toLowerCase()) ||
      o.ownerName.toLowerCase().includes(search.toLowerCase())
    ), [opportunities, search]);

  const exportExcel = () => {
    const ws = XLSX.utils.json_to_sheet(filtered);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Opportunities");
    XLSX.writeFile(wb, "opportunities.xlsx");
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    (doc as any).autoTable({
      head: [Object.keys(filtered[0] || {})],
      body: filtered.map(row => Object.values(row)),
    });
    doc.save("opportunities.pdf");
  };

  return (
    <Card style={{  mt: 2  }}>
      <Toolbar style={{  justifyContent: "space-between", flexDirection: "row-reverse"  }}>
        <Button variant="outlined" onClick={exportExcel}>خروجی Excel</Button>
        <Button variant="outlined" onClick={exportPDF}>خروجی PDF</Button>
        <Input
          label="جستجو"
          value={search}
          onChange={e => setSearch(e.target.value)}
          size="small"
          style={{  width: 200  }}
        />
      </Toolbar>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell align="right">عنوان</TableCell>
              <TableCell align="right">مشتری</TableCell>
              <TableCell align="right">کارشناس</TableCell>
              <TableCell align="right">مرحله</TableCell>
              <TableCell align="right">مبلغ</TableCell>
              <TableCell align="right">درصد احتمال</TableCell>
              <TableCell align="right">وضعیت</TableCell>
              <TableCell align="right">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.length === 0 ? (
              <TableRow><TableCell colSpan={8} align="center">هیچ فرصتی یافت نشد.</TableCell></TableRow>
            ) : (
              filtered.map((op) => (
                <TableRow key={op.id} hover>
                  <TableCell align="right">{op.title}</TableCell>
                  <TableCell align="right">{op.customerName}</TableCell>
                  <TableCell align="right">{op.ownerName}</TableCell>
                  <TableCell align="right">{op.stage}</TableCell>
                  <TableCell align="right">{op.amount.toLocaleString()} {op.currency}</TableCell>
                  <TableCell align="right">{op.probability}%</TableCell>
                  <TableCell align="right">
                    <Tag label={op.status} color={op.status === "برنده" ? "success" : op.status === "باخته" ? "error" : "default"} size="small" />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="مشاهده جزئیات">
                      <Button type="text" onClick={() => onView(op)}><VisibilityIcon /></Button>
                    </Tooltip>
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(op)}><EditIcon /></Button>
                    </Tooltip>
                    <Tooltip title="حذف">
                      <Button type="text" onClick={() => onDelete(op.id!)}><DeleteIcon color="error" /></Button>
                    </Tooltip>
                    {renderActions && renderActions(op)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
      <Snackbar
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