import React, { useState } from 'react';
import { Alert, Button, Card, Col, Collapse, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { CheckCircleOutlined, DollarOutlined, DownOutlined, GiftOutlined, StarOutlined, TrophyOutlined, UserOutlined, WarningOutlined } from '@ant-design/icons';

const mockBenefits = [
  {
    id: 1,
    employeeName: 'علی احمدی',
    employeeId: 'EMP001',
    position: 'برنامه‌نویس ارشد',
    department: 'توسعه نرم‌افزار',
    baseSalary: 25000000,
    benefits: [
      { type: 'bonus', amount: 5000000, description: 'پاداش عملکرد عالی', date: '1402/11/01' },
      { type: 'insurance', amount: 2000000, description: 'بیمه تکمیلی', date: '1402/10/01' },
      { type: 'transportation', amount: 800000, description: 'حق حمل و نقل', date: '1402/11/01' },
    ],
    totalBenefits: 7800000,
    performanceRating: 4.5,
    lastReview: '1402/09/15',
  },
  {
    id: 2,
    employeeName: 'فاطمه محمدی',
    employeeId: 'EMP002',
    position: 'طراح UI/UX',
    department: 'طراحی',
    baseSalary: 20000000,
    benefits: [
      { type: 'bonus', amount: 3000000, description: 'پاداش پروژه موفق', date: '1402/11/01' },
      { type: 'insurance', amount: 1500000, description: 'بیمه تکمیلی', date: '1402/10/01' },
      { type: 'transportation', amount: 600000, description: 'حق حمل و نقل', date: '1402/11/01' },
    ],
    totalBenefits: 5100000,
    performanceRating: 4.2,
    lastReview: '1402/09/20',
  },
  {
    id: 3,
    employeeName: 'محمد رضایی',
    employeeId: 'EMP003',
    position: 'مدیر پروژه',
    department: 'مدیریت',
    baseSalary: 35000000,
    benefits: [
      { type: 'bonus', amount: 8000000, description: 'پاداش مدیریت عالی', date: '1402/11/01' },
      { type: 'insurance', amount: 3000000, description: 'بیمه تکمیلی', date: '1402/10/01' },
      { type: 'transportation', amount: 1200000, description: 'حق حمل و نقل', date: '1402/11/01' },
      { type: 'meal', amount: 1000000, description: 'حق غذا', date: '1402/11/01' },
    ],
    totalBenefits: 13200000,
    performanceRating: 4.8,
    lastReview: '1402/09/10',
  },
];

const benefitTypes = [
  { value: 'bonus', label: 'پاداش', color: 'success' },
  { value: 'insurance', label: 'بیمه', color: 'primary' },
  { value: 'transportation', label: 'حمل و نقل', color: 'info' },
  { value: 'meal', label: 'غذا', color: 'warning' },
  { value: 'housing', label: 'مسکن', color: 'secondary' },
  { value: 'education', label: 'آموزش', color: 'default' },
];

const departments = [
  'توسعه نرم‌افزار',
  'طراحی',
  'مدیریت',
  'فروش',
  'پشتیبانی',
  'مالی',
];

export const Benefits: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedBenefit, setSelectedBenefit] = useState<any>(null);
  const [newBenefit, setNewBenefit] = useState({
    employeeId: '',
    type: '',
    amount: '',
    description: '',
    date: '',
  });

  const handleAddBenefit = () => {
    setSelectedBenefit(null);
    setOpenDialog(true);
  };

  const handleEditBenefit = (benefit: any) => {
    setSelectedBenefit(benefit);
    setNewBenefit({
      employeeId: benefit.employeeId,
      type: benefit.type,
      amount: benefit.amount.toString(),
      description: benefit.description,
      date: benefit.date,
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedBenefit(null);
    setNewBenefit({
      employeeId: '',
      type: '',
      amount: '',
      description: '',
      date: '',
    });
  };

  const handleSaveBenefit = () => {
    // در اینجا مزیت ذخیره می‌شود
    handleCloseDialog();
  };

  const getTypeColor = (type: string) => {
    const benefitType = benefitTypes.find(t => t.value === type);
    return benefitType ? benefitType.color : 'default';
  };

  const getTypeText = (type: string) => {
    const benefitType = benefitTypes.find(t => t.value === type);
    return benefitType ? benefitType.label : 'نامشخص';
  };

  const getPerformanceColor = (rating: number) => {
    if (rating >= 4.5) return 'success';
    if (rating >= 4.0) return 'primary';
    if (rating >= 3.5) return 'warning';
    return 'error';
  };

  const totalEmployees = mockBenefits.length;
  const totalBenefits = mockBenefits.reduce((sum, b) => sum + b.totalBenefits, 0);
  const averageSalary = mockBenefits.reduce((sum, b) => sum + b.baseSalary, 0) / totalEmployees;
  const averageRating = mockBenefits.reduce((sum, b) => sum + b.performanceRating, 0) / totalEmployees;

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <CardGiftcard style={{  mr: 1  }} />
            مدیریت مزایا و پاداش
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<CardGiftcard />}
            onClick={handleAddBenefit}
          >
            مزیت جدید
          </Button>
        </div>

        {/* خلاصه آمار */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalEmployees}
              </Typography.Title>
              <Typography.Text>
                کل کارکنان
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalBenefits.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                کل مزایا
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {averageSalary.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                میانگین حقوق پایه
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {averageRating.toFixed(1)}
              </Typography.Title>
              <Typography.Text>
                میانگین عملکرد
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        {/* لیست مزایای کارکنان */}
        {mockBenefits.map((employee) => (
          <Accordion key={employee.id} style={{  mb: 2  }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <div>
                <div>
                  <Typography.Title level={4}>{employee.employeeName}</Typography.Title>
                  <Typography.Text>
                    {employee.position} • {employee.department}
                  </Typography.Text>
                </div>
                <div>
                  <Tag
                    label={`${employee.totalBenefits.toLocaleString()} تومان`}
                    color="success"
                    size="small"
                  />
                  <Tag
                    label={`${employee.performanceRating}/5`}
                    color={getPerformanceColor(employee.performanceRating) as any}
                    size="small"
                  />
                </div>
              </div>
            </div>
            <AccordionDetails>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  {/* جزئیات مزایا */}
                  <Typography variant="subtitle2" gutterBottom>
                    جزئیات مزایا:
                  </Typography>
                  <div>
                    {employee.benefits.map((benefit, index) => (
                      <div>
                        <div>
                          <Tag
                            label={getTypeText(benefit.type)}
                            color={getTypeColor(benefit.type) as any}
                            size="small"
                          />
                          <Typography.Text>{benefit.description}</Typography.Text>
                        </div>
                        <div>
                          <Typography.Text>
                            {benefit.amount.toLocaleString()} تومان
                          </Typography.Text>
                          <Typography variant="caption" color="textSecondary">
                            {benefit.date}
                          </Typography>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* اطلاعات حقوق */}
                  <Typography variant="subtitle2" gutterBottom>
                    اطلاعات حقوق:
                  </Typography>
                  <div>
                    <div>
                      <Typography.Text>حقوق پایه:</Typography.Text>
                      <Typography.Text>{employee.baseSalary.toLocaleString()} تومان</Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>کل مزایا:</Typography.Text>
                      <Typography.Text>
                        {employee.totalBenefits.toLocaleString()} تومان
                      </Typography.Text>
                    </div>
                    <div>
                      <Typography.Text>مجموع:</Typography.Text>
                      <Typography.Text>
                        {(employee.baseSalary + employee.totalBenefits).toLocaleString()} تومان
                      </Typography.Text>
                    </div>
                  </div>
                </Col>
                
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Card style={{  p: 2  }}>
                    <Typography variant="subtitle2" gutterBottom>
                      اطلاعات کارمند
                    </Typography>
                    <div>
                      <div>
                        <Typography.Text>کد کارمند:</Typography.Text>
                        <Typography.Text>{employee.employeeId}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>آخرین ارزیابی:</Typography.Text>
                        <Typography.Text>{employee.lastReview}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>امتیاز عملکرد:</Typography.Text>
                        <Typography.Text>
                          {employee.performanceRating}/5
                        </Typography.Text>
                      </div>
                    </div>
                    
                    <div style={{  mt: 2  }}>
                      <Button
                        variant="outlined"
                        size="small"
                        fullWidth
                        onClick={() => handleEditBenefit(employee)}
                      >
                        ویرایش مزایا
                      </Button>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
          </div>
        ))}

        {/* Dialog برای اضافه/ویرایش مزیت */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedBenefit ? 'ویرایش مزیت' : 'افزودن مزیت جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="کد کارمند"
                  value={newBenefit.employeeId}
                  onChange={(e) => setNewBenefit({ ...newBenefit, employeeId: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>نوع مزیت</span>
                  <Select
                    value={newBenefit.type}
                    label="نوع مزیت"
                    onChange={(e) => setNewBenefit({ ...newBenefit, type: e.target.value })}
                  >
                    {benefitTypes.map((type) => (
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
                  label="مبلغ"
                  type="number"
                  value={newBenefit.amount}
                  onChange={(e) => setNewBenefit({ ...newBenefit, amount: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ"
                  type="date"
                  value={newBenefit.date}
                  onChange={(e) => setNewBenefit({ ...newBenefit, date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newBenefit.description}
                  onChange={(e) => setNewBenefit({ ...newBenefit, description: e.target.value })}
                  placeholder="توضیحات مزیت..."
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveBenefit} variant="contained">
              {selectedBenefit ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 