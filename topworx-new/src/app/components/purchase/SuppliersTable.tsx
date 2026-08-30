import React, { useState, useMemo } from 'react';
import { Button, Card, Input, InputNumber, Pagination, Rate, Table, Tag, Tooltip, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { Supplier } from '../../../types/procurement';
import { useSuppliers, useDeleteSupplier } from '../../../api/procurement';

interface SuppliersTableProps {
  filter?: any;
  onEdit: (supplier: Supplier) => void;
  onExport: (suppliers: Supplier[]) => void;
  userRole: string;
}

export const SuppliersTable: React.FC<SuppliersTableProps> = ({ 
  filter, 
  onEdit, 
  onExport, 
  userRole 
}) => {
  const { data: suppliers = [], isLoading } = useSuppliers(filter);
  const deleteSupplier = useDeleteSupplier();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');

  const filtered = useMemo(() =>
    suppliers.filter(s =>
      s.code.includes(search) ||
      s.name.includes(search) ||
      s.contactPerson.includes(search)
    ), [suppliers, search]);

  const paged = useMemo(() =>
    filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filtered, page, rowsPerPage]);

  const handleDelete = (id?: number) => {
    if (!id) return;
    deleteSupplier.mutate(id);
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
              <TableCell>کد</TableCell>
              <TableCell>نام</TableCell>
              <TableCell>شخص تماس</TableCell>
              <TableCell>تلفن</TableCell>
              <TableCell>ایمیل</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell>امتیاز</TableCell>
              <TableCell align="right">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paged.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  هیچ تأمین‌کننده‌ای یافت نشد.
                </TableCell>
              </TableRow>
            ) : (
              paged.map((supplier) => (
                <TableRow key={supplier.id} hover>
                  <TableCell>{supplier.code}</TableCell>
                  <TableCell>{supplier.name}</TableCell>
                  <TableCell>{supplier.contactPerson}</TableCell>
                  <TableCell>{supplier.phone}</TableCell>
                  <TableCell>{supplier.email}</TableCell>
                  <TableCell>
                    <Tag 
                      label={supplier.status} 
                      color={
                        supplier.status === 'فعال' ? 'success' :
                        supplier.status === 'غیرفعال' ? 'error' :
                        'warning'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Rating value={supplier.rating} readOnly size="small" />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(supplier)} size="small">
                        <EditIcon />
                      </Button>
                    </Tooltip>
                    {userRole === 'admin' && (
                      <Tooltip title="حذف">
                        <Button type="text" 
                          onClick={() => handleDelete(supplier.id)} 
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