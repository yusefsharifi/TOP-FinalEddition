import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Row, Table, Tag, Typography } from 'antd';
import { CreditCardOutlined, MailOutlined, PhoneOutlined, PlusOutlined } from '@ant-design/icons';

const mockReceivables = [
  {
    id: 1,
    customer: 'شرکت ABC',
    invoiceNumber: 'INV-001',
    amount: 50000,
    dueDate: '2024-05-15',
    status: 'overdue',
    daysOverdue: 7,
    contact: '+98-912-123-4567',
    email: 'finance@abc.com',
  },
  {
    id: 2,
    customer: 'شرکت XYZ',
    invoiceNumber: 'INV-002',
    amount: 75000,
    dueDate: '2024-05-20',
    status: 'pending',
    daysOverdue: 0,
    contact: '+98-912-123-4568',
    email: 'accounting@xyz.com',
  },
  {
    id: 3,
    customer: 'شرکت DEF',
    invoiceNumber: 'INV-003',
    amount: 30000,
    dueDate: '2024-04-30',
    status: 'paid',
    daysOverdue: 0,
    contact: '+98-912-123-4569',
    email: 'payments@def.com',
  },
];

export const AccountsReceivable: React.FC = () => {
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

  const totalReceivables = mockReceivables.reduce((sum, item) => sum + item.amount, 0);
  const overdueAmount = mockReceivables
    .filter(item => item.status === 'overdue')
    .reduce((sum, item) => sum + item.amount, 0);

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            حساب‌های دریافتنی
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
                {totalReceivables.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                کل مطالبات
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {overdueAmount.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                مطالبات معوق
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {mockReceivables.filter(item => item.status === 'paid').length}
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
                <TableCell>مشتری</TableCell>
                <TableCell>شماره فاکتور</TableCell>
                <TableCell align="right">مبلغ</TableCell>
                <TableCell>تاریخ سررسید</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>روزهای معوق</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockReceivables.map((receivable) => (
                <TableRow key={receivable.id}>
                  <TableCell>{receivable.customer}</TableCell>
                  <TableCell>{receivable.invoiceNumber}</TableCell>
                  <TableCell align="right">
                    {receivable.amount.toLocaleString()} تومان
                  </TableCell>
                  <TableCell>{receivable.dueDate}</TableCell>
                  <TableCell>
                    <Tag
                      label={getStatusText(receivable.status)}
                      color={getStatusColor(receivable.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {receivable.daysOverdue > 0 ? `${receivable.daysOverdue} روز` : '-'}
                  </TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleContact(receivable)}
                      >
                        <Payment />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleContact(receivable)}
                      >
                        <Email />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleContact(receivable)}
                      >
                        <Phone />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Dialog برای تماس با مشتری */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>تماس با مشتری</div>
          <div>
            {selectedInvoice && (
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography.Title level={5}>
                    {selectedInvoice.customer}
                  </Typography.Title>
                  <Typography.Text>
                    شماره فاکتور: {selectedInvoice.invoiceNumber}
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
                    placeholder="پیام خود را برای یادآوری پرداخت بنویسید..."
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