import React, { useState } from 'react';
import { Button, Card, Col, Divider, Input, InputNumber, Modal, Row, Select, Table, Tag, Typography } from 'antd';
import { BankOutlined as AccountBalanceIcon, DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, PlusOutlined as AddIcon, SearchOutlined as SearchIcon } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

interface Account {
  id: number;
  code: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
  category: string;
  balance: number;
  status: 'active' | 'inactive';
}

const Accounts: React.FC = () => {
  const { t } = useTranslation();
  const [accounts, setAccounts] = useState<Account[]>([
    {
      id: 1,
      code: '1001',
      name: 'صندوق',
      type: 'asset',
      category: 'دارایی‌های جاری',
      balance: 50000000,
      status: 'active',
    },
    {
      id: 2,
      code: '2001',
      name: 'حساب‌های پرداختنی',
      type: 'liability',
      category: 'بدهی‌های جاری',
      balance: 25000000,
      status: 'active',
    },
  ]);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<Partial<Account>>({});
  const [editingId, setEditingId] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const handleOpenDialog = (account?: Account) => {
    if (account) {
      setFormData(account);
      setEditingId(account.id);
    } else {
      setFormData({});
      setEditingId(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({});
    setEditingId(null);
  };

  const handleSubmit = () => {
    if (editingId) {
      setAccounts(accounts.map(acc =>
        acc.id === editingId ? { ...acc, ...formData } : acc
      ));
    } else {
      const newAccount: Account = {
        ...formData as Account,
        id: accounts.length + 1,
      };
      setAccounts([...accounts, newAccount]);
    }
    handleCloseDialog();
  };

  const handleDeleteClick = (id: number) => {
    setDeleteId(id);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (deleteId) {
      setAccounts(accounts.filter(acc => acc.id !== deleteId));
      setDeleteConfirmOpen(false);
      setDeleteId(null);
    }
  };

  const calculateTotals = () => {
    const totals = {
      assets: accounts.filter(a => a.type === 'asset').reduce((sum, acc) => sum + acc.balance, 0),
      liabilities: accounts.filter(a => a.type === 'liability').reduce((sum, acc) => sum + acc.balance, 0),
      equity: accounts.filter(a => a.type === 'equity').reduce((sum, acc) => sum + acc.balance, 0),
      revenue: accounts.filter(a => a.type === 'revenue').reduce((sum, acc) => sum + acc.balance, 0),
      expenses: accounts.filter(a => a.type === 'expense').reduce((sum, acc) => sum + acc.balance, 0),
    };
    
    return {
      ...totals,
      netWorth: totals.assets - totals.liabilities,
      netIncome: totals.revenue - totals.expenses,
    };
  };

  const totals = calculateTotals();

  const filteredAccounts = accounts.filter(account => {
    const matchesSearch = 
      account.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.category.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = filterType === 'all' || account.type === filterType;
    
    return matchesSearch && matchesType;
  });

  return (
    <div>
      <div>
        <Typography.Title level={3}>{t('accounting.accounts')}</Typography.Title>
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
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
              <FormControl style={{  minWidth: 200  }}>
                <InputLabel>{t('common.type')}</span>
                <Select
                  value={filterType}
                  label={t('common.type')}
                  onChange={(e) => setFilterType(e.target.value)}
                >
                  <MenuItem value="all">{t('accounting.accountTypes.all')}</Select.Option>
                  <MenuItem value="asset">{t('accounting.accountTypes.asset')}</Select.Option>
                  <MenuItem value="liability">{t('accounting.accountTypes.liability')}</Select.Option>
                  <MenuItem value="equity">{t('accounting.accountTypes.equity')}</Select.Option>
                  <MenuItem value="revenue">{t('accounting.accountTypes.revenue')}</Select.Option>
                  <MenuItem value="expense">{t('accounting.accountTypes.expense')}</Select.Option>
                </Select>
              </div>
            </div>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>{t('common.code')}</TableCell>
                    <TableCell>{t('common.name')}</TableCell>
                    <TableCell>{t('common.type')}</TableCell>
                    <TableCell>{t('common.category')}</TableCell>
                    <TableCell align="right">{t('common.balance')}</TableCell>
                    <TableCell>{t('common.status')}</TableCell>
                    <TableCell>{t('common.actions')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredAccounts.map((account) => (
                    <TableRow key={account.id}>
                      <TableCell>{account.code}</TableCell>
                      <TableCell>{account.name}</TableCell>
                      <TableCell>
                        <Tag
                          label={t(`accounting.accountTypes.${account.type}`)}
                          color={account.type === 'asset' ? 'success' :
                                 account.type === 'liability' ? 'error' :
                                 account.type === 'equity' ? 'info' :
                                 account.type === 'revenue' ? 'primary' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{account.category}</TableCell>
                      <TableCell align="right">
                        {new Intl.NumberFormat('fa-IR').format(account.balance)}
                      </TableCell>
                      <TableCell>
                        <Tag
                          label={t(`accounting.accountStatus.${account.status}`)}
                          color={account.status === 'active' ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Button type="text" onClick={() => handleOpenDialog(account)} size="small">
                          <EditIcon />
                        </Button>
                        <Button type="text" onClick={() => handleDeleteClick(account.id)} size="small">
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
              title={t('accounting.accountSummary')}
              avatar={<AccountBalanceIcon />}
            />
            <div>
              <div>
                <div>
                  <Typography>{t('accounting.totalAssets')}:</Typography>
                  <Typography>
                    {new Intl.NumberFormat('fa-IR').format(totals.assets)}
                  </Typography>
                </div>
                <div>
                  <Typography>{t('accounting.totalLiabilities')}:</Typography>
                  <Typography>
                    {new Intl.NumberFormat('fa-IR').format(totals.liabilities)}
                  </Typography>
                </div>
                <Divider />
                <div>
                  <Typography>{t('accounting.netWorth')}:</Typography>
                  <Typography>
                    {new Intl.NumberFormat('fa-IR').format(totals.netWorth)}
                  </Typography>
                </div>
                <Divider />
                <div>
                  <Typography>{t('accounting.totalRevenue')}:</Typography>
                  <Typography>
                    {new Intl.NumberFormat('fa-IR').format(totals.revenue)}
                  </Typography>
                </div>
                <div>
                  <Typography>{t('accounting.totalExpenses')}:</Typography>
                  <Typography>
                    {new Intl.NumberFormat('fa-IR').format(totals.expenses)}
                  </Typography>
                </div>
                <Divider />
                <div>
                  <Typography>{t('accounting.netIncome')}:</Typography>
                  <Typography>
                    {new Intl.NumberFormat('fa-IR').format(totals.netIncome)}
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
              label={t('common.code')}
              value={formData.code || ''}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              fullWidth
            />
            <Input
              label={t('common.name')}
              value={formData.name || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>{t('common.type')}</span>
              <Select
                value={formData.type || ''}
                label={t('common.type')}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as Account['type'] })}
              >
                <MenuItem value="asset">دارایی</Select.Option>
                <MenuItem value="liability">بدهی</Select.Option>
                <MenuItem value="equity">سرمایه</Select.Option>
                <MenuItem value="revenue">درآمد</Select.Option>
                <MenuItem value="expense">هزینه</Select.Option>
              </Select>
            </div>
            <Input
              label={t('common.category')}
              value={formData.category || ''}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              fullWidth
            />
            <Input
              label={t('common.balance')}
              type="number"
              value={formData.balance || ''}
              onChange={(e) => setFormData({ ...formData, balance: Number(e.target.value) })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>{t('common.status')}</span>
              <Select
                value={formData.status || ''}
                label={t('common.status')}
                onChange={(e) => setFormData({ ...formData, status: e.target.value as Account['status'] })}
              >
                <MenuItem value="active">{t('accounting.accountStatus.active')}</Select.Option>
                <MenuItem value="inactive">{t('accounting.accountStatus.inactive')}</Select.Option>
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
          <Typography>
            {t('accounting.confirmDelete')}
          </Typography>
        </div>
        <div>
          <Button onClick={() => setDeleteConfirmOpen(false)}>
            {t('common.cancel')}
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            {t('common.delete')}
          </Button>
        </div>
      </Modal>
    </div>
  );
};

export default Accounts; 