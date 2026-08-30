import React from "react";
import { Card, Row, Col, Statistic, Typography } from "antd";
import {
  AppstoreOutlined,
  DollarOutlined,
  ToolOutlined,
  BarChartOutlined,
} from "@ant-design/icons";

const { Title, Paragraph } = Typography;

const AssetsDashboard: React.FC = () => {
  return (
    <div>
      <Title level={2}>مدیریت دارایی‌ها</Title>
      <Paragraph>ثبت و مدیریت دارایی‌های ثابت سازمان</Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="تعداد دارایی‌ها"
              value={0}
              prefix={<AppstoreOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="ارزش کل"
              value={0}
              prefix={<DollarOutlined />}
              suffix="ریال"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="استهلاک انباشته"
              value={0}
              prefix={<ToolOutlined />}
              suffix="ریال"
              valueStyle={{ color: "#cf1322" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="ارزش دفتری"
              value={0}
              prefix={<BarChartOutlined />}
              suffix="ریال"
              valueStyle={{ color: "#3f8600" }}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 24 }}>
        <Paragraph type="secondary">
          ماژول دارایی‌های ثابت در حال توسعه است. به زودی قابلیت‌های زیر اضافه خواهد شد:
        </Paragraph>
        <ul>
          <li>ثبت دارایی‌های ثابت</li>
          <li>محاسبه استهلاک</li>
          <li>انتقال و اlsefaq دارایی</li>
          <li>گزارش دارایی‌ها</li>
        </ul>
      </Card>
    </div>
  );
};

export { AssetsDashboard };
