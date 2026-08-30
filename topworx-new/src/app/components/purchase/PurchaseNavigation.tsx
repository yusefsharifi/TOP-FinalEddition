import React from 'react';
import { Divider, Drawer, List, List.Item, Typography } from 'antd';
import { BankOutlined as SuppliersIcon, BarChartOutlined as ReportsIcon, CheckSquareOutlined as RequestsIcon, DashboardOutlined as DashboardIcon, FileTextOutlined as InvoicesIcon, ShoppingCartOutlined as OrdersIcon } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

interface PurchaseNavigationProps {
  open: boolean;
  onClose: () => void;
}

const menuItems = [
  { text: 'داشبورد', icon: <DashboardIcon />, path: '/purchase/dashboard' },
  { text: 'سفارشات خرید', icon: <OrdersIcon />, path: '/purchase/orders' },
  { text: 'درخواست‌های خرید', icon: <RequestsIcon />, path: '/purchase/requests' },
  { text: 'فاکتورهای خرید', icon: <InvoicesIcon />, path: '/purchase/invoices' },
  { text: 'تأمین‌کنندگان', icon: <SuppliersIcon />, path: '/purchase/suppliers' },
  { text: 'گزارشات', icon: <ReportsIcon />, path: '/purchase/reports' }
];

export const PurchaseNavigation: React.FC<PurchaseNavigationProps> = ({ open, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path: string) => {
    navigate(path);
    onClose();
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: 280,
          boxSizing: 'border-box',
        },
      }}
    >
      <div style={{  p: 2  }}>
        <Typography.Title level={4}>
          تدارکات و خرید
        </Typography.Title>
      </div>
      
      <Divider />
      
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.light',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                  },
                },
              }}
            >
              <ListItemIcon style={{  color: location.pathname === item.path ? 'primary.main' : 'inherit'  }}>
                {item.icon}
              </span>
              <ListItemText 
                primary={item.text}
                style={{  
                  color: location.pathname === item.path ? 'primary.main' : 'inherit',
                  fontWeight: location.pathname === item.path ? 'bold' : 'normal'
                 }}
              />
            </div>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}; 