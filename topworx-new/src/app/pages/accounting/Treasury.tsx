import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Col, Divider, Row, Spin, Tabs, Tag, Tooltip, Typography } from 'antd';
import { ApartmentOutlined as AccountTreeIcon, BankOutlined as AccountBalanceIcon, FallOutlined as TrendingDownIcon, FileTextOutlined as ReceiptIcon, PlusOutlined as AddIcon, ReloadOutlined as RefreshIcon, RiseOutlined as TrendingUpIcon, SyncOutlined as SyncIcon, WalletOutlined as WalletIcon } from '@ant-design/icons';
import { BankAccountsTable } from '../../components/accounting/BankAccountsTable';
import { BankTransactionsTable } from '../../components/accounting/BankTransactionsTable';
import { BankReconciliationTable } from '../../components/accounting/BankReconciliationTable';
import { BankAccountForm } from '../../components/accounting/BankAccountForm';
import { BankTransactionForm } from '../../components/accounting/BankTransactionForm';
import { 
  BankAccount, 
  BankTransaction, 
  BankReconciliation, 
  BankAccountFormData, 
  BankTransactionFormData,
  AccountingStats 
} from '../../../types/accounting';
import { accountingApi } from '../../../api/accounting';
import { useAuth } from '../../../core/auth/AuthContext';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`treasury-tabpanel-${index}`}
      aria-labelledby={`treasury-tab-${index}`}
      {...other}
    >
      {value === index && <div style={{  py: 3  }}>{children}</div>}
    </div>
  );
}

