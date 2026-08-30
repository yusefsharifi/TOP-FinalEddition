import React, { useState } from 'react';
import { Alert, Button, Card, Checkbox, Col, Collapse, Divider, Input, InputNumber, Modal, Progress, Rate, Row, Select, Table, Tag, Typography } from 'antd';
import { BarChartOutlined, BugOutlined, CheckCircleOutlined, ClockCircleOutlined, CloseCircleOutlined, DownOutlined, EditOutlined, EyeOutlined, FilterOutlined, MailOutlined, PlusOutlined, PrinterOutlined, ReloadOutlined, SafetyOutlined, SpeedOutlined, StarOutlined, WarningOutlined } from '@ant-design/icons';

const mockInspections = [
  {
    id: 'INS-001',
    product: 'لپ‌تاپ Dell XPS 13',
    batch: 'BATCH-2024-001',
    inspector: 'علی احمدی',
    department: 'کنترل کیفیت',
    status: 'completed',
    result: 'passed',
    score: 95,
    date: '1402/11/15',
    duration: '45 دقیقه',
    priority: 'high',
    defects: [
      { name: 'نقص در بسته‌بندی', severity: 'low', resolved: true },
      { name: 'مشکل در رنگ‌آمیزی', severity: 'medium', resolved: false },
    ],
    notes: 'کیفیت عالی، تمام تست‌ها موفق. نیاز به بهبود جزئی در بسته‌بندی.',
    nextInspection: '1402/12/15',
    standards: ['ISO 9001', 'CE Mark'],
    photos: ['photo1.jpg', 'photo2.jpg'],
    documents: ['report.pdf', 'certificate.pdf'],
  },
  {
    id: 'INS-002',
    product: 'ماوس بی‌سیم Logitech',
    batch: 'BATCH-2024-002',
    inspector: 'فاطمه محمدی',
    department: 'تولید',
    status: 'in_progress',
    result: 'failed',
    score: 65,
    date: '1402/11/14',
    duration: '30 دقیقه',
    priority: 'critical',
    defects: [
      { name: 'مشکل در عملکرد دکمه‌ها', severity: 'high', resolved: false },
      { name: 'نقص در اتصال بی‌سیم', severity: 'critical', resolved: false },
    ],
    notes: 'مشکلات جدی در عملکرد. نیاز به بازبینی کامل فرآیند تولید.',
    nextInspection: '1402/11/20',
    standards: ['ISO 9001'],
    photos: ['photo3.jpg'],
    documents: ['report.pdf'],
  },
  {
    id: 'INS-003',
    product: 'کیف چرمی مردانه',
    batch: 'BATCH-2024-003',
    inspector: 'محمد رضایی',
    department: 'بسته‌بندی',
    status: 'scheduled',
    result: 'pending',
    score: 0,
    date: '1402/11/16',
    duration: '20 دقیقه',
    priority: 'medium',
    defects: [],
    notes: 'بازرسی برنامه‌ریزی شده',
    nextInspection: '1402/11/16',
    standards: ['ISO 9001'],
    photos: [],
    documents: [],
  },
];

const inspectionStatuses = [
  { value: 'scheduled', label: 'برنامه‌ریزی شده', color: 'info' },
  { value: 'in_progress', label: 'در حال انجام', color: 'warning' },
  { value: 'completed', label: 'تکمیل شده', color: 'success' },
  { value: 'cancelled', label: 'لغو شده', color: 'error' },
];

const inspectionResults = [
  { value: 'passed', label: 'تأیید شده', color: 'success' },
  { value: 'failed', label: 'رد شده', color: 'error' },
  { value: 'conditional', label: 'مشروط', color: 'warning' },
  { value: 'pending', label: 'در انتظار', color: 'info' },
];

const priorityLevels = [
  { value: 'low', label: 'کم', color: 'success' },
  { value: 'medium', label: 'متوسط', color: 'warning' },
  { value: 'high', label: 'بالا', color: 'error' },
  { value: 'critical', label: 'بحرانی', color: 'error' },
];

