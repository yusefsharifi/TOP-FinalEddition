import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Row, Table, Tag, Typography } from 'antd';
import { CreditCardOutlined, FileTextOutlined, MailOutlined, PhoneOutlined, PlusOutlined } from '@ant-design/icons';

const mockPayables = [
  {
    id: 1,
    supplier: 'تأمین‌کننده A',
    invoiceNumber: 'SUP-001',
    amount: 45000,
    dueDate: '2024-05-10',
    status: 'overdue',
    daysOverdue: 12,
    contact: '+98-912-123-4570',
    email: 'accounts@suppliera.com',
    category: 'مواد اولیه',
  },
  {
    id: 2,
    supplier: 'تأمین‌کننده B',
    invoiceNumber: 'SUP-002',
    amount: 80000,
    dueDate: '2024-05-25',
    status: 'pending',
    daysOverdue: 0,
    contact: '+98-912-123-4571',
    email: 'finance@supplierb.com',
    category: 'تجهیزات',
  },
  {
    id: 3,
    supplier: 'تأمین‌کننده C',
    invoiceNumber: 'SUP-003',
    amount: 25000,
    dueDate: '2024-04-28',
    status: 'paid',
    daysOverdue: 0,
    contact: '+98-912-123-4572',
    email: 'payments@supplierc.com',
    category: 'خدمات',
  },
];

export const AccountsPayable: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<any>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'overdue':
        return 'error';
      case 'pending':
        return 'warning';
      case 'paid':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'overdue':
        return 'معوق';
      case 'pending':
        return 'در انتظار';
      case 'paid':
        return 'پرداخت شده';
      default:
        return 'نامشخص';
    }
  };

  const handleContact = (invoice: any) => {
    setSelectedInvoice(invoice);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedInvoice(null);
  };

  const totalPayables = mockPayables.reduce((sum, item) => sum + item.amount, 0);
  const overdueAmount = mockPayables
    .filter(item => item.status === 'overdue')
    .reduce((sum, item) => sum + item.amount, 0);

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            حساب‌های پرداختنی
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
          >
            فاکتور جدید
          </Button>
        </div>

        {/* خلاصه آماری */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalPayables.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                کل بدهی‌ها
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {overdueAmount.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                بدهی‌های معوق
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {mockPayables.filter(item => item.status === 'paid').length}
              </Typography.Title>
              <Typography.Text>
                فاکتورهای پرداخت شده
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>تأمین‌کننده</TableCell>
                <TableCell>شماره فاکتور</TableCell>
                <TableCell>دسته‌بندی</TableCell>
                <TableCell align="right">مبلغ</TableCell>
                <TableCell>تاریخ سررسید</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>روزهای معوق</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockPayables.map((payable) => (
                <TableRow key={payable.id}>
                  <TableCell>{payable.supplier}</TableCell>
                  <TableCell>{payable.invoiceNumber}</TableCell>
                  <TableCell>{payable.category}</TableCell>
                  <TableCell align="right">
                    {payable.amount.toLocaleString()} تومان
                  </TableCell>
                  <TableCell>{payable.dueDate}</TableCell>
                  <TableCell>
                    <Tag
                      label={getStatusText(payable.status)}
                      color={getStatusColor(payable.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {payable.daysOverdue > 0 ? `${payable.daysOverdue} روز` : '-'}
                  </TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleContact(payable)}
                      >
                        <Payment />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleContact(payable)}
                      >
                        <Email />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleContact(payable)}
                      >
                        <Phone />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleContact(payable)}
                      >
                        <Receipt />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Dialog برای تماس با تأمین‌کننده */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>تماس با تأمین‌کننده</div>
          <div>
            {selectedInvoice && (
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography.Title level={5}>
                    {selectedInvoice.supplier}
                  </Typography.Title>
                  <Typography.Text>
                    شماره فاکتور: {selectedInvoice.invoiceNumber}
                  </Typography.Text>
                  <Typography.Text>
                    دسته‌بندی: {selectedInvoice.category}
                  </Typography.Text>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="شماره تماس"
                    value={selectedInvoice.contact}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="ایمیل"
                    value={selectedInvoice.email}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="پیام"
                    multiline
                    rows={4}
                    placeholder="پیام خود را برای هماهنگی پرداخت بنویسید..."
                  />
                </Col>
              </Row>
            )}
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button variant="contained" color="primary">
              ارسال پیام
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 