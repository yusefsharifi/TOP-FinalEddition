import React, { useState } from 'react';
import { Alert, Badge, Button, Card, Col, Collapse, Input, InputNumber, Modal, Progress, Rate, Row, Select, Slider, Switch, Table, Tabs, Tag, Typography } from 'antd';
import { AppstoreOutlined, CameraOutlined, CheckCircleOutlined, CloseOutlined, DownOutlined, EditOutlined, EyeInvisibleOutlined, EyeOutlined, FallOutlined, FileTextOutlined, InboxOutlined, PlusOutlined, PriceOutlined, RiseOutlined, StarOutlined, TagOutlined, VisibilityOnOutlined, WarningOutlined } from '@ant-design/icons';

const mockProducts = [
  {
    id: 'PROD-001',
    name: 'لپ‌تاپ Dell XPS 13',
    sku: 'LAP-001',
    category: 'الکترونیک',
    subcategory: 'لپ‌تاپ',
    brand: 'Dell',
    price: 45000000,
    cost: 38000000,
    stock: 15,
    minStock: 5,
    maxStock: 50,
    status: 'active',
    rating: 4.5,
    reviews: 128,
    description: 'لپ‌تاپ فوق‌العاده سبک و قدرتمند با صفحه نمایش 13 اینچی',
    features: [
      'پردازنده Intel Core i7',
      'رم 16GB DDR4',
      'هارد 512GB SSD',
      'صفحه نمایش 13.3 اینچ Full HD',
      'باتری تا 12 ساعت',
    ],
    specifications: {
      weight: '1.2 kg',
      dimensions: '304 x 199 x 15 mm',
      color: 'نقره‌ای',
      warranty: '2 سال',
    },
    images: ['laptop1.jpg', 'laptop2.jpg', 'laptop3.jpg'],
    tags: ['لپ‌تاپ', 'Dell', 'XPS', 'سبک'],
    supplier: 'شرکت Dell ایران',
    supplierContact: '021-12345678',
    lastUpdated: '1402/11/15',
    createdDate: '1402/10/01',
    salesCount: 45,
    revenue: 2025000000,
    profit: 315000000,
  },
  {
    id: 'PROD-002',
    name: 'ماوس بی‌سیم Logitech',
    sku: 'MOU-002',
    category: 'لوازم جانبی',
    subcategory: 'ماوس',
    brand: 'Logitech',
    price: 2500000,
    cost: 1800000,
    stock: 50,
    minStock: 10,
    maxStock: 100,
    status: 'active',
    rating: 4.2,
    reviews: 89,
    description: 'ماوس بی‌سیم با دقت بالا و عمر باتری طولانی',
    features: [
      'اتصال بی‌سیم 2.4GHz',
      'حساسیت 1200 DPI',
      'عمر باتری تا 12 ماه',
      '6 دکمه قابل برنامه‌ریزی',
      'طراحی ارگونومیک',
    ],
    specifications: {
      weight: '95 g',
      dimensions: '125 x 67 x 40 mm',
      color: 'مشکی',
      warranty: '1 سال',
    },
    images: ['mouse1.jpg', 'mouse2.jpg'],
    tags: ['ماوس', 'بی‌سیم', 'Logitech'],
    supplier: 'شرکت Logitech ایران',
    supplierContact: '021-87654321',
    lastUpdated: '1402/11/14',
    createdDate: '1402/09/15',
    salesCount: 120,
    revenue: 300000000,
    profit: 84000000,
  },
  {
    id: 'PROD-003',
    name: 'کیف چرمی مردانه',
    sku: 'BAG-003',
    category: 'پوشاک',
    subcategory: 'کیف',
    brand: 'Leather Craft',
    price: 400000,
    cost: 250000,
    stock: 25,
    minStock: 5,
    maxStock: 30,
    status: 'active',
    rating: 4.0,
    reviews: 56,
    description: 'کیف چرمی با کیفیت بالا و طراحی مدرن',
    features: [
      'چرم طبیعی 100%',
      'زیپ با کیفیت بالا',
      'جیب‌های متعدد',
      'دستگیره چرمی',
      'قابل شستشو',
    ],
    specifications: {
      weight: '800 g',
      dimensions: '30 x 25 x 10 cm',
      color: 'قهوه‌ای',
      warranty: '6 ماه',
    },
    images: ['bag1.jpg', 'bag2.jpg'],
    tags: ['کیف', 'چرم', 'مردانه'],
    supplier: 'کارگاه چرم‌سازی تهران',
    supplierContact: '021-11111111',
    lastUpdated: '1402/11/13',
    createdDate: '1402/08/20',
    salesCount: 78,
    revenue: 31200000,
    profit: 11700000,
  },
];

