import React, { useState } from 'react';
import { Divider, Drawer, List, List.Item, Typography } from 'antd';
import { ApartmentOutlined as AccountTreeIcon, BankOutlined as AccountBalanceIcon, BankOutlined as BusinessIcon, BarChartOutlined as AssessmentIcon, BarChartOutlined as AssessmentIcon2, BarChartOutlined as BarChartIcon, BellOutlined as NotificationsIcon, CalendarOutlined as CalendarTodayIcon, CarOutlined as LocalShippingIcon, ClockCircleOutlined as AccessTimeIcon, CreditCardOutlined as PaymentIcon, DashboardOutlined as DashboardIcon, DollarOutlined as AttachMoneyIcon, DownOutlined, FieldTimeOutlined as TimelineIcon, FileTextOutlined as DescriptionIcon, FileTextOutlined as ReceiptIcon, InboxOutlined as InventoryIcon, PieChartOutlined as PieChartIcon, QuestionCircleOutlined as HelpIcon, SafetyOutlined as SecurityIcon, SettingOutlined as SettingsIcon, ShoppingCartOutlined as ShoppingCartIcon, TeamOutlined as PeopleIcon, ToolOutlined as WorkIcon, UpOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation } from 'react-router-dom';

interface MenuItem {
  id: string;
  title: string;
  icon: React.ReactNode;
  path?: string;
  children?: MenuItem[];
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    title: 'menu.dashboard',
    icon: <DashboardIcon />,
    path: '/dashboard',
  },
  {
    id: 'crm',
    title: 'menu.crm',
    icon: <PeopleIcon />,
    children: [
      {
        id: 'customers',
        title: 'menu.crm.customers',
        icon: <PeopleIcon />,
        path: '/crm/customers',
      },
      {
        id: 'opportunities',
        title: 'menu.crm.opportunities',
        icon: <BusinessIcon />,
        path: '/crm/opportunities',
      },
      {
        id: 'contacts',
        title: 'menu.crm.contacts',
        icon: <PeopleIcon />,
        path: '/crm/contacts',
      },
      {
        id: 'leads',
        title: 'menu.crm.leads',
        icon: <DescriptionIcon />,
        path: '/crm/leads',
      },
      {
        id: 'campaigns',
        title: 'menu.crm.campaigns',
        icon: <AssessmentIcon />,
        path: '/crm/campaigns',
      },
    ],
  },
  {
    id: 'inventory',
    title: 'menu.inventory',
    icon: <InventoryIcon />,
    children: [
      {
        id: 'products',
        title: 'menu.inventory.products',
        icon: <InventoryIcon />,
        path: '/inventory/products',
      },
      {
        id: 'warehouse',
        title: 'menu.inventory.warehouse',
        icon: <LocalShippingIcon />,
        path: '/inventory/warehouse',
      },
      {
        id: 'orders',
        title: 'menu.inventory.orders',
        icon: <ShoppingCartIcon />,
        path: '/inventory/orders',
      },
      {
        id: 'stock',
        title: 'menu.inventory.stock',
        icon: <InventoryIcon />,
        path: '/inventory/stock',
      },
      {
        id: 'transfers',
        title: 'menu.inventory.transfers',
        icon: <LocalShippingIcon />,
        path: '/inventory/transfers',
      },
    ],
  },
  {
    id: 'accounting',
    title: 'menu.accounting',
    icon: <AccountBalanceIcon />,
    children: [
      {
        id: 'accounts',
        title: 'menu.accounting.accounts',
        icon: <AccountTreeIcon />,
        path: '/accounting/accounts',
      },
      {
        id: 'invoices',
        title: 'menu.accounting.invoices',
        icon: <ReceiptIcon />,
        path: '/accounting/invoices',
      },
      {
        id: 'payments',
        title: 'menu.accounting.payments',
        icon: <PaymentIcon />,
        path: '/accounting/payments',
      },
      {
        id: 'reports',
        title: 'menu.accounting.reports',
        icon: <AssessmentIcon2 />,
        path: '/accounting/reports',
      },
      {
        id: 'taxes',
        title: 'menu.accounting.taxes',
        icon: <AttachMoneyIcon />,
        path: '/accounting/taxes',
      },
    ],
  },
  {
    id: 'hr',
    title: 'menu.hr',
    icon: <WorkIcon />,
    children: [
      {
        id: 'employees',
        title: 'menu.hr.employees',
        icon: <PeopleIcon />,
        path: '/hr/employees',
      },
      {
        id: 'attendance',
        title: 'menu.hr.attendance',
        icon: <AccessTimeIcon />,
        path: '/hr/attendance',
      },
      {
        id: 'payroll',
        title: 'menu.hr.payroll',
        icon: <AttachMoneyIcon />,
        path: '/hr/payroll',
      },
      {
        id: 'leaves',
        title: 'menu.hr.leaves',
        icon: <CalendarTodayIcon />,
        path: '/hr/leaves',
      },
      {
        id: 'performance',
        title: 'menu.hr.performance',
        icon: <AssessmentIcon2 />,
        path: '/hr/performance',
      },
    ],
  },
  {
    id: 'reports',
    title: 'menu.reports',
    icon: <AssessmentIcon />,
    children: [
      {
        id: 'sales',
        title: 'menu.reports.sales',
        icon: <BarChartIcon />,
        path: '/reports/sales',
      },
      {
        id: 'inventory',
        title: 'menu.reports.inventory',
        icon: <PieChartIcon />,
        path: '/reports/inventory',
      },
      {
        id: 'financial',
        title: 'menu.reports.financial',
        icon: <TimelineIcon />,
        path: '/reports/financial',
      },
      {
        id: 'hr',
        title: 'menu.reports.hr',
        icon: <AssessmentIcon2 />,
        path: '/reports/hr',
      },
    ],
  },
  {
    id: 'settings',
    title: 'menu.settings',
    icon: <SettingsIcon />,
    children: [
      {
        id: 'general',
        title: 'menu.settings.general',
        icon: <SettingsIcon />,
        path: '/settings/general',
      },
      {
        id: 'security',
        title: 'menu.settings.security',
        icon: <SecurityIcon />,
        path: '/settings/security',
      },
      {
        id: 'notifications',
        title: 'menu.settings.notifications',
        icon: <NotificationsIcon />,
        path: '/settings/notifications',
      },
      {
        id: 'help',
        title: 'menu.settings.help',
        icon: <HelpIcon />,
        path: '/settings/help',
      },
    ],
  },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const handleItemClick = (item: MenuItem) => {
    if (item.children) {
      setExpandedItems((prev) =>
        prev.includes(item.id)
          ? prev.filter((id) => id !== item.id)
          : [...prev, item.id]
      );
    } else if (item.path) {
      navigate(item.path);
      onClose();
    }
  };

  const isItemActive = (item: MenuItem): boolean => {
    if (item.path) {
      return location.pathname === item.path;
    }
    if (item.children) {
      return item.children.some((child) => isItemActive(child));
    }
    return false;
  };

  const renderMenuItem = (item: MenuItem, level: number = 0) => {
    const isActive = isItemActive(item);
    const isExpanded = expandedItems.includes(item.id);

    return (
      <React.Fragment key={item.id}>
        <ListItem
          button
          onClick={() => handleItemClick(item)}
          sx={{
            pl: level * 2,
            backgroundColor: isActive ? 'action.selected' : 'transparent',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
        >
          <ListItemIcon
            style={{ 
              minWidth: 40,
              color: isActive ? 'primary.main' : 'inherit',
             }}
          >
            {item.icon}
          </span>
          <ListItemText
            primary={t(item.title)}
            sx={{
              '& .MuiTypography-root': {
                color: isActive ? 'primary.main' : 'inherit',
                fontWeight: isActive ? 600 : 400,
              },
            }}
          />
          {item.children && (isExpanded ? <ExpandLess /> : <ExpandMore />)}
        </ListItem>
        {item.children && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children.map((child) => renderMenuItem(child, level + 1))}
            </List>
          </div>
        )}
      </React.Fragment>
    );
  };

  return (
    <Drawer
      variant="persistent"
      anchor="right"
      open={open}
      sx={{
        width: 280,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 280,
          boxSizing: 'border-box',
          borderLeft: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      <div style={{  p: 2  }}>
        <Typography.Title level={4}>
          {t('common.appName')}
        </Typography.Title>
      </div>
      <Divider />
      <List style={{  pt: 1  }}>
        {menuItems.map((item) => renderMenuItem(item))}
      </List>
    </Drawer>
  );
};

export default Sidebar; 