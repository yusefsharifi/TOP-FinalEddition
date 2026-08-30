// src/app/components/layout/MainLayout.tsx
// ============================================================================
// MainLayout — قالب اصلی برنامه با Sidebar + Header + Content
// تمام صفحات private داخل این layout رندر می‌شوند
// ============================================================================

import React, { useState } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { Layout, Menu, Avatar, Dropdown, Badge, Tooltip, Button } from "antd";
import type { MenuProps } from "antd";
import {
  DashboardOutlined,
  DollarOutlined,
  AccountBookOutlined,
  RobotOutlined,
  MailOutlined,
  TeamOutlined,
  ShoppingCartOutlined,
  AppstoreOutlined,
  SafetyOutlined,
  CheckSquareOutlined,
  BarChartOutlined,
  FundOutlined,
  SettingOutlined,
  MessageOutlined,
  WalletOutlined,
  InboxOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from "@ant-design/icons";
import { ThemeToggle } from "../common/ThemeToggle";

const { Header, Sider, Content } = Layout;

// ── تعریف آیتم‌های منوی ناوبری ─────────────────────────────────────────────
const menuItems: MenuProps["items"] = [
  {
    key: "/dashboard",
    icon: <DashboardOutlined />,
    label: "داشبورد",
  },
  {
    key: "finance-group",
    icon: <DollarOutlined />,
    label: "مالی",
    children: [
      { key: "/finance",    label: "مدیریت مالی" },
      { key: "/accounting", label: "حسابداری" },
      { key: "/budget",     label: "بودجه" },
    ],
  },
  {
    key: "crm-group",
    icon: <TeamOutlined />,
    label: "مشتریان (CRM)",
    children: [
      { key: "/crm/customers",    label: "مشتریان" },
      { key: "/crm/sales-orders", label: "سفارشات" },
      { key: "/crm/sales-invoices", label: "فاکتورها" },
    ],
  },
  {
    key: "inventory-group",
    icon: <InboxOutlined />,
    label: "انبارداری",
    children: [
      { key: "/inventory",            label: "داشبورد انبار" },
      { key: "/inventory/items",      label: "کالاها" },
      { key: "/inventory/warehouses", label: "انبارها" },
      { key: "/inventory/movements",  label: "جابجایی کالا" },
    ],
  },
  {
    key: "hr-group",
    icon: <UserOutlined />,
    label: "منابع انسانی",
    children: [
      { key: "/hr",           label: "داشبورد HR" },
      { key: "/hr/employees", label: "کارمندان" },
      { key: "/hr/leaves",    label: "مرخصی‌ها" },
      { key: "/payroll",      label: "حقوق و دستمزد" },
    ],
  },
  {
    key: "procurement-group",
    icon: <ShoppingCartOutlined />,
    label: "تدارکات",
    children: [
      { key: "/procurement",           label: "داشبورد تدارکات" },
      { key: "/procurement/requests",  label: "درخواست‌های خرید" },
      { key: "/procurement/suppliers", label: "تامین‌کنندگان" },
    ],
  },
  {
    key: "/assets",
    icon: <AppstoreOutlined />,
    label: "دارایی‌ها",
  },
  {
    key: "/hse",
    icon: <SafetyOutlined />,
    label: "HSE",
  },
  {
    key: "/tasks",
    icon: <CheckSquareOutlined />,
    label: "وظایف",
  },
  {
    key: "analytics-group",
    icon: <BarChartOutlined />,
    label: "گزارشات",
    children: [
      { key: "/reports", label: "گزارشات" },
      { key: "/bi",      label: "هوش تجاری (BI)" },
    ],
  },
  {
    key: "ai-group",
    icon: <RobotOutlined />,
    label: "هوش مصنوعی",
    children: [
      { key: "/ai",               label: "داشبورد AI" },
      { key: "/ai/assistant",     label: "دستیار هوش مصنوعی" },
      { key: "/ai/analytics",     label: "تحلیل‌ها" },
      { key: "/ai/reports",       label: "گزارشات AI" },
      { key: "/ai/automation",    label: "اتوماسیون" },
    ],
  },
  {
    key: "/correspondence",
    icon: <MailOutlined />,
    label: "مکاتبات",
  },
  {
    key: "/messages",
    icon: <MessageOutlined />,
    label: "پیام‌ها",
  },
  {
    key: "/settings",
    icon: <SettingOutlined />,
    label: "تنظیمات",
  },
];

// ── Dropdown منوی کاربر ──────────────────────────────────────────────────────
const getUserMenuItems = (onLogout: () => void): MenuProps["items"] => [
  {
    key: "profile",
    icon: <UserOutlined />,
    label: "پروفایل",
  },
  {
    key: "divider",
    type: "divider",
  },
  {
    key: "logout",
    icon: <LogoutOutlined />,
    label: "خروج",
    danger: true,
    onClick: onLogout,
  },
];

// ============================================================================
export const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed]   = useState(false);
  const navigate                    = useNavigate();
  const location                    = useLocation();

  // مسیر فعلی برای highlight منوی فعال
  const selectedKey = location.pathname;

  // پیدا کردن open keys برای submenhu‌های باز
  const openKeys = menuItems
    .filter((item: any) => item.children?.some((child: any) => child.key === selectedKey))
    .map((item: any) => item.key as string);

  const handleMenuClick: MenuProps["onClick"] = ({ key }) => {
    navigate(key);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login", { replace: true });
  };

  return (
    <Layout style={{ minHeight: "100vh", direction: "rtl" }}>
      {/* ── Sidebar ───────────────────────────────────────────────────────── */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={240}
        style={{
          overflow: "auto",
          height: "100vh",
          position: "sticky",
          top: 0,
          right: 0,    // RTL: سمت راست
        }}
        trigger={null}
      >
        {/* Logo */}
        <div
          style={{
            height: 64,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "0 16px",
          }}
        >
          {!collapsed && (
            <span style={{ color: "#fff", fontSize: 18, fontWeight: "bold" }}>
              TOP WorX
            </span>
          )}
        </div>

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          defaultOpenKeys={openKeys}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>

      <Layout>
        {/* ── Header ──────────────────────────────────────────────────────── */}
        <Header
          style={{
            position: "sticky",
            top: 0,
            zIndex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 24px",
            background: "#fff",
            boxShadow: "0 1px 4px rgba(0,0,0,0.12)",
          }}
        >
          {/* دکمه collapse sidebar */}
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: 18 }}
          />

          {/* سمت چپ هدر: اعلان‌ها + تغییر تم + آواتار کاربر */}
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <ThemeToggle />

            <Tooltip title="اعلان‌ها">
              <Badge count={3} size="small">
                <Button
                  type="text"
                  icon={<BellOutlined style={{ fontSize: 18 }} />}
                  onClick={() => navigate("/messages")}
                />
              </Badge>
            </Tooltip>

            <Dropdown
              menu={{ items: getUserMenuItems(handleLogout) }}
              placement="bottomLeft"
              trigger={["click"]}
            >
              <Avatar
                icon={<UserOutlined />}
                style={{ cursor: "pointer", backgroundColor: "#1677ff" }}
              />
            </Dropdown>
          </div>
        </Header>

        {/* ── Main Content ────────────────────────────────────────────────── */}
        <Content
          style={{
            margin: "24px 16px",
            padding: 24,
            minHeight: 280,
            background: "#fff",
            borderRadius: 8,
            overflow: "auto",
          }}
        >
          {/* Outlet = صفحه فعلی بر اساس روت */}
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};
