import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { CarOutlined, DeleteOutlined, EditOutlined, EnvironmentOutlined, FieldTimeOutlined, PlusOutlined } from '@ant-design/icons';

const mockSupplyChain = [
  {
    id: 1,
    orderNumber: 'PO-001',
    supplier: 'تأمین‌کننده A',
    product: 'لپ‌تاپ Dell XPS 13',
    quantity: 50,
    orderDate: '2024-04-15',
    expectedDelivery: '2024-04-25',
    actualDelivery: '2024-04-23',
    status: 'delivered',
    cost: 1900000000,
    location: 'تهران',
    transportMethod: 'هوایی',
    trackingNumber: 'TRK-001',
  },
  {
    id: 2,
    orderNumber: 'PO-002',
    supplier: 'تأمین‌کننده B',
    product: 'ماوس بی‌سیم Logitech',
    quantity: 200,
    orderDate: '2024-04-18',
    expectedDelivery: '2024-04-28',
    actualDelivery: null,
    status: 'in-transit',
    cost: 130000000,
    location: 'اصفهان',
    transportMethod: 'زمینی',
    trackingNumber: 'TRK-002',
  },
  {
    id: 3,
    orderNumber: 'PO-003',
    supplier: 'تأمین‌کننده C',
    product: 'کیف چرمی مردانه',
    quantity: 100,
    orderDate: '2024-04-20',
    expectedDelivery: '2024-05-05',
    actualDelivery: null,
    status: 'ordered',
    cost: 90000000,
    location: 'مشهد',
    transportMethod: 'زمینی',
    trackingNumber: 'TRK-003',
  },
];

const orderStatuses = [
  { value: 'ordered', label: 'سفارش شده', color: 'info' },
  { value: 'confirmed', label: 'تأیید شده', color: 'warning' },
  { value: 'in-transit', label: 'در حال حمل', color: 'primary' },
  { value: 'delivered', label: 'تحویل شده', color: 'success' },
  { value: 'cancelled', label: 'لغو شده', color: 'error' },
];

const transportMethods = [
  'هوایی',
  'زمینی',
  'دریایی',
  'ریلی',
];

export const SupplyChainManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<any>(null);
  const [newOrder, setNewOrder] = useState({
    orderNumber: '',
    supplier: '',
    product: '',
    quantity: '',
    orderDate: '',
    expectedDelivery: '',
    cost: '',
    location: '',
    transportMethod: '',
    trackingNumber: '',
    notes: '',
  });

  const handleAddOrder = () => {
    setSelectedOrder(null);
    setOpenDialog(true);
  };

  const handleEditOrder = (order: any) => {
    setSelectedOrder(order);
    setNewOrder({
      orderNumber: order.orderNumber,
      supplier: order.supplier,
      product: order.product,
      quantity: order.quantity.toString(),
      orderDate: order.orderDate,
      expectedDelivery: order.expectedDelivery,
      cost: order.cost.toString(),
      location: order.location,
      transportMethod: order.transportMethod,
      trackingNumber: order.trackingNumber,
      notes: '',
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedOrder(null);
    setNewOrder({
      orderNumber: '',
      supplier: '',
      product: '',
      quantity: '',
      orderDate: '',
      expectedDelivery: '',
      cost: '',
      location: '',
      transportMethod: '',
      trackingNumber: '',
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

  const totalOrders = mockSupplyChain.length;
  const deliveredOrders = mockSupplyChain.filter(o => o.status === 'delivered').length;
  const inTransitOrders = mockSupplyChain.filter(o => o.status === 'in-transit').length;
  const totalCost = mockSupplyChain.reduce((sum, order) => sum + order.cost, 0);

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <LocalShipping style={{  mr: 1  }} />
            مدیریت زنجیره تأمین
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddOrder}
          >
            سفارش جدید
          </Button>
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
                {deliveredOrders}
              </Typography.Title>
              <Typography.Text>
                تحویل شده
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {inTransitOrders}
              </Typography.Title>
              <Typography.Text>
                در حال حمل
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalCost.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                کل هزینه
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>شماره سفارش</TableCell>
                <TableCell>تأمین‌کننده</TableCell>
                <TableCell>محصول</TableCell>
                <TableCell align="right">تعداد</TableCell>
                <TableCell>تاریخ سفارش</TableCell>
                <TableCell>تاریخ تحویل</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>روش حمل</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockSupplyChain.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>{order.orderNumber}</TableCell>
                  <TableCell>{order.supplier}</TableCell>
                  <TableCell>{order.product}</TableCell>
                  <TableCell align="right">{order.quantity}</TableCell>
                  <TableCell>{order.orderDate}</TableCell>
                  <TableCell>
                    {order.actualDelivery || order.expectedDelivery}
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={getStatusText(order.status)}
                      color={getStatusColor(order.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{order.transportMethod}</TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleEditOrder(order)}
                      >
                        <Edit />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleEditOrder(order)}
                      >
                        <Delete />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

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
                  label="شماره سفارش"
                  value={newOrder.orderNumber}
                  onChange={(e) => setNewOrder({ ...newOrder, orderNumber: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تأمین‌کننده"
                  value={newOrder.supplier}
                  onChange={(e) => setNewOrder({ ...newOrder, supplier: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="محصول"
                  value={newOrder.product}
                  onChange={(e) => setNewOrder({ ...newOrder, product: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تعداد"
                  type="number"
                  value={newOrder.quantity}
                  onChange={(e) => setNewOrder({ ...newOrder, quantity: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ سفارش"
                  type="date"
                  value={newOrder.orderDate}
                  onChange={(e) => setNewOrder({ ...newOrder, orderDate: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ تحویل مورد انتظار"
                  type="date"
                  value={newOrder.expectedDelivery}
                  onChange={(e) => setNewOrder({ ...newOrder, expectedDelivery: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="هزینه"
                  type="number"
                  value={newOrder.cost}
                  onChange={(e) => setNewOrder({ ...newOrder, cost: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="محل"
                  value={newOrder.location}
                  onChange={(e) => setNewOrder({ ...newOrder, location: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>روش حمل</span>
                  <Select
                    value={newOrder.transportMethod}
                    label="روش حمل"
                    onChange={(e) => setNewOrder({ ...newOrder, transportMethod: e.target.value })}
                  >
                    {transportMethods.map((method) => (
                      <MenuItem key={method} value={method}>
                        {method}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="شماره پیگیری"
                  value={newOrder.trackingNumber}
                  onChange={(e) => setNewOrder({ ...newOrder, trackingNumber: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newOrder.notes}
                  onChange={(e) => setNewOrder({ ...newOrder, notes: e.target.value })}
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
    </Card>
  );
}; 