import React, { useState, useMemo } from 'react';
import { Avatar, Button, Card, Input, InputNumber, Pagination, Progress, Select, Table, Tag, Tooltip, Typography } from 'antd';
import { BankOutlined as BusinessIcon, ConvertOutlined as ConvertIcon, DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, EyeOutlined as ViewIcon, FallOutlined as TrendingDownIcon, MailOutlined as EmailIcon, PhoneOutlined as PhoneIcon, PlusOutlined as AddIcon, RiseOutlined as TrendingUpIcon, UserOutlined as PersonIcon } from '@ant-design/icons';
import { Lead, LeadFilters } from '../../../types/sales';

interface LeadsTableProps {
  leads: Lead[];
  loading?: boolean;
  onEdit: (lead: Lead) => void;
  onDelete: (lead: Lead) => void;
  onView: (lead: Lead) => void;
  onAdd: () => void;
  onConvert: (lead: Lead) => void;
  onFiltersChange: (filters: LeadFilters) => void;
  total: number;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
  userRole?: string;
}

const statusColors = {
  new: 'default',
  contacted: 'info',
  qualified: 'primary',
  proposal: 'warning',
  negotiation: 'secondary',
  won: 'success',
  lost: 'error',
} as const;

const statusLabels = {
  new: 'جدید',
  contacted: 'تماس گرفته شده',
  qualified: 'تأیید شده',
  proposal: 'پیشنهاد',
  negotiation: 'مذاکره',
  won: 'موفق',
  lost: 'ناموفق',
};

const priorityColors = {
  low: 'default',
  medium: 'info',
  high: 'warning',
  urgent: 'error',
} as const;

const priorityLabels = {
  low: 'کم',
  medium: 'متوسط',
  high: 'زیاد',
  urgent: 'فوری',
};

const sourceColors = {
  website: 'primary',
  social_media: 'secondary',
  referral: 'success',
  cold_call: 'warning',
  event: 'info',
  other: 'default',
} as const;

const sourceLabels = {
  website: 'وب‌سایت',
  social_media: 'شبکه‌های اجتماعی',
  referral: 'معرفی',
  cold_call: 'تماس سرد',
  event: 'رویداد',
  other: 'سایر',
};

