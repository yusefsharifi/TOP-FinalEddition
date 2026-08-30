import React, { useState, useEffect } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Row, Select, Spin, Table, Tag, Typography } from 'antd';
import { BankOutlined as BusinessIcon, DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, PlusOutlined as AddIcon, SearchOutlined as SearchIcon } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

interface Customer {
  id: number;
  name: string;
  company: string;
  email: string;
  phone: string;
  address: string;
  type: 'retail' | 'wholesale' | 'corporate';
  status: 'active' | 'inactive' | 'pending';
  totalOrders: number;
  totalSpent: number;
  lastOrderDate: string;
  createdAt: string;
}

interface FormData {
  name: string;
  company: string;
  email: string;
  phone: string;
  address: string;
  type: 'retail' | 'wholesale' | 'corporate';
  status: 'active' | 'inactive' | 'pending';
}

const initialFormData: FormData = {
  name: '',
  company: '',
  email: '',
  phone: '',
  address: '',
  type: 'retail',
  status: 'active',
};

const Customers: React.FC = () => {
  const { t } = useTranslation();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      // TODO: Replace with actual API call
      const mockData: Customer[] = [
        {
          id: 1,
          name: 'علی محمدی',
          company: 'شرکت الف',
          email: 'ali@company.com',
          phone: '09123456789',
          address: 'تهران، خیابان ولیعصر',
          type: 'corporate',
          status: 'active',
          totalOrders: 15,
          totalSpent: 150000000,
          lastOrderDate: '1402/12/15',
          createdAt: '1402/01/01',
        },
        {
          id: 2,
          name: 'مریم احمدی',
          company: 'فروشگاه ب',
          email: 'maryam@store.com',
          phone: '09187654321',
          address: 'تهران، خیابان انقلاب',
          type: 'retail',
          status: 'active',
          totalOrders: 8,
          totalSpent: 45000000,
          lastOrderDate: '1402/12/10',
          createdAt: '1402/02/15',
        },
      ];
      setCustomers(mockData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching customers:', error);
      setLoading(false);
    }
  };

  const handleOpenDialog = (customer?: Customer) => {
    if (customer) {
      setFormData({
        name: customer.name,
        company: customer.company,
        email: customer.email,
        phone: customer.phone,
        address: customer.address,
        type: customer.type,
        status: customer.status,
      });
      setEditingId(customer.id);
    } else {
      setFormData(initialFormData);
      setEditingId(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData(initialFormData);
    setEditingId(null);
  };

  const handleSubmit = async () => {
    try {
      if (editingId) {
        // TODO: Replace with actual API call
        const existingCustomer = customers.find(c => c.id === editingId);
        if (existingCustomer) {
          const updatedCustomer: Customer = {
            ...existingCustomer,
            ...formData,
            id: editingId,
          };
          setCustomers(customers.map(cust =>
            cust.id === editingId ? updatedCustomer : cust
          ));
        }
      } else {
        // TODO: Replace with actual API call
        const newCustomer: Customer = {
          ...formData,
          id: customers.length + 1,
          totalOrders: 0,
          totalSpent: 0,
          lastOrderDate: '',
          createdAt: new Date().toLocaleDateString('fa-IR'),
        };
        setCustomers([...customers, newCustomer]);
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving customer:', error);
    }
  };

  const handleDeleteClick = (id: number) => {
    setDeleteId(id);
    setDeleteConfirmOpen(true);
  };

  const handleDelete = async () => {
    try {
      // TODO: Replace with actual API call
      setCustomers(customers.filter(cust => cust.id !== deleteId));
      setDeleteConfirmOpen(false);
    } catch (error) {
      console.error('Error deleting customer:', error);
    }
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const filteredCustomers = customers.filter(customer => {
    const matchesSearch = 
      customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || customer.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <div>
        <Spin />
      </div>
    );
  }

  return (
    <div>
      <div>
        <Typography.Title level={3}>{t('crm.customers')}</Typography.Title>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          {t('common.add')}
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, mb: 3  }}>
            <div>
              <Input
                fullWidth
                variant="outlined"
                placeholder={t('common.search')}
                value={searchTerm}
                onChange={handleSearch}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
              <FormControl style={{  minWidth: 200  }}>
                <InputLabel>{t('common.status')}</span>
                <Select
                  value={filterStatus}
                  label={t('common.status')}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">همه</Select.Option>
                  <MenuItem value="active">فعال</Select.Option>
                  <MenuItem value="inactive">غیرفعال</Select.Option>
                  <MenuItem value="pending">در انتظار</Select.Option>
                </Select>
              </div>
            </div>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>{t('common.name')}</TableCell>
                    <TableCell>{t('common.company')}</TableCell>
                    <TableCell>{t('common.email')}</TableCell>
                    <TableCell>{t('common.phone')}</TableCell>
                    <TableCell>{t('common.status')}</TableCell>
                    <TableCell>{t('common.actions')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredCustomers.map((customer) => (
                    <TableRow key={customer.id}>
                      <TableCell>{customer.name}</TableCell>
                      <TableCell>{customer.company}</TableCell>
                      <TableCell>{customer.email}</TableCell>
                      <TableCell>{customer.phone}</TableCell>
                      <TableCell>
                        <Tag
                          label={customer.status}
                          color={getStatusColor(customer.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Button type="text" onClick={() => handleOpenDialog(customer)} size="small">
                          <EditIcon />
                        </Button>
                        <Button type="text" onClick={() => handleDeleteClick(customer.id)} size="small">
                          <DeleteIcon />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <CardHeader
              title="آمار کلی"
              avatar={<BusinessIcon />}
            />
            <div>
              <div>
                <div>
                  <Typography>کل مشتریان:</Typography>
                  <Typography>{customers.length}</Typography>
                </div>
                <div>
                  <Typography>مشتریان فعال:</Typography>
                  <Typography>
                    {customers.filter(c => c.status === 'active').length}
                  </Typography>
                </div>
                <div>
                  <Typography>مشتریان غیرفعال:</Typography>
                  <Typography>
                    {customers.filter(c => c.status === 'inactive').length}
                  </Typography>
                </div>
                <div>
                  <Typography>مشتریان در انتظار:</Typography>
                  <Typography>
                    {customers.filter(c => c.status === 'pending').length}
                  </Typography>
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          {editingId ? t('common.edit') : t('common.add')}
        </div>
        <div>
          <div>
            <Input
              label={t('common.name')}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
            />
            <Input
              label={t('common.company')}
              value={formData.company}
              onChange={(e) => setFormData({ ...formData, company: e.target.value })}
              fullWidth
            />
            <Input
              label={t('common.email')}
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              fullWidth
            />
            <Input
              label={t('common.phone')}
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              fullWidth
            />
            <Input
              label={t('common.address')}
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              fullWidth
              multiline
              rows={3}
            />
            <FormControl fullWidth>
              <InputLabel>{t('common.type')}</span>
              <Select
                value={formData.type}
                label={t('common.type')}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as 'retail' | 'wholesale' | 'corporate' })}
              >
                <MenuItem value="retail">خرده فروشی</Select.Option>
                <MenuItem value="wholesale">عمده فروشی</Select.Option>
                <MenuItem value="corporate">شرکتی</Select.Option>
              </Select>
            </div>
            <FormControl fullWidth>
              <InputLabel>{t('common.status')}</span>
              <Select
                value={formData.status}
                label={t('common.status')}
                onChange={(e) => setFormData({ ...formData, status: e.target.value as 'active' | 'inactive' | 'pending' })}
              >
                <MenuItem value="active">فعال</Select.Option>
                <MenuItem value="inactive">غیرفعال</Select.Option>
                <MenuItem value="pending">در انتظار</Select.Option>
              </Select>
            </div>
          </div>
        </div>
        <div>
          <Button onClick={handleCloseDialog}>{t('common.cancel')}</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {t('common.save')}
          </Button>
        </div>
      </Modal>

      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>{t('common.delete')}</div>
        <div>
          <Typography>{t('crm.confirmDelete')}</Typography>
        </div>
        <div>
          <Button onClick={() => setDeleteConfirmOpen(false)}>{t('common.cancel')}</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            {t('common.delete')}
          </Button>
        </div>
      </Modal>
    </div>
  );
};

export default Customers; 