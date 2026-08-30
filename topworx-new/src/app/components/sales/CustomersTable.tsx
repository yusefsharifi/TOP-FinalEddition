import React, { useState, useMemo } from 'react';
import { Avatar, Badge, Button, Card, Input, InputNumber, Pagination, Select, Table, Tag, Tooltip, Typography } from 'antd';
import { BankOutlined as AccountBalanceIcon, BankOutlined as BusinessIcon, DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, EyeOutlined as ViewIcon, FallOutlined as TrendingDownIcon, PlusOutlined as AddIcon, RiseOutlined as TrendingUpIcon, UserOutlined as PersonIcon } from '@ant-design/icons';
import { Customer, CustomerFilters } from '../../../types/sales';

interface CustomersTableProps {
  customers: Customer[];
  loading?: boolean;
  onEdit: (customer: Customer) => void;
  onDelete: (customer: Customer) => void;
  onView: (customer: Customer) => void;
  onAdd: () => void;
  onFiltersChange: (filters: CustomerFilters) => void;
  total: number;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
  userRole?: string;
}

const customerTypeColors = {
  individual: 'primary',
  corporate: 'success',
  government: 'warning',
} as const;

const customerTypeLabels = {
  individual: 'شخصی',
  corporate: 'شرکتی',
  government: 'دولتی',
};

const statusColors = {
  active: 'success',
  inactive: 'default',
  suspended: 'error',
} as const;

const statusLabels = {
  active: 'فعال',
  inactive: 'غیرفعال',
  suspended: 'معلق',
};

export const CustomersTable: React.FC<CustomersTableProps> = ({
  customers,
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
  const [filters, setFilters] = useState<CustomerFilters>({
    customer_type: '',
    status: '',
    segment_id: '',
    assigned_to: '',
    search: '',
  });
  const [sortField, setSortField] = useState<keyof Customer>('name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (field: keyof Customer) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const handleFilterChange = (key: keyof CustomerFilters, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const sortedCustomers = useMemo(() => {
    return [...customers].sort((a, b) => {
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
  }, [customers, sortField, sortDirection]);

  const canEdit = userRole === 'admin' || userRole === 'manager' || userRole === 'sales';
  const canDelete = userRole === 'admin';

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const getCustomerIcon = (type: string) => {
    switch (type) {
      case 'individual':
        return <PersonIcon />;
      case 'corporate':
        return <BusinessIcon />;
      case 'government':
        return <AccountBalanceIcon />;
      default:
        return <PersonIcon />;
    }
  };

  const getBalanceColor = (balance: number) => {
    if (balance > 0) return 'error';
    if (balance < 0) return 'success';
    return 'default';
  };

  const getBalanceIcon = (balance: number) => {
    if (balance > 0) return <TrendingDownIcon />;
    if (balance < 0) return <TrendingUpIcon />;
    return null;
  };

  return (
    <Card style={{  width: '100%', overflow: 'hidden'  }}>
      {/* Filters */}
      <div style={{  p: 2, borderBottom: 1, borderColor: 'divider'  }}>
        <div style={{  display: 'flex', gap: 2, alignItems: 'center', mb: 2, flexWrap: 'wrap'  }}>
          <Input
            label="جستجو"
            size="small"
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            style={{  minWidth: 200  }}
            placeholder="نام، ایمیل، تلفن یا کد مشتری..."
          />
          <FormControl size="small" style={{  minWidth: 150  }}>
            <InputLabel>نوع مشتری</span>
            <Select
              value={filters.customer_type}
              label="نوع مشتری"
              onChange={(e) => handleFilterChange('customer_type', e.target.value)}
            >
              <MenuItem value="">همه</Select.Option>
              <MenuItem value="individual">شخصی</Select.Option>
              <MenuItem value="corporate">شرکتی</Select.Option>
              <MenuItem value="government">دولتی</Select.Option>
            </Select>
          </div>
          <FormControl size="small" style={{  minWidth: 150  }}>
            <InputLabel>وضعیت</span>
            <Select
              value={filters.status}
              label="وضعیت"
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <MenuItem value="">همه</Select.Option>
              <MenuItem value="active">فعال</Select.Option>
              <MenuItem value="inactive">غیرفعال</Select.Option>
              <MenuItem value="suspended">معلق</Select.Option>
            </Select>
          </div>
          <FormControl size="small" style={{  minWidth: 150  }}>
            <InputLabel>بخش</span>
            <Select
              value={filters.segment_id}
              label="بخش"
              onChange={(e) => handleFilterChange('segment_id', e.target.value)}
            >
              <MenuItem value="">همه</Select.Option>
              <MenuItem value="vip">VIP</Select.Option>
              <MenuItem value="regular">عادی</Select.Option>
              <MenuItem value="premium">پریمیوم</Select.Option>
            </Select>
          </div>
          <div>
          <Tooltip title="افزودن مشتری جدید">
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
              <TableCell>مشتری</TableCell>
              <TableCell>اطلاعات تماس</TableCell>
              <TableCell>نوع</TableCell>
              <TableCell>بخش</TableCell>
              <TableCell>اعتبار</TableCell>
              <TableCell align="right">موجودی</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell>تخصیص</TableCell>
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
                <TableCell colSpan={10} align="center">
                  <Typography>در حال بارگذاری...</Typography>
                </TableCell>
              </TableRow>
            ) : sortedCustomers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} align="center">
                  <Typography>هیچ مشتری یافت نشد</Typography>
                </TableCell>
              </TableRow>
            ) : (
              sortedCustomers.map((customer) => (
                <TableRow key={customer.id} hover>
                  <TableCell>
                    <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                      <Avatar style={{  bgcolor: customerTypeColors[customer.customer_type]  }}>
                        {getCustomerIcon(customer.customer_type)}
                      </Avatar>
                      <div>
                        <Typography.Text>
                          {customer.name}
                        </Typography.Text>
                        <Typography variant="caption" color="text.secondary" fontFamily="monospace">
                          {customer.code}
                        </Typography>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {customer.email}
                      </Typography.Text>
                      <Typography variant="caption" color="text.secondary">
                        {customer.phone}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={customerTypeLabels[customer.customer_type]}
                      color={customerTypeColors[customer.customer_type]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={customer.segment_name || 'نامشخص'}
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {formatCurrency(customer.credit_limit)}
                    </Typography.Text>
                  </TableCell>
                  <TableCell align="right">
                    <div style={{  display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'flex-end'  }}>
                      {getBalanceIcon(customer.current_balance)}
                      <Typography.Text>
                        {formatCurrency(customer.current_balance)}
                      </Typography.Text>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={statusLabels[customer.status]}
                      color={statusColors[customer.status]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {customer.assigned_to_name || 'تخصیص نیافته'}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {new Date(customer.created_at).toLocaleDateString('fa-IR')}
                    </Typography.Text>
                  </TableCell>
                  <TableCell align="center">
                    <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                      <Tooltip title="مشاهده">
                        <Button type="text" size="small" onClick={() => onView(customer)}
                        >
                          <ViewIcon />
                        </Button>
                      </Tooltip>
                      {canEdit && (
                        <Tooltip title="ویرایش">
                          <Button type="text" size="small" onClick={() => onEdit(customer)}
                          >
                            <EditIcon />
                          </Button>
                        </Tooltip>
                      )}
                      {canDelete && (
                        <Tooltip title="حذف">
                          <Button type="text" size="small" onClick={() => onDelete(customer)}
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