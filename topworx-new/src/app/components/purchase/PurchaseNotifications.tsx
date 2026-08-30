import React, { useEffect, useState } from 'react';
import { Alert, Card, List, List.Item, Tag, Typography } from 'antd';
import { CheckCircleOutlined as SuccessIcon, CloseCircleOutlined as ErrorIcon, InfoCircleOutlined as InfoIcon, WarningOutlined as WarningIcon } from '@ant-design/icons';
import { usePurchaseOrders, usePurchaseInvoices, usePurchaseRequests } from '../../../api/procurement';

interface Notification {
  id: string;
  type: 'warning' | 'info' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: Date;
}

export const PurchaseNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [currentNotification, setCurrentNotification] = useState<Notification | null>(null);

  const { data: orders = [] } = usePurchaseOrders();
  const { data: invoices = [] } = usePurchaseInvoices();
  const { data: requests = [] } = usePurchaseRequests();

  useEffect(() => {
    const newNotifications: Notification[] = [];

    // بررسی سفارشات با تأخیر
    orders.forEach(order => {
      const expectedDate = new Date(order.expectedDeliveryDate);
      const today = new Date();
      const diffTime = expectedDate.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays < 0 && order.status !== 'دریافت شده') {
        newNotifications.push({
          id: `order-${order.id}`,
          type: 'error',
          title: 'تأخیر در تحویل سفارش',
          message: `سفارش ${order.orderNumber} با ${Math.abs(diffDays)} روز تأخیر مواجه شده است.`,
          timestamp: new Date()
        });
      } else if (diffDays <= 3 && diffDays >= 0 && order.status !== 'دریافت شده') {
        newNotifications.push({
          id: `order-${order.id}`,
          type: 'warning',
          title: 'نزدیک شدن به تاریخ تحویل',
          message: `سفارش ${order.orderNumber} تا ${diffDays} روز دیگر باید تحویل داده شود.`,
          timestamp: new Date()
        });
      }
    });

    // بررسی فاکتورهای معوق
    invoices.forEach(invoice => {
      const dueDate = new Date(invoice.dueDate);
      const today = new Date();
      const diffTime = dueDate.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays < 0 && invoice.status !== 'پرداخت شده') {
        newNotifications.push({
          id: `invoice-${invoice.id}`,
          type: 'error',
          title: 'فاکتور معوق',
          message: `فاکتور ${invoice.invoiceNumber} با ${Math.abs(diffDays)} روز تأخیر در پرداخت مواجه است.`,
          timestamp: new Date()
        });
      } else if (diffDays <= 7 && diffDays >= 0 && invoice.status !== 'پرداخت شده') {
        newNotifications.push({
          id: `invoice-${invoice.id}`,
          type: 'warning',
          title: 'نزدیک شدن به تاریخ سررسید',
          message: `فاکتور ${invoice.invoiceNumber} تا ${diffDays} روز دیگر سررسید می‌شود.`,
          timestamp: new Date()
        });
      }
    });

    // بررسی درخواست‌های با اولویت بالا
    requests.forEach(request => {
      if (request.priority === 'فوری' && request.status === 'در انتظار بررسی') {
        newNotifications.push({
          id: `request-${request.id}`,
          type: 'warning',
          title: 'درخواست فوری',
          message: `درخواست ${request.requestNumber} با اولویت فوری نیاز به بررسی دارد.`,
          timestamp: new Date()
        });
      }
    });

    // اعلان‌های موفقیت
    const completedOrders = orders.filter(o => o.status === 'دریافت شده').length;
    const paidInvoices = invoices.filter(i => i.status === 'پرداخت شده').length;

    if (completedOrders > 0) {
      newNotifications.push({
        id: 'completed-orders',
        type: 'success',
        title: 'سفارشات تکمیل شده',
        message: `${completedOrders} سفارش با موفقیت تحویل داده شده است.`,
        timestamp: new Date()
      });
    }

    if (paidInvoices > 0) {
      newNotifications.push({
        id: 'paid-invoices',
        type: 'success',
        title: 'فاکتورهای پرداخت شده',
        message: `${paidInvoices} فاکتور با موفقیت پرداخت شده است.`,
        timestamp: new Date()
      });
    }

    setNotifications(newNotifications);

    // نمایش اولین اعلان
    if (newNotifications.length > 0) {
      setCurrentNotification(newNotifications[0]);
      setOpenSnackbar(true);
    }
  }, [orders, invoices, requests]);

  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'success':
        return <SuccessIcon color="success" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      case 'success':
        return 'success';
      default:
        return 'info';
    }
  };

  return (
    <>
      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        {currentNotification && (
          <Alert
            onClose={handleCloseSnackbar}
            severity={getNotificationColor(currentNotification.type)}
            style={{  width: '100%'  }}
          >
            <AlertTitle>{currentNotification.title}</AlertTitle>
            {currentNotification.message}
          </Alert>
        )}
      </div>

      {notifications.length > 0 && (
        <Card style={{  mb: 2  }}>
          <div>
            <Typography.Title level={4}>
              اعلان‌های تدارکات ({notifications.length})
            </Typography.Title>
            <List>
              {notifications.slice(0, 5).map((notification) => (
                <ListItem key={notification.id}>
                  <ListItemIcon>
                    {getNotificationIcon(notification.type)}
                  </span>
                  <ListItemText
                    primary={notification.title}
                    secondary={
                      <div>
                        <Typography.Text>
                          {notification.message}
                        </Typography.Text>
                        <Tag
                          label={notification.timestamp.toLocaleString()}
                          size="small"
                          style={{  mt: 1  }}
                        />
                      </div>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </div>
        </Card>
      )}
    </>
  );
}; 