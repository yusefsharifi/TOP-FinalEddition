import React, { useState } from 'react';
import { Alert, Button, Card, Col, Collapse, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { AppstoreOutlined, CalculatorOutlined, CheckCircleOutlined, DollarOutlined, DownOutlined, EditOutlined, FileTextOutlined, PlusOutlined, UploadOutlined, WarningOutlined } from '@ant-design/icons';

const mockTaxes = [
  {
    id: 1,
    title: 'مالیات بر ارزش افزوده',
    type: 'vat',
    period: '1402/10',
    amount: 15000000,
    dueDate: '1402/11/15',
    status: 'paid',
    paidDate: '1402/11/10',
    description: 'مالیات بر ارزش افزوده دوره مهر 1402',
    receipt: 'vat-receipt-001.pdf',
    rate: 9,
    taxableAmount: 166666667,
    penalty: 0,
    interest: 0,
  },
  {
    id: 2,
    title: 'مالیات بر درآمد',
    type: 'income-tax',
    period: '1402',
    amount: 45000000,
    dueDate: '1403/03/15',
    status: 'pending',
    paidDate: '',
    description: 'مالیات بر درآمد سال 1402',
    receipt: '',
    rate: 25,
    taxableAmount: 180000000,
    penalty: 0,
    interest: 0,
  },
  {
    id: 3,
    title: 'عوارض شهرداری',
    type: 'municipal',
    period: '1402/11',
    amount: 8000000,
    dueDate: '1402/12/15',
    status: 'overdue',
    paidDate: '',
    description: 'عوارض شهرداری آبان 1402',
    receipt: '',
    rate: 3,
    taxableAmount: 266666667,
    penalty: 1200000,
    interest: 240000,
  },
  {
    id: 4,
    title: 'مالیات بر حقوق',
    type: 'payroll-tax',
    period: '1402/11',
    amount: 12000000,
    dueDate: '1402/12/05',
    status: 'paid',
    paidDate: '1402/12/01',
    description: 'مالیات بر حقوق کارکنان آبان 1402',
    receipt: 'payroll-tax-receipt-001.pdf',
    rate: 10,
    taxableAmount: 120000000,
    penalty: 0,
    interest: 0,
  },
];

const taxTypes = [
  { value: 'vat', label: 'مالیات بر ارزش افزوده', color: 'primary' },
  { value: 'income-tax', label: 'مالیات بر درآمد', color: 'secondary' },
  { value: 'payroll-tax', label: 'مالیات بر حقوق', color: 'info' },
  { value: 'municipal', label: 'عوارض شهرداری', color: 'warning' },
  { value: 'property-tax', label: 'مالیات بر دارایی', color: 'success' },
  { value: 'customs', label: 'عوارض گمرکی', color: 'error' },
];

const taxStatuses = [
  { value: 'pending', label: 'در انتظار پرداخت', color: 'warning' },
  { value: 'paid', label: 'پرداخت شده', color: 'success' },
  { value: 'overdue', label: 'معوق', color: 'error' },
  { value: 'partial', label: 'پرداخت جزئی', color: 'info' },
];

export const TaxManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTax, setSelectedTax] = useState<any>(null);
  const [newTax, setNewTax] = useState({
    title: '',
    type: '',
    period: '',
    amount: '',
    dueDate: '',
    description: '',
    rate: '',
    taxableAmount: '',
  });

  const handleAddTax = () => {
    setSelectedTax(null);
    setOpenDialog(true);
  };

  const handleEditTax = (tax: any) => {
    setSelectedTax(tax);
    setNewTax({
      title: tax.title,
      type: tax.type,
      period: tax.period,
      amount: tax.amount.toString(),
      dueDate: tax.dueDate,
      description: tax.description,
      rate: tax.rate.toString(),
      taxableAmount: tax.taxableAmount.toString(),
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedTax(null);
    setNewTax({
      title: '',
      type: '',
      period: '',
      amount: '',
      dueDate: '',
      description: '',
      rate: '',
      taxableAmount: '',
    });
  };

  const handleSaveTax = () => {
    // در اینجا مالیات ذخیره می‌شود
    handleCloseDialog();
  };

  const getTypeColor = (type: string) => {
    const taxType = taxTypes.find(t => t.value === type);
    return taxType ? taxType.color : 'default';
  };

  const getTypeText = (type: string) => {
    const taxType = taxTypes.find(t => t.value === type);
    return taxType ? taxType.label : 'نامشخص';
  };

  const getStatusColor = (status: string) => {
    const taxStatus = taxStatuses.find(s => s.value === status);
    return taxStatus ? taxStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const taxStatus = taxStatuses.find(s => s.value === status);
    return taxStatus ? taxStatus.label : 'نامشخص';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid':
        return <CheckCircle color="success" />;
      case 'overdue':
        return <Warning color="error" />;
      case 'pending':
        return <Warning color="warning" />;
      case 'partial':
        return <Calculate color="info" />;
      default:
        return <Receipt color="action" />;
    }
  };

  const totalTaxes = mockTaxes.length;
  const paidTaxes = mockTaxes.filter(t => t.status === 'paid').length;
  const overdueTaxes = mockTaxes.filter(t => t.status === 'overdue').length;
  const totalAmount = mockTaxes.reduce((sum, t) => sum + t.amount, 0);
  const totalPenalty = mockTaxes.reduce((sum, t) => sum + t.penalty + t.interest, 0);

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <Receipt style={{  mr: 1  }} />
            مدیریت مالیات و عوارض
          </Typography.Title>
          <div>
            <Button
              variant="outlined"
              startIcon={<Calculate />}
            >
              محاسبه مالیات
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddTax}
            >
              مالیات جدید
            </Button>
          </div>
        </div>

        {/* خلاصه آمار */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalTaxes}
              </Typography.Title>
              <Typography.Text>
                کل مالیات‌ها
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalAmount.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                کل مبلغ مالیات
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {overdueTaxes}
              </Typography.Title>
              <Typography.Text>
                مالیات معوق
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalPenalty.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                جریمه و بهره
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        {/* هشدار مالیات معوق */}
        {overdueTaxes > 0 && (
          <Alert severity="error" style={{  mb: 3  }}>
            {overdueTaxes} مالیات معوق وجود دارد که نیاز به پرداخت فوری دارد!
          </Alert>
        )}

        {/* لیست مالیات‌ها */}
        {mockTaxes.map((tax) => (
          <Accordion key={tax.id} style={{  mb: 2  }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <div>
                <div>
                  <Typography.Title level={4}>{tax.title}</Typography.Title>
                  <Typography.Text>
                    دوره: {tax.period} • نرخ: {tax.rate}%
                  </Typography.Text>
                </div>
                <div>
                  <Tag
                    label={tax.amount.toLocaleString() + ' تومان'}
                    color="success"
                    size="small"
                  />
                  <Tag
                    label={getTypeText(tax.type)}
                    color={getTypeColor(tax.type) as any}
                    size="small"
                  />
                  <div>
                    {getStatusIcon(tax.status)}
                    <Tag
                      label={getStatusText(tax.status)}
                      color={getStatusColor(tax.status) as any}
                      size="small"
                    />
                  </div>
                </div>
              </div>
            </div>
            <AccordionDetails>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  {/* جزئیات مالیات */}
                  <Typography variant="subtitle2" gutterBottom>
                    توضیحات:
                  </Typography>
                  <Typography.Text>
                    {tax.description}
                  </Typography.Text>

                  {/* محاسبات مالیات */}
                  <Typography variant="subtitle2" gutterBottom>
                    محاسبات مالیات:
                  </Typography>
                  <div style={{  mb: 2  }}>
                    <div>
                      <Typography.Text>مبلغ مشمول مالیات:</Typography.Text>
                      <Typography.Text>{tax.taxableAmount.toLocaleString()} تومان</Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>نرخ مالیات:</Typography.Text>
                      <Typography.Text>{tax.rate}%</Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>مبلغ مالیات:</Typography.Text>
                      <Typography.Text>
                        {tax.amount.toLocaleString()} تومان
                      </Typography.Text>
                    </div>
                    {(tax.penalty > 0 || tax.interest > 0) && (
                      <>
                        <div>
                          <Typography.Text>جریمه:</Typography.Text>
                          <Typography.Text>
                            {tax.penalty.toLocaleString()} تومان
                          </Typography.Text>
                        </div>
                        <div>
                          <Typography.Text>بهره:</Typography.Text>
                          <Typography.Text>
                            {tax.interest.toLocaleString()} تومان
                          </Typography.Text>
                        </div>
                      </>
                    )}
                    <div>
                      <Typography.Text>مجموع قابل پرداخت:</Typography.Text>
                      <Typography.Text>
                        {(tax.amount + tax.penalty + tax.interest).toLocaleString()} تومان
                      </Typography.Text>
                    </div>
                  </div>

                  {/* رسید */}
                  {tax.receipt && (
                    <div>
                      <Typography variant="subtitle2" gutterBottom>
                        رسید پرداخت:
                      </Typography>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<FileUpload />}
                      >
                        {tax.receipt}
                      </Button>
                    </div>
                  )}
                </Col>
                
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Card style={{  p: 2  }}>
                    <Typography variant="subtitle2" gutterBottom>
                      اطلاعات پرداخت
                    </Typography>
                    <div>
                      <div>
                        <Typography.Text>تاریخ سررسید:</Typography.Text>
                        <Typography.Text>{tax.dueDate}</Typography.Text>
                      </div>
                      {tax.paidDate && (
                        <div>
                          <Typography.Text>تاریخ پرداخت:</Typography.Text>
                          <Typography.Text>
                            {tax.paidDate}
                          </Typography.Text>
                        </div>
                      )}
                      <div>
                        <Typography.Text>وضعیت:</Typography.Text>
                        <Typography.Text>
                          {getStatusText(tax.status)}
                        </Typography.Text>
                      </div>
                    </div>
                    
                    <div style={{  mt: 2  }}>
                      <Button
                        variant="outlined"
                        size="small"
                        fullWidth
                        onClick={() => handleEditTax(tax)}
                      >
                        ویرایش مالیات
                      </Button>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
          </div>
        ))}

        {/* Dialog برای اضافه/ویرایش مالیات */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedTax ? 'ویرایش مالیات' : 'افزودن مالیات جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="عنوان مالیات"
                  value={newTax.title}
                  onChange={(e) => setNewTax({ ...newTax, title: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>نوع مالیات</span>
                  <Select
                    value={newTax.type}
                    label="نوع مالیات"
                    onChange={(e) => setNewTax({ ...newTax, type: e.target.value })}
                  >
                    {taxTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="دوره مالیاتی"
                  value={newTax.period}
                  onChange={(e) => setNewTax({ ...newTax, period: e.target.value })}
                  placeholder="مثال: 1402/10"
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="مبلغ مالیات"
                  type="number"
                  value={newTax.amount}
                  onChange={(e) => setNewTax({ ...newTax, amount: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ سررسید"
                  type="date"
                  value={newTax.dueDate}
                  onChange={(e) => setNewTax({ ...newTax, dueDate: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نرخ مالیات (%)"
                  type="number"
                  value={newTax.rate}
                  onChange={(e) => setNewTax({ ...newTax, rate: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="مبلغ مشمول مالیات"
                  type="number"
                  value={newTax.taxableAmount}
                  onChange={(e) => setNewTax({ ...newTax, taxableAmount: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newTax.description}
                  onChange={(e) => setNewTax({ ...newTax, description: e.target.value })}
                  placeholder="توضیحات مالیات..."
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveTax} variant="contained">
              {selectedTax ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 