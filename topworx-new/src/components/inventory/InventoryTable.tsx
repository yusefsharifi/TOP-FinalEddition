import React from "react";
import { Button, Table, Tag, Tooltip } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { InventoryItem } from "../../api/inventory/types";

const statusLabels: Record<string, string> = {
  ok: "عادی",
  low: "کمبود",
  over: "مازاد",
};

export const InventoryTable: React.FC<{
  data: InventoryItem[];
  onDetails: (id: string) => void;
}> = ({ data, onDetails }) => (
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>کد کالا</TableCell>
        <TableCell>نام کالا</TableCell>
        <TableCell>دسته‌بندی</TableCell>
        <TableCell>انبار</TableCell>
        <TableCell>موجودی</TableCell>
        <TableCell>واحد</TableCell>
        <TableCell>وضعیت</TableCell>
        <TableCell>عملیات</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((item) => (
        <TableRow key={item.id}>
          <TableCell>{item.product.code}</TableCell>
          <TableCell>{item.product.name}</TableCell>
          <TableCell>{item.product.category}</TableCell>
          <TableCell>{item.warehouse.name}</TableCell>
          <TableCell>{item.quantity}</TableCell>
          <TableCell>{item.product.unit}</TableCell>
          <TableCell>
            <Tag label={statusLabels[item.status]} color={
              item.status === "ok" ? "success" :
              item.status === "low" ? "error" : "warning"
            } />
          </TableCell>
          <TableCell>
            <Tooltip title="مشاهده جزئیات">
              <Button type="text" onClick={() => onDetails(item.id)}><VisibilityIcon /></Button>
            </Tooltip>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);