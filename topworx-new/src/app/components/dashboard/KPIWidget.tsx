import React from "react";
import { Card, Statistic, Typography, Skeleton } from "antd";
import {
  TrendingUp,
  DollarOutlined,
  ShoppingCartOutlined,
  UserOutlined,
  TeamOutlined,
  BarChartOutlined,
} from "@ant-design/icons";

const { Text } = Typography;

const ICON_MAP: Record<string, React.ReactNode> = {
  TrendingUp: <TrendingUp />,
  DollarOutlined: <DollarOutlined />,
  ShoppingCartOutlined: <ShoppingCartOutlined />,
  UserOutlined: <UserOutlined />,
  TeamOutlined: <TeamOutlined />,
  BarChartOutlined: <BarChartOutlined />,
};

export interface KPIWidgetProps {
  title: string;
  value: string | number;
  icon?: string;
  color?: string;
  loading?: boolean;
  description?: string;
}

export const KPIWidget: React.FC<KPIWidgetProps> = ({
  title,
  value,
  icon = "TrendingUp",
  color = "#1677ff",
  loading = false,
  description,
}) => {
  const iconNode = ICON_MAP[icon] || <TrendingUp />;

  return (
    <Card style={{ borderRight: `6px solid ${color}`, height: 140, minWidth: 200 }}>
      {loading ? (
        <Skeleton active paragraph={{ rows: 2 }} />
      ) : (
        <Statistic
          title={title}
          value={value}
          prefix={<span style={{ color, fontSize: 20 }}>{iconNode}</span>}
          valueStyle={{ color, fontWeight: 800 }}
        />
      )}
      {description && <Text type="secondary" style={{ fontSize: 12 }}>{description}</Text>}
    </Card>
  );
};