const productCategories = [
  { value: 'electronics', label: 'الکترونیک' },
  { value: 'accessories', label: 'لوازم جانبی' },
  { value: 'clothing', label: 'پوشاک' },
  { value: 'home', label: 'خانه و آشپزخانه' },
  { value: 'sports', label: 'ورزشی' },
  { value: 'books', label: 'کتاب' },
];

const productStatuses = [
  { value: 'active', label: 'فعال', color: 'success' },
  { value: 'inactive', label: 'غیرفعال', color: 'error' },
  { value: 'draft', label: 'پیش‌نویس', color: 'warning' },
  { value: 'discontinued', label: 'متوقف شده', color: 'error' },
];

export const ProductCatalog: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [tabValue, setTabValue] = useState(0);
  const [newProduct, setNewProduct] = useState({
    name: '',
    sku: '',
    category: '',
    brand: '',
    price: '',
    cost: '',
    stock: '',
    description: '',
    status: 'active',
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
      brand: product.brand,
      price: product.price.toString(),
      cost: product.cost.toString(),
      stock: product.stock.toString(),
      description: product.description,
      status: product.status,
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
      brand: '',
      price: '',
      cost: '',
      stock: '',
      description: '',
      status: 'active',
    });
  };

  const handleSaveProduct = () => {
    // در اینجا محصول ذخیره می‌شود
    handleCloseDialog();
  };

  const getStatusColor = (status: string) => {
    const productStatus = productStatuses.find(s => s.value === status);
    return productStatus ? productStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const productStatus = productStatuses.find(s => s.value === status);
    return productStatus ? productStatus.label : 'نامشخص';
  };

  const getStockColor = (stock: number, minStock: number) => {
    if (stock <= minStock) return 'error';
    if (stock <= minStock * 2) return 'warning';
    return 'success';
  };

  const getProfitMargin = (price: number, cost: number) => {
    return ((price - cost) / price) * 100;
  };

  const totalProducts = mockProducts.length;
  const activeProducts = mockProducts.filter(p => p.status === 'active').length;
  const lowStockProducts = mockProducts.filter(p => p.stock <= p.minStock).length;
  const totalRevenue = mockProducts.reduce((sum, p) => sum + p.revenue, 0);

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          کاتالوگ محصولات
        </Typography.Title>
        <div>
          <Button variant="outlined" startIcon={<Category />}>
            دسته‌بندی‌ها
          </Button>
          <Button variant="outlined" startIcon={<TrendingUp />}>
            گزارش فروش
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={handleAddProduct}>
            محصول جدید
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {totalProducts}
            </Typography.Title>
            <Typography.Text>
              کل محصولات
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {activeProducts}
            </Typography.Title>
            <Typography.Text>
              محصولات فعال
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {lowStockProducts}
            </Typography.Title>
            <Typography.Text>
              موجودی کم
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

      {/* Alerts */}
      {lowStockProducts > 0 && (
        <Alert severity="warning" style={{  mb: 3  }}>
          {lowStockProducts} محصول با موجودی کم وجود دارد که نیاز به سفارش مجدد دارد!
        </Alert>
      )}

      {/* Products List */}
      <Card>
        <div>
          <Typography.Title level={4}>
            لیست محصولات
          </Typography.Title>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>محصول</TableCell>
                  <TableCell>دسته‌بندی</TableCell>
                  <TableCell align="right">قیمت</TableCell>
                  <TableCell align="right">موجودی</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>امتیاز</TableCell>
                  <TableCell>عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {mockProducts.map((product) => (
                  <TableRow key={product.id}>
                    <TableCell>
                      <div>
                        <Typography.Text>
                          {product.name}
                        </Typography.Text>
                        <Typography variant="caption" color="textSecondary">
                          {product.sku}
                        </Typography>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Tag label={product.category} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {product.price.toLocaleString()} تومان
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        حاشیه: {getProfitMargin(product.price, product.cost).toFixed(1)}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <div>
                        <Typography.Text>
                          {product.stock}
                        </Typography.Text>
                        {product.stock <= product.minStock && (
                          <Warning color="warning" fontSize="small" />
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getStatusText(product.status)}
                        color={getStatusColor(product.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <div>
                        <Rating value={product.rating} readOnly size="small" />
                        <Typography variant="caption">
                          ({product.reviews})
                        </Typography>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <Button type="text" size="small" color="primary">
                          <Visibility />
                        </Button>
                        <Button type="text" size="small" onClick={() => handleEditProduct(product)}>
                          <Edit />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </Card>

      {/* Detailed Product View */}
      <div style={{  mt: 3  }}>
        <Typography.Title level={4}>
          جزئیات محصولات
        </Typography.Title>
        {mockProducts.map((product, index) => (
          <Accordion key={index} style={{  mb: 1  }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <div>
                <div>
                  <Typography.Title level={4}>{product.name}</Typography.Title>
                  <Typography.Text>
                    {product.brand} • {product.category}
                  </Typography.Text>
                </div>
                <div>
                  <Tag
                    label={product.price.toLocaleString() + ' تومان'}
                    color="success"
                    size="small"
                  />
                  <Tag
                    label={getStatusText(product.status)}
                    color={getStatusColor(product.status) as any}
                    size="small"
                  />
                  <Rating value={product.rating} readOnly size="small" />
                </div>
              </div>
            </div>
            <AccordionDetails>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
                    <Tab label="اطلاعات کلی" />
                    <Tab label="ویژگی‌ها" />
                    <Tab label="فروش" />
                  </Tabs>

                  <div style={{  mt: 2  }}>
                    {tabValue === 0 && (
                      <div>
                        <Typography.Text>
                          {product.description}
                        </Typography.Text>
                        <Row gutter={[16, 16]}>
                          <Col xs={Math.round(6 / 12 * 24)}>
                            <Typography variant="subtitle2">برند:</Typography>
                            <Typography.Text>{product.brand}</Typography.Text>
                          </Col>
                          <Col xs={Math.round(6 / 12 * 24)}>
                            <Typography variant="subtitle2">دسته‌بندی:</Typography>
                            <Typography.Text>{product.category}</Typography.Text>
                          </Col>
                          <Col xs={Math.round(6 / 12 * 24)}>
                            <Typography variant="subtitle2">SKU:</Typography>
                            <Typography.Text>{product.sku}</Typography.Text>
                          </Col>
                          <Col xs={Math.round(6 / 12 * 24)}>
                            <Typography variant="subtitle2">تاریخ ایجاد:</Typography>
                            <Typography.Text>{product.createdDate}</Typography.Text>
                          </Col>
                        </Row>
                      </div>
                    )}

                    {tabValue === 1 && (
                      <div>
                        <Typography variant="subtitle2" gutterBottom>
                          ویژگی‌های محصول:
                        </Typography>
                        <div>
                          {product.features.map((feature, featureIndex) => (
                            <Typography key={featureIndex} component="li" variant="body2">
                              {feature}
                            </Typography>
                          ))}
                        </div>

                        <Typography variant="subtitle2" gutterBottom style={{  mt: 2  }}>
                          مشخصات فنی:
                        </Typography>
                        <Row gutter={[16, 16]}>
                          {Object.entries(product.specifications).map(([key, value]) => (
                            <Col xs={Math.round(6 / 12 * 24)}>
                              <Typography.Text>
                                <strong>{key}:</strong> {value}
                              </Typography.Text>
                            </Col>
                          ))}
                        </Row>
                      </div>
                    )}

                    {tabValue === 2 && (
                      <div>
                        <Row gutter={[16, 16]}>
                          <Col xs={Math.round(6 / 12 * 24)}>
                            <Typography variant="subtitle2">تعداد فروش:</Typography>
                            <Typography.Title level={4}>
                              {product.salesCount}
                            </Typography.Title>
                          </Col>
                          <Col xs={Math.round(6 / 12 * 24)}>
                            <Typography variant="subtitle2">درآمد کل:</Typography>
                            <Typography.Title level={4}>
                              {product.revenue.toLocaleString()} تومان
                            </Typography.Title>
                          </Col>
                          <Col xs={Math.round(6 / 12 * 24)}>
                            <Typography variant="subtitle2">سود:</Typography>
                            <Typography.Title level={4}>
                              {product.profit.toLocaleString()} تومان
                            </Typography.Title>
                          </Col>
                          <Col xs={Math.round(6 / 12 * 24)}>
                            <Typography variant="subtitle2">حاشیه سود:</Typography>
                            <Typography.Title level={4}>
                              {getProfitMargin(product.price, product.cost).toFixed(1)}%
                            </Typography.Title>
                          </Col>
                        </Row>
                      </div>
                    )}
                  </div>
                </Col>

                <Col xs={Math.round(12 / 12 * 24)}>
                  <Card style={{  p: 2  }}>
                    <Typography variant="subtitle2" gutterBottom>
                      اطلاعات موجودی
                    </Typography>
                    <div>
                      <div>
                        <Typography.Text>موجودی فعلی:</Typography.Text>
                        <Typography.Text>
                          {product.stock}
                        </Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>حداقل موجودی:</Typography.Text>
                        <Typography.Text>{product.minStock}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>حداکثر موجودی:</Typography.Text>
                        <Typography.Text>{product.maxStock}</Typography.Text>
                      </div>
                    </div>

                    <Typography variant="subtitle2" gutterBottom>
                      اطلاعات مالی
                    </Typography>
                    <div>
                      <div>
                        <Typography.Text>قیمت فروش:</Typography.Text>
                        <Typography.Text>{product.price.toLocaleString()} تومان</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>هزینه خرید:</Typography.Text>
                        <Typography.Text>{product.cost.toLocaleString()} تومان</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>سود واحد:</Typography.Text>
                        <Typography.Text>
                          {(product.price - product.cost).toLocaleString()} تومان
                        </Typography.Text>
                      </div>
                    </div>

                    <Typography variant="subtitle2" gutterBottom>
                      تامین‌کننده
                    </Typography>
                    <div>
                      <Typography.Text>{product.supplier}</Typography.Text>
                      <Typography.Text>
                        {product.supplierContact}
                      </Typography.Text>
                    </div>

                    <div style={{  mt: 2  }}>
                      <Button variant="outlined" size="small" fullWidth startIcon={<Edit />}>
                        ویرایش محصول
                      </Button>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
          </div>
        ))}
      </div>

      {/* Add/Edit Product Dialog */}
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
                    <MenuItem key={category.value} value={category.value}>
                      {category.label}
                    </Select.Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="برند"
                value={newProduct.brand}
                onChange={(e) => setNewProduct({ ...newProduct, brand: e.target.value })}
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
                label="هزینه خرید"
                type="number"
                value={newProduct.cost}
                onChange={(e) => setNewProduct({ ...newProduct, cost: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="موجودی"
                type="number"
                value={newProduct.stock}
                onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <FormControl fullWidth>
                <InputLabel>وضعیت</span>
                <Select
                  value={newProduct.status}
                  label="وضعیت"
                  onChange={(e) => setNewProduct({ ...newProduct, status: e.target.value })}
                >
                  {productStatuses.map((status) => (
                    <MenuItem key={status.value} value={status.value}>
                      {status.label}
                    </Select.Option>
                  ))}
                </Select>
              </div>
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
  );
}; 