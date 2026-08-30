import React, { useState } from 'react';
import { Button, Card, Input, InputNumber, Menu, Modal, Pagination, Table, Tag, Typography } from 'antd';
import { DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, EllipsisOutlined as MoreVertIcon, InboxOutlined as InventoryIcon, PlusOutlined as AddIcon, SearchOutlined as SearchIcon } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

interface Product {
  id: string;
  code: string;
  name: string;
  category: string;
  unit: string;
  price: number;
  stock: number;
  minStock: number;
  status: string;
}

const Products: React.FC = () => {
  const { t } = useTranslation();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [openDialog, setOpenDialog] = useState(false);

  // Mock data
  const products: Product[] = [
    {
      id: '1',
      code: 'PRD001',
      name: 'لپ تاپ',
      category: 'الکترونیک',
      unit: 'عدد',
      price: 25000000,
      stock: 15,
      minStock: 5,
      status: 'فعال',
    },
    {
      id: '2',
      code: 'PRD002',
      name: 'موبایل',
      category: 'الکترونیک',
      unit: 'عدد',
      price: 15000000,
      stock: 25,
      minStock: 10,
      status: 'فعال',
    },
    // Add more mock data as needed
  ];

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, product: Product) => {
    setAnchorEl(event.currentTarget);
    setSelectedProduct(product);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedProduct(null);
  };

  const handleEdit = () => {
    setOpenDialog(true);
    handleMenuClose();
  };

  const handleDelete = () => {
    // Add delete logic here
    handleMenuClose();
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
  };

  const getStockStatus = (stock: number, minStock: number) => {
    if (stock <= minStock) {
      return <Tag color="error">کم</Tag>;
    } else if (stock <= minStock * 2) {
      return <Tag color="warning">متوسط</Tag>;
    } else {
      return <Tag color="success">کافی</Tag>;
    }
  };

  const filteredProducts = products.filter((product) =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div>
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <Typography.Title level={2}>
          {t('products.title')}
        </Typography.Title>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          {t('products.addProduct')}
        </Button>
      </div>

      <Card style={{  mb: 3  }}>
        <Input
          fullWidth
          variant="outlined"
          placeholder={t('products.searchPlaceholder')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Card>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('products.code')}</TableCell>
              <TableCell>{t('products.name')}</TableCell>
              <TableCell>{t('products.category')}</TableCell>
              <TableCell>{t('products.unit')}</TableCell>
              <TableCell align="right">{t('products.price')}</TableCell>
              <TableCell align="right">{t('products.stock')}</TableCell>
              <TableCell align="right">{t('products.minStock')}</TableCell>
              <TableCell>{t('products.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredProducts
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((product) => (
                <TableRow key={product.id}>
                  <TableCell>{product.code}</TableCell>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{product.category}</TableCell>
                  <TableCell>{product.unit}</TableCell>
                  <TableCell align="right">
                    {product.price.toLocaleString()} تومان
                  </TableCell>
                  <TableCell align="right">
                    {product.stock} {getStockStatus(product.stock, product.minStock)}
                  </TableCell>
                  <TableCell align="right">{product.minStock}</TableCell>
                  <TableCell>{product.status}</TableCell>
                  <TableCell align="right">
                    <Button type="text" onClick={(e) => handleMenuClick(e, product)}>
                      <MoreVertIcon />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredProducts.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </div>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEdit}>
          <EditIcon style={{  mr: 1  }} /> {t('common.edit')}
        </Select.Option>
        <MenuItem onClick={handleDelete}>
          <DeleteIcon style={{  mr: 1  }} /> {t('common.delete')}
        </Select.Option>
      </Menu>

      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          {selectedProduct ? t('products.editProduct') : t('products.addProduct')}
        </div>
        <div>
          {/* Add form fields here */}
          <div style={{  mt: 2  }}>
            <Typography color="text.secondary">
              {t('products.formPlaceholder')}
            </Typography>
          </div>
        </div>
        <div>
          <Button onClick={handleDialogClose}>{t('common.cancel')}</Button>
          <Button variant="contained" onClick={handleDialogClose}>
            {t('common.save')}
          </Button>
        </div>
      </Modal>
    </div>
  );
};

export default Products; 