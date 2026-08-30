import React from "react";
import { Card, Col, Row, Skeleton, Typography } from 'antd';
import { KPIWidget } from "../../components/dashboard/KPIWidget";
import { ChartWidget } from "../../components/dashboard/ChartWidget";
import { useDashboardData } from "../../api/dashboard";

export const Dashboard: React.FC = () => {
  const { data, isLoading } = useDashboardData();

  return (
    <div>
      <Typography.Title level={2}>داشبورد مدیریتی</Typography.Title>
      <Row gutter={[16, 16]}>
        {/* KPI Widgets */}
        {(isLoading ? Array(4).fill(null) : data?.kpis).map((kpi, idx) => (
          <Col xs={Math.round(12 / 12 * 24)}>
            {isLoading ? (
              <Skeleton variant="rectangular" height={100} />
            ) : (
              <KPIWidget title={kpi.title} value={kpi.value} icon={kpi.icon} color={kpi.color} />
            )}
          </Col>
        ))}
      </Row>
      <Row gutter={[16, 16]}>
        {/* Chart Widgets */}
        {(isLoading ? Array(2).fill(null) : data?.charts).map((chart, idx) => (
          <Col xs={Math.round(12 / 12 * 24)}>
            {isLoading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : (
              <ChartWidget title={chart.title} data={chart.data} type={chart.type} />
            )}
          </Col>
        ))}
      </Row>
    </div>
  );
};