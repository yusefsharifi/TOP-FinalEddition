import React, { useState } from 'react';
import { Alert, Button, Card, Checkbox, Col, Collapse, Divider, Input, InputNumber, List, List.Item, Modal, Progress, Row, Select, Switch, Table, Tag, Typography } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, CloseOutlined, DeleteOutlined, DownOutlined, DownloadOutlined, EditOutlined, EnvironmentOutlined, EyeInvisibleOutlined, EyeOutlined, FieldTimeOutlined, FilterOutlined, GuestAccountOutlined, HistoryOutlined, InfoCircleOutlined, KeyOutlined, LockOutlined, MailOutlined, PhoneOutlined, PlusOutlined, PrinterOutlined, ReadOutlined, ReloadOutlined, SafetyOutlined, SearchOutlined, SettingOutlined, TeamOutlined, ToolOutlined, UserOutlined, WarningOutlined } from '@ant-design/icons';

// تعریف انواع فعالیت‌ها
const activityTypes = [
  { value: 'login', label: 'ورود به سیستم', color: 'success' },
  { value: 'logout', label: 'خروج از سیستم', color: 'info' },
  { value: 'create', label: 'ایجاد', color: 'primary' },
  { value: 'update', label: 'ویرایش', color: 'warning' },
  { value: 'delete', label: 'حذف', color: 'error' },
  { value: 'view', label: 'مشاهده', color: 'default' },
  { value: 'export', label: 'خروجی', color: 'secondary' },
  { value: 'import', label: 'ورودی', color: 'secondary' },
  { value: 'download', label: 'دانلود', color: 'info' },
  { value: 'upload', label: 'آپلود', color: 'info' },
  { value: 'approve', label: 'تأیید', color: 'success' },
  { value: 'reject', label: 'رد', color: 'error' },
  { value: 'security_violation', label: 'نقض امنیتی', color: 'error' },
  { value: 'permission_change', label: 'تغییر دسترسی', color: 'warning' },
  { value: 'system_change', label: 'تغییر سیستم', color: 'warning' },
];

// تعریف ماژول‌ها
const modules = [
  'Dashboard',
  'CRM',
  'Inventory',
  'Finance',
  'Accounting',
  'HR',
  'Sales',
  'Purchase',
  'Procurement',
  'Quality',
  'Projects',
  'BI',
  'AI',
  'Reports',
  'Tasks',
  'Correspondence',
  'HSE',
  'Calendar',
  'Documents',
  'Settings',
  'Security',
];