const severityLevels = [
  { value: 'low', label: 'کم', color: 'success' },
  { value: 'medium', label: 'متوسط', color: 'warning' },
  { value: 'high', label: 'بالا', color: 'error' },
  { value: 'critical', label: 'بحرانی', color: 'error' },
];

const inspectionSteps = [
  'بررسی ظاهری',
  'تست عملکرد',
  'کنترل ابعاد',
  'تست ایمنی',
  'بسته‌بندی',
  'مستندسازی',
];

export const InspectionManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedInspection, setSelectedInspection] = useState<any>(null);
  const [newInspection, setNewInspection] = useState({
    product: '',
    batch: '',
    inspector: '',
    department: '',
    priority: 'medium',
    date: '',
    notes: '',
  });

  const getStatusColor = (status: string) => {
    const inspectionStatus = inspectionStatuses.find(s => s.value === status);
    return inspectionStatus ? inspectionStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const inspectionStatus = inspectionStatuses.find(s => s.value === status);
    return inspectionStatus ? inspectionStatus.label : 'نامشخص';
  };

  const getResultColor = (result: string) => {
    const inspectionResult = inspectionResults.find(r => r.value === result);
    return inspectionResult ? inspectionResult.color : 'default';
  };

  const getResultText = (result: string) => {
    const inspectionResult = inspectionResults.find(r => r.value === result);
    return inspectionResult ? inspectionResult.label : 'نامشخص';
  };

  const getPriorityColor = (priority: string) => {
    const priorityLevel = priorityLevels.find(p => p.value === priority);
    return priorityLevel ? priorityLevel.color : 'default';
  };

  const getPriorityText = (priority: string) => {
    const priorityLevel = priorityLevels.find(p => p.value === priority);
    return priorityLevel ? priorityLevel.label : 'نامشخص';
  };

  const getSeverityColor = (severity: string) => {
    const severityLevel = severityLevels.find(s => s.value === severity);
    return severityLevel ? severityLevel.color : 'default';
  };

  const getSeverityText = (severity: string) => {
    const severityLevel = severityLevels.find(s => s.value === severity);
    return severityLevel ? severityLevel.label : 'نامشخص';
  };

  const getQualityColor = (score: number) => {
    if (score >= 95) return 'success';
    if (score >= 85) return 'primary';
    if (score >= 75) return 'warning';
    return 'error';
  };

  const handleAddInspection = () => {
    setSelectedInspection(null);
    setOpenDialog(true);
  };

  const handleEditInspection = (inspection: any) => {
    setSelectedInspection(inspection);
    setNewInspection({
      product: inspection.product,
      batch: inspection.batch,
      inspector: inspection.inspector,
      department: inspection.department,
      priority: inspection.priority,
      date: inspection.date,
      notes: inspection.notes,
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedInspection(null);
    setNewInspection({
      product: '',
      batch: '',
      inspector: '',
      department: '',
      priority: 'medium',
      date: '',
      notes: '',
    });
  };

  const handleSaveInspection = () => {
    // در اینجا بازرسی ذخیره می‌شود
    handleCloseDialog();
  };

  const totalInspections = mockInspections.length;
  const completedInspections = mockInspections.filter(i => i.status === 'completed').length;
  const failedInspections = mockInspections.filter(i => i.result === 'failed').length;
  const pendingInspections = mockInspections.filter(i => i.status === 'scheduled').length;

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          مدیریت بازرسی‌ها
        </Typography.Title>
        <div>
          <Button variant="outlined" startIcon={<FilterList />}>
            فیلتر
          </Button>
          <Button variant="outlined" startIcon={<Refresh />}>
            به‌روزرسانی
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={handleAddInspection}>
            بازرسی جدید
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {totalInspections}
            </Typography.Title>
            <Typography.Text>
              کل بازرسی‌ها
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {completedInspections}
            </Typography.Title>
            <Typography.Text>
              تکمیل شده
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {failedInspections}
            </Typography.Title>
            <Typography.Text>
              ناموفق
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {pendingInspections}
            </Typography.Title>
            <Typography.Text>
              در انتظار
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      {/* Alerts */}
      {failedInspections > 0 && (
        <Alert severity="warning" style={{  mb: 3  }}>
          {failedInspections} بازرسی ناموفق وجود دارد که نیاز به بررسی فوری دارد!
        </Alert>
      )}

      {/* Inspections List */}
      <Card>
        <div>
          <Typography.Title level={4}>
            لیست بازرسی‌ها
          </Typography.Title>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>شماره</TableCell>
                  <TableCell>محصول</TableCell>
                  <TableCell>بازرس</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>نتیجه</TableCell>
                  <TableCell align="right">امتیاز</TableCell>
                  <TableCell>اولویت</TableCell>
                  <TableCell>تاریخ</TableCell>
                  <TableCell>عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {mockInspections.map((inspection) => (
                  <TableRow key={inspection.id}>
                    <TableCell>
                      <Typography.Text>
                        {inspection.id}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>{inspection.product}</Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {inspection.batch}
                      </Typography>
                    </TableCell>
                    <TableCell>{inspection.inspector}</TableCell>
                    <TableCell>
                      <Tag
                        label={getStatusText(inspection.status)}
                        color={getStatusColor(inspection.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getResultText(inspection.result)}
                        color={getResultColor(inspection.result) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {inspection.score > 0 ? (
                        <div>
                          <Rating value={inspection.score / 20} readOnly size="small" />
                          <Typography.Text>
                            {inspection.score}/100
                          </Typography.Text>
                        </div>
                      ) : (
                        <Typography.Text>
                          -
                        </Typography.Text>
                      )}
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getPriorityText(inspection.priority)}
                        color={getPriorityColor(inspection.priority) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{inspection.date}</TableCell>
                    <TableCell>
                      <div>
                        <Button type="text" size="small" color="primary">
                          <Visibility />
                        </Button>
                        <Button type="text" size="small" onClick={() => handleEditInspection(inspection)}>
                          <Edit />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </Card>

      {/* Detailed Inspection View */}
      <div style={{  mt: 3  }}>
        <Typography.Title level={4}>
          جزئیات بازرسی‌ها
        </Typography.Title>
        {mockInspections.map((inspection, index) => (
          <Accordion key={index} style={{  mb: 1  }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <div>
                <div>
                  <Typography.Title level={4}>{inspection.id}</Typography.Title>
                  <Typography.Text>
                    {inspection.product} - {inspection.inspector}
                  </Typography.Text>
                </div>
                <div>
                  <Tag
                    label={getStatusText(inspection.status)}
                    color={getStatusColor(inspection.status) as any}
                    size="small"
                  />
                  <Tag
                    label={getResultText(inspection.result)}
                    color={getResultColor(inspection.result) as any}
                    size="small"
                  />
                  {inspection.score > 0 && (
                    <Typography.Text>
                      {inspection.score}/100
                    </Typography.Text>
                  )}
                </div>
              </div>
            </div>
            <AccordionDetails>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  {/* Inspection Steps */}
                  <Typography variant="subtitle2" gutterBottom>
                    مراحل بازرسی:
                  </Typography>
                  <Stepper activeStep={inspection.status === 'completed' ? 5 : 2} orientation="vertical" style={{  mb: 3  }}>
                    {inspectionSteps.map((step, stepIndex) => (
                      <Step key={stepIndex}>
                        <StepLabel>{step}</StepLabel>
                        <StepContent>
                          <Typography.Text>
                            این مرحله {inspection.status === 'completed' ? 'تکمیل شده' : 'در حال انجام'} است.
                          </Typography.Text>
                        </StepContent>
                      </Step>
                    ))}
                  </Stepper>

                  {/* Defects */}
                  {inspection.defects.length > 0 && (
                    <div style={{  mb: 3  }}>
                      <Typography variant="subtitle2" gutterBottom>
                        نقص‌های شناسایی شده:
                      </Typography>
                      {inspection.defects.map((defect, defectIndex) => (
                        <div>
                          <div>
                            <Typography.Text>
                              {defect.name}
                            </Typography.Text>
                            <div>
                              <Tag
                                label={getSeverityText(defect.severity)}
                                color={getSeverityColor(defect.severity) as any}
                                size="small"
                              />
                              <Tag
                                label={defect.resolved ? 'حل شده' : 'حل نشده'}
                                color={defect.resolved ? 'success' : 'error'}
                                size="small"
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Notes */}
                  <Typography variant="subtitle2" gutterBottom>
                    یادداشت‌ها:
                  </Typography>
                  <Typography.Text>
                    {inspection.notes}
                  </Typography.Text>
                </Col>

                <Col xs={Math.round(12 / 12 * 24)}>
                  <Card style={{  p: 2  }}>
                    <Typography variant="subtitle2" gutterBottom>
                      اطلاعات تکمیلی
                    </Typography>
                    <div>
                      <div>
                        <Typography.Text>بخش:</Typography.Text>
                        <Typography.Text>{inspection.department}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>مدت زمان:</Typography.Text>
                        <Typography.Text>{inspection.duration}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>اولویت:</Typography.Text>
                        <Tag
                          label={getPriorityText(inspection.priority)}
                          color={getPriorityColor(inspection.priority) as any}
                          size="small"
                        />
                      </div>
                      <div>
                        <Typography.Text>بازرسی بعدی:</Typography.Text>
                        <Typography.Text>{inspection.nextInspection}</Typography.Text>
                      </div>
                    </div>

                    <Divider style={{  my: 2  }} />

                    <Typography variant="subtitle2" gutterBottom>
                      استانداردها:
                    </Typography>
                    <div>
                      {inspection.standards.map((standard, standardIndex) => (
                        <Tag key={standardIndex} label={standard} size="small" variant="outlined" />
                      ))}
                    </div>

                    <div style={{  mt: 2  }}>
                      <Button variant="outlined" size="small" fullWidth startIcon={<Print />}>
                        چاپ گزارش
                      </Button>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
          </div>
        ))}
      </div>

      {/* Add/Edit Inspection Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          {selectedInspection ? 'ویرایش بازرسی' : 'افزودن بازرسی جدید'}
        </div>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="محصول"
                value={newInspection.product}
                onChange={(e) => setNewInspection({ ...newInspection, product: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="شماره بچ"
                value={newInspection.batch}
                onChange={(e) => setNewInspection({ ...newInspection, batch: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="بازرس"
                value={newInspection.inspector}
                onChange={(e) => setNewInspection({ ...newInspection, inspector: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="بخش"
                value={newInspection.department}
                onChange={(e) => setNewInspection({ ...newInspection, department: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <FormControl fullWidth>
                <InputLabel>اولویت</span>
                <Select
                  value={newInspection.priority}
                  label="اولویت"
                  onChange={(e) => setNewInspection({ ...newInspection, priority: e.target.value })}
                >
                  {priorityLevels.map((priority) => (
                    <MenuItem key={priority.value} value={priority.value}>
                      {priority.label}
                    </Select.Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="تاریخ"
                type="date"
                value={newInspection.date}
                onChange={(e) => setNewInspection({ ...newInspection, date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="یادداشت"
                multiline
                rows={3}
                value={newInspection.notes}
                onChange={(e) => setNewInspection({ ...newInspection, notes: e.target.value })}
              />
            </Col>
          </Row>
        </div>
        <div>
          <Button onClick={handleCloseDialog}>انصراف</Button>
          <Button onClick={handleSaveInspection} variant="contained">
            {selectedInspection ? 'ویرایش' : 'ثبت'}
          </Button>
        </div>
      </Modal>
    </div>
  );
}; 