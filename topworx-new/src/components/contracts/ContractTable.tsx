import React from "react";
import { Button, Table, Tag, Tooltip } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { DownloadOutlined } from '@ant-design/icons';
import { Contract } from "../../api/contracts/types";

<Button onClick={() => archiveContract(contract.id)}>آرشیو</Button>

const statusLabels: Record<string, string> = {
  active: "فعال",
  expired: "منقضی",
  terminated: "فسخ‌شده",
  renewed: "تمدیدشده",
};

export const ContractTable: React.FC<{
  data: Contract[];
  onDetails: (id: string) => void;
}> = ({ data, onDetails }) => (
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>عنوان</TableCell>
        <TableCell>نوع</TableCell>
        <TableCell>طرف قرارداد</TableCell>
        <TableCell>تاریخ شروع</TableCell>
        <TableCell>تاریخ پایان</TableCell>
        <TableCell>وضعیت</TableCell>
        <TableCell>عملیات</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((c) => (
        <TableRow key={c.id}>
          <TableCell>{c.title}</TableCell>
          <TableCell>{c.type}</TableCell>
          <TableCell>{c.party.name}</TableCell>
          <TableCell>{new Date(c.startDate).toLocaleDateString("fa-IR")}</TableCell>
          <TableCell>{new Date(c.endDate).toLocaleDateString("fa-IR")}</TableCell>
          <TableCell>
            <Tag label={statusLabels[c.status]} color={
              c.status === "active" ? "success" :
              c.status === "renewed" ? "primary" :
              c.status === "expired" ? "warning" : "error"
            } />
          </TableCell>
          <TableCell>
            <Tooltip title="مشاهده جزئیات">
              <Button type="text" onClick={() => onDetails(c.id)}><VisibilityIcon /></Button>
            </Tooltip>
            <Tooltip title="دانلود">
              <Button type="text" component="a" href={c.fileUrl} target="_blank"><DownloadIcon /></Button>
            </Tooltip>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);