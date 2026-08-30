import React, { useState, useMemo } from 'react';
import { Alert, Button, Card, Input, InputNumber, Modal, Pagination, Select, Table, Tag, Tooltip, Typography } from 'antd';
import { CheckCircleOutlined as CheckCircleIcon, CloseOutlined as CancelIcon, DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, EyeOutlined as ViewIcon, FallOutlined as TrendingDownIcon, FileTextOutlined as ReceiptIcon, PlusOutlined as AddIcon, RiseOutlined as TrendingUpIcon, SyncOutlined as SyncIcon } from '@ant-design/icons';
import { BankTransaction, BankTransactionFilters } from '../../../types/accounting';

interface BankTransactionsTableProps {
  transactions: BankTransaction[];
  loading?: boolean;
  onEdit: (transaction: BankTransaction) => void;
  onDelete: (transaction: BankTransaction) => void;
  onView: (transaction: BankTransaction) => void;
  onAdd: () => void;
  onReconcile: (transaction: BankTransaction) => void;
  onFiltersChange: (filters: BankTransactionFilters) => void;
  total: number;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
  userRole?: string;
}

const transactionTypeColors = {
  deposit: 'success',
  withdrawal: 'error',
  transfer: 'info',
  fee: 'warning',
  interest: 'primary',
} as const;

const transactionTypeLabels = {
  deposit: 'واریز',
  withdrawal: 'برداشت',
  transfer: 'انتقال',
  fee: 'کارمزد',
  interest: 'سود',
};

const statusColors = {
  pending: 'warning',
  completed: 'success',
  cancelled: 'error',
} as const;

const statusLabels = {
  pending: 'معلق',
  completed: 'تکمیل شده',
  cancelled: 'لغو شده',
};

