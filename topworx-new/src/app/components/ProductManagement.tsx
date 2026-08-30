import React, { useState } from 'react';
import { Alert, Button, Card, Col, Input, InputNumber, Modal, Row, Select, Spin, Table, Tag, Typography } from 'antd';
import { DeleteOutlined, EditOutlined, EyeOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons';
import {
  useProducts,
  useCreateProduct,
  useUpdateProduct,
  useDeleteProduct,
  useCategories,
  useSuppliers,
} from '../../api/inventory';
import { Product } from '../../api/inventory/types';

const emptyForm = {
  name: '', code: '', category: '', unit: '',
  minStock: '', maxStock: '',
};

type FormState = typeof emptyForm;

export const ProductManagement: React.FC = () => {
  const [openDialog, setOpenDialog]       = useState(false);
  const [viewMode, setViewMode]           = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [form, setForm]                   = useState<FormState>(emptyForm);
  const [searchTerm, setSearchTerm]       = useState('');
  const [filterCategory, setFilterCategory] = useState('');

  const { data: products, isLoading, isError } = useProducts();
  const { data: categories = [] }              = useCategories();
  const { data: suppliers = [] }               = useSuppliers();

  const createProduct = useCreateProduct();
  const updateProduct = useUpdateProduct();
  const deleteProduct = useDeleteProduct();

  const isMutating =
    createProduct.isLoading || updateProduct.isLoading || deleteProduct.isLoading;

  // --- helpers ---
  const openAdd = () => {
    setSelectedProduct(null);
    setViewMode(false);
    setForm(emptyForm);
    setOpenDialog(true);
  };

  const openEdit = (product: Product) => {
    setSelectedProduct(product);
    setViewMode(false);
    setForm({
      name:     product.name,
      code:     product.code,
      category: product.category,
      unit:     product.unit,
      minStock: String(product.minStock),
      maxStock: String(product.maxStock),
    });
    setOpenDialog(true);
  };

  const openView = (product: Product) => {
    setSelectedProduct(product);
    setViewMode(true);
    setOpenDialog(true);
  };

  const handleClose = () => {
    setOpenDialog(false);
    setSelectedProduct(null);
    setViewMode(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    const payload: Partial<Product> = {
      ...form,
      minStock: Number(form.minStock),
      maxStock: Number(form.maxStock),
    };

    if (selectedProduct) {
      await updateProduct.mutateAsync({ ...payload, id: selectedProduct.id });
    } else {
      await createProduct.mutateAsync(payload);
    }
    handleClose();
  };

  const handleDelete = (id: string) => {
    if (window.confirm('آیا از حذف این محصول مطمئن هستید؟')) {
      deleteProduct.mutate(Number(id));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ok':   return 'success';
      case 'low':  return 'warning';
      case 'over': return 'info';
      default:     return 'default';
    }
  };

  const filtered = (products ?? []).filter((p) => {
    const matchSearch =
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchCat = !filterCategory || p.category === filterCategory;
    return matchSearch && matchCat;
  });

  if (isLoading) return <div><Spin /></div>;
  if (isError)   return <Alert severity="error">خطا در دریافت محصولات</Alert>;

  return (
    <div>
      <Typography.Title level={2}>مدیریت محصولات</Typography.Title>

      {/* فیلترها */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Input
            fullWidth label="جستجو بر اساس نام یا کد" variant="outlined"
            value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{ endAdornment: <Search /> }}
          />
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <FormControl fullWidth>
            <InputLabel>دسته‌بندی</span>
            <Select
              value={filterCategory} label="دسته‌بندی"
              onChange={(e) => setFilterCategory(e.target.value as string)}
            >
              <MenuItem value=""><em>همه</em></Select.Option>
              {categories.map((c: any) => (
                <MenuItem key={c.id ?? c} value={c.name ?? c}>{c.name ?? c}</Select.Option>
              ))}
            </Select>
          </div>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Button variant="contained" startIcon={<Add />} onClick={openAdd}>
            افزودن محصول
          </Button>
        </Col>
      </Row>

      {/* جدول */}
      <Card>
        <div>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>نام محصول</TableCell>
                  <TableCell>کد</TableCell>
                  <TableCell>دسته‌بندی</TableCell>
                  <TableCell>واحد</TableCell>
                  <TableCell align="right">حداقل موجودی</TableCell>
                  <TableCell align="right">حداکثر موجودی</TableCell>
                  <TableCell align="right">عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filtered.map((product) => (
                  <TableRow key={product.id}>
                    <TableCell>{product.name}</TableCell>
                    <TableCell>{product.code}</TableCell>
                    <TableCell>{product.category}</TableCell>
                    <TableCell>{product.unit}</TableCell>
                    <TableCell align="right">{product.minStock}</TableCell>
                    <TableCell align="right">{product.maxStock}</TableCell>
                    <TableCell align="right">
                      <Button type="text" onClick={() => openView(product)}>
                        <Visibility />
                      </Button>
                      <Button type="text" onClick={() => openEdit(product)}>
                        <Edit />
                      </Button>
                      <Button type="text" onClick={() => handleDelete(product.id)}>
                        <Delete />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {filtered.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">محصولی یافت نشد</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      </Card>

      {/* دیالوگ افزودن/ویرایش/مشاهده */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          {viewMode ? 'مشاهده محصول' : selectedProduct ? 'ویرایش محصول' : 'افزودن محصول جدید'}
        </div>
        <div>
          {viewMode && selectedProduct ? (
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(6 / 12 * 24)}><Typography.Text>نام</Typography.Text><Typography>{selectedProduct.name}</Typography></Col>
              <Col xs={Math.round(6 / 12 * 24)}><Typography.Text>کد</Typography.Text><Typography>{selectedProduct.code}</Typography></Col>
              <Col xs={Math.round(6 / 12 * 24)}><Typography.Text>دسته‌بندی</Typography.Text><Typography>{selectedProduct.category}</Typography></Col>
              <Col xs={Math.round(6 / 12 * 24)}><Typography.Text>واحد</Typography.Text><Typography>{selectedProduct.unit}</Typography></Col>
              <Col xs={Math.round(6 / 12 * 24)}><Typography.Text>حداقل موجودی</Typography.Text><Typography>{selectedProduct.minStock}</Typography></Col>
              <Col xs={Math.round(6 / 12 * 24)}><Typography.Text>حداکثر موجودی</Typography.Text><Typography>{selectedProduct.maxStock}</Typography></Col>
            </Row>
          ) : (
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input fullWidth label="نام محصول" name="name"
                  value={form.name} onChange={handleChange} margin="dense" />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input fullWidth label="کد کالا" name="code"
                  value={form.code} onChange={handleChange} margin="dense" />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth margin="dense">
                  <InputLabel>دسته‌بندی</span>
                  <Select
                    name="category" value={form.category} label="دسته‌بندی"
                    onChange={(e) => setForm((p) => ({ ...p, category: e.target.value as string }))}
                  >
                    {categories.map((c: any) => (
                      <MenuItem key={c.id ?? c} value={c.name ?? c}>{c.name ?? c}</Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input fullWidth label="واحد" name="unit"
                  value={form.unit} onChange={handleChange} margin="dense" />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input fullWidth label="حداقل موجودی" name="minStock" type="number"
                  value={form.minStock} onChange={handleChange} margin="dense" />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input fullWidth label="حداکثر موجودی" name="maxStock" type="number"
                  value={form.maxStock} onChange={handleChange} margin="dense" />
              </Col>
            </Row>
          )}
        </div>
        <div>
          <Button onClick={handleClose}>بستن</Button>
          {!viewMode && (
            <Button
              onClick={handleSave} variant="contained"
              disabled={isMutating}
            >
              {isMutating ? <Spin /> : 'ذخیره'}
            </Button>
          )}
        </div>
      </Modal>
    </div>
  );
};
