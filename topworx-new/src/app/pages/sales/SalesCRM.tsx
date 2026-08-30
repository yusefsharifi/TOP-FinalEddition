import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Col, Divider, Row, Spin, Tabs, Tag, Tooltip, Typography } from 'antd';
import { BankOutlined as BusinessIcon, BarChartOutlined as AssessmentIcon, DownloadOutlined as DownloadIcon, EyeOutlined as VisibilityIcon, FallOutlined as TrendingDownIcon, FileTextOutlined as ReceiptIcon, PlusOutlined as AddIcon, ReloadOutlined as RefreshIcon, RiseOutlined as TrendingUpIcon, TeamOutlined as PeopleIcon } from '@ant-design/icons';
import { CustomersTable } from '../../components/sales/CustomersTable';
import { LeadsTable } from '../../components/sales/LeadsTable';
import { SalesDashboard } from '../../components/sales/SalesDashboard';
import { OrderManagement } from '../../components/sales/OrderManagement';
import { ProductCatalog } from '../../components/sales/ProductCatalog';
import { SalesAnalytics } from '../../components/sales/SalesAnalytics';
import { 
  Customer, 
  Lead, 
  SalesStats,
  CustomerFilters,
  LeadFilters
} from '../../../types/sales';
import { salesApi } from '../../../api/sales';
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
      id={`sales-tabpanel-${index}`}
      aria-labelledby={`sales-tab-${index}`}
      {...other}
    >
      {value === index && <div style={{  py: 3  }}>{children}</div>}
    </div>
  );
}

