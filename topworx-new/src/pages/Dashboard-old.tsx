import React, { useEffect, useState, useCallback } from 'react';
import { Card, Col, Divider, List, List.Item, Row, Spin, Typography } from 'antd';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useTranslation } from 'react-i18next';
import { dashboardService } from '../services/api';

interface DashboardData {
  totalSales: number;
  totalCustomers: number;
  inventoryValue: number;
  totalRevenue: number;
  salesData: {
    date: string;
    sales: number;
  }[];
  recentActivities: {
    id: number;
    type: string;
    description: string;
    timestamp: string;
  }[];
}

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DashboardData | null>(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await dashboardService.getOverview();
      setData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Use mock data for demonstration
      setData({
        totalSales: 2450000,
        totalCustomers: 1234,
        inventoryValue: 3456000,
        totalRevenue: 4567000,
        salesData: [
          { date: t('dashboard.today'), sales: 450000 },
          { date: t('dashboard.thisWeek'), sales: 1250000 },
          { date: t('dashboard.thisMonth'), sales: 2450000 },
          { date: t('dashboard.lastMonth'), sales: 2100000 },
        ],
        recentActivities: [
          {
            id: 1,
            type: 'sale',
            description: 'فروش جدید به مشتری شماره ۱۲۳',
            timestamp: '۱۰ دقیقه پیش',
          },
          {
            id: 2,
            type: 'inventory',
            description: 'به‌روزرسانی موجودی محصول کد ۴۵۶',
            timestamp: '۳۰ دقیقه پیش',
          },
          {
            id: 3,
            type: 'customer',
            description: 'ثبت مشتری جدید',
            timestamp: '۱ ساعت پیش',
          },
        ],
      });
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('fa-IR').format(value) + ' ' + t('dashboard.currency');
  };

  if (loading) {
    return (
      <div>
        <Spin />
      </div>
    );
  }

  return (
    <div>
      <Typography.Title level={2}>
        {t('dashboard.title')}
      </Typography.Title>

      <Row gutter={[16, 16]}>
        {/* Statistics Cards */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography color="textSecondary" gutterBottom>
                {t('dashboard.totalSales')}
              </Typography>
              <Typography.Title level={3}>{formatCurrency(data?.totalSales || 0)}</Typography.Title>
            </div>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography color="textSecondary" gutterBottom>
                {t('dashboard.totalCustomers')}
              </Typography>
              <Typography.Title level={3}>
                {new Intl.NumberFormat('fa-IR').format(data?.totalCustomers || 0)}
              </Typography.Title>
            </div>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography color="textSecondary" gutterBottom>
                {t('dashboard.inventoryValue')}
              </Typography>
              <Typography.Title level={3}>{formatCurrency(data?.inventoryValue || 0)}</Typography.Title>
            </div>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography color="textSecondary" gutterBottom>
                {t('dashboard.totalRevenue')}
              </Typography>
              <Typography.Title level={3}>{formatCurrency(data?.totalRevenue || 0)}</Typography.Title>
            </div>
          </Card>
        </Col>

        {/* Sales Chart */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2  }}>
            <Typography.Title level={4}>
              {t('dashboard.salesChart')}
            </Typography.Title>
            <div>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data?.salesData || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Legend />
                  <Bar dataKey="sales" fill="#8884d8" name={t('dashboard.totalSales')} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        {/* Recent Activities */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, height: '100%'  }}>
            <Typography.Title level={4}>
              {t('dashboard.recentActivities')}
            </Typography.Title>
            <List>
              {data?.recentActivities.map((activity) => (
                <React.Fragment key={activity.id}>
                  <ListItem>
                    <ListItemText
                      primary={activity.description}
                      secondary={activity.timestamp}
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 