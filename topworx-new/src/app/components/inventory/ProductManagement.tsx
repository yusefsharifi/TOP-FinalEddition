import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Row, Select, Table, Tag, Typography } from 'antd';
import { DeleteOutlined, EditOutlined, EyeOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons';

const mockProducts = [
  {
    id: 1,
    name: 'لپ‌تاپ Dell XPS 13',
    sku: 'LAP-001',
    category: 'الکترونیک',
    price: 45000000,
    cost: 38000000,
    stock: 25,
    minStock: 5,
    maxStock: 50,
    location: 'انبار A - قفسه 1',
    supplier: 'تأمین‌کننده A',
    status: 'active',
    description: 'لپ‌تاپ 13 اینچی با پردازنده Intel i7',
  },
  {
    id: 2,
    name: 'ماوس بی‌سیم Logitech',
    sku: 'MOU-002',
    category: 'الکترونیک',
    price: 850000,
    cost: 650000,
    stock: 0,
    minStock: 10,
    maxStock: 100,
    location: 'انبار A - قفسه 2',
    supplier: 'تأمین‌کننده B',
    status: 'out-of-stock',
    description: 'ماوس بی‌سیم با دقت بالا',
  },
  {
    id: 3,
    name: 'کیف چرمی مردانه',
    sku: 'BAG-003',
    category: 'پوشاک',
    price: 1200000,
    cost: 900000,
    stock: 8,
    minStock: 5,
    maxStock: 30,
    location: 'انبار B - قفسه 1',
    supplier: 'تأمین‌کننده C',
    status: 'low-stock',
    description: 'کیف چرمی با کیفیت بالا',
  },
];

const productCategories = [
  'الکترونیک',
  'پوشاک',
  'کتاب',
  'خودرو',
  'لوازم خانگی',
  'سایر',
];

const productStatuses = [
  'فعال',
  'غیرفعال',
  'ناموجود',
  'کم‌موجود',
];

export const ProductManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [newProduct, setNewProduct] = useState({
    name: '',
    sku: '',
    category: '',
    price: '',
    cost: '',
    stock: '',
    minStock: '',
    maxStock: '',
    location: '',
    supplier: '',
    description: '',
  });

  const handleAddProduct = () => {
    setSelectedProduct(null);
    setOpenDialog(true);
  };

  const handleEditProduct = (product: any) => {
    setSelectedProduct(product);
    setNewProduct({
      name: product.name,
      sku: product.sku,
      category: product.category,
      price: product.price.toString(),
      cost: product.cost.toString(),
      stock: product.stock.toString(),
      minStock: product.minStock.toString(),
      maxStock: product.maxStock.toString(),
      location: product.location,
      supplier: product.supplier,
      description: product.description,
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedProduct(null);
    setNewProduct({
      name: '',
      sku: '',
      category: '',
      price: '',
      cost: '',
      stock: '',
      minStock: '',
      maxStock: '',
      location: '',
      supplier: '',
      description: '',
    });
  };

  const handleSaveProduct = () => {
    // در اینجا محصول ذخیره می‌شود
    handleCloseDialog();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'low-stock':
        return 'warning';
      case 'out-of-stock':
        return 'error';
      case 'inactive':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'فعال';
      case 'low-stock':
        return 'کم‌موجود';
      case 'out-of-stock':
        return 'ناموجود';
      case 'inactive':
        return 'غیرفعال';
      default:
        return 'نامشخص';
    }
  };

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            مدیریت محصولات
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddProduct}
          >
            محصول جدید
          </Button>
        </div>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام محصول</TableCell>
                <TableCell>SKU</TableCell>
                <TableCell>دسته‌بندی</TableCell>
                <TableCell align="right">قیمت</TableCell>
                <TableCell align="right">موجودی</TableCell>
                <TableCell>محل</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockProducts.map((product) => (
                <TableRow key={product.id}>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{product.sku}</TableCell>
                  <TableCell>{product.category}</TableCell>
                  <TableCell align="right">
                    {product.price.toLocaleString()} تومان
                  </TableCell>
                  <TableCell align="right">{product.stock}</TableCell>
                  <TableCell>{product.location}</TableCell>
                  <TableCell>
                    <Tag
                      label={getStatusText(product.status)}
                      color={getStatusColor(product.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleEditProduct(product)}
                      >
                        <Edit />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleEditProduct(product)}
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

        {/* Dialog برای اضافه/ویرایش محصول */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedProduct ? 'ویرایش محصول' : 'افزودن محصول جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام محصول"
                  value={newProduct.name}
                  onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="SKU"
                  value={newProduct.sku}
                  onChange={(e) => setNewProduct({ ...newProduct, sku: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>دسته‌بندی</span>
                  <Select
                    value={newProduct.category}
                    label="دسته‌بندی"
                    onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}
                  >
                    {productCategories.map((category) => (
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
                  label="تأمین‌کننده"
                  value={newProduct.supplier}
                  onChange={(e) => setNewProduct({ ...newProduct, supplier: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="قیمت فروش"
                  type="number"
                  value={newProduct.price}
                  onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="قیمت تمام شده"
                  type="number"
                  value={newProduct.cost}
                  onChange={(e) => setNewProduct({ ...newProduct, cost: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="موجودی فعلی"
                  type="number"
                  value={newProduct.stock}
                  onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="حداقل موجودی"
                  type="number"
                  value={newProduct.minStock}
                  onChange={(e) => setNewProduct({ ...newProduct, minStock: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="حداکثر موجودی"
                  type="number"
                  value={newProduct.maxStock}
                  onChange={(e) => setNewProduct({ ...newProduct, maxStock: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="محل در انبار"
                  value={newProduct.location}
                  onChange={(e) => setNewProduct({ ...newProduct, location: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newProduct.description}
                  onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveProduct} variant="contained">
              {selectedProduct ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 