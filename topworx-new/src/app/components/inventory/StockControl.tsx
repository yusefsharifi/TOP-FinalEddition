import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Row, Select, Table, Tag, Typography } from 'antd';
import { DeleteOutlined, EditOutlined, ExportOutlined, FallOutlined, InboxOutlined, PlusOutlined, RiseOutlined } from '@ant-design/icons';

const mockStockMovements = [
  {
    id: 1,
    productName: 'لپ‌تاپ Dell XPS 13',
    sku: 'LAP-001',
    type: 'in',
    quantity: 50,
    date: '2024-04-22',
    reference: 'PO-001',
    warehouse: 'انبار مرکزی',
    location: 'قفسه A-1',
    operator: 'علی احمدی',
    notes: 'سفارش از تأمین‌کننده A',
  },
  {
    id: 2,
    productName: 'ماوس بی‌سیم Logitech',
    sku: 'MOU-002',
    type: 'out',
    quantity: -25,
    date: '2024-04-22',
    reference: 'SO-001',
    warehouse: 'انبار مرکزی',
    location: 'قفسه A-2',
    operator: 'مریم محمدی',
    notes: 'فروش به مشتری ABC',
  },
  {
    id: 3,
    productName: 'کیف چرمی مردانه',
    sku: 'BAG-003',
    type: 'adjustment',
    quantity: 5,
    date: '2024-04-21',
    reference: 'ADJ-001',
    warehouse: 'انبار شمال',
    location: 'قفسه B-1',
    operator: 'حسن رضایی',
    notes: 'تعدیل موجودی - کالای آسیب دیده',
  },
];

const movementTypes = [
  { value: 'in', label: 'ورود کالا', color: 'success' },
  { value: 'out', label: 'خروج کالا', color: 'error' },
  { value: 'adjustment', label: 'تعدیل موجودی', color: 'warning' },
  { value: 'transfer', label: 'انتقال', color: 'info' },
];

export const StockControl: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedMovement, setSelectedMovement] = useState<any>(null);
  const [newMovement, setNewMovement] = useState({
    productName: '',
    sku: '',
    type: 'in',
    quantity: '',
    date: '',
    reference: '',
    warehouse: '',
    location: '',
    operator: '',
    notes: '',
  });

  const handleAddMovement = () => {
    setSelectedMovement(null);
    setOpenDialog(true);
  };

  const handleEditMovement = (movement: any) => {
    setSelectedMovement(movement);
    setNewMovement({
      productName: movement.productName,
      sku: movement.sku,
      type: movement.type,
      quantity: movement.quantity.toString(),
      date: movement.date,
      reference: movement.reference,
      warehouse: movement.warehouse,
      location: movement.location,
      operator: movement.operator,
      notes: movement.notes,
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedMovement(null);
    setNewMovement({
      productName: '',
      sku: '',
      type: 'in',
      quantity: '',
      date: '',
      reference: '',
      warehouse: '',
      location: '',
      operator: '',
      notes: '',
    });
  };

  const handleSaveMovement = () => {
    // در اینجا حرکت موجودی ذخیره می‌شود
    handleCloseDialog();
  };

  const getMovementTypeColor = (type: string) => {
    const movementType = movementTypes.find(t => t.value === type);
    return movementType ? movementType.color : 'default';
  };

  const getMovementTypeText = (type: string) => {
    const movementType = movementTypes.find(t => t.value === type);
    return movementType ? movementType.label : 'نامشخص';
  };

  const totalIn = mockStockMovements
    .filter(m => m.type === 'in')
    .reduce((sum, m) => sum + m.quantity, 0);

  const totalOut = Math.abs(mockStockMovements
    .filter(m => m.type === 'out')
    .reduce((sum, m) => sum + m.quantity, 0));

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            کنترل موجودی
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddMovement}
          >
            ثبت حرکت موجودی
          </Button>
        </div>

        {/* خلاصه آمار */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalIn}
              </Typography.Title>
              <Typography.Text>
                کل ورودی
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalOut}
              </Typography.Title>
              <Typography.Text>
                کل خروجی
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalIn - totalOut}
              </Typography.Title>
              <Typography.Text>
                موجودی خالص
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>محصول</TableCell>
                <TableCell>نوع حرکت</TableCell>
                <TableCell align="right">تعداد</TableCell>
                <TableCell>تاریخ</TableCell>
                <TableCell>مرجع</TableCell>
                <TableCell>انبار</TableCell>
                <TableCell>محل</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockStockMovements.map((movement) => (
                <TableRow key={movement.id}>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {movement.productName}
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {movement.sku}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={getMovementTypeText(movement.type)}
                      color={getMovementTypeColor(movement.type) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Typography
                      color={movement.quantity >= 0 ? 'success.main' : 'error.main'}
                    >
                      {movement.quantity >= 0 ? '+' : ''}{movement.quantity}
                    </Typography>
                  </TableCell>
                  <TableCell>{movement.date}</TableCell>
                  <TableCell>{movement.reference}</TableCell>
                  <TableCell>{movement.warehouse}</TableCell>
                  <TableCell>{movement.location}</TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleEditMovement(movement)}
                      >
                        <Edit />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleEditMovement(movement)}
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

        {/* Dialog برای ثبت حرکت موجودی */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedMovement ? 'ویرایش حرکت موجودی' : 'ثبت حرکت موجودی جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام محصول"
                  value={newMovement.productName}
                  onChange={(e) => setNewMovement({ ...newMovement, productName: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="SKU"
                  value={newMovement.sku}
                  onChange={(e) => setNewMovement({ ...newMovement, sku: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>نوع حرکت</span>
                  <Select
                    value={newMovement.type}
                    label="نوع حرکت"
                    onChange={(e) => setNewMovement({ ...newMovement, type: e.target.value })}
                  >
                    {movementTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تعداد"
                  type="number"
                  value={newMovement.quantity}
                  onChange={(e) => setNewMovement({ ...newMovement, quantity: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ"
                  type="date"
                  value={newMovement.date}
                  onChange={(e) => setNewMovement({ ...newMovement, date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="شماره مرجع"
                  value={newMovement.reference}
                  onChange={(e) => setNewMovement({ ...newMovement, reference: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="انبار"
                  value={newMovement.warehouse}
                  onChange={(e) => setNewMovement({ ...newMovement, warehouse: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="محل در انبار"
                  value={newMovement.location}
                  onChange={(e) => setNewMovement({ ...newMovement, location: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="اپراتور"
                  value={newMovement.operator}
                  onChange={(e) => setNewMovement({ ...newMovement, operator: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newMovement.notes}
                  onChange={(e) => setNewMovement({ ...newMovement, notes: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveMovement} variant="contained">
              {selectedMovement ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 