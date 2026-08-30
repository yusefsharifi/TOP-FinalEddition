import React from 'react';
import { Card, Col, Progress, Row, Typography } from 'antd';
import { AppstoreOutlined, CarOutlined, DollarOutlined, EnvironmentOutlined, InboxOutlined, RiseOutlined, WarningOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const mockInventoryData = {
  totalItems: 1250,
  lowStockItems: 23,
  totalValue: 450000000,
  averageStockLevel: 78,
  reorderPoints: 156,
  categories: [
    { name: 'مواد اولیه', value: 35 },
    { name: 'محصولات نهایی', value: 28 },
    { name: 'قطعات یدکی', value: 20 },
    { name: 'لوازم مصرفی', value: 17 },
  ],
};

export const InventoryDashboard: React.FC = () => {
  return (
    <div>
      <Title level={3}>داشبورد انبارداری</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <InboxOutlined style={{ fontSize: 32, color: '#1677ff' }} />
              <Title level={4}>{mockInventoryData.totalItems}</Title>
              <Text type="secondary">کل اقلام</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <WarningOutlined style={{ fontSize: 32, color: '#faad14' }} />
              <Title level={4}>{mockInventoryData.lowStockItems}</Title>
              <Text type="secondary">کمتر از حد مجاز</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <DollarOutlined style={{ fontSize: 32, color: '#52c41a' }} />
              <Title level={4}>{mockInventoryData.totalValue.toLocaleString()}</Title>
              <Text type="secondary">ارزش کل موجودی</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <RiseOutlined style={{ fontSize: 32, color: '#722ed1' }} />
              <Title level={4}>{mockInventoryData.reorderPoints}</Title>
              <Text type="secondary">نقاط سفارش مجدد</Text>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12}>
          <Card title="وضعیت موجودی">
            <Text>میانگین سطح موجودی</Text>
            <Progress percent={mockInventoryData.averageStockLevel} style={{ marginBottom: 16 }} />
            <Text type="secondary">
              <AppstoreOutlined /> تعداد دسته‌بندی‌ها: {mockInventoryData.categories.length}
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card title="توزیع محصولات">
            {mockInventoryData.categories.map((cat) => (
              <div key={cat.name} style={{ marginBottom: 8 }}>
                <Text>{cat.name}</Text>
                <Progress percent={cat.value} size="small" />
              </div>
            ))}
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12}>
          <Card title="موجودی انبارها">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <EnvironmentOutlined />
              <Text>انبار مرکزی</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card title="حرکات اخیر">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <CarOutlined />
              <Text>آخرین انتقال: ۲ ساعت پیش</Text>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};
