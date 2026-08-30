import React, { useState } from 'react';
import { Alert, Badge, Button, Card, Col, Collapse, Divider, Input, InputNumber, Modal, Progress, Rate, Row, Select, Table, Tabs, Tag, Typography } from 'antd';
import { BarChartOutlined, BugOutlined, CalendarOutlined, DollarOutlined, DownOutlined, DownloadOutlined, EnvironmentOutlined, EyeOutlined, FallOutlined, FilterOutlined, MailOutlined, PieChartOutlined, PlusOutlined, PrinterOutlined, ReloadOutlined, RiseOutlined, SafetyOutlined, SpeedOutlined, StarOutlined, TeamOutlined } from '@ant-design/icons';

const mockAnalytics = {
  totalSales: 1250000000,
  monthlyGrowth: 12.5,
  conversionRate: 8.7,
  averageOrderValue: 25000000,
  customerLifetimeValue: 450000000,
  repeatCustomerRate: 35.2,
  topRegions: [
    { name: 'تهران', sales: 450000000, growth: 15.2, customers: 1250, orders: 1800 },
    { name: 'اصفهان', sales: 300000000, growth: 8.7, customers: 850, orders: 1200 },
    { name: 'مشهد', sales: 250000000, growth: 22.1, customers: 720, orders: 950 },
    { name: 'شیراز', sales: 180000000, growth: 5.3, customers: 520, orders: 680 },
    { name: 'تبریز', sales: 120000000, growth: 18.9, customers: 380, orders: 450 },
  ],
  topProducts: [
    { name: 'لپ‌تاپ Dell XPS 13', sales: 25, revenue: 125000000, growth: 12.5, margin: 28.5 },
    { name: 'ماوس بی‌سیم Logitech', sales: 120, revenue: 48000000, growth: 8.2, margin: 35.2 },
    { name: 'کیف چرمی مردانه', sales: 78, revenue: 31200000, growth: 15.8, margin: 42.1 },
    { name: 'ساعت هوشمند Apple Watch', sales: 15, revenue: 450000000, growth: 25.3, margin: 32.8 },
    { name: 'هدفون Sony WH-1000XM4', sales: 45, revenue: 135000000, growth: 18.7, margin: 38.9 },
  ],
  salesByMonth: [
    { month: 'مهر', sales: 850000000, orders: 340, customers: 280 },
    { month: 'آبان', sales: 920000000, orders: 368, customers: 310 },
    { month: 'آذر', sales: 980000000, orders: 392, customers: 335 },
    { month: 'دی', sales: 1050000000, orders: 420, customers: 360 },
    { month: 'بهمن', sales: 1120000000, orders: 448, customers: 385 },
    { month: 'اسفند', sales: 1250000000, orders: 500, customers: 420 },
  ],
  customerSegments: [
    { segment: 'VIP', count: 150, revenue: 450000000, percentage: 36 },
    { segment: 'عادی', count: 850, revenue: 600000000, percentage: 48 },
    { segment: 'جدید', count: 200, revenue: 200000000, percentage: 16 },
  ],
  salesChannels: [
    { channel: 'وب‌سایت', sales: 750000000, percentage: 60 },
    { channel: 'موبایل', sales: 375000000, percentage: 30 },
    { channel: 'فروشگاه فیزیکی', sales: 125000000, percentage: 10 },
  ],
  topSalespeople: [
    { name: 'علی احمدی', sales: 180000000, orders: 72, customers: 45, commission: 18000000 },
    { name: 'فاطمه محمدی', sales: 150000000, orders: 60, customers: 38, commission: 15000000 },
    { name: 'محمد رضایی', sales: 120000000, orders: 48, customers: 32, commission: 12000000 },
    { name: 'زهرا کریمی', sales: 100000000, orders: 40, customers: 28, commission: 10000000 },
    { name: 'حسین نوری', sales: 80000000, orders: 32, customers: 25, commission: 8000000 },
  ],
  salesForecast: [
    { month: 'فروردین', forecast: 1350000000, confidence: 85 },
    { month: 'اردیبهشت', forecast: 1420000000, confidence: 82 },
    { month: 'خرداد', forecast: 1480000000, confidence: 78 },
    { month: 'تیر', forecast: 1550000000, confidence: 75 },
  ],
};

