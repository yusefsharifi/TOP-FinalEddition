import React, { useState, useMemo } from 'react';
import { Button, Card, Input, InputNumber, Pagination, Progress, Table, Tag, Tooltip, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { Account, AccountType } from '../../../types/finance';
import { useAccounts, useDeleteAccount } from '../../../api/finance';

interface AccountsTableProps {
  filter?: any;
  onEdit: (account: Account) => void;
  onView: (account: Account) => void;
  onExport: (accounts: Account[]) => void;
  userRole: string;
}

export const AccountsTable: React.FC<AccountsTableProps> = ({ 
  filter, 
  onEdit, 
  onView, 
  onExport, 
  userRole 
}) => {
  const { data: accounts = [], isLoading } = useAccounts(filter);
  const deleteAccount = useDeleteAccount();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');

  const filtered = useMemo(() =>
    accounts.filter(a =>
      a.code.includes(search) ||
      a.name.includes(search) ||
      a.description?.includes(search)
    ), [accounts, search]);

  const paged = useMemo(() =>
    filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filtered, page, rowsPerPage]);

  const handleDelete = (id?: number) => {
    if (!id) return;
    deleteAccount.mutate(id);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getAccountTypeColor = (type: AccountType) => {
    switch (type) {
      case 'asset':
        return 'success';
      case 'liability':
        return 'error';
      case 'equity':
        return 'primary';
      case 'revenue':
        return 'info';
      case 'expense':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getAccountTypeLabel = (type: AccountType) => {
    switch (type) {
      case 'asset':
        return 'دارایی';
      case 'liability':
        return 'بدهی';
      case 'equity':
        return 'سرمایه';
      case 'revenue':
        return 'درآمد';
      case 'expense':
        return 'هزینه';
      default:
        return type;
    }
  };

  const getBalanceColor = (balance: number, type: AccountType) => {
    if (type === 'asset' || type === 'expense') {
      return balance >= 0 ? 'success.main' : 'error.main';
    } else {
      return balance >= 0 ? 'error.main' : 'success.main';
    }
  };

  if (isLoading) {
    return <LinearProgress />;
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
              <TableCell>کد حساب</TableCell>
              <TableCell>نام حساب</TableCell>
              <TableCell>نوع</TableCell>
              <TableCell>توضیحات</TableCell>
              <TableCell align="right">موجودی</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell align="right">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paged.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  هیچ حسابی یافت نشد.
                </TableCell>
              </TableRow>
            ) : (
              paged.map((account) => (
                <TableRow key={account.id} hover>
                  <TableCell>
                    <Typography.Text>
                      {account.code}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>{account.name}</TableCell>
                  <TableCell>
                    <Tag 
                      label={getAccountTypeLabel(account.type)} 
                      color={getAccountTypeColor(account.type)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {account.description || '-'}
                    </Typography.Text>
                  </TableCell>
                  <TableCell align="right">
                    <Typography.Text>
                      {account.balance.toLocaleString()} {account.currency}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <Tag 
                      label={account.isActive ? 'فعال' : 'غیرفعال'} 
                      color={account.isActive ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="مشاهده جزئیات">
                      <Button type="text" onClick={() => onView(account)} size="small">
                        <VisibilityIcon />
                      </Button>
                    </Tooltip>
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(account)} size="small">
                        <EditIcon />
                      </Button>
                    </Tooltip>
                    {userRole === 'admin' && (
                      <Tooltip title="حذف">
                        <Button type="text" 
                          onClick={() => handleDelete(account.id)} 
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