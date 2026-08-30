import React, { useState, useMemo } from 'react';
import { Button, Card, Input, InputNumber, Pagination, Table, Tag, Tooltip, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { PurchaseInvoice } from '../../../types/procurement';
import { usePurchaseInvoices, useDeletePurchaseInvoice } from '../../../api/procurement';
import { PurchaseInvoiceDetails } from './PurchaseInvoiceDetails';

interface PurchaseInvoicesTableProps {
  filter?: any;
  onEdit: (invoice: PurchaseInvoice) => void;
  onView: (invoice: PurchaseInvoice) => void;
  onExport: (invoices: PurchaseInvoice[]) => void;
  userRole: string;
}

export const PurchaseInvoicesTable: React.FC<PurchaseInvoicesTableProps> = ({ 
  filter, 
  onEdit, 
  onView, 
  onExport, 
  userRole 
}) => {
  const { data: invoices = [], isLoading } = usePurchaseInvoices(filter);
  const deleteInvoice = useDeletePurchaseInvoice();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<PurchaseInvoice | null>(null);

  const filtered = useMemo(() =>
    invoices.filter(i =>
      i.invoiceNumber.includes(search) ||
      i.supplierName.includes(search)
    ), [invoices, search]);

  const paged = useMemo(() =>
    filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filtered, page, rowsPerPage]);

  const handleDelete = (id?: number) => {
    if (!id) return;
    deleteInvoice.mutate(id);
  };

  const handleDetails = (invoice: PurchaseInvoice) => {
    setSelectedInvoice(invoice);
    setDetailsOpen(true);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (isLoading) {
    return <Typography>در حال بارگذاری...</Typography>;
  }

  return (
    <div>
      <div style={{  mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center'  }}>
        <Input
          label="جستجو"
          variant="outlined"
          size="small"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{  width: 300  }}
        />
        <Typography.Text>
          تعداد کل: {filtered.length}
        </Typography.Text>
      </div>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>شماره فاکتور</TableCell>
              <TableCell>تأمین‌کننده</TableCell>
              <TableCell>تاریخ سررسید</TableCell>
              <TableCell>مبلغ کل</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell align="right">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paged.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  هیچ فاکتوری یافت نشد.
                </TableCell>
              </TableRow>
            ) : (
              paged.map((invoice) => (
                <TableRow key={invoice.id} hover>
                  <TableCell>{invoice.invoiceNumber}</TableCell>
                  <TableCell>{invoice.supplierName}</TableCell>
                  <TableCell>
                    {new Date(invoice.dueDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {invoice.totalAmount.toLocaleString()} تومان
                  </TableCell>
                  <TableCell>
                    <Tag 
                      label={invoice.status} 
                      color={
                        invoice.status === 'پرداخت شده' ? 'success' :
                        invoice.status === 'در انتظار پرداخت' ? 'warning' :
                        'default'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="مشاهده فایل">
                      <Button type="text" onClick={() => handleDetails(invoice)} size="small">
                        <VisibilityIcon />
                      </Button>
                    </Tooltip>
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(invoice)} size="small">
                        <EditIcon />
                      </Button>
                    </Tooltip>
                    {userRole === 'admin' && (
                      <Tooltip title="حذف">
                        <Button type="text" 
                          onClick={() => handleDelete(invoice.id)} 
                          size="small"
                          color="error"
                        >
                          <DeleteIcon />
                        </Button>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={filtered.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="تعداد در صفحه:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} از ${count}`}
      />

      <PurchaseInvoiceDetails
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        invoice={selectedInvoice}
      />
    </div>
  );
}; 