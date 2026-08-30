import React, { useState } from 'react';
import { Alert, Badge, Button, Card, Col, Collapse, Divider, Input, InputNumber, Modal, Progress, Rate, Row, Select, Table, Tag, Typography } from 'antd';
import { BugOutlined, CheckCircleOutlined, CheckSquareOutlined, ClockCircleOutlined, CloseCircleOutlined, DownOutlined, EditOutlined, ExclamationCircleOutlined, EyeOutlined, FilterOutlined, MailOutlined, PlusOutlined, PrinterOutlined, ReloadOutlined, SafetyOutlined, SpeedOutlined, StarOutlined, UserOutlined, WarningOutlined } from '@ant-design/icons';

const mockDefects = [
  {
    id: 'DEF-001',
    title: 'نقص در بسته‌بندی محصولات',
    category: 'بسته‌بندی',
    severity: 'medium',
    status: 'resolved',
    priority: 'high',
    reportedBy: 'علی احمدی',
    assignedTo: 'فاطمه محمدی',
    reportedDate: '1402/11/15',
    resolvedDate: '1402/11/18',
    product: 'لپ‌تاپ Dell XPS 13',
    batch: 'BATCH-2024-001',
    description: 'مشکل در بسته‌بندی محصولات که باعث آسیب به محصول می‌شود.',
    rootCause: 'عدم کنترل کیفیت در خط بسته‌بندی',
    solution: 'بهبود فرآیند بسته‌بندی و اضافه کردن کنترل‌های بیشتر',
    impact: 'تأثیر متوسط بر رضایت مشتری',
    cost: 2500000,
    timeSpent: '8 ساعت',
    attachments: ['photo1.jpg', 'report.pdf'],
    history: [
      { date: '1402/11/15', action: 'گزارش شد', user: 'علی احمدی', status: 'open' },
      { date: '1402/11/16', action: 'تخصیص داده شد', user: 'مدیر کیفیت', status: 'assigned' },
      { date: '1402/11/17', action: 'تحلیل علت ریشه', user: 'فاطمه محمدی', status: 'investigating' },
      { date: '1402/11/18', action: 'حل شد', user: 'فاطمه محمدی', status: 'resolved' },
    ],
  },
  {
    id: 'DEF-002',
    title: 'مشکل در عملکرد دکمه‌های ماوس',
    category: 'عملکردی',
    severity: 'high',
    status: 'investigating',
    priority: 'critical',
    reportedBy: 'محمد رضایی',
    assignedTo: 'احمد کریمی',
    reportedDate: '1402/11/14',
    resolvedDate: null,
    product: 'ماوس بی‌سیم Logitech',
    batch: 'BATCH-2024-002',
    description: 'دکمه‌های ماوس به درستی کار نمی‌کنند و گاهی گیر می‌کنند.',
    rootCause: 'مشکل در طراحی مکانیکی دکمه‌ها',
    solution: 'بازبینی طراحی و بهبود کیفیت مواد',
    impact: 'تأثیر بالا بر عملکرد محصول',
    cost: 5000000,
    timeSpent: '12 ساعت',
    attachments: ['video1.mp4', 'analysis.pdf'],
    history: [
      { date: '1402/11/14', action: 'گزارش شد', user: 'محمد رضایی', status: 'open' },
      { date: '1402/11/15', action: 'تخصیص داده شد', user: 'مدیر کیفیت', status: 'assigned' },
      { date: '1402/11/16', action: 'تحلیل علت ریشه', user: 'احمد کریمی', status: 'investigating' },
    ],
  },
  {
    id: 'DEF-003',
    title: 'مشکل در رنگ‌آمیزی کیف',
    category: 'ظاهری',
    severity: 'low',
    status: 'open',
    priority: 'medium',
    reportedBy: 'زهرا احمدی',
    assignedTo: null,
    reportedDate: '1402/11/13',
    resolvedDate: null,
    product: 'کیف چرمی مردانه',
    batch: 'BATCH-2024-003',
    description: 'رنگ‌آمیزی کیف یکنواخت نیست و لکه‌هایی دارد.',
    rootCause: null,
    solution: null,
    impact: 'تأثیر کم بر ظاهر محصول',
    cost: 1000000,
    timeSpent: '2 ساعت',
    attachments: ['photo2.jpg'],
    history: [
      { date: '1402/11/13', action: 'گزارش شد', user: 'زهرا احمدی', status: 'open' },
    ],
  },
];

