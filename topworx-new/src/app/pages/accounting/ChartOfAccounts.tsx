import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Col, Row, Spin, Tag, Tooltip, Typography } from 'antd';
import { ApartmentOutlined as AccountTreeIcon, BankOutlined as AccountBalanceIcon, FallOutlined as TrendingDownIcon, PlusOutlined as AddIcon, ReloadOutlined as RefreshIcon, RiseOutlined as TrendingUpIcon } from '@ant-design/icons';
import { ChartOfAccountsTable } from '../../components/accounting/ChartOfAccountsTable';
import { ChartOfAccountsForm } from '../../components/accounting/ChartOfAccountsForm';
import { ChartOfAccountsFormData, ChartOfAccounts, AccountingFilters, AccountingStats } from '../../../types/accounting';
import { accountingApi } from '../../../api/accounting';
import { useAuth } from '../../../core/auth/AuthContext';

export const ChartOfAccountsPage: React.FC = () => {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<ChartOfAccounts[]>([]);
  const [parentAccounts, setParentAccounts] = useState<ChartOfAccounts[]>([]);
  const [loading, setLoading] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<ChartOfAccounts | null>(null);
  const [filters, setFilters] = useState<AccountingFilters>({});
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(25);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });
  const [stats, setStats] = useState<{
    totalAccounts: number;
    activeAccounts: number;
    assetAccounts: number;
    liabilityAccounts: number;
    equityAccounts: number;
    revenueAccounts: number;
    expenseAccounts: number;
  }>({
    totalAccounts: 0,
    activeAccounts: 0,
    assetAccounts: 0,
    liabilityAccounts: 0,
    equityAccounts: 0,
    revenueAccounts: 0,
    expenseAccounts: 0,
  });

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const response = await accountingApi.chartOfAccounts.getAll({
        ...filters,
        page: page + 1,
        limit,
      });
      setAccounts(response.data);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading accounts:', error);
      showSnackbar('خطا در بارگذاری حساب‌ها', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadParentAccounts = async () => {
    try {
      const response = await accountingApi.chartOfAccounts.getTree();
      setParentAccounts(response.data || []);
    } catch (error) {
      console.error('Error loading parent accounts:', error);
    }
  };

  const loadStats = async () => {
    try {
      const allAccounts = await accountingApi.chartOfAccounts.getAll({ limit: 1000 });
      const accountsData = allAccounts.data;
      
      setStats({
        totalAccounts: accountsData.length,
        activeAccounts: accountsData.filter(acc => acc.is_active).length,
        assetAccounts: accountsData.filter(acc => acc.type === 'asset').length,
        liabilityAccounts: accountsData.filter(acc => acc.type === 'liability').length,
        equityAccounts: accountsData.filter(acc => acc.type === 'equity').length,
        revenueAccounts: accountsData.filter(acc => acc.type === 'revenue').length,
        expenseAccounts: accountsData.filter(acc => acc.type === 'expense').length,
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  useEffect(() => {
    loadAccounts();
    loadParentAccounts();
    loadStats();
  }, [filters, page, limit]);

  const handleAdd = () => {
    setSelectedAccount(null);
    setFormOpen(true);
  };

  const handleEdit = (account: ChartOfAccounts) => {
    setSelectedAccount(account);
    setFormOpen(true);
  };

  const handleDelete = async (account: ChartOfAccounts) => {
    if (!confirm(`آیا از حذف حساب "${account.name}" اطمینان دارید؟`)) {
      return;
    }

    try {
      await accountingApi.chartOfAccounts.delete(account.id);
      showSnackbar('حساب با موفقیت حذف شد', 'success');
      loadAccounts();
      loadStats();
    } catch (error) {
      console.error('Error deleting account:', error);
      showSnackbar('خطا در حذف حساب', 'error');
    }
  };

  const handleView = (account: ChartOfAccounts) => {
    // TODO: Implement detailed view
    showSnackbar(`مشاهده حساب: ${account.name}`, 'info');
  };

  const handleSubmit = async (data: ChartOfAccountsFormData) => {
    try {
      if (selectedAccount) {
        await accountingApi.chartOfAccounts.update(selectedAccount.id, data);
        showSnackbar('حساب با موفقیت ویرایش شد', 'success');
      } else {
        await accountingApi.chartOfAccounts.create(data);
        showSnackbar('حساب با موفقیت ایجاد شد', 'success');
      }
      setFormOpen(false);
      loadAccounts();
      loadParentAccounts();
      loadStats();
    } catch (error) {
      console.error('Error saving account:', error);
      showSnackbar('خطا در ذخیره حساب', 'error');
    }
  };

  const handleFiltersChange = (newFilters: AccountingFilters) => {
    setFilters(newFilters);
    setPage(0);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleLimitChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(0);
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleRefresh = () => {
    loadAccounts();
    loadStats();
  };

  return (
    <div style={{  p: 3  }}>
      {/* Header */}
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
          <AccountTreeIcon style={{  fontSize: 32, color: 'primary.main'  }} />
          <div>
            <Typography.Title level={2}>
              حساب‌های کل
            </Typography.Title>
            <Typography.Text>
              مدیریت ساختار حساب‌های کل و کدینگ حسابداری
            </Typography.Text>
          </div>
        </div>
        <div style={{  display: 'flex', gap: 1  }}>
          <Tooltip title="بارگذاری مجدد">
            <Button type="text" onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </Button>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAdd}
            disabled={loading}
          >
            افزودن حساب
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <AccountBalanceIcon style={{  fontSize: 32, color: 'primary.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.totalAccounts}
                  </Typography.Title>
                  <Typography.Text>
                    کل حساب‌ها
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <TrendingUpIcon style={{  fontSize: 32, color: 'success.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.activeAccounts}
                  </Typography.Title>
                  <Typography.Text>
                    حساب‌های فعال
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <AccountTreeIcon style={{  fontSize: 32, color: 'info.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.assetAccounts}
                  </Typography.Title>
                  <Typography.Text>
                    حساب‌های دارایی
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <TrendingDownIcon style={{  fontSize: 32, color: 'warning.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.liabilityAccounts}
                  </Typography.Title>
                  <Typography.Text>
                    حساب‌های بدهی
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Account Type Summary */}
      <Card style={{  p: 2, mb: 3  }}>
        <Typography.Title level={4}>
          خلاصه انواع حساب
        </Typography.Title>
        <div style={{  display: 'flex', gap: 2, flexWrap: 'wrap'  }}>
          <Tag
            label={`سرمایه: ${stats.equityAccounts}`}
            color="primary"
            variant="outlined"
          />
          <Tag
            label={`درآمد: ${stats.revenueAccounts}`}
            color="success"
            variant="outlined"
          />
          <Tag
            label={`هزینه: ${stats.expenseAccounts}`}
            color="error"
            variant="outlined"
          />
        </div>
      </Card>

      {/* Main Table */}
      <Card style={{  width: '100%'  }}>
        <ChartOfAccountsTable
          accounts={accounts}
          loading={loading}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={handleView}
          onAdd={handleAdd}
          onFiltersChange={handleFiltersChange}
          total={total}
          page={page}
          limit={limit}
          onPageChange={handlePageChange}
          onLimitChange={handleLimitChange}
          userRole={user?.role}
        />
      </Card>

      {/* Form Dialog */}
      <ChartOfAccountsForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleSubmit}
        account={selectedAccount}
        parentAccounts={parentAccounts}
        loading={loading}
      />

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          style={{  width: '100%'  }}
        >
          {snackbar.message}
        </Alert>
      </div>
    </div>
  );
}; 