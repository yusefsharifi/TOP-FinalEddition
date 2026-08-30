import React from "react";
import { Button, Table, Typography } from 'antd';

export const EmployeeAttendance: React.FC<{
  attendance: { date: string; type: "present" | "absent" | "leave"; description?: string }[];
  onAdd: (data: any) => void;
}> = ({ attendance, onAdd }) => (
  <div>
    <Typography.Title level={4}>حضور و غیاب / مرخصی‌ها</Typography.Title>
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>تاریخ</TableCell>
          <TableCell>نوع</TableCell>
          <TableCell>توضیحات</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {attendance.map(a => (
          <TableRow key={a.date}>
            <TableCell>{a.date}</TableCell>
            <TableCell>
              {a.type === "present" ? "حاضر" : a.type === "absent" ? "غایب" : "مرخصی"}
            </TableCell>
            <TableCell>{a.description}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
    <Button variant="outlined" size="small" style={{  mt: 1  }}>ثبت مرخصی/حضور جدید</Button>
  </div>
);