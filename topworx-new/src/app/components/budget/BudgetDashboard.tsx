import React from "react";
import { Card, Row, Col, Statistic, Typography } from "antd";
import {
  DollarOutlined,
  FundOutlined,
  WarningOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";

const { Title, Paragraph } = Typography;

const BudgetDashboard: React.FC = () => {
  return (
    <div>
      <Title level={2}>مدیریت بودجه</Title>
      <Paragraph>برنامه‌ریزی و کنترل بودجه سازمان</Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="بودجه کل"
              value={0}
              prefix={<DollarOutlined />}
              suffix="ریال"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="مصرف شده"
              value={0}
              prefix={<FundOutlined />}
              suffix="ریال"
              valueStyle={{ color: "#cf1322" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="مانده"
              value={0}
              prefix={<CheckCircleOutlined />}
              suffix="ریال"
              valueStyle={{ color: "#3f8600" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="انحراف"
              value={0}
              prefix={<WarningOutlined />}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 24 }}>
        <Paragraph type="secondary">
          ماژول بودجه در حال توسعه است. به زودی قابلیت‌های زیر اضافه خواهد شد:
        </Paragraph>
        <ul>
          <li>تهیه و تنظیم بودجه سالانه</li>
          <li>کنترل بودجه بخش‌ها</li>
          <li>گزارش انحراف بودجه</li>
          <li>تأیید درخواست‌های بودجه</li>
        </ul>
      </Card>
    </div>
  );
};

export { BudgetDashboard };
