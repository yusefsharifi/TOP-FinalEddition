import React from "react";
import { Card, Button, Space } from "antd";
import { DashboardOutlined, CheckSquareOutlined, TeamOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

const links = [
  { label: "داشبورد", icon: <DashboardOutlined />, to: "/dashboard" },
  { label: "وظایف", icon: <CheckSquareOutlined />, to: "/tasks" },
  { label: "مشتریان", icon: <TeamOutlined />, to: "/crm/customers" },
  { label: "هوش مصنوعی", icon: <ThunderboltOutlined />, to: "/ai" },
];

export const QuickLinksWidget: React.FC = () => {
  const navigate = useNavigate();
  return (
    <Card title={<span><ThunderboltOutlined style={{ marginRight: 8 }} />لینک‌های سریع</span>} style={{ minHeight: 120 }}>
      <Space wrap>
        {links.map((l) => <Button key={l.label} icon={l.icon} onClick={() => navigate(l.to)}>{l.label}</Button>)}
      </Space>
    </Card>
  );
};
