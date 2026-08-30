import React, { useState, useMemo } from 'react';
import { Button, Card, Input, InputNumber, Pagination, Table, Tag, Tooltip, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { HistoryOutlined } from '@ant-design/icons';
import { PurchaseOrder } from '../../../types/procurement';
import { usePurchaseOrders, useDeletePurchaseOrder } from '../../../api/procurement';

interface PurchaseOrdersTableProps {
  filter?: any;
  onEdit: (order: PurchaseOrder) => void;
  onViewStatusHistory: (order: PurchaseOrder) => void;
  onExport: (orders: PurchaseOrder[]) => void;
  userRole: string;
}

export const PurchaseOrdersTable: React.FC<PurchaseOrdersTableProps> = ({ 
  filter, 
  onEdit, 
  onViewStatusHistory, 
  onExport, 
  userRole 
}) => {
  const { data: orders = [], isLoading } = usePurchaseOrders(filter);
  const deleteOrder = useDeletePurchaseOrder();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');

  const filtered = useMemo(() =>
    orders.filter(o =>
      o.orderNumber.includes(search) ||
      o.supplierName.includes(search)
    ), [orders, search]);

  const paged = useMemo(() =>
    filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filtered, page, rowsPerPage]);

  const handleDelete = (id?: number) => {
    if (!id) return;
    deleteOrder.mutate(id);
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
              <TableCell>شماره سفارش</TableCell>
              <TableCell>تأمین‌کننده</TableCell>
              <TableCell>تاریخ سفارش</TableCell>
              <TableCell>تاریخ تحویل</TableCell>
              <TableCell>مبلغ نهایی</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell align="right">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paged.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  هیچ سفارشی یافت نشد.
                </TableCell>
              </TableRow>
            ) : (
              paged.map((order) => (
                <TableRow key={order.id} hover>
                  <TableCell>{order.orderNumber}</TableCell>
                  <TableCell>{order.supplierName}</TableCell>
                  <TableCell>
                    {new Date(order.orderDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {new Date(order.expectedDeliveryDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {order.finalAmount.toLocaleString()} تومان
                  </TableCell>
                  <TableCell>
                    <Tag 
                      label={order.status} 
                      color={
                        order.status === 'دریافت شده' ? 'success' :
                        order.status === 'لغو شده' ? 'error' :
                        order.status === 'ارسال شده' ? 'primary' :
                        order.status === 'تأیید شده' ? 'info' :
                        'default'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="تاریخچه وضعیت">
                      <Button type="text" onClick={() => onViewStatusHistory(order)} size="small">
                        <HistoryIcon />
                      </Button>
                    </Tooltip>
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(order)} size="small">
                        <EditIcon />
                      </Button>
                    </Tooltip>
                    {userRole === 'admin' && (
                      <Tooltip title="حذف">
                        <Button type="text" 
                          onClick={() => handleDelete(order.id)} 
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
    </div>
  );
}; 