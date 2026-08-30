import React from "react";
import { Button, Table, Tag, Tooltip } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { DownloadOutlined } from '@ant-design/icons';
import { Payroll } from "../../api/payroll/types";
import { Button, Checkbox } from 'antd';

const [selected, setSelected] = useState<string[]>([]);

<TableCell>
  <Checkbox checked={selected.includes(p.id)} onChange={e => {
    setSelected(e.target.checked ? [...selected, p.id] : selected.filter(id => id !== p.id));
  }} />
</TableCell>

<Button onClick={() => payMultiple(selected)}>پرداخت گروهی</Button>
const statusLabels: Record<string, string> = {
  pending: "در انتظار پرداخت",
  paid: "پرداخت شده",
  cancelled: "لغو شده",
};

export const PayrollTable: React.FC<{
  data: Payroll[];
  onDetails: (id: string) => void;
}> = ({ data, onDetails }) => (
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>نام پرسنل</TableCell>
        <TableCell>ماه</TableCell>
        <TableCell>سال</TableCell>
        <TableCell>جمع کل</TableCell>
        <TableCell>خالص پرداختی</TableCell>
        <TableCell>وضعیت</TableCell>
        <TableCell>عملیات</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((p) => (
        <TableRow key={p.id}>
          <TableCell>{p.employeeName}</TableCell>
          <TableCell>{p.month}</TableCell>
          <TableCell>{p.year}</TableCell>
          <TableCell>{p.total.toLocaleString()}</TableCell>
          <TableCell>{p.net.toLocaleString()}</TableCell>
          <TableCell>
            <Tag label={statusLabels[p.status]} color={
              p.status === "paid" ? "success" :
              p.status === "pending" ? "warning" : "error"
            } />
          </TableCell>
          <TableCell>
            <Tooltip title="مشاهده جزئیات">
              <Button type="text" onClick={() => onDetails(p.id)}><VisibilityIcon /></Button>
            </Tooltip>
            {p.pdfUrl && (
              <Tooltip title="دانلود PDF">
                <Button type="text" component="a" href={p.pdfUrl} target="_blank"><DownloadIcon /></Button>
              </Tooltip>
            )}
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);