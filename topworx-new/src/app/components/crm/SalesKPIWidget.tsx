import React from "react";
import { Card, Typography } from 'antd';
export interface SalesKPIWidgetProps {
  icon: keyof typeof MuiIcons;
  value: number | string;
  title: string;
  description?: string;
  color?: string;
}

export const SalesKPIWidget: React.FC<SalesKPIWidgetProps> = ({ icon, value, title, description, color }) => {
  const Icon = MuiIcons[icon] || MuiIcons.BarChart;
  return (
    <Card style={{ width: "100%" }}>
      <div>
        <Icon style={{  fontSize: 40, color: color || "primary.main"  }} />
      </div>
      <div>
        <Typography.Title level={3}>{value}</Typography.Title>
        <Typography.Title level={5}>{title}</Typography.Title>
        {description && <Typography variant="caption" color="text.secondary">{description}</Typography>}
      </div>
    </Card>
  );
}; 