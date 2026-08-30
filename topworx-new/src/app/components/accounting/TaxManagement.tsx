import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Col, Input, InputNumber, Modal, Row, Select, Spin, Table, Tabs, Tag, Tooltip, Typography } from 'antd';
import { CreditCardOutlined as PaymentIcon, DeleteOutlined as DeleteIcon, DownloadOutlined as DownloadIcon, EditOutlined as EditIcon, EyeOutlined as VisibilityIcon, FallOutlined as TrendingDownIcon, FileTextOutlined as ReceiptIcon, PlusOutlined as AddIcon, ReloadOutlined as RefreshIcon, RiseOutlined as TrendingUpIcon, WarningOutlined as WarningIcon } from '@ant-design/icons';
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
import { TaxCode, TaxTransaction } from '../../../types/accounting';
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
      id={`tax-tabpanel-${index}`}
      aria-labelledby={`tax-tab-${index}`}
      {...other}
    >
      {value === index && <div style={{  py: 3  }}>{children}</div>}
    </div>
  );
}

export const TaxManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [taxCodes, setTaxCodes] = useState<TaxCode[]>([]);
  const [taxTransactions, setTaxTransactions] = useState<TaxTransaction[]>([]);
  const [selectedTaxCode, setSelectedTaxCode] = useState<TaxCode | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [taxData, setTaxData] = useState<any[]>([]);
  const [taxTypeData, setTaxTypeData] = useState<any[]>([]);

  const loadTaxData = async () => {
    try {
      setLoading(true);
      
      // Load tax codes
      const codesResponse = await accountingApi.taxCodes.getAll({ limit: 100 });
      setTaxCodes(codesResponse.data);

      // Load tax transactions
      const transactionsResponse = await accountingApi.taxTransactions.getAll({ limit: 100 });
      setTaxTransactions(transactionsResponse.data);

      // Mock data for charts
      setTaxData([
        { month: 'فروردین', payable: 500000, receivable: 300000, net: 200000 },
        { month: 'اردیبهشت', payable: 600000, receivable: 400000, net: 200000 },
        { month: 'خرداد', payable: 450000, receivable: 350000, net: 100000 },
        { month: 'تیر', payable: 700000, receivable: 500000, net: 200000 },
        { month: 'مرداد', payable: 550000, receivable: 450000, net: 100000 },
        { month: 'شهریور', payable: 650000, receivable: 550000, net: 100000 },
      ]);

      setTaxTypeData([
        { type: 'مالیات بر ارزش افزوده', amount: 2500000, percentage: 45 },
        { type: 'مالیات بر درآمد', amount: 1800000, percentage: 32 },
        { type: 'مالیات بر دارایی', amount: 800000, percentage: 15 },
        { type: 'سایر مالیات‌ها', amount: 400000, percentage: 8 },
      ]);
    } catch (error) {
      console.error('Error loading tax data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTaxData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleViewTaxCode = (taxCode: TaxCode) => {
    setSelectedTaxCode(taxCode);
    setDialogOpen(true);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR');
  };

  const getTaxTypeColor = (type: string) => {
    switch (type) {
      case 'sales_tax': return 'primary';
      case 'purchase_tax': return 'secondary';
      case 'withholding_tax': return 'warning';
      default: return 'default';
    }
  };

  const getTaxTypeLabel = (type: string) => {
    switch (type) {
      case 'sales_tax': return 'مالیات فروش';
      case 'purchase_tax': return 'مالیات خرید';
      case 'withholding_tax': return 'مالیات کسر شده';
      default: return type;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'paid': return 'success';
      case 'refunded': return 'info';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return 'در انتظار پرداخت';
      case 'paid': return 'پرداخت شده';
      case 'refunded': return 'بازپرداخت شده';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div style={{  display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400  }}>
        <Spin />
      </div>
    );
  }

  return (
    <div style={{  p: 3  }}>
      {/* Header */}
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <Typography.Title level={2}>
          مدیریت مالیات
        </Typography.Title>
        <div style={{  display: 'flex', gap: 1  }}>
          <Tooltip title="بارگذاری مجدد">
            <Button type="text" onClick={loadTaxData} disabled={loading}>
              <RefreshIcon />
            </Button>
          </Tooltip>
          <Button variant="contained" startIcon={<AddIcon />}>
            افزودن کد مالیاتی جدید
          </Button>
        </div>
      </div>

      {/* Tax Overview Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <ReceiptIcon style={{  fontSize: 32, color: 'primary.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {taxCodes.length}
                  </Typography.Title>
                  <Typography.Text>
                    کدهای مالیاتی
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
                <TrendingUpIcon style={{  fontSize: 32, color: 'error.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {formatCurrency(taxTransactions.filter(t => t.type === 'output').reduce((sum, t) => sum + t.tax_amount, 0))}
                  </Typography.Title>
                  <Typography.Text>
                    مالیات قابل پرداخت
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
                <TrendingDownIcon style={{  fontSize: 32, color: 'success.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {formatCurrency(taxTransactions.filter(t => t.type === 'input').reduce((sum, t) => sum + t.tax_amount, 0))}
                  </Typography.Title>
                  <Typography.Text>
                    مالیات قابل استرداد
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
                <PaymentIcon style={{  fontSize: 32, color: 'warning.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {taxTransactions.filter(t => t.status === 'pending').length}
                  </Typography.Title>
                  <Typography.Text>
                    تراکنش‌های معلق
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
      </Col>

      {/* Tax Charts */}
      <Card style={{  p: 3, mb: 3  }}>
        <Typography.Title level={4}>
          روند مالیات‌ها
        </Typography.Title>
        <div style={{  height: 400  }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={taxData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <RechartsTooltip formatter={(value) => formatCurrency(Number(value))} />
              <Legend />
              <Line type="monotone" dataKey="payable" stroke="#ff0000" name="قابل پرداخت" />
              <Line type="monotone" dataKey="receivable" stroke="#00ff00" name="قابل استرداد" />
              <Line type="monotone" dataKey="net" stroke="#0000ff" name="خالص" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Tax Type Distribution */}
      <Card style={{  p: 3, mb: 3  }}>
        <Typography.Title level={4}>
          توزیع انواع مالیات
        </Typography.Title>
        <div style={{  height: 400  }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={taxTypeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="amount"
              >
                {taxTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={['#0088FE', '#00C49F', '#FFBB28', '#FF8042'][index]} />
                ))}
              </Pie>
              <RechartsTooltip formatter={(value) => formatCurrency(Number(value))} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Tabs */}
      <Card style={{  width: '100%'  }}>
        <div style={{  borderBottom: 1, borderColor: 'divider'  }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="tax tabs">
            <Tab label="کدهای مالیاتی" />
            <Tab label="تراکنش‌های مالیاتی" />
          </Tabs>
        </div>

        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>کد</TableCell>
                  <TableCell>نام</TableCell>
                  <TableCell>نوع</TableCell>
                  <TableCell align="right">نرخ (%)</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell align="center">عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {taxCodes.map((taxCode) => (
                  <TableRow key={taxCode.id} hover>
                    <TableCell>
                      <Typography.Text>
                        {taxCode.code}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {taxCode.name}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getTaxTypeLabel(taxCode.type)}
                        color={getTaxTypeColor(taxCode.type)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {taxCode.rate}%
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={taxCode.is_active ? 'فعال' : 'غیرفعال'}
                        color={taxCode.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                        <Tooltip title="مشاهده جزئیات">
                          <Button type="text" size="small" onClick={() => handleViewTaxCode(taxCode)}
                          >
                            <VisibilityIcon />
                          </Button>
                        </Tooltip>
                        <Tooltip title="ویرایش">
                          <Button type="text" size="small" color="primary">
                            <EditIcon />
                          </Button>
                        </Tooltip>
                        <Tooltip title="حذف">
                          <Button type="text" size="small" color="error">
                            <DeleteIcon />
                          </Button>
                        </Tooltip>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>تاریخ</TableCell>
                  <TableCell>مرجع</TableCell>
                  <TableCell>کد مالیاتی</TableCell>
                  <TableCell>نوع</TableCell>
                  <TableCell align="right">مبلغ مشمول</TableCell>
                  <TableCell align="right">مبلغ مالیات</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>تاریخ سررسید</TableCell>
                  <TableCell align="center">عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {taxTransactions.map((transaction) => (
                  <TableRow key={transaction.id} hover>
                    <TableCell>
                      <Typography.Text>
                        {formatDate(transaction.transaction_date)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {transaction.reference}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {transaction.tax_code_name}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={transaction.type === 'input' ? 'ورودی' : 'خروجی'}
                        color={transaction.type === 'input' ? 'success' : 'error'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(transaction.taxable_amount)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(transaction.tax_amount)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getStatusLabel(transaction.status)}
                        color={getStatusColor(transaction.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {formatDate(transaction.due_date)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="center">
                      <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                        <Tooltip title="مشاهده">
                          <Button type="text" size="small" color="info">
                            <VisibilityIcon />
                          </Button>
                        </Tooltip>
                        {transaction.status === 'pending' && (
                          <Tooltip title="پرداخت">
                            <Button type="text" size="small" color="success">
                              <PaymentIcon />
                            </Button>
                          </Tooltip>
                        )}
                        <Tooltip title="ویرایش">
                          <Button type="text" size="small" color="primary">
                            <EditIcon />
                          </Button>
                        </Tooltip>
                        <Tooltip title="حذف">
                          <Button type="text" size="small" color="error">
                            <DeleteIcon />
                          </Button>
                        </Tooltip>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabPanel>
      </Card>

      {/* Tax Code Details Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          <Typography.Title level={4}>
            جزئیات کد مالیاتی: {selectedTaxCode?.name}
          </Typography.Title>
        </div>
        <div>
          {selectedTaxCode && (
            <div>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    کد
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedTaxCode.code}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    نام
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedTaxCode.name}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    نوع
                  </Typography>
                  <Tag
                    label={getTaxTypeLabel(selectedTaxCode.type)}
                    color={getTaxTypeColor(selectedTaxCode.type)}
                    style={{  mb: 2  }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    نرخ
                  </Typography>
                  <Typography.Title level={4}>
                    {selectedTaxCode.rate}%
                  </Typography.Title>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    توضیحات
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedTaxCode.description || 'توضیحی ثبت نشده'}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    وضعیت
                  </Typography>
                  <Tag
                    label={selectedTaxCode.is_active ? 'فعال' : 'غیرفعال'}
                    color={selectedTaxCode.is_active ? 'success' : 'default'}
                    style={{  mb: 2  }}
                  />
                </Col>
              </Row>
            </div>
          )}
        </div>
        <div>
          <Button onClick={() => setDialogOpen(false)}>
            بستن
          </Button>
        </div>
      </Modal>
    </div>
  );
}; 