export const SalesCRM: React.FC = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<SalesStats>({
    total_revenue: 0,
    total_opportunities: 0,
    total_leads: 0,
    total_customers: 0,
    conversion_rate: 0,
    average_deal_size: 0,
    sales_cycle_days: 0,
    win_rate: 0,
  });
  const [customerFilters, setCustomerFilters] = useState<CustomerFilters>({});
  const [leadFilters, setLeadFilters] = useState<LeadFilters>({});
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(25);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const response = await salesApi.customers.getAll({
        ...customerFilters,
        page: page + 1,
        limit,
      });
      setCustomers(response.data);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading customers:', error);
      showSnackbar('خطا در بارگذاری مشتریان', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadLeads = async () => {
    try {
      setLoading(true);
      const response = await salesApi.leads.getAll({
        ...leadFilters,
        page: page + 1,
        limit,
      });
      setLeads(response.data);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading leads:', error);
      showSnackbar('خطا در بارگذاری لیدها', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await salesApi.stats.getDashboard();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  useEffect(() => {
    if (tabValue === 0) {
      loadCustomers();
    } else if (tabValue === 1) {
      loadLeads();
    }
    loadStats();
  }, [tabValue, page, limit, customerFilters, leadFilters]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setPage(0);
  };

  const handleCustomerEdit = (customer: Customer) => {
    showSnackbar(`ویرایش مشتری: ${customer.name}`, 'info');
  };

  const handleCustomerDelete = async (customer: Customer) => {
    if (!confirm(`آیا از حذف مشتری "${customer.name}" اطمینان دارید؟`)) {
      return;
    }

    try {
      await salesApi.customers.delete(customer.id);
      showSnackbar('مشتری با موفقیت حذف شد', 'success');
      loadCustomers();
      loadStats();
    } catch (error) {
      console.error('Error deleting customer:', error);
      showSnackbar('خطا در حذف مشتری', 'error');
    }
  };

  const handleCustomerView = (customer: Customer) => {
    showSnackbar(`مشاهده مشتری: ${customer.name}`, 'info');
  };

  const handleCustomerAdd = () => {
    showSnackbar('افزودن مشتری جدید', 'info');
  };

  const handleLeadEdit = (lead: Lead) => {
    showSnackbar(`ویرایش لید: ${lead.name}`, 'info');
  };

  const handleLeadDelete = async (lead: Lead) => {
    if (!confirm(`آیا از حذف لید "${lead.name}" اطمینان دارید؟`)) {
      return;
    }

    try {
      await salesApi.leads.delete(lead.id);
      showSnackbar('لید با موفقیت حذف شد', 'success');
      loadLeads();
      loadStats();
    } catch (error) {
      console.error('Error deleting lead:', error);
      showSnackbar('خطا در حذف لید', 'error');
    }
  };

  const handleLeadView = (lead: Lead) => {
    showSnackbar(`مشاهده لید: ${lead.name}`, 'info');
  };

  const handleLeadAdd = () => {
    showSnackbar('افزودن لید جدید', 'info');
  };

  const handleLeadConvert = (lead: Lead) => {
    showSnackbar(`تبدیل لید به مشتری: ${lead.name}`, 'info');
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
      loadCustomers();
    } else if (tabValue === 1) {
      loadLeads();
    }
    loadStats();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  return (
    <div style={{  p: 3  }}>
      {/* Header */}
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
          <BusinessIcon style={{  fontSize: 32, color: 'primary.main'  }} />
          <div>
            <Typography.Title level={2}>
              مدیریت فروش و CRM
            </Typography.Title>
            <Typography.Text>
              مدیریت مشتریان، لیدها و فرصت‌های فروش
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
            onClick={tabValue === 0 ? handleCustomerAdd : handleLeadAdd}
            disabled={loading}
          >
            {tabValue === 0 ? 'افزودن مشتری' : 'افزودن لید'}
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <PeopleIcon style={{  fontSize: 32, color: 'primary.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.total_customers}
                  </Typography.Title>
                  <Typography.Text>
                    کل مشتریان
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
                    {formatCurrency(stats.total_revenue)}
                  </Typography.Title>
                  <Typography.Text>
                    کل درآمد
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
                <AssessmentIcon style={{  fontSize: 32, color: 'info.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.total_opportunities}
                  </Typography.Title>
                  <Typography.Text>
                    فرصت‌های فروش
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
                <ReceiptIcon style={{  fontSize: 32, color: 'warning.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.total_leads}
                  </Typography.Title>
                  <Typography.Text>
                    کل لیدها
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
      </Col>

      {/* Performance Summary */}
      <Card style={{  p: 2, mb: 3  }}>
        <Typography.Title level={4}>
          خلاصه عملکرد
        </Typography.Title>
        <div style={{  display: 'flex', gap: 2, flexWrap: 'wrap'  }}>
          <Tag
            label={`نرخ تبدیل: ${formatPercentage(stats.conversion_rate)}`}
            color="success"
            variant="outlined"
          />
          <Tag
            label={`نرخ موفقیت: ${formatPercentage(stats.win_rate)}`}
            color="primary"
            variant="outlined"
          />
          <Tag
            label={`متوسط اندازه معامله: ${formatCurrency(stats.average_deal_size)}`}
            color="info"
            variant="outlined"
          />
          <Tag
            label={`چرخه فروش: ${stats.sales_cycle_days} روز`}
            color="warning"
            variant="outlined"
          />
        </div>
      </Card>

      {/* Tabs */}
      <Card style={{  width: '100%'  }}>
        <div style={{  borderBottom: 1, borderColor: 'divider'  }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="sales tabs">
            <Tab label="داشبورد" />
            <Tab label="مشتریان" />
            <Tab label="لیدها" />
            <Tab label="سفارشات" />
            <Tab label="محصولات" />
            <Tab label="تحلیل" />
          </Tabs>
        </div>

        <TabPanel value={tabValue} index={0}>
          <SalesDashboard />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <CustomersTable
            customers={customers}
            loading={loading}
            onEdit={handleCustomerEdit}
            onDelete={handleCustomerDelete}
            onView={handleCustomerView}
            onAdd={handleCustomerAdd}
            onFiltersChange={setCustomerFilters}
            total={total}
            page={page}
            limit={limit}
            onPageChange={handlePageChange}
            onLimitChange={handleLimitChange}
            userRole={user?.role}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <LeadsTable
            leads={leads}
            loading={loading}
            onEdit={handleLeadEdit}
            onDelete={handleLeadDelete}
            onView={handleLeadView}
            onAdd={handleLeadAdd}
            onConvert={handleLeadConvert}
            onFiltersChange={setLeadFilters}
            total={total}
            page={page}
            limit={limit}
            onPageChange={handlePageChange}
            onLimitChange={handleLimitChange}
            userRole={user?.role}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <OrderManagement />
        </TabPanel>

        <TabPanel value={tabValue} index={4}>
          <ProductCatalog />
        </TabPanel>

        <TabPanel value={tabValue} index={5}>
          <SalesAnalytics />
        </TabPanel>
      </Card>

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