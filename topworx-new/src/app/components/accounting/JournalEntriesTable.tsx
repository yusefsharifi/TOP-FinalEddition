import React, { useState, useMemo } from 'react';
import { Button, Card, Input, InputNumber, Modal, Pagination, Select, Table, Tag, Tooltip, Typography } from 'antd';
import { CloseOutlined as CancelIcon, DeleteOutlined as DeleteIcon, DownOutlined as ExpandMoreIcon, EditOutlined as EditIcon, EyeOutlined as ViewIcon, FileTextOutlined as ReceiptIcon, FormOutlined as PostIcon, PlusOutlined as AddIcon, UpOutlined as ExpandLessIcon } from '@ant-design/icons';
import { JournalEntry, JournalEntryLine, AccountingFilters } from '../../../types/accounting';

interface JournalEntriesTableProps {
  entries: JournalEntry[];
  loading?: boolean;
  onEdit: (entry: JournalEntry) => void;
  onDelete: (entry: JournalEntry) => void;
  onView: (entry: JournalEntry) => void;
  onAdd: () => void;
  onPost: (entry: JournalEntry) => void;
  onCancel: (entry: JournalEntry) => void;
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
  posted: 'success',
  cancelled: 'error',
} as const;

const statusLabels = {
  draft: 'پیش‌نویس',
  posted: 'ثبت شده',
  cancelled: 'لغو شده',
};