// داده‌های نمونه Audit Trail
const mockAuditData = [
  {
    id: 1,
    timestamp: '1402/11/15 15:30:25',
    user: 'superadmin',
    fullName: 'مدیر کل سیستم',
    ip: '192.168.1.100',
    activity: 'login',
    module: 'Security',
    description: 'ورود موفق به سیستم',
    details: {
      browser: 'Chrome 120.0.0.0',
      os: 'Windows 11',
      location: 'تهران، ایران',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    },
    severity: 'low',
    status: 'success',
  },
  {
    id: 2,
    timestamp: '1402/11/15 15:25:10',
    user: 'crm_admin',
    fullName: 'مدیر CRM',
    ip: '10.0.0.50',
    activity: 'create',
    module: 'CRM',
    description: 'ایجاد مشتری جدید: شرکت فناوری پیشرو',
    details: {
      recordId: 'CUST-2024-001',
      changes: {
        name: 'شرکت فناوری پیشرو',
        email: 'info@techpro.com',
        phone: '021-12345678',
      },
    },
    severity: 'medium',
    status: 'success',
  },
  {
    id: 3,
    timestamp: '1402/11/15 15:20:45',
    user: 'finance_admin',
    fullName: 'مدیر مالی',
    ip: '172.16.0.25',
    activity: 'update',
    module: 'Finance',
    description: 'ویرایش حساب بانکی: بانک ملی',
    details: {
      recordId: 'ACC-2024-005',
      changes: {
        balance: '50000000 تومان',
        lastTransaction: '1402/11/15 15:20:00',
      },
    },
    severity: 'high',
    status: 'success',
  },
  {
    id: 4,
    timestamp: '1402/11/15 15:15:30',
    user: 'hr_admin',
    fullName: 'مدیر منابع انسانی',
    ip: '192.168.1.150',
    activity: 'delete',
    module: 'HR',
    description: 'حذف کارمند: احمد محمدی',
    details: {
      recordId: 'EMP-2023-045',
      reason: 'استعفا',
      approvalBy: 'superadmin',
    },
    severity: 'high',
    status: 'success',
  },
  {
    id: 5,
    timestamp: '1402/11/15 15:10:15',
    user: 'inventory_admin',
    fullName: 'مدیر انبار',
    ip: '10.0.0.75',
    activity: 'export',
    module: 'Inventory',
    description: 'خروجی گزارش موجودی انبار',
    details: {
      format: 'Excel',
      records: 1250,
      fileSize: '2.5 MB',
      destination: 'Downloads/inventory_report_2024.xlsx',
    },
    severity: 'medium',
    status: 'success',
  },
  {
    id: 6,
    timestamp: '1402/11/15 15:05:00',
    user: 'unknown',
    fullName: 'کاربر نامشخص',
    ip: '203.45.67.89',
    activity: 'security_violation',
    module: 'Security',
    description: 'تلاش ناموفق ورود با رمز عبور اشتباه',
    details: {
      attempts: 5,
      blocked: true,
      reason: 'Multiple failed login attempts',
    },
    severity: 'critical',
    status: 'blocked',
  },
  {
    id: 7,
    timestamp: '1402/11/15 15:00:30',
    user: 'superadmin',
    fullName: 'مدیر کل سیستم',
    ip: '192.168.1.100',
    activity: 'permission_change',
    module: 'Security',
    description: 'تغییر دسترسی کاربر: crm_admin',
    details: {
      userId: 'crm_admin',
      oldPermissions: ['CRM:view', 'CRM:create'],
      newPermissions: ['CRM:view', 'CRM:create', 'CRM:edit', 'CRM:delete'],
      reason: 'ارتقاء نقش کاربر',
    },
    severity: 'high',
    status: 'success',
  },
  {
    id: 8,
    timestamp: '1402/11/15 14:55:20',
    user: 'sales_manager',
    fullName: 'مدیر فروش',
    ip: '192.168.1.200',
    activity: 'view',
    module: 'Sales',
    description: 'مشاهده گزارش فروش ماهانه',
    details: {
      reportType: 'Monthly Sales Report',
      period: '1402/10',
      filters: {
        region: 'تهران',
        productCategory: 'الکترونیک',
      },
    },
    severity: 'low',
    status: 'success',
  },
  {
    id: 9,
    timestamp: '1402/11/15 14:50:10',
    user: 'quality_admin',
    fullName: 'مدیر کیفیت',
    ip: '10.0.0.100',
    activity: 'approve',
    module: 'Quality',
    description: 'تأیید بازرسی کیفیت محصول: PRD-2024-023',
    details: {
      recordId: 'PRD-2024-023',
      inspector: 'علی رضایی',
      result: 'Passed',
      notes: 'تمام معیارهای کیفیت برآورده شده',
    },
    severity: 'medium',
    status: 'success',
  },
  {
    id: 10,
    timestamp: '1402/11/15 14:45:00',
    user: 'project_manager',
    fullName: 'مدیر پروژه',
    ip: '172.16.0.50',
    activity: 'system_change',
    module: 'Projects',
    description: 'تغییر وضعیت پروژه: توسعه نرم‌افزار ERP',
    details: {
      projectId: 'PRJ-2024-001',
      oldStatus: 'In Progress',
      newStatus: 'Testing',
      milestone: 'Phase 2 Complete',
    },
    severity: 'medium',
    status: 'success',
  },
];

