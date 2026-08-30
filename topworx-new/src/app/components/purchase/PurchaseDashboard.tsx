import React from 'react';
import { Card, Col, Progress, Row, Tag, Typography } from 'antd';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { usePurchaseOrders, usePurchaseRequests, usePurchaseInvoices, useSuppliers } from '../../../api/procurement';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export const PurchaseDashboard: React.FC = () => {
  const { data: orders = [] } = usePurchaseOrders();
  const { data: requests = [] } = usePurchaseRequests();
  const { data: invoices = [] } = usePurchaseInvoices();
  const { data: suppliers = [] } = useSuppliers();

  // محاسبه آمار
  const totalOrders = orders.length;
  const totalRequests = requests.length;
  const totalInvoices = invoices.length;
  const totalSuppliers = suppliers.length;

  const completedOrders = orders.filter(o => o.status === 'دریافت شده').length;
  const pendingOrders = orders.filter(o => o.status === 'در انتظار تأیید').length;
  const approvedRequests = requests.filter(r => r.status === 'تأیید شده').length;
  const paidInvoices = invoices.filter(i => i.status === 'پرداخت شده').length;

  const orderCompletionRate = totalOrders > 0 ? (completedOrders / totalOrders) * 100 : 0;
  const requestApprovalRate = totalRequests > 0 ? (approvedRequests / totalRequests) * 100 : 0;
  const invoicePaymentRate = totalInvoices > 0 ? (paidInvoices / totalInvoices) * 100 : 0;

  // داده‌های نمودار وضعیت سفارشات
  const orderStatusData = [
    { name: 'در انتظار تأیید', value: orders.filter(o => o.status === 'در انتظار تأیید').length },
    { name: 'تأیید شده', value: orders.filter(o => o.status === 'تأیید شده').length },
    { name: 'ارسال شده', value: orders.filter(o => o.status === 'ارسال شده').length },
    { name: 'دریافت شده', value: orders.filter(o => o.status === 'دریافت شده').length },
    { name: 'لغو شده', value: orders.filter(o => o.status === 'لغو شده').length }
  ];

  // داده‌های نمودار وضعیت درخواست‌ها
  const requestStatusData = [
    { name: 'در انتظار بررسی', value: requests.filter(r => r.status === 'در انتظار بررسی').length },
    { name: 'تأیید شده', value: requests.filter(r => r.status === 'تأیید شده').length },
    { name: 'رد شده', value: requests.filter(r => r.status === 'رد شده').length },
    { name: 'در حال خرید', value: requests.filter(r => r.status === 'در حال خرید').length },
    { name: 'تکمیل شده', value: requests.filter(r => r.status === 'تکمیل شده').length }
  ];

  // داده‌های نمودار وضعیت فاکتورها
  const invoiceStatusData = [
    { name: 'در انتظار پرداخت', value: invoices.filter(i => i.status === 'در انتظار پرداخت').length },
    { name: 'پرداخت شده', value: invoices.filter(i => i.status === 'پرداخت شده').length },
    { name: 'تأخیر', value: invoices.filter(i => i.status === 'تأخیر').length }
  ];

  return (
    <div style={{  p: 3  }}>
      <Typography.Title level={2}>
        داشبورد تدارکات و خرید
      </Typography.Title>

      {/* کارت‌های آمار */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography color="textSecondary" gutterBottom>
                کل سفارشات
              </Typography>
              <Typography.Title level={2}>
                {totalOrders}
              </Typography.Title>
              <div style={{  mt: 2  }}>
                <Typography.Text>
                  نرخ تکمیل: {orderCompletionRate.toFixed(1)}%
                </Typography.Text>
                <LinearProgress 
                  variant="determinate" 
                  value={orderCompletionRate} 
                  style={{  mt: 1  }}
                />
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography color="textSecondary" gutterBottom>
                کل درخواست‌ها
              </Typography>
              <Typography.Title level={2}>
                {totalRequests}
              </Typography.Title>
              <div style={{  mt: 2  }}>
                <Typography.Text>
                  نرخ تأیید: {requestApprovalRate.toFixed(1)}%
                </Typography.Text>
                <LinearProgress 
                  variant="determinate" 
                  value={requestApprovalRate} 
                  style={{  mt: 1  }}
                />
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography color="textSecondary" gutterBottom>
                کل فاکتورها
              </Typography>
              <Typography.Title level={2}>
                {totalInvoices}
              </Typography.Title>
              <div style={{  mt: 2  }}>
                <Typography.Text>
                  نرخ پرداخت: {invoicePaymentRate.toFixed(1)}%
                </Typography.Text>
                <LinearProgress 
                  variant="determinate" 
                  value={invoicePaymentRate} 
                  style={{  mt: 1  }}
                />
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography color="textSecondary" gutterBottom>
                کل تأمین‌کنندگان
              </Typography>
              <Typography.Title level={2}>
                {totalSuppliers}
              </Typography.Title>
              <div style={{  mt: 2  }}>
                <Typography.Text>
                  فعال: {suppliers.filter(s => s.status === 'فعال').length}
                </Typography.Text>
                <Tag 
                  label="فعال" 
                  color="success" 
                  size="small" 
                  style={{  mt: 1  }}
                />
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* نمودارها */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography.Title level={4}>
                وضعیت سفارشات
              </Typography.Title>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={orderStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {orderStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography.Title level={4}>
                وضعیت درخواست‌ها
              </Typography.Title>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={requestStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {requestStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography.Title level={4}>
                وضعیت فاکتورها
              </Typography.Title>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={invoiceStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {invoiceStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}; 