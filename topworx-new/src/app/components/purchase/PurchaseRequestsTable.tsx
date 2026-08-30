import React, { useState, useMemo } from 'react';
import { Button, Card, Input, InputNumber, Pagination, Table, Tag, Tooltip, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { PurchaseRequest } from '../../../types/procurement';
import { usePurchaseRequests, useDeletePurchaseRequest } from '../../../api/procurement';

interface PurchaseRequestsTableProps {
  filter?: any;
  onEdit: (request: PurchaseRequest) => void;
  onExport: (requests: PurchaseRequest[]) => void;
  userRole: string;
}

export const PurchaseRequestsTable: React.FC<PurchaseRequestsTableProps> = ({ 
  filter, 
  onEdit, 
  onExport, 
  userRole 
}) => {
  const { data: requests = [], isLoading } = usePurchaseRequests(filter);
  const deleteRequest = useDeletePurchaseRequest();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');

  const filtered = useMemo(() =>
    requests.filter(r =>
      r.requestNumber.includes(search) ||
      r.department.includes(search)
    ), [requests, search]);

  const paged = useMemo(() =>
    filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filtered, page, rowsPerPage]);

  const handleDelete = (id?: number) => {
    if (!id) return;
    deleteRequest.mutate(id);
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
              <TableCell>شماره درخواست</TableCell>
              <TableCell>دپارتمان</TableCell>
              <TableCell>تاریخ درخواست</TableCell>
              <TableCell>تاریخ مورد نیاز</TableCell>
              <TableCell>اولویت</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell align="right">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paged.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  هیچ درخواستی یافت نشد.
                </TableCell>
              </TableRow>
            ) : (
              paged.map((request) => (
                <TableRow key={request.id} hover>
                  <TableCell>{request.requestNumber}</TableCell>
                  <TableCell>{request.department}</TableCell>
                  <TableCell>
                    {new Date(request.requestDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {new Date(request.requiredDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Tag 
                      label={request.priority} 
                      color={
                        request.priority === 'فوری' ? 'error' :
                        request.priority === 'زیاد' ? 'warning' :
                        request.priority === 'متوسط' ? 'primary' :
                        'default'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag 
                      label={request.status} 
                      color={
                        request.status === 'تکمیل شده' ? 'success' :
                        request.status === 'رد شده' ? 'error' :
                        request.status === 'تأیید شده' ? 'primary' :
                        request.status === 'در حال خرید' ? 'info' :
                        'default'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(request)} size="small">
                        <EditIcon />
                      </Button>
                    </Tooltip>
                    {userRole === 'admin' && (
                      <Tooltip title="حذف">
                        <Button type="text" 
                          onClick={() => handleDelete(request.id)} 
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