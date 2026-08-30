import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Col, Divider, Row, Spin, Tabs, Tag, Tooltip, Typography } from 'antd';
import { BankOutlined as AccountBalanceIcon, DownloadOutlined as DownloadIcon, EyeOutlined, FallOutlined as TrendingDownIcon, FileTextOutlined as ReceiptIcon, ReloadOutlined as RefreshIcon, RiseOutlined as TrendingUpIcon, SyncOutlined as SyncIcon } from '@ant-design/icons';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { AccountingStats } from '../../../types/accounting';
import { accountingApi } from '../../../api/accounting';

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
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <div style={{  py: 3  }}>{children}</div>}
    </div>
  );
}

export const AccountingDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<AccountingStats | null>(null);
  const [cashFlowData, setCashFlowData] = useState<any[]>([]);
  const [balanceSheetData, setBalanceSheetData] = useState<any[]>([]);
  const [incomeData, setIncomeData] = useState<any[]>([]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load basic stats
      const statsResponse = await accountingApi.stats.getDashboard();
      setStats(statsResponse.data);

      // Load cash flow data (mock data for now)
      setCashFlowData([
        { month: 'فروردین', operating: 1200000, investing: -500000, financing: 300000 },
        { month: 'اردیبهشت', operating: 1400000, investing: -600000, financing: 400000 },
        { month: 'خرداد', operating: 1100000, investing: -400000, financing: 200000 },
        { month: 'تیر', operating: 1600000, investing: -700000, financing: 500000 },
        { month: 'مرداد', operating: 1300000, investing: -550000, financing: 350000 },
        { month: 'شهریور', operating: 1500000, investing: -650000, financing: 450000 },
      ]);

      // Load balance sheet data
      setBalanceSheetData([
        { category: 'دارایی‌های جاری', amount: 2500000, percentage: 40 },
        { category: 'دارایی‌های ثابت', amount: 3000000, percentage: 48 },
        { category: 'سایر دارایی‌ها', amount: 700000, percentage: 12 },
      ]);

      // Load income data
      setIncomeData([
        { month: 'فروردین', revenue: 2000000, expenses: 1500000, profit: 500000 },
        { month: 'اردیبهشت', revenue: 2200000, expenses: 1600000, profit: 600000 },
        { month: 'خرداد', revenue: 1800000, expenses: 1400000, profit: 400000 },
        { month: 'تیر', revenue: 2400000, expenses: 1700000, profit: 700000 },
        { month: 'مرداد', revenue: 2100000, expenses: 1550000, profit: 550000 },
        { month: 'شهریور', revenue: 2300000, expenses: 1650000, profit: 650000 },
      ]);

    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <div style={{  display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400  }}>
        <Spin />
      </div>
    );
  }

  if (!stats) {
    return (
      <Alert severity="error">
        خطا در بارگذاری اطلاعات داشبورد
      </Alert>
    );
  }

  return (
    <div style={{  p: 3  }}>
      {/* Header */}
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <Typography.Title level={2}>
          داشبورد حسابداری
        </Typography.Title>
        <div style={{  display: 'flex', gap: 1  }}>
          <Tooltip title="بارگذاری مجدد">
            <Button type="text" onClick={loadDashboardData} disabled={loading}>
              <RefreshIcon />
            </Button>
          </Tooltip>
          <Tooltip title="دانلود گزارش">
            <Button type="text">
              <DownloadIcon />
            </Button>
          </Tooltip>
        </div>
      </div>

      {/* KPI Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <AccountBalanceIcon style={{  fontSize: 32, color: 'primary.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {formatCurrency(stats.total_assets)}
                  </Typography.Title>
                  <Typography.Text>
                    کل دارایی‌ها
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
                    {formatCurrency(stats.net_income)}
                  </Typography.Title>
                  <Typography.Text>
                    سود خالص
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
                    {formatCurrency(stats.cash_balance)}
                  </Typography.Title>
                  <Typography.Text>
                    موجودی نقدی
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
                    {formatCurrency(stats.accounts_receivable)}
                  </Typography.Title>
                  <Typography.Text>
                    حساب‌های دریافتنی
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Financial Summary */}
      <Card style={{  p: 2, mb: 3  }}>
        <Typography.Title level={4}>
          خلاصه مالی
        </Typography.Title>
        <div style={{  display: 'flex', gap: 2, flexWrap: 'wrap'  }}>
          <Tag
            label={`بدهی‌ها: ${formatCurrency(stats.total_liabilities)}`}
            color="error"
            variant="outlined"
          />
          <Tag
            label={`سرمایه: ${formatCurrency(stats.total_equity)}`}
            color="primary"
            variant="outlined"
          />
          <Tag
            label={`حساب‌های پرداختنی: ${formatCurrency(stats.accounts_payable)}`}
            color="warning"
            variant="outlined"
          />
        </div>
      </Card>

      {/* Tabs */}
      <Card style={{  width: '100%'  }}>
        <div style={{  borderBottom: 1, borderColor: 'divider'  }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="dashboard tabs">
            <Tabs.TabPane label="جریان نقدی" />
            <Tabs.TabPane label="ترازنامه" />
            <Tabs.TabPane label="صورت سود و زیان" />
          </Tabs>
        </div>

        <TabPanel value={tabValue} index={0}>
          <div style={{  height: 400  }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={cashFlowData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <RechartsTooltip formatter={(value) => formatCurrency(Number(value))} />
                <Legend />
                <Line type="monotone" dataKey="operating" stroke="#8884d8" name="فعالیت‌های عملیاتی" />
                <Line type="monotone" dataKey="investing" stroke="#82ca9d" name="فعالیت‌های سرمایه‌گذاری" />
                <Line type="monotone" dataKey="financing" stroke="#ffc658" name="فعالیت‌های تأمین مالی" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <div style={{  height: 400  }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={balanceSheetData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="amount"
                >
                  {balanceSheetData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip formatter={(value) => formatCurrency(Number(value))} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <div style={{  height: 400  }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={incomeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <RechartsTooltip formatter={(value) => formatCurrency(Number(value))} />
                <Legend />
                <Bar dataKey="revenue" fill="#8884d8" name="درآمد" />
                <Bar dataKey="expenses" fill="#82ca9d" name="هزینه" />
                <Bar dataKey="profit" fill="#ffc658" name="سود" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </TabPanel>
      </Card>

      {/* Quick Actions */}
      <Card style={{  p: 2, mt: 3  }}>
        <Typography.Title level={4}>
          عملیات سریع
        </Typography.Title>
        <div style={{  display: 'flex', gap: 2, flexWrap: 'wrap'  }}>
          <Button variant="outlined" startIcon={<EyeOutlined />}>
            مشاهده ترازنامه
          </Button>
          <Button variant="outlined" startIcon={<ReceiptIcon />}>
            ثبت سند جدید
          </Button>
          <Button variant="outlined" startIcon={<SyncIcon />}>
            تطبیق بانکی
          </Button>
          <Button variant="outlined" startIcon={<DownloadIcon />}>
            دانلود گزارش
          </Button>
        </div>
      </Card>
    </div>
  );
}; 