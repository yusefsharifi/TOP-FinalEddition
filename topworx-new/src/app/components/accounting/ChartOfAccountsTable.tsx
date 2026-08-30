import React, { useState, useMemo } from 'react';
import { Button, Card, Input, InputNumber, Pagination, Select, Table, Tag, Tooltip, Typography } from 'antd';
import { ApartmentOutlined as AccountTreeIcon, DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, EyeOutlined as ViewIcon, PlusOutlined as AddIcon } from '@ant-design/icons';
import { ChartOfAccounts, AccountingFilters } from '../../../types/accounting';

interface ChartOfAccountsTableProps {
  accounts: ChartOfAccounts[];
  loading?: boolean;
  onEdit: (account: ChartOfAccounts) => void;
  onDelete: (account: ChartOfAccounts) => void;
  onView: (account: ChartOfAccounts) => void;
  onAdd: () => void;
  onFiltersChange: (filters: AccountingFilters) => void;
  total: number;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
  userRole?: string;
}

const accountTypeColors = {
  asset: 'success',
  liability: 'error',
  equity: 'warning',
  revenue: 'info',
  expense: 'secondary',
} as const;

const accountTypeLabels = {
  asset: 'دارایی',
  liability: 'بدهی',
  equity: 'سرمایه',
  revenue: 'درآمد',
  expense: 'هزینه',
};

export const ChartOfAccountsTable: React.FC<ChartOfAccountsTableProps> = ({
  accounts,
  loading = false,
  onEdit,
  onDelete,
  onView,
  onAdd,
  onFiltersChange,
  total,
  page,
  limit,
  onPageChange,
  onLimitChange,
  userRole,
}) => {
  const [filters, setFilters] = useState<AccountingFilters>({
    account_type: '',
    search: '',
  });
  const [sortField, setSortField] = useState<keyof ChartOfAccounts>('code');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (field: keyof ChartOfAccounts) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const handleFilterChange = (key: keyof AccountingFilters, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const sortedAccounts = useMemo(() => {
    return [...accounts].sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      return 0;
    });
  }, [accounts, sortField, sortDirection]);

  const canEdit = userRole === 'admin' || userRole === 'accountant';
  const canDelete = userRole === 'admin';

  return (
    <Card style={{  width: '100%', overflow: 'hidden'  }}>
      {/* Filters */}
      <div style={{  p: 2, borderBottom: 1, borderColor: 'divider'  }}>
        <div style={{  display: 'flex', gap: 2, alignItems: 'center', mb: 2  }}>
          <Input
            label="جستجو"
            size="small"
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            style={{  minWidth: 200  }}
          />
          <FormControl size="small" style={{  minWidth: 150  }}>
            <InputLabel>نوع حساب</span>
            <Select
              value={filters.account_type}
              label="نوع حساب"
              onChange={(e) => handleFilterChange('account_type', e.target.value)}
            >
              <MenuItem value="">همه</Select.Option>
              <MenuItem value="asset">دارایی</Select.Option>
              <MenuItem value="liability">بدهی</Select.Option>
              <MenuItem value="equity">سرمایه</Select.Option>
              <MenuItem value="revenue">درآمد</Select.Option>
              <MenuItem value="expense">هزینه</Select.Option>
            </Select>
          </div>
          <div>
          <Tooltip title="افزودن حساب جدید">
            <Button type="text" onClick={onAdd}>
              <AddIcon />
            </Button>
          </Tooltip>
        </div>
      </div>

      {/* Table */}
      <TableContainer style={{  maxHeight: 600  }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'code'}
                  direction={sortField === 'code' ? sortDirection : 'asc'}
                  onClick={() => handleSort('code')}
                >
                  کد حساب
                </span>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'name'}
                  direction={sortField === 'name' ? sortDirection : 'asc'}
                  onClick={() => handleSort('name')}
                >
                  نام حساب
                </span>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'type'}
                  direction={sortField === 'type' ? sortDirection : 'asc'}
                  onClick={() => handleSort('type')}
                >
                  نوع
                </span>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'level'}
                  direction={sortField === 'level' ? sortDirection : 'asc'}
                  onClick={() => handleSort('level')}
                >
                  سطح
                </span>
              </TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'created_at'}
                  direction={sortField === 'created_at' ? sortDirection : 'asc'}
                  onClick={() => handleSort('created_at')}
                >
                  تاریخ ایجاد
                </span>
              </TableCell>
              <TableCell align="center">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography>در حال بارگذاری...</Typography>
                </TableCell>
              </TableRow>
            ) : sortedAccounts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography>هیچ حسابی یافت نشد</Typography>
                </TableCell>
              </TableRow>
            ) : (
              sortedAccounts.map((account) => (
                <TableRow key={account.id} hover>
                  <TableCell>
                    <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                      <AccountTreeIcon style={{  fontSize: 16, color: 'text.secondary'  }} />
                      <Typography.Text>
                        {account.code}
                      </Typography.Text>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Typography
                      style={{ 
                        fontWeight: account.level === 1 ? 'bold' : 'normal',
                        pl: (account.level - 1) * 2,
                       }}
                    >
                      {account.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={accountTypeLabels[account.type]}
                      color={accountTypeColors[account.type]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={`سطح ${account.level}`}
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={account.is_active ? 'فعال' : 'غیرفعال'}
                      color={account.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {new Date(account.created_at).toLocaleDateString('fa-IR')}
                    </Typography.Text>
                  </TableCell>
                  <TableCell align="center">
                    <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                      <Tooltip title="مشاهده">
                        <Button type="text" size="small" onClick={() => onView(account)}
                        >
                          <ViewIcon />
                        </Button>
                      </Tooltip>
                      {canEdit && (
                        <Tooltip title="ویرایش">
                          <Button type="text" size="small" onClick={() => onEdit(account)}
                          >
                            <EditIcon />
                          </Button>
                        </Tooltip>
                      )}
                      {canDelete && (
                        <Tooltip title="حذف">
                          <Button type="text" size="small" onClick={() => onDelete(account)}
                          >
                            <DeleteIcon />
                          </Button>
                        </Tooltip>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <TablePagination
        component="div"
        count={total}
        page={page}
        onPageChange={(_, newPage) => onPageChange(newPage)}
        rowsPerPage={limit}
        onRowsPerPageChange={(e) => onLimitChange(parseInt(e.target.value, 10))}
        rowsPerPageOptions={[10, 25, 50, 100]}
        labelRowsPerPage="تعداد در صفحه:"
        labelDisplayedRows={({ from, to, count }) =>
          `${from}-${to} از ${count !== -1 ? count : `بیش از ${to}`}`
        }
      />
    </Card>
  );
}; 