const timePeriods = [
  { value: 'week', label: 'هفته' },
  { value: 'month', label: 'ماه' },
  { value: 'quarter', label: 'فصل' },
  { value: 'year', label: 'سال' },
];

const chartTypes = [
  { value: 'line', label: 'خطی' },
  { value: 'bar', label: 'ستونی' },
  { value: 'pie', label: 'دایره‌ای' },
  { value: 'area', label: 'ناحیه‌ای' },
];

export const SalesAnalytics: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [selectedChartType, setSelectedChartType] = useState('line');
  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);

  const formatCurrency = (amount: number) => {
    return amount.toLocaleString() + ' تومان';
  };

  const formatPercentage = (value: number) => {
    return value.toFixed(1) + '%';
  };

  const getGrowthColor = (growth: number) => {
    return growth >= 0 ? 'success' : 'error';
  };

  const getGrowthIcon = (growth: number) => {
    return growth >= 0 ? <TrendingUp /> : <TrendingDown />;
  };

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          تحلیل فروش
        </Typography.Title>
        <div>
          <FormControl size="small" style={{  minWidth: 120  }}>
            <InputLabel>دوره</span>
            <Select
              value={selectedPeriod}
              label="دوره"
              onChange={(e) => setSelectedPeriod(e.target.value)}
            >
              {timePeriods.map((period) => (
                <MenuItem key={period.value} value={period.value}>
                  {period.value}
                </Select.Option>
              ))}
            </Select>
          </div>
          <FormControl size="small" style={{  minWidth: 120  }}>
            <InputLabel>نوع نمودار</span>
            <Select
              value={selectedChartType}
              label="نوع نمودار"
              onChange={(e) => setSelectedChartType(e.target.value)}
            >
              {chartTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </Select.Option>
              ))}
            </Select>
          </div>
          <Button type="text">
            <Refresh />
          </Button>
          <Button variant="outlined" startIcon={<Download />}>
            دانلود گزارش
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
                    {formatCurrency(mockAnalytics.totalSales)}
                  </Typography.Title>
                  <Typography.Text>
                    کل فروش
                  </Typography.Text>
                </div>
                <AttachMoney style={{  fontSize: 40, color: 'primary.main'  }} />
              </div>
              <div>
                {getGrowthIcon(mockAnalytics.monthlyGrowth)}
                <Typography.Text>
                  +{mockAnalytics.monthlyGrowth}% نسبت به ماه قبل
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
                    {formatPercentage(mockAnalytics.conversionRate)}
                  </Typography.Title>
                  <Typography.Text>
                    نرخ تبدیل
                  </Typography.Text>
                </div>
                <TrendingUp style={{  fontSize: 40, color: 'success.main'  }} />
              </div>
              <div>
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
                    {formatCurrency(mockAnalytics.averageOrderValue)}
                  </Typography.Title>
                  <Typography.Text>
                    متوسط سفارش
                  </Typography.Text>
                </div>
                <Assessment style={{  fontSize: 40, color: 'info.main'  }} />
              </div>
              <div>
                <Typography.Text>
                  +5.3% نسبت به ماه قبل
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
                    {formatPercentage(mockAnalytics.repeatCustomerRate)}
                  </Typography.Title>
                  <Typography.Text>
                    مشتریان بازگشتی
                  </Typography.Text>
                </div>
                <People style={{  fontSize: 40, color: 'warning.main'  }} />
              </div>
              <div>
                <Typography.Text>
                  +1.8% نسبت به ماه قبل
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
                  <TrendingUp />
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

        {/* Sales by Channel */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography.Title level={4}>
                فروش بر اساس کانال
              </Typography.Title>
              <div>
                {mockAnalytics.salesChannels.map((channel, index) => (
                  <div>
                    <div>
                      <Typography.Text>{channel.channel}</Typography.Text>
                      <Typography.Text>
                        {formatPercentage(channel.percentage)}
                      </Typography.Text>
                    </div>
                    <LinearProgress
                      variant="determinate"
                      value={channel.percentage}
                      style={{  height: 8, borderRadius: 4  }}
                    />
                    <Typography variant="caption" color="textSecondary">
                      {formatCurrency(channel.sales)}
                    </Typography>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Detailed Analytics */}
      <Card>
        <div>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="مناطق برتر" />
            <Tab label="محصولات پرفروش" />
            <Tab label="بازاریابان برتر" />
            <Tab label="پیش‌بینی" />
          </Tabs>

          <div style={{  mt: 2  }}>
            {tabValue === 0 && (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>منطقه</TableCell>
                      <TableCell align="right">فروش</TableCell>
                      <TableCell align="right">مشتریان</TableCell>
                      <TableCell align="right">سفارشات</TableCell>
                      <TableCell>رشد</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockAnalytics.topRegions.map((region, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <div>
                            <LocationOn fontSize="small" />
                            <Typography.Text>
                              {region.name}
                            </Typography.Text>
                          </div>
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>
                            {formatCurrency(region.sales)}
                          </Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>{region.customers}</Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>{region.orders}</Typography.Text>
                        </TableCell>
                        <TableCell>
                          <div>
                            {getGrowthIcon(region.growth)}
                            <Typography.Text>
                              +{region.growth}%
                            </Typography.Text>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}

            {tabValue === 1 && (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>محصول</TableCell>
                      <TableCell align="right">فروش</TableCell>
                      <TableCell align="right">درآمد</TableCell>
                      <TableCell>رشد</TableCell>
                      <TableCell>حاشیه</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockAnalytics.topProducts.map((product, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography.Text>
                            {product.name}
                          </Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>{product.sales}</Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>
                            {formatCurrency(product.revenue)}
                          </Typography.Text>
                        </TableCell>
                        <TableCell>
                          <div>
                            {getGrowthIcon(product.growth)}
                            <Typography.Text>
                              +{product.growth}%
                            </Typography.Text>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Typography.Text>
                            {formatPercentage(product.margin)}
                          </Typography.Text>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}

            {tabValue === 2 && (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>بازاریاب</TableCell>
                      <TableCell align="right">فروش</TableCell>
                      <TableCell align="right">سفارشات</TableCell>
                      <TableCell align="right">مشتریان</TableCell>
                      <TableCell align="right">کمیسیون</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockAnalytics.topSalespeople.map((salesperson, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography.Text>
                            {salesperson.name}
                          </Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>
                            {formatCurrency(salesperson.sales)}
                          </Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>{salesperson.orders}</Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>{salesperson.customers}</Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Typography.Text>
                            {formatCurrency(salesperson.commission)}
                          </Typography.Text>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}

            {tabValue === 3 && (
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <div style={{  height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center'  }}>
                    <Typography.Text>
                      نمودار پیش‌بینی فروش
                    </Typography.Text>
                  </div>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography.Title level={4}>
                    پیش‌بینی ماهانه
                  </Typography.Title>
                  {mockAnalytics.salesForecast.map((forecast, index) => (
                    <div>
                      <div>
                        <Typography.Text>{forecast.month}</Typography.Text>
                        <Typography.Text>
                          {formatCurrency(forecast.forecast)}
                        </Typography.Text>
                      </div>
                      <LinearProgress
                        variant="determinate"
                        value={forecast.confidence}
                        style={{  height: 6, borderRadius: 3  }}
                      />
                      <Typography variant="caption" color="textSecondary">
                        اطمینان: {forecast.confidence}%
                      </Typography>
                    </div>
                  ))}
                </Col>
              </Row>
            )}
          </div>
        </div>
      </Card>

      {/* Customer Segments */}
      <div style={{  mt: 3  }}>
        <Typography.Title level={4}>
          تحلیل مشتریان
        </Typography.Title>
        <Row gutter={[16, 16]}>
          {mockAnalytics.customerSegments.map((segment, index) => (
            <Col xs={Math.round(12 / 12 * 24)}>
              <Card style={{  p: 2, textAlign: 'center'  }}>
                <Typography.Title level={4}>
                  {segment.segment}
                </Typography.Title>
                <Typography.Title level={2}>
                  {segment.count}
                </Typography.Title>
                <Typography.Text>
                  مشتری
                </Typography.Text>
                <LinearProgress
                  variant="determinate"
                  value={segment.percentage}
                  style={{  height: 8, borderRadius: 4, mb: 1  }}
                />
                <Typography.Text>
                  {formatPercentage(segment.percentage)} از کل مشتریان
                </Typography.Text>
                <Typography.Text>
                  {formatCurrency(segment.revenue)} درآمد
                </Typography.Text>
              </Card>
            </Col>
          ))}
        </Row>
      </div>
    </div>
  );
}; 