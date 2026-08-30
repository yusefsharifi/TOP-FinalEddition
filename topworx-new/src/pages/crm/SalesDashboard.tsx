import React from "react";
import { Card, Col, Row, Space, Typography } from 'antd';
import { SalesKPIWidget } from "../../app/components/crm/SalesKPIWidget";
import { SalesChartWidget } from "../../app/components/crm/SalesChartWidget";
import { RiseOutlined } from '@ant-design/icons';
import { TeamOutlined } from '@ant-design/icons';
import { DollarOutlined } from '@ant-design/icons';
import { CheckCircleOutlined } from '@ant-design/icons';

const kpis = [
  { icon: "TrendingUp", value: 24, title: "فرصت‌های فعال" },
  { icon: "People", value: 12, title: "مشتریان جدید" },
  { icon: "MonetizationOn", value: "2,350,000", title: "فروش ماه جاری (تومان)" },
  { icon: "AssignmentTurnedIn", value: "68%", title: "نرخ تبدیل" },
];

const salesData = [
  { month: "فروردین", sales: 1200000 },
  { month: "اردیبهشت", sales: 1350000 },
  { month: "خرداد", sales: 980000 },
  { month: "تیر", sales: 1450000 },
  { month: "مرداد", sales: 1600000 },
  { month: "شهریور", sales: 1100000 },
];

const conversionData = [
  { stage: "سرنخ", count: 40 },
  { stage: "مذاکره", count: 25 },
  { stage: "پیشنهاد", count: 18 },
  { stage: "توافق", count: 12 },
  { stage: "برنده", count: 8 },
  { stage: "باخته", count: 7 },
];

const reminders = [
  { id: 1, title: "پیگیری فرصت مذاکره با شرکت الف", due: "1403/03/20" },
  { id: 2, title: "تماس با مشتری جدید: شرکت ب", due: "1403/03/22" },
  { id: 3, title: "ارسال پیش‌فاکتور به شرکت ج", due: "1403/03/25" },
];

export const SalesDashboard: React.FC = () => {
  return (
    <div>
      <Typography.Title level={2}>داشبورد فروش و CRM</Typography.Title>
      <Row gutter={[16, 16]}>
        {kpis.map((kpi, idx) => (
          <Col xs={Math.round(12 / 12 * 24)}>
            <SalesKPIWidget {...kpi} />
          </Col>
        ))}
      </Row>
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <SalesChartWidget type="line" data={salesData} title="روند فروش ماهانه" dataKey="month" valueKey="sales" />
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <SalesChartWidget type="bar" data={conversionData} title="تعداد فرصت در هر مرحله" dataKey="stage" valueKey="count" />
        </Col>
      </Row>
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2  }}>
            <Typography.Title level={5}>یادآوری‌های مهم</Typography.Title>
            <Stack spacing={1}>
              {reminders.map(r => (
                <div>
                  <Typography>{r.title}</Typography>
                  <Typography color="text.secondary" fontSize={13}>{r.due}</Typography>
                </div>
              ))}
            </Stack>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2  }}>
            <Typography.Title level={5}>فرصت‌های باز</Typography.Title>
            <Stack spacing={1}>
              <Typography>شرکت الف - مذاکره</Typography>
              <Typography>شرکت ب - پیشنهاد</Typography>
              <Typography>شرکت ج - سرنخ</Typography>
            </Stack>
          </Card>
        </Col>
      </Row>
    </div>
  );
}; 