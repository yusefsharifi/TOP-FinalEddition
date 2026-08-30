import React from "react";
import { Avatar, Button, Table, Tag, Tooltip } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { Employee } from "../../api/hr/types";

const statusLabels: Record<string, string> = {
  active: "فعال",
  inactive: "غیرفعال",
  on_leave: "مرخصی",
  retired: "بازنشسته",
};

export const EmployeeTable: React.FC<{
  data: Employee[];
  onEdit: (emp: Employee) => void;
  onDelete: (id: string) => void;
  onProfile: (id: string) => void;
}> = ({ data, onEdit, onDelete, onProfile }) => (
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>عکس</TableCell>
        <TableCell>کد پرسنلی</TableCell>
        <TableCell>نام</TableCell>
        <TableCell>سمت</TableCell>
        <TableCell>دپارتمان</TableCell>
        <TableCell>وضعیت</TableCell>
        <TableCell>عملیات</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((emp) => (
        <TableRow key={emp.id}>
          <TableCell>
            <Avatar src={emp.avatarUrl}>{emp.firstName[0]}</Avatar>
          </TableCell>
          <TableCell>{emp.code}</TableCell>
          <TableCell>{emp.firstName} {emp.lastName}</TableCell>
          <TableCell>{emp.position}</TableCell>
          <TableCell>{emp.department}</TableCell>
          <TableCell>
            <Tag label={statusLabels[emp.status]} color={
              emp.status === "active" ? "success" :
              emp.status === "on_leave" ? "warning" :
              emp.status === "retired" ? "default" : "error"
            } />
          </TableCell>
          <TableCell>
            <Tooltip title="پروفایل">
              <Button type="text" onClick={() => onProfile(emp.id)}><VisibilityIcon /></Button>
            </Tooltip>
            <Tooltip title="ویرایش">
              <Button type="text" onClick={() => onEdit(emp)}><EditIcon /></Button>
            </Tooltip>
            <Tooltip title="حذف">
              <Button type="text" onClick={() => onDelete(emp.id)}><DeleteIcon /></Button>
            </Tooltip>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);