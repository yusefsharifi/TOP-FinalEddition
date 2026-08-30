import React, { useState } from 'react';
import { Alert, Badge, Button, Card, Col, Collapse, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { CarOutlined, CheckCircleOutlined, ClockCircleOutlined, CloseOutlined, CreditCardOutlined, EditOutlined, EnvironmentOutlined, EyeOutlined, InboxOutlined, MailOutlined, PhoneOutlined, PlusOutlined, PrinterOutlined, ShoppingCartOutlined } from '@ant-design/icons';

const mockOrders = [
  {
    id: 'ORD-001',
    customerName: 'علی احمدی',
    customerEmail: 'ali.ahmadi@example.com',
    customerPhone: '09123456789',
    customerAddress: 'تهران، خیابان ولیعصر، پلاک 123',
    orderDate: '1402/11/15',
    deliveryDate: '1402/11/20',
    status: 'processing',
    paymentStatus: 'paid',
    paymentMethod: 'online',
    totalAmount: 50000000,
    items: [
      {
        productId: 'PROD-001',
        productName: 'لپ‌تاپ Dell XPS 13',
        quantity: 1,
        unitPrice: 45000000,
        totalPrice: 45000000,
      },
      {
        productId: 'PROD-002',
        productName: 'ماوس بی‌سیم Logitech',
        quantity: 2,
        unitPrice: 2500000,
        totalPrice: 5000000,
      },
    ],
    shippingCost: 0,
    taxAmount: 4500000,
    discountAmount: 2000000,
    notes: 'تحویل در محل کار',
    trackingNumber: 'TRK-123456789',
    orderHistory: [
      { date: '1402/11/15 10:30', status: 'سفارش ثبت شد', user: 'سیستم' },
      { date: '1402/11/15 11:00', status: 'پرداخت تأیید شد', user: 'مدیر مالی' },
      { date: '1402/11/15 14:30', status: 'در حال پردازش', user: 'مدیر انبار' },
    ],
  },
  {
    id: 'ORD-002',
    customerName: 'فاطمه محمدی',
    customerEmail: 'fateme.mohammadi@example.com',
    customerPhone: '09187654321',
    customerAddress: 'اصفهان، خیابان چهارباغ، پلاک 456',
    orderDate: '1402/11/14',
    deliveryDate: '1402/11/18',
    status: 'pending',
    paymentStatus: 'pending',
    paymentMethod: 'bank_transfer',
    totalAmount: 400000,
    items: [
      {
        productId: 'PROD-003',
        productName: 'کیف چرمی مردانه',
        quantity: 1,
        unitPrice: 400000,
        totalPrice: 400000,
      },
    ],
    shippingCost: 50000,
    taxAmount: 36000,
    discountAmount: 0,
    notes: '',
    trackingNumber: '',
    orderHistory: [
      { date: '1402/11/14 16:45', status: 'سفارش ثبت شد', user: 'سیستم' },
    ],
  },
  {
    id: 'ORD-003',
    customerName: 'محمد رضایی',
    customerEmail: 'mohammad.rezaei@example.com',
    customerPhone: '09111111111',
    customerAddress: 'مشهد، خیابان امام رضا، پلاک 789',
    orderDate: '1402/11/13',
    deliveryDate: '1402/11/17',
    status: 'completed',
    paymentStatus: 'paid',
    paymentMethod: 'cash_on_delivery',
    totalAmount: 30000000,
    items: [
      {
        productId: 'PROD-004',
        productName: 'ساعت هوشمند Apple Watch',
        quantity: 1,
        unitPrice: 30000000,
        totalPrice: 30000000,
      },
    ],
    shippingCost: 0,
    taxAmount: 2700000,
    discountAmount: 1000000,
    notes: 'تحویل در منزل',
    trackingNumber: 'TRK-987654321',
    orderHistory: [
      { date: '1402/11/13 09:15', status: 'سفارش ثبت شد', user: 'سیستم' },
      { date: '1402/11/13 10:00', status: 'پرداخت تأیید شد', user: 'مدیر مالی' },
      { date: '1402/11/13 11:30', status: 'در حال پردازش', user: 'مدیر انبار' },
      { date: '1402/11/13 14:00', status: 'آماده ارسال', user: 'مدیر انبار' },
      { date: '1402/11/13 15:30', status: 'ارسال شد', user: 'پیک' },
      { date: '1402/11/17 10:00', status: 'تحویل شد', user: 'پیک' },
    ],
  },
];

const orderStatuses = [
  { value: 'pending', label: 'در انتظار', color: 'warning' },
  { value: 'processing', label: 'در حال پردازش', color: 'info' },
  { value: 'shipped', label: 'ارسال شده', color: 'primary' },
  { value: 'delivered', label: 'تحویل شده', color: 'success' },
  { value: 'cancelled', label: 'لغو شده', color: 'error' },
];

const paymentStatuses = [
  { value: 'pending', label: 'در انتظار', color: 'warning' },
  { value: 'paid', label: 'پرداخت شده', color: 'success' },
  { value: 'failed', label: 'ناموفق', color: 'error' },
  { value: 'refunded', label: 'بازگشت', color: 'info' },
];

const paymentMethods = [
  { value: 'online', label: 'آنلاین', color: 'primary' },
  { value: 'bank_transfer', label: 'انتقال بانکی', color: 'info' },
  { value: 'cash_on_delivery', label: 'پرداخت در محل', color: 'warning' },
  { value: 'check', label: 'چک', color: 'secondary' },
];

const orderSteps = [
  'ثبت سفارش',
  'تأیید پرداخت',
  'پردازش',
  'آماده ارسال',
  'ارسال',
  'تحویل',
];

export const OrderManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<any>(null);
  const [newOrder, setNewOrder] = useState({
    customerName: '',
    customerEmail: '',
    customerPhone: '',
    customerAddress: '',
    items: '',
    notes: '',
  });

  const handleAddOrder = () => {
    setSelectedOrder(null);
    setOpenDialog(true);
  };

  const handleEditOrder = (order: any) => {
    setSelectedOrder(order);
    setNewOrder({
      customerName: order.customerName,
      customerEmail: order.customerEmail,
      customerPhone: order.customerPhone,
      customerAddress: order.customerAddress,
      items: '',
      notes: order.notes,
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedOrder(null);
    setNewOrder({
      customerName: '',
      customerEmail: '',
      customerPhone: '',
      customerAddress: '',
      items: '',
      notes: '',
    });
  };

  const handleSaveOrder = () => {
    // در اینجا سفارش ذخیره می‌شود
    handleCloseDialog();
  };

  const getStatusColor = (status: string) => {
    const orderStatus = orderStatuses.find(s => s.value === status);
    return orderStatus ? orderStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const orderStatus = orderStatuses.find(s => s.value === status);
    return orderStatus ? orderStatus.label : 'نامشخص';
  };

  const getPaymentStatusColor = (status: string) => {
    const paymentStatus = paymentStatuses.find(s => s.value === status);
    return paymentStatus ? paymentStatus.color : 'default';
  };

  const getPaymentStatusText = (status: string) => {
    const paymentStatus = paymentStatuses.find(s => s.value === status);
    return paymentStatus ? paymentStatus.label : 'نامشخص';
  };

  const getPaymentMethodText = (method: string) => {
    const paymentMethod = paymentMethods.find(m => m.value === method);
    return paymentMethod ? paymentMethod.label : 'نامشخص';
  };

  const getStepIndex = (status: string) => {
    switch (status) {
      case 'pending':
        return 0;
      case 'processing':
        return 2;
      case 'shipped':
        return 4;
      case 'delivered':
        return 5;
      default:
        return 0;
    }
  };

  const totalOrders = mockOrders.length;
  const pendingOrders = mockOrders.filter(o => o.status === 'pending').length;
  const processingOrders = mockOrders.filter(o => o.status === 'processing').length;
  const completedOrders = mockOrders.filter(o => o.status === 'delivered').length;
  const totalRevenue = mockOrders.reduce((sum, o) => sum + o.totalAmount, 0);

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          مدیریت سفارشات
        </Typography.Title>
        <div>
          <Button
            variant="outlined"
            startIcon={<Print />}
          >
            چاپ گزارش
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddOrder}
          >
            سفارش جدید
          </Button>
        </div>
      </div>

      {/* خلاصه آمار */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {totalOrders}
            </Typography.Title>
            <Typography.Text>
              کل سفارشات
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {pendingOrders}
            </Typography.Title>
            <Typography.Text>
              در انتظار
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {processingOrders}
            </Typography.Title>
            <Typography.Text>
              در حال پردازش
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {totalRevenue.toLocaleString()} تومان
            </Typography.Title>
            <Typography.Text>
              کل درآمد
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      {/* هشدار سفارشات در انتظار */}
      {pendingOrders > 0 && (
        <Alert severity="warning" style={{  mb: 3  }}>
          {pendingOrders} سفارش در انتظار پردازش وجود دارد.
        </Alert>
      )}

      {/* لیست سفارشات */}
      {mockOrders.map((order) => (
        <Accordion key={order.id} style={{  mb: 2  }}>
          <AccordionSummary expandIcon={<Visibility />}>
            <div>
              <div>
                <Typography.Title level={4}>{order.id}</Typography.Title>
                <Typography.Text>
                  {order.customerName} • {order.orderDate}
                </Typography.Text>
              </div>
              <div>
                <Tag
                  label={order.totalAmount.toLocaleString() + ' تومان'}
                  color="success"
                  size="small"
                />
                <Tag
                  label={getStatusText(order.status)}
                  color={getStatusColor(order.status) as any}
                  size="small"
                />
                <Tag
                  label={getPaymentStatusText(order.paymentStatus)}
                  color={getPaymentStatusColor(order.paymentStatus) as any}
                  size="small"
                />
              </div>
            </div>
          </div>
          <AccordionDetails>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                {/* روند سفارش */}
                <Typography variant="subtitle2" gutterBottom>
                  روند سفارش:
                </Typography>
                <Stepper activeStep={getStepIndex(order.status)} orientation="horizontal" style={{  mb: 3  }}>
                  {orderSteps.map((step, index) => (
                    <Step key={step}>
                      <StepLabel>{step}</StepLabel>
                    </Step>
                  ))}
                </Stepper>

                {/* محصولات سفارش */}
                <Typography variant="subtitle2" gutterBottom>
                  محصولات سفارش:
                </Typography>
                <TableContainer component={Paper} style={{  mb: 3  }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>محصول</TableCell>
                        <TableCell align="right">تعداد</TableCell>
                        <TableCell align="right">قیمت واحد</TableCell>
                        <TableCell align="right">قیمت کل</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {order.items.map((item, index) => (
                        <TableRow key={index}>
                          <TableCell>{item.productName}</TableCell>
                          <TableCell align="right">{item.quantity}</TableCell>
                          <TableCell align="right">{item.unitPrice.toLocaleString()} تومان</TableCell>
                          <TableCell align="right">{item.totalPrice.toLocaleString()} تومان</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* تاریخچه سفارش */}
                <Typography variant="subtitle2" gutterBottom>
                  تاریخچه سفارش:
                </Typography>
                <div>
                  {order.orderHistory.map((history, index) => (
                    <div>
                      <Typography.Text>{history.status}</Typography.Text>
                      <div>
                        <Typography variant="caption" color="textSecondary">
                          {history.date}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {history.user}
                        </Typography>
                      </div>
                    </div>
                  ))}
                </div>
              </Col>
              
              <Col xs={Math.round(12 / 12 * 24)}>
                <Card style={{  p: 2  }}>
                  <Typography variant="subtitle2" gutterBottom>
                    اطلاعات مشتری
                  </Typography>
                  <div>
                    <div>
                      <Phone fontSize="small" />
                      <Typography.Text>{order.customerPhone}</Typography.Text>
                    </div>
                    <div>
                      <Email fontSize="small" />
                      <Typography.Text>{order.customerEmail}</Typography.Text>
                    </div>
                    <div>
                      <LocationOn fontSize="small" />
                      <Typography.Text>{order.customerAddress}</Typography.Text>
                    </div>
                  </div>

                  <Typography variant="subtitle2" gutterBottom>
                    جزئیات پرداخت
                  </Typography>
                  <div>
                    <div>
                      <Typography.Text>روش پرداخت:</Typography.Text>
                      <Typography.Text>{getPaymentMethodText(order.paymentMethod)}</Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>هزینه ارسال:</Typography.Text>
                      <Typography.Text>{order.shippingCost.toLocaleString()} تومان</Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>مالیات:</Typography.Text>
                      <Typography.Text>{order.taxAmount.toLocaleString()} تومان</Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>تخفیف:</Typography.Text>
                      <Typography.Text>
                        -{order.discountAmount.toLocaleString()} تومان
                      </Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>مجموع:</Typography.Text>
                      <Typography.Text>
                        {order.totalAmount.toLocaleString()} تومان
                      </Typography.Text>
                    </div>
                  </div>

                  {order.trackingNumber && (
                    <div style={{  mb: 2  }}>
                      <Typography variant="subtitle2" gutterBottom>
                        شماره پیگیری:
                      </Typography>
                      <Tag label={order.trackingNumber} variant="outlined" />
                    </div>
                  )}

                  <div style={{  mt: 2  }}>
                    <Button
                      variant="outlined"
                      size="small"
                      fullWidth
                      onClick={() => handleEditOrder(order)}
                    >
                      ویرایش سفارش
                    </Button>
                  </div>
                </Card>
              </Col>
            </Row>
          </div>
        </div>
      ))}

      {/* Dialog برای اضافه/ویرایش سفارش */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          {selectedOrder ? 'ویرایش سفارش' : 'افزودن سفارش جدید'}
        </div>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="نام مشتری"
                value={newOrder.customerName}
                onChange={(e) => setNewOrder({ ...newOrder, customerName: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="ایمیل مشتری"
                type="email"
                value={newOrder.customerEmail}
                onChange={(e) => setNewOrder({ ...newOrder, customerEmail: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="شماره تماس"
                value={newOrder.customerPhone}
                onChange={(e) => setNewOrder({ ...newOrder, customerPhone: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="آدرس"
                value={newOrder.customerAddress}
                onChange={(e) => setNewOrder({ ...newOrder, customerAddress: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="محصولات (با کاما جدا کنید)"
                value={newOrder.items}
                onChange={(e) => setNewOrder({ ...newOrder, items: e.target.value })}
                placeholder="مثال: لپ‌تاپ Dell XPS 13, ماوس بی‌سیم Logitech"
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="یادداشت"
                multiline
                rows={3}
                value={newOrder.notes}
                onChange={(e) => setNewOrder({ ...newOrder, notes: e.target.value })}
                placeholder="توضیحات سفارش..."
              />
            </Col>
          </Row>
        </div>
        <div>
          <Button onClick={handleCloseDialog}>انصراف</Button>
          <Button onClick={handleSaveOrder} variant="contained">
            {selectedOrder ? 'ویرایش' : 'ثبت'}
          </Button>
        </div>
      </Modal>
    </div>
  );
}; 