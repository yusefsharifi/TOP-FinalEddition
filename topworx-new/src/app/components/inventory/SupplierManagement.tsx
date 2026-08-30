import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Rate, Row, Select, Table, Tag, Typography } from 'antd';
import { BankOutlined, DeleteOutlined, EditOutlined, MailOutlined, PhoneOutlined, PlusOutlined, StarOutlined } from '@ant-design/icons';

const mockSuppliers = [
  {
    id: 1,
    name: 'تأمین‌کننده A',
    contactPerson: 'علی احمدی',
    phone: '+98-912-123-4567',
    email: 'info@suppliera.com',
    address: 'تهران، خیابان ولیعصر، پلاک 123',
    category: 'الکترونیک',
    rating: 4.5,
    totalOrders: 45,
    onTimeDelivery: 95,
    qualityScore: 92,
    costScore: 88,
    status: 'active',
    contractEndDate: '2024-12-31',
    totalSpent: 2500000000,
  },
  {
    id: 2,
    name: 'تأمین‌کننده B',
    contactPerson: 'مریم محمدی',
    phone: '+98-912-123-4568',
    email: 'sales@supplierb.com',
    address: 'اصفهان، خیابان چهارباغ، پلاک 456',
    category: 'پوشاک',
    rating: 4.2,
    totalOrders: 32,
    onTimeDelivery: 88,
    qualityScore: 89,
    costScore: 85,
    status: 'active',
    contractEndDate: '2024-10-15',
    totalSpent: 1800000000,
  },
  {
    id: 3,
    name: 'تأمین‌کننده C',
    contactPerson: 'حسن رضایی',
    phone: '+98-912-123-4569',
    email: 'contact@supplierc.com',
    address: 'مشهد، خیابان امام رضا، پلاک 789',
    category: 'لوازم خانگی',
    rating: 3.8,
    totalOrders: 28,
    onTimeDelivery: 82,
    qualityScore: 85,
    costScore: 90,
    status: 'warning',
    contractEndDate: '2024-08-20',
    totalSpent: 1200000000,
  },
];

const supplierCategories = [
  'الکترونیک',
  'پوشاک',
  'لوازم خانگی',
  'کتاب',
  'خودرو',
  'سایر',
];

const supplierStatuses = [
  'فعال',
  'هشدار',
  'غیرفعال',
  'در حال بررسی',
];

export const SupplierManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<any>(null);
  const [newSupplier, setNewSupplier] = useState({
    name: '',
    contactPerson: '',
    phone: '',
    email: '',
    address: '',
    category: '',
    contractEndDate: '',
    notes: '',
  });

  const handleAddSupplier = () => {
    setSelectedSupplier(null);
    setOpenDialog(true);
  };

  const handleEditSupplier = (supplier: any) => {
    setSelectedSupplier(supplier);
    setNewSupplier({
      name: supplier.name,
      contactPerson: supplier.contactPerson,
      phone: supplier.phone,
      email: supplier.email,
      address: supplier.address,
      category: supplier.category,
      contractEndDate: supplier.contractEndDate,
      notes: '',
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedSupplier(null);
    setNewSupplier({
      name: '',
      contactPerson: '',
      phone: '',
      email: '',
      address: '',
      category: '',
      contractEndDate: '',
      notes: '',
    });
  };

  const handleSaveSupplier = () => {
    // در اینجا تأمین‌کننده ذخیره می‌شود
    handleCloseDialog();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'warning':
        return 'warning';
      case 'inactive':
        return 'error';
      case 'review':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'فعال';
      case 'warning':
        return 'هشدار';
      case 'inactive':
        return 'غیرفعال';
      case 'review':
        return 'در حال بررسی';
      default:
        return 'نامشخص';
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 80) return 'warning';
    return 'error';
  };

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <Business style={{  mr: 1  }} />
            مدیریت تأمین‌کنندگان
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddSupplier}
          >
            تأمین‌کننده جدید
          </Button>
        </div>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام تأمین‌کننده</TableCell>
                <TableCell>دسته‌بندی</TableCell>
                <TableCell>تماس</TableCell>
                <TableCell>امتیاز</TableCell>
                <TableCell>تحویل به موقع</TableCell>
                <TableCell>کیفیت</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockSuppliers.map((supplier) => (
                <TableRow key={supplier.id}>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {supplier.name}
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {supplier.contactPerson}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell>{supplier.category}</TableCell>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {supplier.phone}
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {supplier.email}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <Rating value={supplier.rating} readOnly size="small" />
                      <Typography.Text>
                        {supplier.rating}
                      </Typography.Text>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={`${supplier.onTimeDelivery}%`}
                      color={supplier.onTimeDelivery >= 90 ? 'success' : supplier.onTimeDelivery >= 80 ? 'warning' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={`${supplier.qualityScore}%`}
                      color={getQualityColor(supplier.qualityScore) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={getStatusText(supplier.status)}
                      color={getStatusColor(supplier.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleEditSupplier(supplier)}
                      >
                        <Edit />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleEditSupplier(supplier)}
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

        {/* Dialog برای اضافه/ویرایش تأمین‌کننده */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedSupplier ? 'ویرایش تأمین‌کننده' : 'افزودن تأمین‌کننده جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام تأمین‌کننده"
                  value={newSupplier.name}
                  onChange={(e) => setNewSupplier({ ...newSupplier, name: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="شخص تماس"
                  value={newSupplier.contactPerson}
                  onChange={(e) => setNewSupplier({ ...newSupplier, contactPerson: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="شماره تماس"
                  value={newSupplier.phone}
                  onChange={(e) => setNewSupplier({ ...newSupplier, phone: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="ایمیل"
                  type="email"
                  value={newSupplier.email}
                  onChange={(e) => setNewSupplier({ ...newSupplier, email: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>دسته‌بندی</span>
                  <Select
                    value={newSupplier.category}
                    label="دسته‌بندی"
                    onChange={(e) => setNewSupplier({ ...newSupplier, category: e.target.value })}
                  >
                    {supplierCategories.map((category) => (
                      <MenuItem key={category} value={category}>
                        {category}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ پایان قرارداد"
                  type="date"
                  value={newSupplier.contractEndDate}
                  onChange={(e) => setNewSupplier({ ...newSupplier, contractEndDate: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="آدرس"
                  value={newSupplier.address}
                  onChange={(e) => setNewSupplier({ ...newSupplier, address: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newSupplier.notes}
                  onChange={(e) => setNewSupplier({ ...newSupplier, notes: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveSupplier} variant="contained">
              {selectedSupplier ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 