const defectCategories = [
  { value: 'appearance', label: 'ظاهری', color: 'info' },
  { value: 'functional', label: 'عملکردی', color: 'error' },
  { value: 'packaging', label: 'بسته‌بندی', color: 'warning' },
  { value: 'safety', label: 'ایمنی', color: 'error' },
  { value: 'performance', label: 'عملکرد', color: 'primary' },
  { value: 'other', label: 'سایر', color: 'default' },
];

const defectStatuses = [
  { value: 'open', label: 'باز', color: 'error' },
  { value: 'assigned', label: 'تخصیص داده شده', color: 'warning' },
  { value: 'investigating', label: 'در حال بررسی', color: 'info' },
  { value: 'resolved', label: 'حل شده', color: 'success' },
  { value: 'closed', label: 'بسته', color: 'default' },
];

const severityLevels = [
  { value: 'low', label: 'کم', color: 'success' },
  { value: 'medium', label: 'متوسط', color: 'warning' },
  { value: 'high', label: 'بالا', color: 'error' },
  { value: 'critical', label: 'بحرانی', color: 'error' },
];

const priorityLevels = [
  { value: 'low', label: 'کم', color: 'success' },
  { value: 'medium', label: 'متوسط', color: 'warning' },
  { value: 'high', label: 'بالا', color: 'error' },
  { value: 'critical', label: 'بحرانی', color: 'error' },
];

