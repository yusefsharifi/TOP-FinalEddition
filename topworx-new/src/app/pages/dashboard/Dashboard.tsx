import React from "react";
import { Typography, Row, Col } from "antd";
import { WidgetManager } from "../../components/dashboard/WidgetManager";
import { NotificationWidget } from "../../components/dashboard/NotificationWidget";
import { TaskWidget } from "../../components/dashboard/TaskWidget";
import { CalendarWidget } from "../../components/dashboard/CalendarWidget";
import { QuickLinksWidget } from "../../components/dashboard/QuickLinksWidget";
import { AIDashboardFull } from "../../components/dashboard/AIDashboardWidgets";

const { Title } = Typography;

export const Dashboard: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>داشبورد مدیریتی</Title>

      {/* AI Dashboard — Full cross-module insights at the top */}
      <div style={{ marginBottom: 24 }}>
        <AIDashboardFull />
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <WidgetManager />
        </Col>
        <Col xs={24} lg={8}>
          <Row gutter={[16, 16]}>
            <Col xs={24}>
              <NotificationWidget />
            </Col>
            <Col xs={24}>
              <TaskWidget />
            </Col>
            <Col xs={24}>
              <CalendarWidget />
            </Col>
            <Col xs={24}>
              <QuickLinksWidget />
            </Col>
          </Row>
        </Col>
      </Row>
    </div>
  );
};
