import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { BarChartOutlined, DollarOutlined, FallOutlined, FieldTimeOutlined, FilterOutlined, LineChartOutlined, PieChartOutlined, PlusOutlined, ReloadOutlined, RiseOutlined, ShoppingCartOutlined, StarOutlined, TeamOutlined } from '@ant-design/icons';

const mockSalesData = {
  totalRevenue: 1250000000,
  monthlyRevenue: 85000000,
  totalOrders: 1250,
  pendingOrders: 45,
  conversionRate: 23.5,
  averageOrderValue: 1000000,
  topProducts: [
    { name: 'لپ‌تاپ Dell XPS 13', sales: 25, revenue: 125000000 },
    { name: 'ماوس بی‌سیم Logitech', sales: 120, revenue: 48000000 },
    { name: 'کیف چرمی مردانه', sales: 85, revenue: 42500000 },
    { name: 'ساعت هوشمند Apple Watch', sales: 30, revenue: 90000000 },
  ],
  salesByRegion: [
    { region: 'تهران', sales: 450000000, percentage: 36 },
    { region: 'اصفهان', sales: 300000000, percentage: 24 },
    { region: 'مشهد', sales: 250000000, percentage: 20 },
    { region: 'شیراز', sales: 150000000, percentage: 12 },
    { region: 'سایر', sales: 100000000, percentage: 8 },
  ],
  salesByCategory: [
    { category: 'الکترونیک', sales: 600000000, percentage: 48 },
    { category: 'لوازم جانبی', sales: 300000000, percentage: 24 },
    { category: 'پوشاک', sales: 200000000, percentage: 16 },
    { category: 'سایر', sales: 150000000, percentage: 12 },
  ],
  recentOrders: [
    {
      id: 'ORD-001',
      customer: 'علی احمدی',
      product: 'لپ‌تاپ Dell XPS 13',
      amount: 50000000,
      status: 'completed',
      date: '1402/11/15',
    },
    {
      id: 'ORD-002',
      customer: 'فاطمه محمدی',
      product: 'ماوس بی‌سیم Logitech',
      amount: 400000,
      status: 'pending',
      date: '1402/11/14',
    },
    {
      id: 'ORD-003',
      customer: 'محمد رضایی',
      product: 'ساعت هوشمند Apple Watch',
      amount: 30000000,
      status: 'processing',
      date: '1402/11/13',
    },
  ],
  salesTrend: [
    { month: 'مهر', revenue: 75000000 },
    { month: 'آبان', revenue: 82000000 },
    { month: 'آذر', revenue: 78000000 },
    { month: 'دی', revenue: 85000000 },
    { month: 'بهمن', revenue: 92000000 },
    { month: 'اسفند', revenue: 88000000 },
  ],
};

const orderStatuses = [
  { value: 'pending', label: 'در انتظار', color: 'warning' },
  { value: 'processing', label: 'در حال پردازش', color: 'info' },
  { value: 'completed', label: 'تکمیل شده', color: 'success' },
  { value: 'cancelled', label: 'لغو شده', color: 'error' },
];

