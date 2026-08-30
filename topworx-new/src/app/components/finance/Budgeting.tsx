import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { BankOutlined, FallOutlined, PlusOutlined, RiseOutlined } from '@ant-design/icons';

const mockBudgets = [
  {
    id: 1,
    name: 'بودجه عملیاتی',
    totalBudget: 500000,
    spentAmount: 375000,
    remainingAmount: 125000,
    period: '2024',
    status: 'on-track',
    category: 'عملیاتی',
    lastUpdated: '2024-04-22',
  },
  {
    id: 2,
    name: 'بودجه پرسنلی',
    totalBudget: 300000,
    spentAmount: 280000,
    remainingAmount: 20000,
    period: '2024',
    status: 'warning',
    category: 'پرسنلی',
    lastUpdated: '2024-04-22',
  },
  {
    id: 3,
    name: 'بودجه بازاریابی',
    totalBudget: 150000,
    spentAmount: 90000,
    remainingAmount: 60000,
    period: '2024',
    status: 'on-track',
    category: 'بازاریابی',
    lastUpdated: '2024-04-22',
  },
  {
    id: 4,
    name: 'بودجه تحقیق و توسعه',
    totalBudget: 200000,
    spentAmount: 220000,
    remainingAmount: -20000,
    period: '2024',
    status: 'over-budget',
    category: 'تحقیق و توسعه',
    lastUpdated: '2024-04-22',
  },
];

const budgetCategories = [
  'عملیاتی',
  'پرسنلی',
  'بازاریابی',
  'تحقیق و توسعه',
  'سرمایه‌گذاری',
  'سایر',
];

export const Budgeting: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [newBudget, setNewBudget] = useState({
    name: '',
    totalBudget: '',
    period: '',
    category: '',
    description: '',
  });

  const handleAddBudget = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setNewBudget({
      name: '',
      totalBudget: '',
      period: '',
      category: '',
      description: '',
    });
  };

  const handleSaveBudget = () => {
    // در اینجا بودجه جدید ذخیره می‌شود
    handleCloseDialog();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on-track':
        return 'success';
      case 'warning':
        return 'warning';
      case 'over-budget':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'on-track':
        return 'در مسیر';
      case 'warning':
        return 'هشدار';
      case 'over-budget':
        return 'فراتر از بودجه';
      default:
        return 'نامشخص';
    }
  };

  const totalBudget = mockBudgets.reduce((sum, budget) => sum + budget.totalBudget, 0);
  const totalSpent = mockBudgets.reduce((sum, budget) => sum + budget.spentAmount, 0);
  const totalRemaining = mockBudgets.reduce((sum, budget) => sum + budget.remainingAmount, 0);
  const utilizationRate = (totalSpent / totalBudget) * 100;

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <AccountBalance style={{  mr: 1  }} />
            بودجه‌بندی
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddBudget}
          >
            بودجه جدید
          </Button>
        </div>

        {/* خلاصه بودجه */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                کل بودجه
              </Typography.Title>
              <Typography.Title level={2}>
                {totalBudget.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                هزینه شده
              </Typography.Title>
              <Typography.Title level={2}>
                {totalSpent.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                باقی‌مانده
              </Typography.Title>
              <Typography.Title level={2}>
                {totalRemaining.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                نرخ استفاده
              </Typography.Title>
              <Typography.Title level={2}>
                {utilizationRate.toFixed(1)}%
              </Typography.Title>
            </Card>
          </Col>
        </Row>

        {/* روند استفاده از بودجه */}
        <Card style={{  p: 3, mb: 3  }}>
          <Typography.Title level={4}>
            روند استفاده از بودجه
          </Typography.Title>
          <div>
            <div style={{  width: '100%', mr: 1  }}>
              <LinearProgress 
                variant="determinate" 
                value={utilizationRate} 
                style={{  height: 10, borderRadius: 5  }}
                color={utilizationRate > 100 ? 'error' : utilizationRate > 80 ? 'warning' : 'success'}
              />
            </div>
            <div style={{  minWidth: 35  }}>
              <Typography.Text>
                {utilizationRate.toFixed(1)}%
              </Typography.Text>
            </div>
          </div>
          <Typography.Text>
            {utilizationRate > 100 ? 'فراتر از بودجه' : utilizationRate > 80 ? 'نزدیک به محدودیت بودجه' : 'در محدوده بودجه'}
          </Typography.Text>
        </Card>

        {/* جدول بودجه‌ها */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام بودجه</TableCell>
                <TableCell>دسته‌بندی</TableCell>
                <TableCell align="right">کل بودجه</TableCell>
                <TableCell align="right">هزینه شده</TableCell>
                <TableCell align="right">باقی‌مانده</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>نرخ استفاده</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockBudgets.map((budget) => {
                const utilization = (budget.spentAmount / budget.totalBudget) * 100;
                return (
                  <TableRow key={budget.id}>
                    <TableCell>{budget.name}</TableCell>
                    <TableCell>{budget.category}</TableCell>
                    <TableCell align="right">
                      {budget.totalBudget.toLocaleString()} تومان
                    </TableCell>
                    <TableCell align="right">
                      {budget.spentAmount.toLocaleString()} تومان
                    </TableCell>
                    <TableCell 
                      align="right"
                      style={{ 
                        color: budget.remainingAmount >= 0 ? 'success.main' : 'error.main',
                       }}
                    >
                      {budget.remainingAmount.toLocaleString()} تومان
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getStatusText(budget.status)}
                        color={getStatusColor(budget.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <div>
                        <div style={{  width: '100%', mr: 1  }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={Math.min(utilization, 100)} 
                            style={{  height: 6, borderRadius: 3  }}
                            color={utilization > 100 ? 'error' : utilization > 80 ? 'warning' : 'success'}
                          />
                        </div>
                        <Typography.Text>
                          {utilization.toFixed(1)}%
                        </Typography.Text>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>

        {/* Dialog برای ایجاد بودجه جدید */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>ایجاد بودجه جدید</div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام بودجه"
                  value={newBudget.name}
                  onChange={(e) => setNewBudget({ ...newBudget, name: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>دسته‌بندی</span>
                  <Select
                    value={newBudget.category}
                    label="دسته‌بندی"
                    onChange={(e) => setNewBudget({ ...newBudget, category: e.target.value })}
                  >
                    {budgetCategories.map((category) => (
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
                  label="مبلغ کل بودجه"
                  type="number"
                  value={newBudget.totalBudget}
                  onChange={(e) => setNewBudget({ ...newBudget, totalBudget: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="دوره بودجه"
                  value={newBudget.period}
                  onChange={(e) => setNewBudget({ ...newBudget, period: e.target.value })}
                  placeholder="مثال: 2024"
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newBudget.description}
                  onChange={(e) => setNewBudget({ ...newBudget, description: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveBudget} variant="contained">
              ایجاد بودجه
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 