export const JournalEntriesTable: React.FC<JournalEntriesTableProps> = ({
  entries,
  loading = false,
  onEdit,
  onDelete,
  onView,
  onAdd,
  onPost,
  onCancel,
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
  const [sortField, setSortField] = useState<keyof JournalEntry>('date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [selectedEntry, setSelectedEntry] = useState<JournalEntry | null>(null);
  const [linesDialogOpen, setLinesDialogOpen] = useState(false);

  const handleSort = (field: keyof JournalEntry) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const handleFilterChange = (key: keyof AccountingFilters, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleRowExpand = (entryId: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(entryId)) {
      newExpanded.delete(entryId);
    } else {
      newExpanded.add(entryId);
    }
    setExpandedRows(newExpanded);
  };

  const handleViewLines = (entry: JournalEntry) => {
    setSelectedEntry(entry);
    setLinesDialogOpen(true);
  };

  const sortedEntries = useMemo(() => {
    return [...entries].sort((a, b) => {
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
  }, [entries, sortField, sortDirection]);

  const canEdit = userRole === 'admin' || userRole === 'accountant';
  const canDelete = userRole === 'admin';
  const canPost = userRole === 'admin' || userRole === 'accountant';

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
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
              placeholder="شماره سند، مرجع یا توضیحات..."
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
                <MenuItem value="posted">ثبت شده</Select.Option>
                <MenuItem value="cancelled">لغو شده</Select.Option>
              </Select>
            </div>
            <div>
            <Tooltip title="افزودن سند جدید">
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
                <TableCell padding="checkbox" />
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'entry_number'}
                    direction={sortField === 'entry_number' ? sortDirection : 'asc'}
                    onClick={() => handleSort('entry_number')}
                  >
                    شماره سند
                  </span>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'date'}
                    direction={sortField === 'date' ? sortDirection : 'asc'}
                    onClick={() => handleSort('date')}
                  >
                    تاریخ
                  </span>
                </TableCell>
                <TableCell>مرجع</TableCell>
                <TableCell>توضیحات</TableCell>
                <TableCell align="right">جمع بدهکار</TableCell>
                <TableCell align="right">جمع بستانکار</TableCell>
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
                  <TableCell colSpan={10} align="center">
                    <Typography>در حال بارگذاری...</Typography>
                  </TableCell>
                </TableRow>
              ) : sortedEntries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    <Typography>هیچ سندی یافت نشد</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                sortedEntries.map((entry) => (
                  <React.Fragment key={entry.id}>
                    <TableRow hover>
                      <TableCell padding="checkbox">
                        <Button type="text"
                          size="small"
                          onClick={() => handleRowExpand(entry.id)}
                        >
                          {expandedRows.has(entry.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </Button>
                      </TableCell>
                      <TableCell>
                        <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                          <ReceiptIcon style={{  fontSize: 16, color: 'text.secondary'  }} />
                          <Typography.Text>
                            {entry.entry_number}
                          </Typography.Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Typography.Text>
                          {new Date(entry.date).toLocaleDateString('fa-IR')}
                        </Typography.Text>
                      </TableCell>
                      <TableCell>
                        <Typography.Text>
                          {entry.reference}
                        </Typography.Text>
                      </TableCell>
                      <TableCell>
                        <Typography.Text>
                          {entry.description}
                        </Typography.Text>
                      </TableCell>
                      <TableCell align="right">
                        <Typography.Text>
                          {formatCurrency(entry.total_debit)}
                        </Typography.Text>
                      </TableCell>
                      <TableCell align="right">
                        <Typography.Text>
                          {formatCurrency(entry.total_credit)}
                        </Typography.Text>
                      </TableCell>
                      <TableCell>
                        <Tag
                          label={statusLabels[entry.status]}
                          color={statusColors[entry.status]}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography.Text>
                          {new Date(entry.created_at).toLocaleDateString('fa-IR')}
                        </Typography.Text>
                      </TableCell>
                      <TableCell align="center">
                        <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                          <Tooltip title="مشاهده">
                            <Button type="text" size="small" onClick={() => onView(entry)}
                            >
                              <ViewIcon />
                            </Button>
                          </Tooltip>
                          <Tooltip title="مشاهده ردیف‌ها">
                            <Button type="text" size="small" onClick={() => handleViewLines(entry)}
                            >
                              <ReceiptIcon />
                            </Button>
                          </Tooltip>
                          {canEdit && entry.status === 'draft' && (
                            <Tooltip title="ویرایش">
                              <Button type="text" size="small" onClick={() => onEdit(entry)}
                              >
                                <EditIcon />
                              </Button>
                            </Tooltip>
                          )}
                          {canPost && entry.status === 'draft' && (
                            <Tooltip title="ثبت سند">
                              <Button type="text" size="small" onClick={() => onPost(entry)}
                              >
                                <PostIcon />
                              </Button>
                            </Tooltip>
                          )}
                          {canPost && entry.status === 'posted' && (
                            <Tooltip title="لغو سند">
                              <Button type="text" size="small" onClick={() => onCancel(entry)}
                              >
                                <CancelIcon />
                              </Button>
                            </Tooltip>
                          )}
                          {canDelete && entry.status === 'draft' && (
                            <Tooltip title="حذف">
                              <Button type="text" size="small" onClick={() => onDelete(entry)}
                              >
                                <DeleteIcon />
                              </Button>
                            </Tooltip>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                    
                    {/* Expanded Row - Summary */}
                    <TableRow>
                      <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={10}>
                        <Collapse in={expandedRows.has(entry.id)} timeout="auto" unmountOnExit>
                          <div style={{  margin: 1  }}>
                            <Typography.Title level={4}>
                              خلاصه سند
                            </Typography.Title>
                            <div style={{  display: 'flex', gap: 4, mb: 2  }}>
                              <Typography.Text>
                                <strong>تاریخ ثبت:</strong> {entry.posted_at ? new Date(entry.posted_at).toLocaleDateString('fa-IR') : 'ثبت نشده'}
                              </Typography.Text>
                              <Typography.Text>
                                <strong>ثبت کننده:</strong> {entry.posted_by || 'ثبت نشده'}
                              </Typography.Text>
                              <Typography.Text>
                                <strong>ایجاد کننده:</strong> {entry.created_by}
                              </Typography.Text>
                            </div>
                            <Typography.Text>
                              {entry.description}
                            </Typography.Text>
                          </div>
                        </div>
                      </TableCell>
                    </TableRow>
                  </React.Fragment>
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

      {/* Lines Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          <Typography.Title level={4}>
            ردیف‌های سند {selectedEntry?.entry_number}
          </Typography.Title>
        </div>
        <div>
          {selectedEntry && (
            <div>
              <div style={{  mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1  }}>
                <Typography.Text>
                  <strong>تاریخ:</strong> {new Date(selectedEntry.date).toLocaleDateString('fa-IR')}
                </Typography.Text>
                <Typography.Text>
                  <strong>مرجع:</strong> {selectedEntry.reference}
                </Typography.Text>
                <Typography.Text>
                  <strong>توضیحات:</strong> {selectedEntry.description}
                </Typography.Text>
              </div>
              
              <Typography.Text>
                ردیف‌های این سند در حال حاضر در حال بارگذاری است...
              </Typography.Text>
            </div>
          )}
        </div>
        <div>
          <Button onClick={() => setLinesDialogOpen(false)}>
            بستن
          </Button>
        </div>
      </Modal>
    </>
  );
}; 