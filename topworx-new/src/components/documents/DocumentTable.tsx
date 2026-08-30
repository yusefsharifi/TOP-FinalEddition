import React from "react";
import { Button, Table, Tag, Tooltip } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { Document } from "../../api/documents/types";

<Button onClick={() => archiveDocument(doc.id)}>آرشیو</Button>

export const DocumentTable: React.FC<{
  data: Document[];
  onPreview: (doc: Document) => void;
  onDelete: (id: string) => void;
}> = ({ data, onPreview, onDelete }) => (
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>نام سند</TableCell>
        <TableCell>نوع</TableCell>
        <TableCell>حجم</TableCell>
        <TableCell>پوشه</TableCell>
        <TableCell>برچسب‌ها</TableCell>
        <TableCell>نسخه</TableCell>
        <TableCell>عملیات</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((doc) => (
        <TableRow key={doc.id}>
          <TableCell>{doc.name}</TableCell>
          <TableCell>{doc.type}</TableCell>
          <TableCell>{(doc.size / 1024).toFixed(1)} KB</TableCell>
          <TableCell>{doc.folder}</TableCell>
          <TableCell>
            {doc.tags.map(tag => <Tag key={tag} label={tag} size="small" style={{  mr: 0.5  }} />)}
          </TableCell>
          <TableCell>{doc.version}</TableCell>
          <TableCell>
            <Tooltip title="پیش‌نمایش">
              <Button type="text" onClick={() => onPreview(doc)}><VisibilityIcon /></Button>
            </Tooltip>
            <Tooltip title="دانلود">
              <Button type="text" component="a" href={doc.url} target="_blank"><DownloadIcon /></Button>
            </Tooltip>
            <Tooltip title="حذف">
              <Button type="text" onClick={() => onDelete(doc.id)}><DeleteIcon /></Button>
            </Tooltip>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);

<Input select label="وضعیت" value={filters.status || ""} onChange={e => onChange({ ...filters, status: e.target.value })}>
  <MenuItem value="">همه</Select.Option>
  <MenuItem value="active">فعال</Select.Option>
  <MenuItem value="archived">آرشیو شده</Select.Option>
</Input>