export const AuditTrail: React.FC = () => {
  const [selectedActivity, setSelectedActivity] = useState<string>('');
  const [selectedModule, setSelectedModule] = useState<string>('');
  const [selectedUser, setSelectedUser] = useState<string>('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [openDetails, setOpenDetails] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<any>(null);

  const handleViewDetails = (record: any) => {
    setSelectedRecord(record);
    setOpenDetails(true);
  };

  const handleCloseDetails = () => {
    setOpenDetails(false);
    setSelectedRecord(null);
  };

  const getActivityColor = (activity: string) => {
    const activityType = activityTypes.find(t => t.value === activity);
    return activityType ? activityType.color : 'default';
  };

  const getActivityText = (activity: string) => {
    const activityType = activityTypes.find(t => t.value === activity);
    return activityType ? activityType.label : 'نامشخص';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'success';
      case 'blocked': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const filteredData = mockAuditData.filter(record => {
    if (selectedActivity && record.activity !== selectedActivity) return false;
    if (selectedModule && record.module !== selectedModule) return false;
    if (selectedUser && record.user !== selectedUser) return false;
    if (selectedSeverity && record.severity !== selectedSeverity) return false;
    return true;
  });

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          Audit Trail - ثبت فعالیت‌ها
        </Typography.Title>
        <div>
          <Button variant="outlined" startIcon={<Download />}>
            خروجی
          </Button>
          <Button variant="outlined" startIcon={<Print />}>
            چاپ
          </Button>
          <Button variant="contained" startIcon={<Refresh />}>
            بروزرسانی
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card style={{  mb: 3  }}>
        <div>
          <Typography.Title level={4}>
            فیلترها
          </Typography.Title>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <FormControl fullWidth size="small">
                <InputLabel>نوع فعالیت</span>
                <Select
                  value={selectedActivity}
                  label="نوع فعالیت"
                  onChange={(e) => setSelectedActivity(e.target.value)}
                >
                  <MenuItem value="">همه</Select.Option>
                  {activityTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </Select.Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <FormControl fullWidth size="small">
                <InputLabel>ماژول</span>
                <Select
                  value={selectedModule}
                  label="ماژول"
                  onChange={(e) => setSelectedModule(e.target.value)}
                >
                  <MenuItem value="">همه</Select.Option>
                  {modules.map((module) => (
                    <MenuItem key={module} value={module}>
                      {module}
                    </Select.Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <FormControl fullWidth size="small">
                <InputLabel>کاربر</span>
                <Select
                  value={selectedUser}
                  label="کاربر"
                  onChange={(e) => setSelectedUser(e.target.value)}
                >
                  <MenuItem value="">همه</Select.Option>
                  {Array.from(new Set(mockAuditData.map(r => r.user))).map((user) => (
                    <MenuItem key={user} value={user}>
                      {user}
                    </Select.Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <FormControl fullWidth size="small">
                <InputLabel>سطح اهمیت</span>
                <Select
                  value={selectedSeverity}
                  label="سطح اهمیت"
                  onChange={(e) => setSelectedSeverity(e.target.value)}
                >
                  <MenuItem value="">همه</Select.Option>
                  <MenuItem value="critical">بحرانی</Select.Option>
                  <MenuItem value="high">بالا</Select.Option>
                  <MenuItem value="medium">متوسط</Select.Option>
                  <MenuItem value="low">کم</Select.Option>
                </Select>
              </div>
            </Col>
          </Row>
        </div>
      </Card>

      {/* Statistics */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {mockAuditData.length}
            </Typography.Title>
            <Typography.Text>
              کل فعالیت‌ها
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {mockAuditData.filter(r => r.severity === 'critical').length}
            </Typography.Title>
            <Typography.Text>
              فعالیت‌های بحرانی
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {mockAuditData.filter(r => r.activity === 'security_violation').length}
            </Typography.Title>
            <Typography.Text>
              نقض‌های امنیتی
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {Array.from(new Set(mockAuditData.map(r => r.user))).length}
            </Typography.Title>
            <Typography.Text>
              کاربران فعال
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      {/* Audit Trail Table */}
      <Card>
        <div>
          <Typography.Title level={4}>
            ثبت فعالیت‌ها
          </Typography.Title>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>زمان</TableCell>
                  <TableCell>کاربر</TableCell>
                  <TableCell>فعالیت</TableCell>
                  <TableCell>ماژول</TableCell>
                  <TableCell>توضیحات</TableCell>
                  <TableCell>سطح اهمیت</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredData.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell>
                      <Typography.Text>
                        {record.timestamp}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <div>
                        <Typography.Text>
                          {record.fullName}
                        </Typography.Text>
                        <Typography variant="caption" color="textSecondary">
                          {record.user} - {record.ip}
                        </Typography>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getActivityText(record.activity)}
                        color={getActivityColor(record.activity) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography.Text>{record.module}</Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {record.description}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={record.severity === 'critical' ? 'بحرانی' :
                               record.severity === 'high' ? 'بالا' :
                               record.severity === 'medium' ? 'متوسط' : 'کم'}
                        color={getSeverityColor(record.severity) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={record.status === 'success' ? 'موفق' :
                               record.status === 'blocked' ? 'مسدود' : 'در انتظار'}
                        color={getStatusColor(record.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Button type="text" size="small" onClick={() => handleViewDetails(record)}>
                        <Visibility />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </Card>

      {/* Details Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          جزئیات فعالیت
        </div>
        <div>
          {selectedRecord && (
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Typography variant="subtitle2" gutterBottom>
                  اطلاعات پایه
                </Typography>
                <Typography.Text>
                  <strong>زمان:</strong> {selectedRecord.timestamp}
                </Typography.Text>
                <Typography.Text>
                  <strong>کاربر:</strong> {selectedRecord.fullName} ({selectedRecord.user})
                </Typography.Text>
                <Typography.Text>
                  <strong>IP:</strong> {selectedRecord.ip}
                </Typography.Text>
                <Typography.Text>
                  <strong>فعالیت:</strong> {getActivityText(selectedRecord.activity)}
                </Typography.Text>
                <Typography.Text>
                  <strong>ماژول:</strong> {selectedRecord.module}
                </Typography.Text>
                <Typography.Text>
                  <strong>سطح اهمیت:</strong> {selectedRecord.severity}
                </Typography.Text>
                <Typography.Text>
                  <strong>وضعیت:</strong> {selectedRecord.status}
                </Typography.Text>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Typography variant="subtitle2" gutterBottom>
                  جزئیات فنی
                </Typography>
                {selectedRecord.details && Object.entries(selectedRecord.details).map(([key, value]) => (
                  <Typography key={key} variant="body2">
                    <strong>{key}:</strong> {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </Typography>
                ))}
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Typography variant="subtitle2" gutterBottom>
                  توضیحات
                </Typography>
                <Typography.Text>
                  {selectedRecord.description}
                </Typography.Text>
              </Col>
            </Row>
          )}
        </div>
        <div>
          <Button onClick={handleCloseDetails}>بستن</Button>
        </div>
      </Modal>
    </div>
  );
}; 