export const TreasuryPage: React.FC = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [transactions, setTransactions] = useState<BankTransaction[]>([]);
  const [reconciliations, setReconciliations] = useState<BankReconciliation[]>([]);
  const [loading, setLoading] = useState(false);
  const [accountFormOpen, setAccountFormOpen] = useState(false);
  const [transactionFormOpen, setTransactionFormOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<BankAccount | null>(null);
  const [selectedTransaction, setSelectedTransaction] = useState<BankTransaction | null>(null);
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
    totalBalance: number;
    totalDeposits: number;
    totalWithdrawals: number;
    pendingTransactions: number;
    reconciledTransactions: number;
  }>({
    totalAccounts: 0,
    activeAccounts: 0,
    totalBalance: 0,
    totalDeposits: 0,
    totalWithdrawals: 0,
    pendingTransactions: 0,
    reconciledTransactions: 0,
  });

  const loadBankAccounts = async () => {
    try {
      setLoading(true);
      const response = await accountingApi.bankAccounts.getAll({
        page: page + 1,
        limit,
      });
      setBankAccounts(response.data);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading bank accounts:', error);
      showSnackbar('خطا در بارگذاری حساب‌های بانکی', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const response = await accountingApi.bankTransactions.getAll({
        page: page + 1,
        limit,
      });
      setTransactions(response.data);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading transactions:', error);
      showSnackbar('خطا در بارگذاری تراکنش‌ها', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadReconciliations = async () => {
    try {
      setLoading(true);
      const response = await accountingApi.bankReconciliation.getAll({
        page: page + 1,
        limit,
      });
      setReconciliations(response.data);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading reconciliations:', error);
      showSnackbar('خطا در بارگذاری تطبیق‌ها', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const accountsResponse = await accountingApi.bankAccounts.getAll({ limit: 1000 });
      const transactionsResponse = await accountingApi.bankTransactions.getAll({ limit: 1000 });
      
      const accounts = accountsResponse.data;
      const allTransactions = transactionsResponse.data;
      
      const totalBalance = accounts.reduce((sum, acc) => sum + acc.current_balance, 0);
      const totalDeposits = allTransactions
        .filter(t => t.type === 'deposit' && t.status === 'completed')
        .reduce((sum, t) => sum + t.amount, 0);
      const totalWithdrawals = allTransactions
        .filter(t => t.type === 'withdrawal' && t.status === 'completed')
        .reduce((sum, t) => sum + t.amount, 0);
      
      setStats({
        totalAccounts: accounts.length,
        activeAccounts: accounts.filter(acc => acc.is_active).length,
        totalBalance,
        totalDeposits,
        totalWithdrawals,
        pendingTransactions: allTransactions.filter(t => t.status === 'pending').length,
        reconciledTransactions: allTransactions.filter(t => t.reconciled).length,
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  useEffect(() => {
    if (tabValue === 0) {
      loadBankAccounts();
    } else if (tabValue === 1) {
      loadTransactions();
    } else if (tabValue === 2) {
      loadReconciliations();
    }
    loadStats();
  }, [tabValue, page, limit]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setPage(0);
  };

  const handleAddAccount = () => {
    setSelectedAccount(null);
    setAccountFormOpen(true);
  };

  const handleEditAccount = (account: BankAccount) => {
    setSelectedAccount(account);
    setAccountFormOpen(true);
  };

  const handleDeleteAccount = async (account: BankAccount) => {
    if (!confirm(`آیا از حذف حساب بانکی "${account.name}" اطمینان دارید؟`)) {
      return;
    }

    try {
      await accountingApi.bankAccounts.delete(account.id);
      showSnackbar('حساب بانکی با موفقیت حذف شد', 'success');
      loadBankAccounts();
      loadStats();
    } catch (error) {
      console.error('Error deleting bank account:', error);
      showSnackbar('خطا در حذف حساب بانکی', 'error');
    }
  };

  const handleAddTransaction = () => {
    setSelectedTransaction(null);
    setTransactionFormOpen(true);
  };

  const handleEditTransaction = (transaction: BankTransaction) => {
    setSelectedTransaction(transaction);
    setTransactionFormOpen(true);
  };

  const handleDeleteTransaction = async (transaction: BankTransaction) => {
    if (!confirm(`آیا از حذف تراکنش "${transaction.reference}" اطمینان دارید؟`)) {
      return;
    }

    try {
      await accountingApi.bankTransactions.delete(transaction.id);
      showSnackbar('تراکنش با موفقیت حذف شد', 'success');
      loadTransactions();
      loadStats();
    } catch (error) {
      console.error('Error deleting transaction:', error);
      showSnackbar('خطا در حذف تراکنش', 'error');
    }
  };

  const handleSubmitAccount = async (data: BankAccountFormData) => {
    try {
      if (selectedAccount) {
        await accountingApi.bankAccounts.update(selectedAccount.id, data);
        showSnackbar('حساب بانکی با موفقیت ویرایش شد', 'success');
      } else {
        await accountingApi.bankAccounts.create(data);
        showSnackbar('حساب بانکی با موفقیت ایجاد شد', 'success');
      }
      setAccountFormOpen(false);
      loadBankAccounts();
      loadStats();
    } catch (error) {
      console.error('Error saving bank account:', error);
      showSnackbar('خطا در ذخیره حساب بانکی', 'error');
    }
  };

  const handleSubmitTransaction = async (data: BankTransactionFormData) => {
    try {
      if (selectedTransaction) {
        await accountingApi.bankTransactions.update(selectedTransaction.id, data);
        showSnackbar('تراکنش با موفقیت ویرایش شد', 'success');
      } else {
        await accountingApi.bankTransactions.create(data);
        showSnackbar('تراکنش با موفقیت ایجاد شد', 'success');
      }
      setTransactionFormOpen(false);
      loadTransactions();
      loadStats();
    } catch (error) {
      console.error('Error saving transaction:', error);
      showSnackbar('خطا در ذخیره تراکنش', 'error');
    }
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
    if (tabValue === 0) {
      loadBankAccounts();
    } else if (tabValue === 1) {
      loadTransactions();
    } else if (tabValue === 2) {
      loadReconciliations();
    }
    loadStats();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  return (
    <div style={{  p: 3  }}>
      {/* Header */}
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
          <WalletIcon style={{  fontSize: 32, color: 'primary.main'  }} />
          <div>
            <Typography.Title level={2}>
              مدیریت خزانه‌داری
            </Typography.Title>
            <Typography.Text>
              مدیریت حساب‌های بانکی، تراکنش‌ها و تطبیق بانکی
            </Typography.Text>
          </div>
        </div>
        <div style={{  display: 'flex', gap: 1  }}>
          <Tooltip title="بارگذاری مجدد">
            <Button type="text" onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </Button>
          </Tooltip>
          {tabValue === 0 && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddAccount}
              disabled={loading}
            >
              افزودن حساب بانکی
            </Button>
          )}
          {tabValue === 1 && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddTransaction}
              disabled={loading}
            >
              افزودن تراکنش
            </Button>
          )}
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
                    کل حساب‌های بانکی
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
                    {formatCurrency(stats.totalBalance)}
                  </Typography.Title>
                  <Typography.Text>
                    موجودی کل
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
                <ReceiptIcon style={{  fontSize: 32, color: 'info.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.pendingTransactions}
                  </Typography.Title>
                  <Typography.Text>
                    تراکنش‌های معلق
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
                <SyncIcon style={{  fontSize: 32, color: 'warning.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.reconciledTransactions}
                  </Typography.Title>
                  <Typography.Text>
                    تراکنش‌های تطبیق شده
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Cash Flow Summary */}
      <Card style={{  p: 2, mb: 3  }}>
        <Typography.Title level={4}>
          خلاصه جریان نقدی
        </Typography.Title>
        <div style={{  display: 'flex', gap: 2, flexWrap: 'wrap'  }}>
          <Tag
            label={`واریز: ${formatCurrency(stats.totalDeposits)}`}
            color="success"
            variant="outlined"
          />
          <Tag
            label={`برداشت: ${formatCurrency(stats.totalWithdrawals)}`}
            color="error"
            variant="outlined"
          />
          <Tag
            label={`خالص: ${formatCurrency(stats.totalDeposits - stats.totalWithdrawals)}`}
            color={stats.totalDeposits - stats.totalWithdrawals >= 0 ? 'success' : 'error'}
            variant="outlined"
          />
        </div>
      </Card>

      {/* Tabs */}
      <Card style={{  width: '100%'  }}>
        <div style={{  borderBottom: 1, borderColor: 'divider'  }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="treasury tabs">
            <Tab label="حساب‌های بانکی" />
            <Tab label="تراکنش‌ها" />
            <Tab label="تطبیق بانکی" />
          </Tabs>
        </div>

        <TabPanel value={tabValue} index={0}>
          <BankAccountsTable
            accounts={bankAccounts}
            loading={loading}
            onEdit={handleEditAccount}
            onDelete={handleDeleteAccount}
            onView={() => {}}
            onAdd={handleAddAccount}
            onFiltersChange={() => {}}
            total={total}
            page={page}
            limit={limit}
            onPageChange={handlePageChange}
            onLimitChange={handleLimitChange}
            userRole={user?.role}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <BankTransactionsTable
            transactions={transactions}
            loading={loading}
            onEdit={handleEditTransaction}
            onDelete={handleDeleteTransaction}
            onView={() => {}}
            onAdd={handleAddTransaction}
            onReconcile={() => {}}
            onFiltersChange={() => {}}
            total={total}
            page={page}
            limit={limit}
            onPageChange={handlePageChange}
            onLimitChange={handleLimitChange}
            userRole={user?.role}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <BankReconciliationTable
            reconciliations={reconciliations}
            loading={loading}
            onEdit={() => {}}
            onDelete={() => {}}
            onView={() => {}}
            onAdd={() => {}}
            onComplete={() => {}}
            onFiltersChange={() => {}}
            total={total}
            page={page}
            limit={limit}
            onPageChange={handlePageChange}
            onLimitChange={handleLimitChange}
            userRole={user?.role}
          />
        </TabPanel>
      </Card>

      {/* Form Dialogs */}
      <BankAccountForm
        open={accountFormOpen}
        onClose={() => setAccountFormOpen(false)}
        onSubmit={handleSubmitAccount}
        account={selectedAccount}
        loading={loading}
      />

      <BankTransactionForm
        open={transactionFormOpen}
        onClose={() => setTransactionFormOpen(false)}
        onSubmit={handleSubmitTransaction}
        transaction={selectedTransaction}
        bankAccounts={bankAccounts}
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