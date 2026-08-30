import React, { useState } from 'react';
import { Alert, Button, Card, Col, Collapse, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { AppstoreOutlined, CheckCircleOutlined, DollarOutlined, DownOutlined, EditOutlined, FileTextOutlined, PlusOutlined, UploadOutlined, WarningOutlined } from '@ant-design/icons';

const mockExpenses = [
  {
    id: 1,
    title: 'خرید تجهیزات اداری',
    category: 'office-supplies',
    amount: 2500000,
    date: '1402/11/15',
    status: 'approved',
    approvedBy: 'مدیر مالی',
    approvedDate: '1402/11/16',
    description: 'خرید میز، صندلی و تجهیزات اداری برای بخش جدید',
    receipt: 'receipt-001.pdf',
    department: 'توسعه نرم‌افزار',
    employee: 'علی احمدی',
    budget: 3000000,
    remainingBudget: 500000,
  },
  {
    id: 2,
    title: 'سفر کاری تهران',
    category: 'travel',
    amount: 1800000,
    date: '1402/11/10',
    status: 'pending',
    approvedBy: '',
    approvedDate: '',
    description: 'سفر کاری برای شرکت در کنفرانس فناوری',
    receipt: 'receipt-002.pdf',
    department: 'فروش',
    employee: 'فاطمه محمدی',
    budget: 2000000,
    remainingBudget: 200000,
  },
  {
    id: 3,
    title: 'نرم‌افزار لایسنس',
    category: 'software',
    amount: 5000000,
    date: '1402/11/08',
    status: 'approved',
    approvedBy: 'مدیر فنی',
    approvedDate: '1402/11/09',
    description: 'خرید لایسنس نرم‌افزارهای توسعه',
    receipt: 'receipt-003.pdf',
    department: 'توسعه نرم‌افزار',
    employee: 'محمد رضایی',
    budget: 6000000,
    remainingBudget: 1000000,
  },
  {
    id: 4,
    title: 'تعمیرات ساختمان',
    category: 'maintenance',
    amount: 3500000,
    date: '1402/11/05',
    status: 'rejected',
    approvedBy: 'مدیر مالی',
    approvedDate: '1402/11/06',
    description: 'تعمیرات سیستم تهویه مطبوع',
    receipt: '',
    department: 'عملیات',
    employee: 'زهرا کریمی',
    budget: 4000000,
    remainingBudget: 500000,
    rejectionReason: 'هزینه بیش از حد مجاز',
  },
];

const expenseCategories = [
  { value: 'office-supplies', label: 'تجهیزات اداری', color: 'primary' },
  { value: 'travel', label: 'سفر', color: 'secondary' },
  { value: 'software', label: 'نرم‌افزار', color: 'info' },
  { value: 'maintenance', label: 'تعمیرات', color: 'warning' },
  { value: 'marketing', label: 'بازاریابی', color: 'success' },
  { value: 'utilities', label: 'خدمات شهری', color: 'default' },
  { value: 'insurance', label: 'بیمه', color: 'error' },
];

const expenseStatuses = [
  { value: 'pending', label: 'در انتظار تأیید', color: 'warning' },
  { value: 'approved', label: 'تأیید شده', color: 'success' },
  { value: 'rejected', label: 'رد شده', color: 'error' },
  { value: 'paid', label: 'پرداخت شده', color: 'info' },
];

const departments = [
  'توسعه نرم‌افزار',
  'طراحی',
  'مدیریت',
  'فروش',
  'پشتیبانی',
  'مالی',
  'عملیات',
];

export const ExpenseManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState<any>(null);
  const [newExpense, setNewExpense] = useState({
    title: '',
    category: '',
    amount: '',
    date: '',
    description: '',
    department: '',
    employee: '',
    budget: '',
  });

  const handleAddExpense = () => {
    setSelectedExpense(null);
    setOpenDialog(true);
  };

  const handleEditExpense = (expense: any) => {
    setSelectedExpense(expense);
    setNewExpense({
      title: expense.title,
      category: expense.category,
      amount: expense.amount.toString(),
      date: expense.date,
      description: expense.description,
      department: expense.department,
      employee: expense.employee,
      budget: expense.budget.toString(),
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedExpense(null);
    setNewExpense({
      title: '',
      category: '',
      amount: '',
      date: '',
      description: '',
      department: '',
      employee: '',
      budget: '',
    });
  };

  const handleSaveExpense = () => {
    // در اینجا هزینه ذخیره می‌شود
    handleCloseDialog();
  };

  const getCategoryColor = (category: string) => {
    const expenseCategory = expenseCategories.find(c => c.value === category);
    return expenseCategory ? expenseCategory.color : 'default';
  };

  const getCategoryText = (category: string) => {
    const expenseCategory = expenseCategories.find(c => c.value === category);
    return expenseCategory ? expenseCategory.label : 'نامشخص';
  };

  const getStatusColor = (status: string) => {
    const expenseStatus = expenseStatuses.find(s => s.value === status);
    return expenseStatus ? expenseStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const expenseStatus = expenseStatuses.find(s => s.value === status);
    return expenseStatus ? expenseStatus.label : 'نامشخص';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle color="success" />;
      case 'rejected':
        return <Warning color="error" />;
      case 'pending':
        return <Warning color="warning" />;
      case 'paid':
        return <CheckCircle color="info" />;
      default:
        return <Receipt color="action" />;
    }
  };

  const totalExpenses = mockExpenses.length;
  const approvedExpenses = mockExpenses.filter(e => e.status === 'approved').length;
  const pendingExpenses = mockExpenses.filter(e => e.status === 'pending').length;
  const totalAmount = mockExpenses.reduce((sum, e) => sum + e.amount, 0);
  const approvedAmount = mockExpenses.filter(e => e.status === 'approved').reduce((sum, e) => sum + e.amount, 0);

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <Receipt style={{  mr: 1  }} />
            مدیریت هزینه‌ها
          </Typography.Title>
          <div>
            <Button
              variant="outlined"
              startIcon={<FileUpload />}
            >
              آپلود رسید
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddExpense}
            >
              هزینه جدید
            </Button>
          </div>
        </div>

        {/* خلاصه آمار */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalExpenses}
              </Typography.Title>
              <Typography.Text>
                کل هزینه‌ها
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalAmount.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                کل مبلغ
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {pendingExpenses}
              </Typography.Title>
              <Typography.Text>
                در انتظار تأیید
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {approvedAmount.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                مبلغ تأیید شده
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        {/* هشدار بودجه */}
        {mockExpenses.some(e => e.remainingBudget < 0) && (
          <Alert severity="warning" style={{  mb: 3  }}>
            برخی بخش‌ها از بودجه تعیین شده فراتر رفته‌اند!
          </Alert>
        )}

        {/* لیست هزینه‌ها */}
        {mockExpenses.map((expense) => (
          <Accordion key={expense.id} style={{  mb: 2  }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <div>
                <div>
                  <Typography.Title level={4}>{expense.title}</Typography.Title>
                  <Typography.Text>
                    {expense.department} • {expense.employee}
                  </Typography.Text>
                </div>
                <div>
                  <Tag
                    label={expense.amount.toLocaleString() + ' تومان'}
                    color="success"
                    size="small"
                  />
                  <Tag
                    label={getCategoryText(expense.category)}
                    color={getCategoryColor(expense.category) as any}
                    size="small"
                  />
                  <div>
                    {getStatusIcon(expense.status)}
                    <Tag
                      label={getStatusText(expense.status)}
                      color={getStatusColor(expense.status) as any}
                      size="small"
                    />
                  </div>
                </div>
              </div>
            </div>
            <AccordionDetails>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  {/* جزئیات هزینه */}
                  <Typography variant="subtitle2" gutterBottom>
                    توضیحات:
                  </Typography>
                  <Typography.Text>
                    {expense.description}
                  </Typography.Text>

                  {/* بودجه */}
                  <Typography variant="subtitle2" gutterBottom>
                    وضعیت بودجه:
                  </Typography>
                  <div style={{  mb: 2  }}>
                    <div>
                      <Typography.Text>بودجه تخصیص یافته:</Typography.Text>
                      <Typography.Text>{expense.budget.toLocaleString()} تومان</Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>هزینه فعلی:</Typography.Text>
                      <Typography.Text>
                        {expense.amount.toLocaleString()} تومان
                      </Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>بودجه باقی‌مانده:</Typography.Text>
                      <Typography.Text>= 0 ? 'success.main' : 'error'}>
                        {expense.remainingBudget.toLocaleString()} تومان
                      </Typography.Text>
                    </div>
                    <LinearProgress
                      variant="determinate"
                      value={(expense.amount / expense.budget) * 100}
                      color={expense.remainingBudget >= 0 ? 'success' : 'error'}
                      style={{  height: 8, borderRadius: 4  }}
                    />
                  </div>

                  {/* رسید */}
                  {expense.receipt && (
                    <div>
                      <Typography variant="subtitle2" gutterBottom>
                        رسید:
                      </Typography>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<FileUpload />}
                      >
                        {expense.receipt}
                      </Button>
                    </div>
                  )}
                </Col>
                
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Card style={{  p: 2  }}>
                    <Typography variant="subtitle2" gutterBottom>
                      اطلاعات تأیید
                    </Typography>
                    <div>
                      <div>
                        <Typography.Text>تاریخ:</Typography.Text>
                        <Typography.Text>{expense.date}</Typography.Text>
                      </div>
                      {expense.approvedBy && (
                        <div>
                          <Typography.Text>تأییدکننده:</Typography.Text>
                          <Typography.Text>{expense.approvedBy}</Typography.Text>
                        </div>
                      )}
                      {expense.approvedDate && (
                        <div>
                          <Typography.Text>تاریخ تأیید:</Typography.Text>
                          <Typography.Text>{expense.approvedDate}</Typography.Text>
                        </div>
                      )}
                      {expense.rejectionReason && (
                        <div>
                          <Typography.Text>دلیل رد:</Typography.Text>
                          <Typography.Text>
                            {expense.rejectionReason}
                          </Typography.Text>
                        </div>
                      )}
                    </div>
                    
                    <div style={{  mt: 2  }}>
                      <Button
                        variant="outlined"
                        size="small"
                        fullWidth
                        onClick={() => handleEditExpense(expense)}
                      >
                        ویرایش هزینه
                      </Button>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
          </div>
        ))}

        {/* Dialog برای اضافه/ویرایش هزینه */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedExpense ? 'ویرایش هزینه' : 'افزودن هزینه جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="عنوان هزینه"
                  value={newExpense.title}
                  onChange={(e) => setNewExpense({ ...newExpense, title: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>دسته‌بندی</span>
                  <Select
                    value={newExpense.category}
                    label="دسته‌بندی"
                    onChange={(e) => setNewExpense({ ...newExpense, category: e.target.value })}
                  >
                    {expenseCategories.map((category) => (
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
                  label="مبلغ"
                  type="number"
                  value={newExpense.amount}
                  onChange={(e) => setNewExpense({ ...newExpense, amount: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ"
                  type="date"
                  value={newExpense.date}
                  onChange={(e) => setNewExpense({ ...newExpense, date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>بخش</span>
                  <Select
                    value={newExpense.department}
                    label="بخش"
                    onChange={(e) => setNewExpense({ ...newExpense, department: e.target.value })}
                  >
                    {departments.map((dept) => (
                      <MenuItem key={dept} value={dept}>
                        {dept}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="کارمند"
                  value={newExpense.employee}
                  onChange={(e) => setNewExpense({ ...newExpense, employee: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="بودجه تخصیص یافته"
                  type="number"
                  value={newExpense.budget}
                  onChange={(e) => setNewExpense({ ...newExpense, budget: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newExpense.description}
                  onChange={(e) => setNewExpense({ ...newExpense, description: e.target.value })}
                  placeholder="توضیحات کامل هزینه..."
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveExpense} variant="contained">
              {selectedExpense ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 