export const BankTransactionsTable: React.FC<BankTransactionsTableProps> = ({
  transactions,
  loading = false,
  onEdit,
  onDelete,
  onView,
  onAdd,
  onReconcile,
  onFiltersChange,
  total,
  page,
  limit,
  onPageChange,
  onLimitChange,
  userRole,
}) => {
  const [filters, setFilters] = useState<BankTransactionFilters>({
    bank_account_id: '',
    type: '',
    status: '',
    reconciled: undefined,
    search: '',
  });
  const [sortField, setSortField] = useState<keyof BankTransaction>('transaction_date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [selectedTransaction, setSelectedTransaction] = useState<BankTransaction | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);

  const handleSort = (field: keyof BankTransaction) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const handleFilterChange = (key: keyof BankTransactionFilters, value: string | boolean | undefined) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleViewDetails = (transaction: BankTransaction) => {
    setSelectedTransaction(transaction);
    setDetailsDialogOpen(true);
  };

  const sortedTransactions = useMemo(() => {
    return [...transactions].sort((a, b) => {
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
  }, [transactions, sortField, sortDirection]);

  const canEdit = userRole === 'admin' || userRole === 'accountant';
  const canDelete = userRole === 'admin';
  const canReconcile = userRole === 'admin' || userRole === 'accountant';

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
          <div style={{  display: 'flex', gap: 2, alignItems: 'center', mb: 2, flexWrap: 'wrap'  }}>
            <Input
              label="جستجو"
              size="small"
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              style={{  minWidth: 200  }}
              placeholder="مرجع، توضیحات یا شماره حساب..."
            />
            <FormControl size="small" style={{  minWidth: 150  }}>
              <InputLabel>نوع تراکنش</span>
              <Select
                value={filters.type}
                label="نوع تراکنش"
                onChange={(e) => handleFilterChange('type', e.target.value)}
              >
                <MenuItem value="">همه</Select.Option>
                <MenuItem value="deposit">واریز</Select.Option>
                <MenuItem value="withdrawal">برداشت</Select.Option>
                <MenuItem value="transfer">انتقال</Select.Option>
                <MenuItem value="fee">کارمزد</Select.Option>
                <MenuItem value="interest">سود</Select.Option>
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
                <MenuItem value="pending">معلق</Select.Option>
                <MenuItem value="completed">تکمیل شده</Select.Option>
                <MenuItem value="cancelled">لغو شده</Select.Option>
              </Select>
            </div>
            <FormControl size="small" style={{  minWidth: 150  }}>
              <InputLabel>تطبیق</span>
              <Select
                value={filters.reconciled === undefined ? '' : filters.reconciled ? 'true' : 'false'}
                label="تطبیق"
                onChange={(e) => {
                  const value = e.target.value;
                  handleFilterChange('reconciled', value === '' ? undefined : value === 'true');
                }}
              >
                <MenuItem value="">همه</Select.Option>
                <MenuItem value="true">تطبیق شده</Select.Option>
                <MenuItem value="false">تطبیق نشده</Select.Option>
              </Select>
            </div>
            <div>
            <Tooltip title="افزودن تراکنش جدید">
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
                    active={sortField === 'transaction_date'}
                    direction={sortField === 'transaction_date' ? sortDirection : 'asc'}
                    onClick={() => handleSort('transaction_date')}
                  >
                    تاریخ تراکنش
                  </span>
                </TableCell>
                <TableCell>حساب بانکی</TableCell>
                <TableCell>مرجع</TableCell>
                <TableCell>توضیحات</TableCell>
                <TableCell>نوع</TableCell>
                <TableCell align="right">مبلغ</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>تطبیق</TableCell>
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
              ) : sortedTransactions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    <Typography>هیچ تراکنشی یافت نشد</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                sortedTransactions.map((transaction) => (
                  <TableRow key={transaction.id} hover>
                    <TableCell>
                      <Typography.Text>
                        {formatDate(transaction.transaction_date)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {transaction.bank_account_name}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {transaction.reference}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {transaction.description}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={transactionTypeLabels[transaction.type]}
                        color={transactionTypeColors[transaction.type]}
                        size="small"
                        icon={
                          transaction.type === 'deposit' ? <TrendingUpIcon /> :
                          transaction.type === 'withdrawal' ? <TrendingDownIcon /> :
                          <ReceiptIcon />
                        }
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(transaction.amount)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={statusLabels[transaction.status]}
                        color={statusColors[transaction.status]}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={transaction.reconciled ? 'تطبیق شده' : 'تطبیق نشده'}
                        color={transaction.reconciled ? 'success' : 'default'}
                        size="small"
                        icon={transaction.reconciled ? <CheckCircleIcon /> : <SyncIcon />}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {formatDate(transaction.created_at)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="center">
                      <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                        <Tooltip title="مشاهده جزئیات">
                          <Button type="text" size="small" onClick={() => handleViewDetails(transaction)}
                          >
                            <ViewIcon />
                          </Button>
                        </Tooltip>
                        {canEdit && transaction.status === 'pending' && (
                          <Tooltip title="ویرایش">
                            <Button type="text" size="small" onClick={() => onEdit(transaction)}
                            >
                              <EditIcon />
                            </Button>
                          </Tooltip>
                        )}
                        {canReconcile && !transaction.reconciled && (
                          <Tooltip title="تطبیق">
                            <Button type="text" size="small" onClick={() => onReconcile(transaction)}
                            >
                              <SyncIcon />
                            </Button>
                          </Tooltip>
                        )}
                        {canDelete && transaction.status === 'pending' && (
                          <Tooltip title="حذف">
                            <Button type="text" size="small" onClick={() => onDelete(transaction)}
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
            جزئیات تراکنش {selectedTransaction?.reference}
          </Typography.Title>
        </div>
        <div>
          {selectedTransaction && (
            <div>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    حساب بانکی
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedTransaction.bank_account_name}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    تاریخ تراکنش
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatDate(selectedTransaction.transaction_date)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    تاریخ ارزش
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatDate(selectedTransaction.value_date)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    نوع تراکنش
                  </Typography>
                  <Tag
                    label={transactionTypeLabels[selectedTransaction.type]}
                    color={transactionTypeColors[selectedTransaction.type]}
                    style={{  mb: 2  }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    مبلغ
                  </Typography>
                  <Typography.Title level={4}>
                    {formatCurrency(selectedTransaction.amount)}
                  </Typography.Title>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    وضعیت
                  </Typography>
                  <Tag
                    label={statusLabels[selectedTransaction.status]}
                    color={statusColors[selectedTransaction.status]}
                    style={{  mb: 2  }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    توضیحات
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedTransaction.description}
                  </Typography>
                </Col>
                {selectedTransaction.reconciled && (
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Alert severity="success">
                      این تراکنش در تاریخ {selectedTransaction.reconciled_at && formatDate(selectedTransaction.reconciled_at)} تطبیق شده است.
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