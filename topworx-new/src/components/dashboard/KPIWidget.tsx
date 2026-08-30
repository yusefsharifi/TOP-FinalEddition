import React from "react";
import { Card, Typography } from 'antd';
export const KPIWidget: React.FC<{ title: string; value: string | number; icon: string; color?: string }> = ({
  title, value, icon, color = "#1976d2"
}) => {
  const Icon = MuiIcons[icon as keyof typeof MuiIcons] || MuiIcons["Info"];
  return (
    <Card style={{  p: 2, display: "flex", alignItems: "center", gap: 2  }}>
      <div style={{  bgcolor: color, color: "#fff", borderRadius: "50%", p: 1  }}>
        <Icon fontSize="large" />
      </div>
      <div>
        <Typography.Title level={4}>{title}</Typography.Title>
        <Typography.Title level={3}>{value}</Typography.Title>
      </div>
    </Card>
  );
};