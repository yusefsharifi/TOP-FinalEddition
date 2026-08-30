import React from "react";
import { Button, Table, Tag, Tooltip } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { Budget } from "../../api/budget/types";

const statusLabels: Record<string, string> = {
  active: "فعال",
  closed: "بسته‌شده",
  over: "عبور از سقف",
};

{budget.allocatedTo?.type === "project" && (
  <Button onClick={() => navigate(`/projects/${budget.allocatedTo.id}`)} size="small" color="primary">
    مشاهده پروژه
  </Button>
)}

<Button onClick={() => archiveBudget(budget.id)}>آرشیو</Button>

export const BudgetTable: React.FC<{
  data: Budget[];
  onDetails: (id: string) => void;
}> = ({ data, onDetails }) => (
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>عنوان</TableCell>
        <TableCell>نوع</TableCell>
        <TableCell>سال</TableCell>
        <TableCell>ماه</TableCell>
        <TableCell>مبلغ بودجه</TableCell>
        <TableCell>هزینه</TableCell>
        <TableCell>درآمد</TableCell>
        <TableCell>وضعیت</TableCell>
        <TableCell>عملیات</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((b) => (
        <TableRow key={b.id}>
          <TableCell>{b.title}</TableCell>
          <TableCell>{b.type === "annual" ? "سالانه" : b.type === "monthly" ? "ماهانه" : "پروژه‌ای"}</TableCell>
          <TableCell>{b.year}</TableCell>
          <TableCell>{b.month || "-"}</TableCell>
          <TableCell>{b.amount.toLocaleString()}</TableCell>
          <TableCell>{b.spent.toLocaleString()}</TableCell>
          <TableCell>{b.income.toLocaleString()}</TableCell>
          <TableCell>
            <Tag label={statusLabels[b.status]} color={
              b.status === "active" ? "success" :
              b.status === "over" ? "error" : "default"
            } />
          </TableCell>
          <TableCell>
            <Tooltip title="مشاهده جزئیات">
              <Button type="text" onClick={() => onDetails(b.id)}><VisibilityIcon /></Button>
            </Tooltip>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);