export const DefectManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedDefect, setSelectedDefect] = useState<any>(null);
  const [newDefect, setNewDefect] = useState({
    title: '',
    category: '',
    severity: 'medium',
    priority: 'medium',
    description: '',
    product: '',
    batch: '',
  });

  const getCategoryColor = (category: string) => {
    const defectCategory = defectCategories.find(c => c.value === category);
    return defectCategory ? defectCategory.color : 'default';
  };

  const getCategoryText = (category: string) => {
    const defectCategory = defectCategories.find(c => c.value === category);
    return defectCategory ? defectCategory.label : 'نامشخص';
  };

  const getStatusColor = (status: string) => {
    const defectStatus = defectStatuses.find(s => s.value === status);
    return defectStatus ? defectStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const defectStatus = defectStatuses.find(s => s.value === status);
    return defectStatus ? defectStatus.label : 'نامشخص';
  };

  const getSeverityColor = (severity: string) => {
    const severityLevel = severityLevels.find(s => s.value === severity);
    return severityLevel ? severityLevel.color : 'default';
  };

  const getSeverityText = (severity: string) => {
    const severityLevel = severityLevels.find(s => s.value === severity);
    return severityLevel ? severityLevel.label : 'نامشخص';
  };

  const getPriorityColor = (priority: string) => {
    const priorityLevel = priorityLevels.find(p => p.value === priority);
    return priorityLevel ? priorityLevel.color : 'default';
  };

  const getPriorityText = (priority: string) => {
    const priorityLevel = priorityLevels.find(p => p.value === priority);
    return priorityLevel ? priorityLevel.label : 'نامشخص';
  };

  const handleAddDefect = () => {
    setSelectedDefect(null);
    setOpenDialog(true);
  };

  const handleEditDefect = (defect: any) => {
    setSelectedDefect(defect);
    setNewDefect({
      title: defect.title,
      category: defect.category,
      severity: defect.severity,
      priority: defect.priority,
      description: defect.description,
      product: defect.product,
      batch: defect.batch,
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedDefect(null);
    setNewDefect({
      title: '',
      category: '',
      severity: 'medium',
      priority: 'medium',
      description: '',
      product: '',
      batch: '',
    });
  };

  const handleSaveDefect = () => {
    // در اینجا نقص ذخیره می‌شود
    handleCloseDialog();
  };

  const totalDefects = mockDefects.length;
  const openDefects = mockDefects.filter(d => d.status === 'open').length;
  const resolvedDefects = mockDefects.filter(d => d.status === 'resolved').length;
  const criticalDefects = mockDefects.filter(d => d.severity === 'critical').length;

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          مدیریت نقص‌ها
        </Typography.Title>
        <div>
          <Button variant="outlined" startIcon={<FilterList />}>
            فیلتر
          </Button>
          <Button variant="outlined" startIcon={<Refresh />}>
            به‌روزرسانی
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={handleAddDefect}>
            نقص جدید
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {totalDefects}
            </Typography.Title>
            <Typography.Text>
              کل نقص‌ها
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {openDefects}
            </Typography.Title>
            <Typography.Text>
              باز
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {resolvedDefects}
            </Typography.Title>
            <Typography.Text>
              حل شده
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {criticalDefects}
            </Typography.Title>
            <Typography.Text>
              بحرانی
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      {/* Alerts */}
      {criticalDefects > 0 && (
        <Alert severity="error" style={{  mb: 3  }}>
          {criticalDefects} نقص بحرانی وجود دارد که نیاز به بررسی فوری دارد!
        </Alert>
      )}

      {openDefects > 5 && (
        <Alert severity="warning" style={{  mb: 3  }}>
          {openDefects} نقص باز وجود دارد که نیاز به رسیدگی دارد.
        </Alert>
      )}

      {/* Defects List */}
      <Card>
        <div>
          <Typography.Title level={4}>
            لیست نقص‌ها
          </Typography.Title>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>شماره</TableCell>
                  <TableCell>عنوان</TableCell>
                  <TableCell>دسته‌بندی</TableCell>
                  <TableCell>شدت</TableCell>
                  <TableCell>اولویت</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>مسئول</TableCell>
                  <TableCell>تاریخ</TableCell>
                  <TableCell>عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {mockDefects.map((defect) => (
                  <TableRow key={defect.id}>
                    <TableCell>
                      <Typography.Text>
                        {defect.id}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {defect.title}
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {defect.product} - {defect.batch}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getCategoryText(defect.category)}
                        color={getCategoryColor(defect.category) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getSeverityText(defect.severity)}
                        color={getSeverityColor(defect.severity) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getPriorityText(defect.priority)}
                        color={getPriorityColor(defect.priority) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getStatusText(defect.status)}
                        color={getStatusColor(defect.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {defect.assignedTo ? (
                        <Typography.Text>{defect.assignedTo}</Typography.Text>
                      ) : (
                        <Typography.Text>
                          تخصیص داده نشده
                        </Typography.Text>
                      )}
                    </TableCell>
                    <TableCell>{defect.reportedDate}</TableCell>
                    <TableCell>
                      <div>
                        <Button type="text" size="small" color="primary">
                          <Visibility />
                        </Button>
                        <Button type="text" size="small" onClick={() => handleEditDefect(defect)}>
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

      {/* Detailed Defect View */}
      <div style={{  mt: 3  }}>
        <Typography.Title level={4}>
          جزئیات نقص‌ها
        </Typography.Title>
        {mockDefects.map((defect, index) => (
          <Accordion key={index} style={{  mb: 1  }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <div>
                <div>
                  <Typography.Title level={4}>{defect.id}</Typography.Title>
                  <Typography.Text>
                    {defect.title} - {defect.reportedBy}
                  </Typography.Text>
                </div>
                <div>
                  <Tag
                    label={getStatusText(defect.status)}
                    color={getStatusColor(defect.status) as any}
                    size="small"
                  />
                  <Tag
                    label={getSeverityText(defect.severity)}
                    color={getSeverityColor(defect.severity) as any}
                    size="small"
                  />
                  <Tag
                    label={getPriorityText(defect.priority)}
                    color={getPriorityColor(defect.priority) as any}
                    size="small"
                  />
                </div>
              </div>
            </div>
            <AccordionDetails>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  {/* Description */}
                  <Typography variant="subtitle2" gutterBottom>
                    توضیحات:
                  </Typography>
                  <Typography.Text>
                    {defect.description}
                  </Typography.Text>

                  {/* Root Cause and Solution */}
                  {defect.rootCause && (
                    <div style={{  mb: 3  }}>
                      <Typography variant="subtitle2" gutterBottom>
                        علت ریشه:
                      </Typography>
                      <Typography.Text>
                        {defect.rootCause}
                      </Typography.Text>
                    </div>
                  )}

                  {defect.solution && (
                    <div style={{  mb: 3  }}>
                      <Typography variant="subtitle2" gutterBottom>
                        راه‌حل:
                      </Typography>
                      <Typography.Text>
                        {defect.solution}
                      </Typography.Text>
                    </div>
                  )}

                  {/* Impact and Cost */}
                  <Row gutter={[16, 16]}>
                    <Col xs={Math.round(12 / 12 * 24)}>
                      <Typography variant="subtitle2" gutterBottom>
                        تأثیر:
                      </Typography>
                      <Typography.Text>
                        {defect.impact}
                      </Typography.Text>
                    </Col>
                    <Col xs={Math.round(12 / 12 * 24)}>
                      <Typography variant="subtitle2" gutterBottom>
                        هزینه تخمینی:
                      </Typography>
                      <Typography.Text>
                        {defect.cost.toLocaleString()} تومان
                      </Typography.Text>
                    </Col>
                  </Row>

                  {/* Timeline */}
                  <Typography variant="subtitle2" gutterBottom>
                    تاریخچه:
                  </Typography>
                  <Timeline>
                    {defect.history.map((item, historyIndex) => (
                      <TimelineItem key={historyIndex}>
                        <TimelineOppositeContent>
                          <Typography variant="caption" color="textSecondary">
                            {item.date}
                          </Typography>
                        </TimelineOppositeContent>
                        <TimelineSeparator>
                          <TimelineDot color={getStatusColor(item.status) as any} />
                          {historyIndex < defect.history.length - 1 && <TimelineConnector />}
                        </TimelineSeparator>
                        <TimelineContent>
                          <Typography.Text>
                            {item.action}
                          </Typography.Text>
                          <Typography variant="caption" color="textSecondary">
                            {item.user}
                          </Typography>
                        </TimelineContent>
                      </TimelineItem>
                    ))}
                  </Timeline>
                </Col>

                <Col xs={Math.round(12 / 12 * 24)}>
                  <Card style={{  p: 2  }}>
                    <Typography variant="subtitle2" gutterBottom>
                      اطلاعات تکمیلی
                    </Typography>
                    <div>
                      <div>
                        <Typography.Text>گزارش‌دهنده:</Typography.Text>
                        <Typography.Text>{defect.reportedBy}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>مسئول:</Typography.Text>
                        <Typography.Text>
                          {defect.assignedTo || 'تخصیص داده نشده'}
                        </Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>زمان صرف شده:</Typography.Text>
                        <Typography.Text>{defect.timeSpent}</Typography.Text>
                      </div>
                      {defect.resolvedDate && (
                        <div>
                          <Typography.Text>تاریخ حل:</Typography.Text>
                          <Typography.Text>{defect.resolvedDate}</Typography.Text>
                        </div>
                      )}
                    </div>

                    <Divider style={{  my: 2  }} />

                    <Typography variant="subtitle2" gutterBottom>
                      پیوست‌ها:
                    </Typography>
                    <div>
                      {defect.attachments.map((attachment, attachmentIndex) => (
                        <Tag key={attachmentIndex} label={attachment} size="small" variant="outlined" />
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

      {/* Add/Edit Defect Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          {selectedDefect ? 'ویرایش نقص' : 'افزودن نقص جدید'}
        </div>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="عنوان نقص"
                value={newDefect.title}
                onChange={(e) => setNewDefect({ ...newDefect, title: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="محصول"
                value={newDefect.product}
                onChange={(e) => setNewDefect({ ...newDefect, product: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                fullWidth
                label="شماره بچ"
                value={newDefect.batch}
                onChange={(e) => setNewDefect({ ...newDefect, batch: e.target.value })}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <FormControl fullWidth>
                <InputLabel>دسته‌بندی</span>
                <Select
                  value={newDefect.category}
                  label="دسته‌بندی"
                  onChange={(e) => setNewDefect({ ...newDefect, category: e.target.value })}
                >
                  {defectCategories.map((category) => (
                    <MenuItem key={category.value} value={category.value}>
                      {category.label}
                    </Select.Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <FormControl fullWidth>
                <InputLabel>شدت</span>
                <Select
                  value={newDefect.severity}
                  label="شدت"
                  onChange={(e) => setNewDefect({ ...newDefect, severity: e.target.value })}
                >
                  {severityLevels.map((severity) => (
                    <MenuItem key={severity.value} value={severity.value}>
                      {severity.label}
                    </Select.Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <FormControl fullWidth>
                <InputLabel>اولویت</span>
                <Select
                  value={newDefect.priority}
                  label="اولویت"
                  onChange={(e) => setNewDefect({ ...newDefect, priority: e.target.value })}
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
                label="توضیحات"
                multiline
                rows={4}
                value={newDefect.description}
                onChange={(e) => setNewDefect({ ...newDefect, description: e.target.value })}
              />
            </Col>
          </Row>
        </div>
        <div>
          <Button onClick={handleCloseDialog}>انصراف</Button>
          <Button onClick={handleSaveDefect} variant="contained">
            {selectedDefect ? 'ویرایش' : 'ثبت'}
          </Button>
        </div>
      </Modal>
    </div>
  );
}; 