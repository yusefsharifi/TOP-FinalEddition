import React, { useState, useMemo } from 'react';
import { Avatar, Badge, Button, Card, Input, InputNumber, Pagination, Select, Table, Tag, Tooltip, Typography } from 'antd';
import { BankOutlined as BusinessIcon, DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, EyeOutlined as ViewIcon, FallOutlined as TrendingDownIcon, MailOutlined as EmailIcon, PhoneOutlined as PhoneIcon, PlusOutlined as AddIcon, RiseOutlined as TrendingUpIcon, ToolOutlined as WorkIcon, UserOutlined as PersonIcon } from '@ant-design/icons';
import { Employee, HRFilters } from '../../../types/hr';

interface EmployeesTableProps {
  employees: Employee[];
  loading?: boolean;
  onEdit: (employee: Employee) => void;
  onDelete: (employee: Employee) => void;
  onView: (employee: Employee) => void;
  onAdd: () => void;
  onFiltersChange: (filters: HRFilters) => void;
  total: number;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
  userRole?: string;
}

const employmentTypeColors = {
  full_time: 'success',
  part_time: 'info',
  contract: 'warning',
  intern: 'secondary',
} as const;

const employmentTypeLabels = {
  full_time: 'تمام وقت',
  part_time: 'نیمه وقت',
  contract: 'قراردادی',
  intern: 'کارآموز',
};

const statusColors = {
  active: 'success',
  inactive: 'default',
  terminated: 'error',
  resigned: 'warning',
} as const;

const statusLabels = {
  active: 'فعال',
  inactive: 'غیرفعال',
  terminated: 'اخراج شده',
  resigned: 'استعفا داده',
};

export const EmployeesTable: React.FC<EmployeesTableProps> = ({
  employees,
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
  const [filters, setFilters] = useState<HRFilters>({
    department_id: '',
    status: '',
    employment_type: '',
    search: '',
  });
  const [sortField, setSortField] = useState<keyof Employee>('first_name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (field: keyof Employee) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const handleFilterChange = (key: keyof HRFilters, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const sortedEmployees = useMemo(() => {
    return [...employees].sort((a, b) => {
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
  }, [employees, sortField, sortDirection]);

  const canEdit = userRole === 'admin' || userRole === 'hr_manager';
  const canDelete = userRole === 'admin';

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR');
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const getYearsOfService = (hireDate: string) => {
    const hire = new Date(hireDate);
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - hire.getTime());
    const diffYears = Math.ceil(diffTime / (1000 * 60 * 60 * 24 * 365));
    return diffYears;
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
            placeholder="نام، ایمیل، کد کارمندی..."
          />
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
              <MenuItem value="terminated">اخراج شده</Select.Option>
              <MenuItem value="resigned">استعفا داده</Select.Option>
            </Select>
          </div>
          <FormControl size="small" style={{  minWidth: 150  }}>
            <InputLabel>نوع استخدام</span>
            <Select
              value={filters.employment_type}
              label="نوع استخدام"
              onChange={(e) => handleFilterChange('employment_type', e.target.value)}
            >
              <MenuItem value="">همه</Select.Option>
              <MenuItem value="full_time">تمام وقت</Select.Option>
              <MenuItem value="part_time">نیمه وقت</Select.Option>
              <MenuItem value="contract">قراردادی</Select.Option>
              <MenuItem value="intern">کارآموز</Select.Option>
            </Select>
          </div>
          <FormControl size="small" style={{  minWidth: 150  }}>
            <InputLabel>بخش</span>
            <Select
              value={filters.department_id}
              label="بخش"
              onChange={(e) => handleFilterChange('department_id', e.target.value)}
            >
              <MenuItem value="">همه</Select.Option>
              <MenuItem value="it">فناوری اطلاعات</Select.Option>
              <MenuItem value="hr">منابع انسانی</Select.Option>
              <MenuItem value="finance">مالی</Select.Option>
              <MenuItem value="sales">فروش</Select.Option>
              <MenuItem value="marketing">بازاریابی</Select.Option>
            </Select>
          </div>
          <div>
          <Tooltip title="افزودن کارمند جدید">
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
              <TableCell>کارمند</TableCell>
              <TableCell>اطلاعات تماس</TableCell>
              <TableCell>بخش</TableCell>
              <TableCell>سمت</TableCell>
              <TableCell>نوع استخدام</TableCell>
              <TableCell align="right">حقوق</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell>مدیر</TableCell>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'hire_date'}
                  direction={sortField === 'hire_date' ? sortDirection : 'asc'}
                  onClick={() => handleSort('hire_date')}
                >
                  تاریخ استخدام
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
            ) : sortedEmployees.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} align="center">
                  <Typography>هیچ کارمندی یافت نشد</Typography>
                </TableCell>
              </TableRow>
            ) : (
              sortedEmployees.map((employee) => (
                <TableRow key={employee.id} hover>
                  <TableCell>
                    <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                      <Badge
                        overlap="circular"
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                        badgeContent={
                          <div>
                        }
                      >
                        <Avatar style={{  bgcolor: 'primary.main'  }}>
                          {getInitials(employee.first_name, employee.last_name)}
                        </Avatar>
                      </Badge>
                      <div>
                        <Typography.Text>
                          {`${employee.first_name} ${employee.last_name}`}
                        </Typography.Text>
                        <Typography variant="caption" color="text.secondary" fontFamily="monospace">
                          {employee.employee_code}
                        </Typography>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                        <EmailIcon style={{  fontSize: 14, color: 'text.secondary'  }} />
                        <Typography.Text>
                          {employee.email}
                        </Typography.Text>
                      </div>
                      <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                        <PhoneIcon style={{  fontSize: 14, color: 'text.secondary'  }} />
                        <Typography variant="caption" color="text.secondary">
                          {employee.phone}
                        </Typography>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                      <BusinessIcon style={{  fontSize: 16, color: 'text.secondary'  }} />
                      <Typography.Text>
                        {employee.department_name}
                      </Typography.Text>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                      <WorkIcon style={{  fontSize: 16, color: 'text.secondary'  }} />
                      <Typography.Text>
                        {employee.position_name}
                      </Typography.Text>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={employmentTypeLabels[employee.employment_type]}
                      color={employmentTypeColors[employee.employment_type]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Typography.Text>
                      {formatCurrency(employee.salary)}
                    </Typography.Text>
                    <Typography variant="caption" color="text.secondary">
                      {employee.currency}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={statusLabels[employee.status]}
                      color={statusColors[employee.status]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {employee.manager_name || '-'}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {formatDate(employee.hire_date)}
                      </Typography.Text>
                      <Typography variant="caption" color="text.secondary">
                        {getYearsOfService(employee.hire_date)} سال سابقه
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell align="center">
                    <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                      <Tooltip title="مشاهده">
                        <Button type="text" size="small" onClick={() => onView(employee)}
                        >
                          <ViewIcon />
                        </Button>
                      </Tooltip>
                      {canEdit && (
                        <Tooltip title="ویرایش">
                          <Button type="text" size="small" onClick={() => onEdit(employee)}
                          >
                            <EditIcon />
                          </Button>
                        </Tooltip>
                      )}
                      {canDelete && (
                        <Tooltip title="حذف">
                          <Button type="text" size="small" onClick={() => onDelete(employee)}
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