import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Table, Typography } from 'antd';
import { BankOutlined, FallOutlined, PlusOutlined, RiseOutlined } from '@ant-design/icons';

const mockCashFlow = {
  currentBalance: 250000,
  expectedInflow: 180000,
  expectedOutflow: 95000,
  projectedBalance: 335000,
  cashFlowTrend: 'positive',
  cashFlowPercentage: 15,
};

const mockCashTransactions = [
  {
    id: 1,
    date: '2024-04-22',
    description: 'دریافت از مشتری ABC',
    type: 'inflow',
    amount: 50000,
    category: 'فروش',
  },
  {
    id: 2,
    date: '2024-04-22',
    description: 'پرداخت به تأمین‌کننده XYZ',
    type: 'outflow',
    amount: -30000,
    category: 'خرید',
  },
  {
    id: 3,
    date: '2024-04-21',
    description: 'پرداخت حقوق کارکنان',
    type: 'outflow',
    amount: -45000,
    category: 'پرسنلی',
  },
  {
    id: 4,
    date: '2024-04-20',
    description: 'دریافت از مشتری DEF',
    type: 'inflow',
    amount: 75000,
    category: 'فروش',
  },
];

const transactionCategories = [
  'فروش',
  'خرید',
  'پرسنلی',
  'عملیاتی',
  'سرمایه‌گذاری',
  'سایر',
];

export const CashManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [newTransaction, setNewTransaction] = useState({
    date: '',
    description: '',
    type: 'inflow',
    amount: '',
    category: '',
  });

  const handleAddTransaction = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setNewTransaction({
      date: '',
      description: '',
      type: 'inflow',
      amount: '',
      category: '',
    });
  };

  const handleSaveTransaction = () => {
    // در اینجا تراکنش جدید ذخیره می‌شود
    handleCloseDialog();
  };

  const totalInflow = mockCashTransactions
    .filter(t => t.type === 'inflow')
    .reduce((sum, t) => sum + t.amount, 0);

  const totalOutflow = Math.abs(mockCashTransactions
    .filter(t => t.type === 'outflow')
    .reduce((sum, t) => sum + t.amount, 0));

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <AccountBalance style={{  mr: 1  }} />
            مدیریت نقدینگی
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddTransaction}
          >
            تراکنش جدید
          </Button>
        </div>

        {/* خلاصه نقدینگی */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                موجودی فعلی
              </Typography.Title>
              <Typography.Title level={2}>
                {mockCashFlow.currentBalance.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                ورودی پیش‌بینی شده
              </Typography.Title>
              <Typography.Title level={2}>
                {mockCashFlow.expectedInflow.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                خروجی پیش‌بینی شده
              </Typography.Title>
              <Typography.Title level={2}>
                {mockCashFlow.expectedOutflow.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                موجودی پیش‌بینی شده
              </Typography.Title>
              <Typography.Title level={2}>
                {mockCashFlow.projectedBalance.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
        </Row>

        {/* روند جریان نقدی */}
        <Card style={{  p: 3, mb: 3  }}>
          <Typography.Title level={4}>
            روند جریان نقدی
          </Typography.Title>
          <div>
            <div style={{  width: '100%', mr: 1  }}>
              <LinearProgress 
                variant="determinate" 
                value={mockCashFlow.cashFlowPercentage} 
                style={{  height: 10, borderRadius: 5  }}
                color={mockCashFlow.cashFlowTrend === 'positive' ? 'success' : 'error'}
              />
            </div>
            <div style={{  minWidth: 35  }}>
              <Typography.Text>
                {mockCashFlow.cashFlowPercentage}%
              </Typography.Text>
            </div>
          </div>
          <Typography.Text>
            روند {mockCashFlow.cashFlowTrend === 'positive' ? 'مثبت' : 'منفی'} - 
            {mockCashFlow.cashFlowPercentage}% تغییر نسبت به ماه گذشته
          </Typography.Text>
        </Card>

        {/* تراکنش‌های نقدی */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>تاریخ</TableCell>
                <TableCell>شرح</TableCell>
                <TableCell>دسته‌بندی</TableCell>
                <TableCell align="right">مبلغ</TableCell>
                <TableCell>نوع</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockCashTransactions.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell>{transaction.date}</TableCell>
                  <TableCell>{transaction.description}</TableCell>
                  <TableCell>{transaction.category}</TableCell>
                  <TableCell 
                    align="right"
                    style={{ 
                      color: transaction.amount >= 0 ? 'success.main' : 'error.main',
                     }}
                  >
                    {Math.abs(transaction.amount).toLocaleString()} تومان
                  </TableCell>
                  <TableCell>
                    <div>
                      {transaction.type === 'inflow' ? (
                        <TrendingUp color="success" style={{  mr: 1  }} />
                      ) : (
                        <TrendingDown color="error" style={{  mr: 1  }} />
                      )}
                      {transaction.type === 'inflow' ? 'ورودی' : 'خروجی'}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Dialog برای ثبت تراکنش جدید */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>ثبت تراکنش نقدی جدید</div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ"
                  type="date"
                  value={newTransaction.date}
                  onChange={(e) => setNewTransaction({ ...newTransaction, date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>نوع تراکنش</span>
                  <Select
                    value={newTransaction.type}
                    label="نوع تراکنش"
                    onChange={(e) => setNewTransaction({ ...newTransaction, type: e.target.value })}
                  >
                    <MenuItem value="inflow">ورودی</Select.Option>
                    <MenuItem value="outflow">خروجی</Select.Option>
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>دسته‌بندی</span>
                  <Select
                    value={newTransaction.category}
                    label="دسته‌بندی"
                    onChange={(e) => setNewTransaction({ ...newTransaction, category: e.target.value })}
                  >
                    {transactionCategories.map((category) => (
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
                  label="مبلغ"
                  type="number"
                  value={newTransaction.amount}
                  onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="شرح تراکنش"
                  multiline
                  rows={3}
                  value={newTransaction.description}
                  onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveTransaction} variant="contained">
              ثبت تراکنش
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 