export const LeadsTable: React.FC<LeadsTableProps> = ({
  leads,
  loading = false,
  onEdit,
  onDelete,
  onView,
  onAdd,
  onConvert,
  onFiltersChange,
  total,
  page,
  limit,
  onPageChange,
  onLimitChange,
  userRole,
}) => {
  const [filters, setFilters] = useState<LeadFilters>({
    status: '',
    source: '',
    priority: '',
    assigned_to: '',
    search: '',
  });
  const [sortField, setSortField] = useState<keyof Lead>('created_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const handleSort = (field: keyof Lead) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const handleFilterChange = (key: keyof LeadFilters, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const sortedLeads = useMemo(() => {
    return [...leads].sort((a, b) => {
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
  }, [leads, sortField, sortDirection]);

  const canEdit = userRole === 'admin' || userRole === 'manager' || userRole === 'sales';
  const canDelete = userRole === 'admin';
  const canConvert = userRole === 'admin' || userRole === 'manager' || userRole === 'sales';

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR');
  };

  const getProbabilityColor = (probability: number) => {
    if (probability >= 80) return 'success';
    if (probability >= 60) return 'primary';
    if (probability >= 40) return 'warning';
    return 'error';
  };

  const getExpectedCloseDateColor = (dateString: string) => {
    const closeDate = new Date(dateString);
    const today = new Date();
    const diffDays = Math.ceil((closeDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'error';
    if (diffDays <= 7) return 'warning';
    return 'success';
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
            placeholder="نام، ایمیل، شرکت یا موقعیت..."
          />
          <FormControl size="small" style={{  minWidth: 150  }}>
            <InputLabel>وضعیت</span>
            <Select
              value={filters.status}
              label="وضعیت"
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <MenuItem value="">همه</Select.Option>
              <MenuItem value="new">جدید</Select.Option>
              <MenuItem value="contacted">تماس گرفته شده</Select.Option>
              <MenuItem value="qualified">تأیید شده</Select.Option>
              <MenuItem value="proposal">پیشنهاد</Select.Option>
              <MenuItem value="negotiation">مذاکره</Select.Option>
              <MenuItem value="won">موفق</Select.Option>
              <MenuItem value="lost">ناموفق</Select.Option>
            </Select>
          </div>
          <FormControl size="small" style={{  minWidth: 150  }}>
            <InputLabel>منبع</span>
            <Select
              value={filters.source}
              label="منبع"
              onChange={(e) => handleFilterChange('source', e.target.value)}
            >
              <MenuItem value="">همه</Select.Option>
              <MenuItem value="website">وب‌سایت</Select.Option>
              <MenuItem value="social_media">شبکه‌های اجتماعی</Select.Option>
              <MenuItem value="referral">معرفی</Select.Option>
              <MenuItem value="cold_call">تماس سرد</Select.Option>
              <MenuItem value="event">رویداد</Select.Option>
              <MenuItem value="other">سایر</Select.Option>
            </Select>
          </div>
          <FormControl size="small" style={{  minWidth: 150  }}>
            <InputLabel>اولویت</span>
            <Select
              value={filters.priority}
              label="اولویت"
              onChange={(e) => handleFilterChange('priority', e.target.value)}
            >
              <MenuItem value="">همه</Select.Option>
              <MenuItem value="low">کم</Select.Option>
              <MenuItem value="medium">متوسط</Select.Option>
              <MenuItem value="high">زیاد</Select.Option>
              <MenuItem value="urgent">فوری</Select.Option>
            </Select>
          </div>
          <div>
          <Tooltip title="افزودن لید جدید">
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
              <TableCell>لید</TableCell>
              <TableCell>شرکت</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell>منبع</TableCell>
              <TableCell>اولویت</TableCell>
              <TableCell align="right">ارزش تخمینی</TableCell>
              <TableCell>احتمال موفقیت</TableCell>
              <TableCell>تاریخ سررسید</TableCell>
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
                <TableCell colSpan={11} align="center">
                  <Typography>در حال بارگذاری...</Typography>
                </TableCell>
              </TableRow>
            ) : sortedLeads.length === 0 ? (
              <TableRow>
                <TableCell colSpan={11} align="center">
                  <Typography>هیچ لیدی یافت نشد</Typography>
                </TableCell>
              </TableRow>
            ) : (
              sortedLeads.map((lead) => (
                <TableRow key={lead.id} hover>
                  <TableCell>
                    <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                      <Avatar style={{  bgcolor: sourceColors[lead.source]  }}>
                        {lead.company ? <BusinessIcon /> : <PersonIcon />}
                      </Avatar>
                      <div>
                        <Typography.Text>
                          {lead.name}
                        </Typography.Text>
                        <Typography variant="caption" color="text.secondary">
                          {lead.email}
                        </Typography>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {lead.company || '-'}
                    </Typography.Text>
                    <Typography variant="caption" color="text.secondary">
                      {lead.position || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={statusLabels[lead.status]}
                      color={statusColors[lead.status]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={sourceLabels[lead.source]}
                      color={sourceColors[lead.source]}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={priorityLabels[lead.priority]}
                      color={priorityColors[lead.priority]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Typography.Text>
                      {formatCurrency(lead.estimated_value)}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                      <div style={{  width: '100%', mr: 1  }}>
                        <LinearProgress
                          variant="determinate"
                          value={lead.probability}
                          color={getProbabilityColor(lead.probability)}
                          style={{  height: 8, borderRadius: 5  }}
                        />
                      </div>
                      <Typography variant="caption" color="text.secondary">
                        {lead.probability}%
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {formatDate(lead.expected_close_date)}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {lead.assigned_to_name || 'تخصیص نیافته'}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {formatDate(lead.created_at)}
                    </Typography.Text>
                  </TableCell>
                  <TableCell align="center">
                    <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                      <Tooltip title="مشاهده">
                        <Button type="text" size="small" onClick={() => onView(lead)}
                        >
                          <ViewIcon />
                        </Button>
                      </Tooltip>
                      {canEdit && (
                        <Tooltip title="ویرایش">
                          <Button type="text" size="small" onClick={() => onEdit(lead)}
                          >
                            <EditIcon />
                          </Button>
                        </Tooltip>
                      )}
                      {canConvert && lead.status !== 'won' && lead.status !== 'lost' && (
                        <Tooltip title="تبدیل به مشتری">
                          <Button type="text" size="small" onClick={() => onConvert(lead)}
                          >
                            <ConvertIcon />
                          </Button>
                        </Tooltip>
                      )}
                      {canDelete && (
                        <Tooltip title="حذف">
                          <Button type="text" size="small" onClick={() => onDelete(lead)}
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