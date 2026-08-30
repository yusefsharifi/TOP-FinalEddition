import React, { useState, useMemo } from 'react';
import { Alert, Button, Card, Col, Input, InputNumber, Modal, Pagination, Row, Select, Table, Tag, Tooltip, Typography } from 'antd';
import { BankOutlined as AccountBalanceIcon, CheckCircleOutlined as CheckCircleIcon, DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, EyeOutlined as ViewIcon, PlusOutlined as AddIcon, SyncOutlined as SyncIcon } from '@ant-design/icons';
import { BankReconciliation, AccountingFilters } from '../../../types/accounting';

interface BankReconciliationTableProps {
  reconciliations: BankReconciliation[];
  loading?: boolean;
  onEdit: (reconciliation: BankReconciliation) => void;
  onDelete: (reconciliation: BankReconciliation) => void;
  onView: (reconciliation: BankReconciliation) => void;
  onAdd: () => void;
  onComplete: (reconciliation: BankReconciliation) => void;
  onFiltersChange: (filters: AccountingFilters) => void;
  total: number;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
  userRole?: string;
}

const statusColors = {
  draft: 'default',
  completed: 'success',
} as const;

const statusLabels = {
  draft: 'پیش‌نویس',
  completed: 'تکمیل شده',
};

export const BankReconciliationTable: React.FC<BankReconciliationTableProps> = ({
  reconciliations,
  loading = false,
  onEdit,
  onDelete,
  onView,
  onAdd,
  onComplete,
  onFiltersChange,
  total,
  page,
  limit,
  onPageChange,
  onLimitChange,
  userRole,
}) => {
  const [filters, setFilters] = useState<AccountingFilters>({
    status: '',
    search: '',
  });
  const [sortField, setSortField] = useState<keyof BankReconciliation>('period_start');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [selectedReconciliation, setSelectedReconciliation] = useState<BankReconciliation | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);

  const handleSort = (field: keyof BankReconciliation) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const handleFilterChange = (key: keyof AccountingFilters, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleViewDetails = (reconciliation: BankReconciliation) => {
    setSelectedReconciliation(reconciliation);
    setDetailsDialogOpen(true);
  };

  const sortedReconciliations = useMemo(() => {
    return [...reconciliations].sort((a, b) => {
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
  }, [reconciliations, sortField, sortDirection]);

  const canEdit = userRole === 'admin' || userRole === 'accountant';
  const canDelete = userRole === 'admin';
  const canComplete = userRole === 'admin' || userRole === 'accountant';

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR');
  };

  return (
    <>
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
              placeholder="نام حساب بانکی..."
            />
            <FormControl size="small" style={{  minWidth: 150  }}>
              <InputLabel>وضعیت</span>
              <Select
                value={filters.status}
                label="وضعیت"
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <MenuItem value="">همه</Select.Option>
                <MenuItem value="draft">پیش‌نویس</Select.Option>
                <MenuItem value="completed">تکمیل شده</Select.Option>
              </Select>
            </div>
            <div>
            <Tooltip title="افزودن تطبیق جدید">
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
                <TableCell>حساب بانکی</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'period_start'}
                    direction={sortField === 'period_start' ? sortDirection : 'asc'}
                    onClick={() => handleSort('period_start')}
                  >
                    دوره شروع
                  </span>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'period_end'}
                    direction={sortField === 'period_end' ? sortDirection : 'asc'}
                    onClick={() => handleSort('period_end')}
                  >
                    دوره پایان
                  </span>
                </TableCell>
                <TableCell align="right">موجودی کتاب</TableCell>
                <TableCell align="right">موجودی بانک</TableCell>
                <TableCell align="right">تفاوت</TableCell>
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
                  <TableCell colSpan={9} align="center">
                    <Typography>در حال بارگذاری...</Typography>
                  </TableCell>
                </TableRow>
              ) : sortedReconciliations.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <Typography>هیچ تطبیقی یافت نشد</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                sortedReconciliations.map((reconciliation) => (
                  <TableRow key={reconciliation.id} hover>
                    <TableCell>
                      <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                        <AccountBalanceIcon style={{  fontSize: 16, color: 'text.secondary'  }} />
                        <Typography.Text>
                          {reconciliation.bank_account_name}
                        </Typography.Text>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {formatDate(reconciliation.period_start)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {formatDate(reconciliation.period_end)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(reconciliation.book_balance)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(reconciliation.bank_balance)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(reconciliation.difference)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={statusLabels[reconciliation.status]}
                        color={statusColors[reconciliation.status]}
                        size="small"
                        icon={reconciliation.status === 'completed' ? <CheckCircleIcon /> : <SyncIcon />}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {formatDate(reconciliation.created_at)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="center">
                      <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                        <Tooltip title="مشاهده جزئیات">
                          <Button type="text" size="small" onClick={() => handleViewDetails(reconciliation)}
                          >
                            <ViewIcon />
                          </Button>
                        </Tooltip>
                        {canEdit && reconciliation.status === 'draft' && (
                          <Tooltip title="ویرایش">
                            <Button type="text" size="small" onClick={() => onEdit(reconciliation)}
                            >
                              <EditIcon />
                            </Button>
                          </Tooltip>
                        )}
                        {canComplete && reconciliation.status === 'draft' && (
                          <Tooltip title="تکمیل تطبیق">
                            <Button type="text" size="small" onClick={() => onComplete(reconciliation)}
                            >
                              <CheckCircleIcon />
                            </Button>
                          </Tooltip>
                        )}
                        {canDelete && reconciliation.status === 'draft' && (
                          <Tooltip title="حذف">
                            <Button type="text" size="small" onClick={() => onDelete(reconciliation)}
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

      {/* Details Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          <Typography.Title level={4}>
            جزئیات تطبیق {selectedReconciliation?.bank_account_name}
          </Typography.Title>
        </div>
        <div>
          {selectedReconciliation && (
            <div>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    حساب بانکی
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedReconciliation.bank_account_name}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    وضعیت
                  </Typography>
                  <Tag
                    label={statusLabels[selectedReconciliation.status]}
                    color={statusColors[selectedReconciliation.status]}
                    style={{  mb: 2  }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    دوره شروع
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatDate(selectedReconciliation.period_start)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    دوره پایان
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatDate(selectedReconciliation.period_end)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    موجودی اولیه
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatCurrency(selectedReconciliation.opening_balance)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    موجودی نهایی
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatCurrency(selectedReconciliation.closing_balance)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    موجودی کتاب
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatCurrency(selectedReconciliation.book_balance)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    موجودی بانک
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatCurrency(selectedReconciliation.bank_balance)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    تفاوت
                  </Typography>
                  <Typography.Title level={4}>
                    {formatCurrency(selectedReconciliation.difference)}
                  </Typography.Title>
                </Col>
                {selectedReconciliation.status === 'completed' && (
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Alert severity="success">
                      این تطبیق در تاریخ {selectedReconciliation.completed_at && formatDate(selectedReconciliation.completed_at)} تکمیل شده است.
                    </Alert>
                  </Col>
                )}
                {Math.abs(selectedReconciliation.difference) >= 0.01 && (
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Alert severity="warning">
                      تفاوت موجود نیاز به بررسی دارد.
                    </Alert>
                  </Col>
                )}
              </Row>
            </div>
          )}
        </div>
        <div>
          <Button onClick={() => setDetailsDialogOpen(false)}>
            بستن
          </Button>
        </div>
      </Modal>
    </>
  );
}; 