export const SalesDashboard: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [openDialog, setOpenDialog] = useState(false);

  const getStatusColor = (status: string) => {
    const orderStatus = orderStatuses.find(s => s.value === status);
    return orderStatus ? orderStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const orderStatus = orderStatuses.find(s => s.value === status);
    return orderStatus ? orderStatus.label : 'نامشخص';
  };

  const formatCurrency = (amount: number) => {
    return amount.toLocaleString() + ' تومان';
  };

  const formatPercentage = (value: number) => {
    return value.toFixed(1) + '%';
  };

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          داشبورد فروش
        </Typography.Title>
        <div>
          <FormControl size="small" style={{  minWidth: 120  }}>
            <InputLabel>دوره</span>
            <Select
              value={selectedPeriod}
              label="دوره"
              onChange={(e) => setSelectedPeriod(e.target.value)}
            >
              <MenuItem value="week">هفته</Select.Option>
              <MenuItem value="month">ماه</Select.Option>
              <MenuItem value="quarter">فصل</Select.Option>
              <MenuItem value="year">سال</Select.Option>
            </Select>
          </div>
          <Button type="text">
            <Refresh />
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography.Title level={2}>
                    {formatCurrency(mockSalesData.totalRevenue)}
                  </Typography.Title>
                  <Typography.Text>
                    کل درآمد
                  </Typography.Text>
                </div>
                <AttachMoney style={{  fontSize: 40, color: 'primary.main'  }} />
              </div>
              <div>
                <TrendingUp color="success" style={{  mr: 0.5  }} />
                <Typography.Text>
                  +12.5% نسبت به ماه قبل
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography.Title level={2}>
                    {mockSalesData.totalOrders}
                  </Typography.Title>
                  <Typography.Text>
                    کل سفارشات
                  </Typography.Text>
                </div>
                <ShoppingCart style={{  fontSize: 40, color: 'success.main'  }} />
              </div>
              <div>
                <TrendingUp color="success" style={{  mr: 0.5  }} />
                <Typography.Text>
                  +8.3% نسبت به ماه قبل
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography.Title level={2}>
                    {formatPercentage(mockSalesData.conversionRate)}
                  </Typography.Title>
                  <Typography.Text>
                    نرخ تبدیل
                  </Typography.Text>
                </div>
                <Star style={{  fontSize: 40, color: 'info.main'  }} />
              </div>
              <div>
                <TrendingUp color="success" style={{  mr: 0.5  }} />
                <Typography.Text>
                  +2.1% نسبت به ماه قبل
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography.Title level={2}>
                    {formatCurrency(mockSalesData.averageOrderValue)}
                  </Typography.Title>
                  <Typography.Text>
                    میانگین سفارش
                  </Typography.Text>
                </div>
                <People style={{  fontSize: 40, color: 'warning.main'  }} />
              </div>
              <div>
                <TrendingUp color="success" style={{  mr: 0.5  }} />
                <Typography.Text>
                  +5.7% نسبت به ماه قبل
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Charts Section */}
      <Row gutter={[16, 16]}>
        {/* Sales Trend Chart */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <Typography.Title level={4}>
                  روند فروش
                </Typography.Title>
                <Button type="text" size="small">
                  <ShowChart />
                </Button>
              </div>
              <div style={{  height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center'  }}>
                <Typography.Text>
                  نمودار روند فروش در 6 ماه گذشته
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>

        {/* Sales by Region */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography.Title level={4}>
                فروش بر اساس منطقه
              </Typography.Title>
              <div>
                {mockSalesData.salesByRegion.map((region, index) => (
                  <div>
                    <div>
                      <Typography.Text>{region.region}</Typography.Text>
                      <Typography.Text>
                        {formatCurrency(region.sales)}
                      </Typography.Text>
                    </div>
                    <LinearProgress
                      variant="determinate"
                      value={region.percentage}
                      style={{  height: 8, borderRadius: 4  }}
                    />
                    <Typography variant="caption" color="textSecondary">
                      {formatPercentage(region.percentage)}
                    </Typography>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Top Products and Recent Orders */}
      <Row gutter={[16, 16]}>
        {/* Top Products */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <Typography.Title level={4}>
                  محصولات پرفروش
                </Typography.Title>
                <Button size="small" startIcon={<Add />}>
                  مشاهده همه
                </Button>
              </div>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>محصول</TableCell>
                      <TableCell align="right">فروش</TableCell>
                      <TableCell align="right">درآمد</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockSalesData.topProducts.map((product, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography.Text>
                            {product.name}
                          </Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Tag label={product.sales} size="small" color="primary" />
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>
                            {formatCurrency(product.revenue)}
                          </Typography.Text>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </Card>
        </Col>

        {/* Recent Orders */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <Typography.Title level={4}>
                  سفارشات اخیر
                </Typography.Title>
                <Button size="small" startIcon={<Add />}>
                  مشاهده همه
                </Button>
              </div>
              <div>
                {mockSalesData.recentOrders.map((order, index) => (
                  <div>
                    <div>
                      <Typography.Text>
                        {order.id}
                      </Typography.Text>
                      <Tag
                        label={getStatusText(order.status)}
                        color={getStatusColor(order.status) as any}
                        size="small"
                      />
                    </div>
                    <Typography.Text>
                      {order.customer} - {order.product}
                    </Typography.Text>
                    <div>
                      <Typography.Text>
                        {formatCurrency(order.amount)}
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {order.date}
                      </Typography>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Performance Alerts */}
      {mockSalesData.pendingOrders > 0 && (
        <Alert severity="warning" style={{  mt: 3  }}>
          {mockSalesData.pendingOrders} سفارش در انتظار پردازش وجود دارد.
        </Alert>
      )}
    </div>
  );
}; 