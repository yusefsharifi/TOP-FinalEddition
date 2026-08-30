import React, { useState } from 'react';
import { Breadcrumb, Button, Divider, Drawer, List, List.Item, Typography, Typography.Link } from 'antd';
import { BankOutlined as SuppliersIcon, BarChartOutlined as ReportsIcon, CheckSquareOutlined as RequestsIcon, DashboardOutlined as DashboardIcon, FileTextOutlined as InvoicesIcon, MenuOutlined as MenuIcon, SettingOutlined as SettingsIcon, ShoppingCartOutlined as OrdersIcon } from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { PurchaseNotifications } from './PurchaseNotifications';

const drawerWidth = 280;

const menuItems = [
  { text: 'داشبورد', icon: <DashboardIcon />, path: '/purchase/dashboard' },
  { text: 'سفارشات خرید', icon: <OrdersIcon />, path: '/purchase/orders' },
  { text: 'درخواست‌های خرید', icon: <RequestsIcon />, path: '/purchase/requests' },
  { text: 'فاکتورهای خرید', icon: <InvoicesIcon />, path: '/purchase/invoices' },
  { text: 'تأمین‌کنندگان', icon: <SuppliersIcon />, path: '/purchase/suppliers' },
  { text: 'گزارشات', icon: <ReportsIcon />, path: '/purchase/reports' },
  { text: 'تنظیمات', icon: <SettingsIcon />, path: '/purchase/settings' }
];

export const PurchaseLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setMobileOpen(false);
  };

  const getBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs = [];
    
    for (let i = 0; i < pathSegments.length; i++) {
      const segment = pathSegments[i];
      const path = '/' + pathSegments.slice(0, i + 1).join('/');
      
      let label = segment;
      if (segment === 'purchase') label = 'تدارکات';
      else if (segment === 'dashboard') label = 'داشبورد';
      else if (segment === 'orders') label = 'سفارشات';
      else if (segment === 'requests') label = 'درخواست‌ها';
      else if (segment === 'invoices') label = 'فاکتورها';
      else if (segment === 'suppliers') label = 'تأمین‌کنندگان';
      else if (segment === 'reports') label = 'گزارشات';
      else if (segment === 'settings') label = 'تنظیمات';
      
      breadcrumbs.push({ label, path });
    }
    
    return breadcrumbs;
  };

  const drawer = (
    <div>
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
    </div>
  );

  return (
    <div style={{  display: 'flex'  }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <Button type="text"
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </Button>
          <Typography.Title level={4}>
            سیستم تدارکات و خرید
          </Typography.Title>
        </Toolbar>
      </AppBar>

      <div>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </div>

      <div>
        <Breadcrumbs style={{  mb: 3  }}>
          {getBreadcrumbs().map((breadcrumb, index) => (
            <Link
              key={breadcrumb.path}
              color={index === getBreadcrumbs().length - 1 ? 'text.primary' : 'inherit'}
              href={breadcrumb.path}
              underline="hover"
              style={{  cursor: 'pointer'  }}
            >
              {breadcrumb.label}
            </Link>
          ))}
        </Breadcrumbs>
        
        <PurchaseNotifications />
        <Outlet />
      </div>
    </div>
  );
}; 