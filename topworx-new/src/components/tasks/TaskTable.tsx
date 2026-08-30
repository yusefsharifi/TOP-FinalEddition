import React from "react";
import { Button, Table, Tag, Tooltip } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { Task } from "../../api/tasks/types";

const statusLabels: Record<string, string> = {
  todo: "در انتظار",
  in_progress: "در حال انجام",
  done: "انجام شده",
  cancelled: "لغو شده",
};

const priorityColors: Record<string, "default" | "primary" | "warning" | "error"> = {
  low: "default",
  medium: "primary",
  high: "error",
};

export const TaskTable: React.FC<{
  data: Task[];
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
}> = ({ data, onEdit, onDelete }) => (
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>عنوان</TableCell>
        <TableCell>وضعیت</TableCell>
        <TableCell>اولویت</TableCell>
        <TableCell>مسئول</TableCell>
        <TableCell>تاریخ سررسید</TableCell>
        <TableCell>عملیات</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((task) => (
        <TableRow key={task.id}>
          <TableCell>{task.title}</TableCell>
          <TableCell>
            <Tag label={statusLabels[task.status]} color={
              task.status === "done" ? "success" :
              task.status === "in_progress" ? "primary" :
              task.status === "cancelled" ? "error" : "default"
            } />
          </TableCell>
          <TableCell>
            <Tag label={task.priority === "high" ? "زیاد" : task.priority === "medium" ? "متوسط" : "کم"}
                  color={priorityColors[task.priority]} />
          </TableCell>
          <TableCell>{task.assignee.name}</TableCell>
          <TableCell>{new Date(task.dueDate).toLocaleDateString("fa-IR")}</TableCell>
          <TableCell>
            <Tooltip title="ویرایش">
              <Button type="text" onClick={() => onEdit(task)}><EditIcon /></Button>
            </Tooltip>
            <Tooltip title="حذف">
              <Button type="text" onClick={() => onDelete(task.id)}><DeleteIcon /></Button>
            </Tooltip>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);