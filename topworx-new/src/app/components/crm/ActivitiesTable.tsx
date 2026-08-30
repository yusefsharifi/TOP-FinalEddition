import React, { useMemo, useState } from "react";
import { Alert, Button, Card, Input, InputNumber, Table, Tag, Tooltip } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { Activity } from "../../../types/crm";

export interface ActivitiesTableProps {
  activities: Activity[];
  onEdit: (activity: Activity) => void;
  onDelete: (id: number) => void;
  onView: (activity: Activity) => void;
}

export const ActivitiesTable: React.FC<ActivitiesTableProps> = ({ activities, onEdit, onDelete, onView }) => {
  const [search, setSearch] = useState("");
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const filtered = useMemo(() =>
    activities.filter(a =>
      a.subject.toLowerCase().includes(search.toLowerCase()) ||
      a.ownerName.toLowerCase().includes(search.toLowerCase())
    ), [activities, search]);

  const exportExcel = () => {
    const ws = XLSX.utils.json_to_sheet(filtered);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Activities");
    XLSX.writeFile(wb, "activities.xlsx");
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    (doc as any).autoTable({
      head: [Object.keys(filtered[0] || {})],
      body: filtered.map(row => Object.values(row)),
    });
    doc.save("activities.pdf");
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
              <TableCell align="right">موضوع</TableCell>
              <TableCell align="right">نوع</TableCell>
              <TableCell align="right">تاریخ</TableCell>
              <TableCell align="right">مسئول</TableCell>
              <TableCell align="right">وضعیت</TableCell>
              <TableCell align="right">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.length === 0 ? (
              <TableRow><TableCell colSpan={6} align="center">هیچ فعالیتی یافت نشد.</TableCell></TableRow>
            ) : (
              filtered.map((activity) => (
                <TableRow key={activity.id} hover>
                  <TableCell align="right">{activity.subject}</TableCell>
                  <TableCell align="right">{activity.type}</TableCell>
                  <TableCell align="right">{activity.date ? new Date(activity.date).toLocaleDateString() : ""}</TableCell>
                  <TableCell align="right">{activity.ownerName}</TableCell>
                  <TableCell align="right">
                    <Tag label={activity.status} color={activity.status === "انجام شده" ? "success" : activity.status === "لغو شده" ? "error" : "default"} size="small" />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="مشاهده جزئیات">
                      <Button type="text" onClick={() => onView(activity)}><VisibilityIcon /></Button>
                    </Tooltip>
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(activity)}><EditIcon /></Button>
                    </Tooltip>
                    <Tooltip title="حذف">
                      <Button type="text" onClick={() => onDelete(activity.id!)}><DeleteIcon color="error" /></Button>
                    </Tooltip>
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