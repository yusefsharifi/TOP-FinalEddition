import React, { useState } from 'react';
import { Alert, Button, Card, Checkbox, Col, Collapse, Divider, Input, InputNumber, List, List.Item, Modal, Progress, Row, Select, Switch, Table, Tag, Typography } from 'antd';
import { CheckCircleOutlined, CloseOutlined, DeleteOutlined, DownOutlined, EditOutlined, EyeInvisibleOutlined, EyeOutlined, GuestAccountOutlined, LockOutlined, PlusOutlined, SafetyOutlined, SettingOutlined, TeamOutlined, UserOutlined, WarningOutlined } from '@ant-design/icons';

// تعریف تمام ماژول‌ها و زیرسیستم‌ها
const allModules = [
  {
    name: 'Dashboard',
    label: 'داشبورد',
    icon: 'Dashboard',
    submodules: [
      { name: 'main_dashboard', label: 'داشبورد اصلی', permissions: ['view', 'edit'] },
      { name: 'analytics_dashboard', label: 'داشبورد تحلیلی', permissions: ['view', 'edit'] },
    ]
  },
  {
    name: 'CRM',
    label: 'مدیریت روابط مشتریان',
    icon: 'People',
    submodules: [
      { name: 'customers', label: 'مشتریان', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'opportunities', label: 'فرصت‌های فروش', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'leads', label: 'لیدها', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'activities', label: 'فعالیت‌های فروش', permissions: ['view', 'create', 'edit'] },
    ]
  },
  {
    name: 'Inventory',
    label: 'انبار و کالا',
    icon: 'Inventory',
    submodules: [
      { name: 'products', label: 'محصولات', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'stock_control', label: 'کنترل موجودی', permissions: ['view', 'edit'] },
      { name: 'suppliers', label: 'تامین‌کنندگان', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'supply_chain', label: 'زنجیره تامین', permissions: ['view', 'edit'] },
      { name: 'demand_forecasting', label: 'پیش‌بینی تقاضا', permissions: ['view', 'edit'] },
      { name: 'inventory_optimization', label: 'بهینه‌سازی موجودی', permissions: ['view', 'edit'] },
    ]
  },
  {
    name: 'Finance',
    label: 'مالی و حسابداری',
    icon: 'AccountBalance',
    submodules: [
      { name: 'accounts', label: 'حساب‌ها', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'budget', label: 'بودجه‌بندی', permissions: ['view', 'create', 'edit'] },
      { name: 'financial_reports', label: 'گزارش‌های مالی', permissions: ['view', 'create'] },
      { name: 'financial_analysis', label: 'تحلیل مالی', permissions: ['view', 'edit'] },
    ]
  },
  {
    name: 'Accounting',
    label: 'حسابداری',
    icon: 'Book',
    submodules: [
      { name: 'general_ledger', label: 'دفتر کل', permissions: ['view', 'create', 'edit'] },
      { name: 'journal', label: 'دفتر روزنامه', permissions: ['view', 'create', 'edit'] },
      { name: 'trial_balance', label: 'تراز آزمایشی', permissions: ['view'] },
      { name: 'accounting_reports', label: 'گزارش‌های حسابداری', permissions: ['view', 'create'] },
    ]
  },
  {
    name: 'HR',
    label: 'منابع انسانی',
    icon: 'Group',
    submodules: [
      { name: 'employees', label: 'کارکنان', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'attendance', label: 'حضور و غیاب', permissions: ['view', 'edit'] },
      { name: 'leave_management', label: 'مدیریت مرخصی', permissions: ['view', 'create', 'edit'] },
      { name: 'payroll', label: 'حقوق و دستمزد', permissions: ['view', 'edit'] },
      { name: 'performance', label: 'ارزیابی عملکرد', permissions: ['view', 'create', 'edit'] },
      { name: 'training', label: 'آموزش', permissions: ['view', 'create', 'edit'] },
      { name: 'recruitment', label: 'استخدام', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'benefits', label: 'مزایا', permissions: ['view', 'create', 'edit'] },
    ]
  },
  {
    name: 'Sales',
    label: 'فروش',
    icon: 'ShoppingCart',
    submodules: [
      { name: 'sales_dashboard', label: 'داشبورد فروش', permissions: ['view', 'edit'] },
      { name: 'order_management', label: 'مدیریت سفارشات', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'product_catalog', label: 'کاتالوگ محصولات', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'sales_analytics', label: 'تحلیل فروش', permissions: ['view', 'edit'] },
      { name: 'customers_table', label: 'جدول مشتریان', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'leads_table', label: 'جدول لیدها', permissions: ['view', 'create', 'edit', 'delete'] },
    ]
  },
  {
    name: 'Purchase',
    label: 'خرید',
    icon: 'ShoppingCart',
    submodules: [
      { name: 'purchase_requests', label: 'درخواست‌های خرید', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'suppliers', label: 'تامین‌کنندگان', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'pricing', label: 'قیمت‌گذاری', permissions: ['view', 'edit'] },
      { name: 'quality_control', label: 'کنترل کیفیت', permissions: ['view', 'edit'] },
    ]
  },
  {
    name: 'Procurement',
    label: 'تأمین و خرید',
    icon: 'LocalShipping',
    submodules: [
      { name: 'procurement_strategy', label: 'استراتژی تامین', permissions: ['view', 'edit'] },
      { name: 'contracts', label: 'مدیریت قراردادها', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'cost_analysis', label: 'تحلیل هزینه‌ها', permissions: ['view', 'edit'] },
      { name: 'procurement_reports', label: 'گزارش‌های تامین', permissions: ['view', 'create'] },
    ]
  },
  {
    name: 'Quality',
    label: 'کیفیت',
    icon: 'Quality',
    submodules: [
      { name: 'quality_dashboard', label: 'داشبورد کیفیت', permissions: ['view', 'edit'] },
      { name: 'inspection_management', label: 'مدیریت بازرسی‌ها', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'defect_management', label: 'مدیریت نقص‌ها', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'quality_standards', label: 'استانداردهای کیفیت', permissions: ['view', 'edit'] },
      { name: 'quality_reports', label: 'گزارش‌های کیفیت', permissions: ['view', 'create'] },
    ]
  },
  {
    name: 'Projects',
    label: 'مدیریت پروژه',
    icon: 'Assignment',
    submodules: [
      { name: 'project_management', label: 'مدیریت پروژه‌ها', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'project_teams', label: 'تیم‌های پروژه', permissions: ['view', 'create', 'edit'] },
      { name: 'scheduling', label: 'زمان‌بندی', permissions: ['view', 'edit'] },
      { name: 'project_budget', label: 'بودجه پروژه', permissions: ['view', 'edit'] },
      { name: 'project_reports', label: 'گزارش‌های پروژه', permissions: ['view', 'create'] },
    ]
  },
  {
    name: 'BI',
    label: 'هوش تجاری',
    icon: 'Analytics',
    submodules: [
      { name: 'analytical_dashboards', label: 'داشبوردهای تحلیلی', permissions: ['view', 'edit'] },
      { name: 'advanced_reports', label: 'گزارش‌های پیشرفته', permissions: ['view', 'create'] },
      { name: 'trend_analysis', label: 'تحلیل روندها', permissions: ['view', 'edit'] },
      { name: 'kpi_management', label: 'مدیریت KPI', permissions: ['view', 'edit'] },
    ]
  },
  {
    name: 'AI',
    label: 'هوش مصنوعی',
    icon: 'Psychology',
    submodules: [
      { name: 'sales_prediction', label: 'پیش‌بینی فروش', permissions: ['view', 'edit'] },
      { name: 'customer_behavior', label: 'تحلیل رفتار مشتریان', permissions: ['view', 'edit'] },
      { name: 'process_optimization', label: 'بهینه‌سازی فرآیندها', permissions: ['view', 'edit'] },
      { name: 'chatbot', label: 'چت‌بات', permissions: ['view', 'edit'] },
    ]
  },
  {
    name: 'Reports',
    label: 'گزارشات',
    icon: 'Assessment',
    submodules: [
      { name: 'standard_reports', label: 'گزارش‌های استاندارد', permissions: ['view', 'create'] },
      { name: 'custom_reports', label: 'گزارش‌های سفارشی', permissions: ['view', 'create', 'edit'] },
      { name: 'report_export', label: 'خروجی گزارش‌ها', permissions: ['view'] },
      { name: 'report_scheduling', label: 'برنامه‌ریزی گزارش‌ها', permissions: ['view', 'edit'] },
    ]
  },
  {
    name: 'Tasks',
    label: 'وظایف',
    icon: 'Assignment',
    submodules: [
      { name: 'task_management', label: 'مدیریت وظایف', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'workflow', label: 'فرآیندهای کاری', permissions: ['view', 'edit'] },
      { name: 'task_calendar', label: 'تقویم وظایف', permissions: ['view', 'edit'] },
      { name: 'performance_reports', label: 'گزارش‌های عملکرد', permissions: ['view', 'create'] },
    ]
  },
  {
    name: 'Correspondence',
    label: 'نامه‌نگاری',
    icon: 'Mail',
    submodules: [
      { name: 'letter_management', label: 'مدیریت نامه‌ها', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'letter_templates', label: 'قالب‌های نامه', permissions: ['view', 'create', 'edit'] },
      { name: 'letter_tracking', label: 'پیگیری نامه‌ها', permissions: ['view', 'edit'] },
      { name: 'correspondence_reports', label: 'گزارش‌های مکاتبات', permissions: ['view', 'create'] },
    ]
  },
  {
    name: 'HSE',
    label: 'سلامت، ایمنی و محیط زیست',
    icon: 'Security',
    submodules: [
      { name: 'safety_management', label: 'مدیریت ایمنی', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'health_control', label: 'کنترل بهداشت', permissions: ['view', 'create', 'edit'] },
      { name: 'environment', label: 'محیط زیست', permissions: ['view', 'create', 'edit'] },
      { name: 'hse_reports', label: 'گزارش‌های HSE', permissions: ['view', 'create'] },
    ]
  },
  {
    name: 'Calendar',
    label: 'تقویم',
    icon: 'CalendarToday',
    submodules: [
      { name: 'organizational_calendar', label: 'تقویم سازمانی', permissions: ['view', 'create', 'edit'] },
      { name: 'planning', label: 'برنامه‌ریزی', permissions: ['view', 'create', 'edit'] },
      { name: 'reminders', label: 'یادآوری', permissions: ['view', 'create', 'edit'] },
      { name: 'synchronization', label: 'همگام‌سازی', permissions: ['view', 'edit'] },
    ]
  },
  {
    name: 'Documents',
    label: 'مستندات',
    icon: 'Description',
    submodules: [
      { name: 'document_management', label: 'مدیریت مستندات', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'version_control', label: 'کنترل نسخه‌ها', permissions: ['view', 'edit'] },
      { name: 'secure_access', label: 'دسترسی امن', permissions: ['view', 'edit'] },
      { name: 'digital_archive', label: 'آرشیو دیجیتال', permissions: ['view', 'create', 'edit'] },
    ]
  },
  {
    name: 'Settings',
    label: 'تنظیمات',
    icon: 'Settings',
    submodules: [
      { name: 'system_settings', label: 'تنظیمات سیستم', permissions: ['view', 'edit'] },
      { name: 'user_management', label: 'مدیریت کاربران', permissions: ['view', 'create', 'edit', 'delete'] },
      { name: 'module_settings', label: 'تنظیمات ماژول‌ها', permissions: ['view', 'edit'] },
      { name: 'backup_recovery', label: 'پشتیبان‌گیری', permissions: ['view', 'edit'] },
    ]
  },
];

// تعریف نقش‌های کاربری
const userRoles = [
  {
    id: 'super_admin',
    name: 'Super Admin',
    label: 'مدیر کل سیستم',
    description: 'دسترسی کامل به تمام ماژول‌ها و تنظیمات',
    permissions: ['all'],
    users: 3,
  },
  {
    id: 'module_admin',
    name: 'Module Admin',
    label: 'مدیر ماژول',
    description: 'دسترسی کامل به ماژول‌های مشخص شده',
    permissions: ['module_specific'],
    users: 25,
  },
  {
    id: 'manager',
    name: 'Manager',
    label: 'مدیر',
    description: 'دسترسی مدیریتی به بخش‌های مشخص شده',
    permissions: ['department'],
    users: 45,
  },
  {
    id: 'user',
    name: 'User',
    label: 'کاربر',
    description: 'دسترسی محدود به بخش‌های مشخص شده',
    permissions: ['limited'],
    users: 200,
  },
  {
    id: 'guest',
    name: 'Guest',
    label: 'مهمان',
    description: 'دسترسی فقط خواندن به بخش‌های مشخص شده',
    permissions: ['read_only'],
    users: 15,
  },
];

// تعریف کاربران نمونه
const mockUsers = [
  {
    id: 1,
    username: 'superadmin',
    fullName: 'مدیر کل سیستم',
    email: 'superadmin@topworx.com',
    role: 'super_admin',
    status: 'active',
    lastLogin: '1402/11/15 15:00',
    modules: allModules.map(m => ({ name: m.name, permissions: ['all'] })),
  },
  {
    id: 2,
    username: 'crm_admin',
    fullName: 'مدیر CRM',
    email: 'crm.admin@topworx.com',
    role: 'module_admin',
    status: 'active',
    lastLogin: '1402/11/15 14:45',
    modules: [
      { name: 'CRM', permissions: ['all'] },
      { name: 'Sales', permissions: ['view', 'create', 'edit'] },
    ],
  },
  {
    id: 3,
    username: 'finance_admin',
    fullName: 'مدیر مالی',
    email: 'finance.admin@topworx.com',
    role: 'module_admin',
    status: 'active',
    lastLogin: '1402/11/15 14:30',
    modules: [
      { name: 'Finance', permissions: ['all'] },
      { name: 'Accounting', permissions: ['all'] },
    ],
  },
  {
    id: 4,
    username: 'hr_admin',
    fullName: 'مدیر منابع انسانی',
    email: 'hr.admin@topworx.com',
    role: 'module_admin',
    status: 'active',
    lastLogin: '1402/11/15 14:15',
    modules: [
      { name: 'HR', permissions: ['all'] },
    ],
  },
  {
    id: 5,
    username: 'inventory_admin',
    fullName: 'مدیر انبار',
    email: 'inventory.admin@topworx.com',
    role: 'module_admin',
    status: 'active',
    lastLogin: '1402/11/15 14:00',
    modules: [
      { name: 'Inventory', permissions: ['all'] },
      { name: 'Purchase', permissions: ['view', 'create', 'edit'] },
    ],
  },
];

export const AccessManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [selectedModule, setSelectedModule] = useState<string>('');
  const [tabValue, setTabValue] = useState(0);

  const handleEditUser = (user: any) => {
    setSelectedUser(user);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedUser(null);
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin': return 'error';
      case 'module_admin': return 'warning';
      case 'manager': return 'primary';
      case 'user': return 'success';
      case 'guest': return 'info';
      default: return 'default';
    }
  };

  const getRoleText = (role: string) => {
    const roleObj = userRoles.find(r => r.id === role);
    return roleObj ? roleObj.label : 'نامشخص';
  };

  const getStatusColor = (status: string) => {
    return status === 'active' ? 'success' : 'error';
  };

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          مدیریت دسترسی‌ها
        </Typography.Title>
        <div>
          <Button variant="outlined" startIcon={<Security />}>
            تنظیمات امنیتی
          </Button>
          <Button variant="contained" startIcon={<Add />}>
            کاربر جدید
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {mockUsers.length}
            </Typography.Title>
            <Typography.Text>
              کل کاربران
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {mockUsers.filter(u => u.status === 'active').length}
            </Typography.Title>
            <Typography.Text>
              کاربران فعال
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {allModules.length}
            </Typography.Title>
            <Typography.Text>
              ماژول‌های سیستم
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 2, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              {userRoles.length}
            </Typography.Title>
            <Typography.Text>
              نقش‌های کاربری
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      {/* Main Content */}
      <Card>
        <div>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="کاربران و دسترسی‌ها" />
            <Tab label="نقش‌های کاربری" />
            <Tab label="ماژول‌ها و مجوزها" />
          </Tabs>

          <div style={{  mt: 2  }}>
            {tabValue === 0 && (
              <div>
                <Typography.Title level={4}>
                  مدیریت کاربران
                </Typography.Title>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>کاربر</TableCell>
                        <TableCell>نقش</TableCell>
                        <TableCell>وضعیت</TableCell>
                        <TableCell>ماژول‌های دسترسی</TableCell>
                        <TableCell>آخرین ورود</TableCell>
                        <TableCell>عملیات</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {mockUsers.map((user) => (
                        <TableRow key={user.id}>
                          <TableCell>
                            <div>
                              <Typography.Text>
                                {user.fullName}
                              </Typography.Text>
                              <Typography variant="caption" color="textSecondary">
                                {user.email}
                              </Typography>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Tag
                              label={getRoleText(user.role)}
                              color={getRoleColor(user.role) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Tag
                              label={user.status === 'active' ? 'فعال' : 'غیرفعال'}
                              color={getStatusColor(user.status) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <div>
                              {user.modules.slice(0, 3).map((module, index) => (
                                <Tag
                                  key={index}
                                  label={module.name}
                                  size="small"
                                  variant="outlined"
                                />
                              ))}
                              {user.modules.length > 3 && (
                                <Tag
                                  label={`+${user.modules.length - 3}`}
                                  size="small"
                                  color="primary"
                                />
                              )}
                            </div>
                          </TableCell>
                          <TableCell>{user.lastLogin}</TableCell>
                          <TableCell>
                            <div>
                              <Button type="text" size="small" onClick={() => handleEditUser(user)}>
                                <Edit />
                              </Button>
                              <Button type="text" size="small" color="secondary">
                                <Visibility />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}

            {tabValue === 1 && (
              <div>
                <Typography.Title level={4}>
                  نقش‌های کاربری
                </Typography.Title>
                <Row gutter={[16, 16]}>
                  {userRoles.map((role) => (
                    <Col xs={Math.round(12 / 12 * 24)}>
                      <Card style={{  p: 2  }}>
                        <div>
                          <Typography.Title level={4}>
                            {role.label}
                          </Typography.Title>
                          <Tag label={`${role.users} کاربر`} size="small" color="primary" />
                        </div>
                        <Typography.Text>
                          {role.description}
                        </Typography.Text>
                        <div>
                          <Button variant="outlined" size="small">
                            ویرایش نقش
                          </Button>
                          <Button variant="outlined" size="small">
                            مدیریت مجوزها
                          </Button>
                        </div>
                      </Card>
                    </Col>
                  ))}
                </Row>
              </div>
            )}

            {tabValue === 2 && (
              <div>
                <Typography.Title level={4}>
                  ماژول‌ها و مجوزها
                </Typography.Title>
                {allModules.map((module) => (
                  <Accordion key={module.name} style={{  mb: 1  }}>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <div>
                        <Typography.Title level={4}>{module.label}</Typography.Title>
                        <Tag label={`${module.submodules.length} زیرماژول`} size="small" />
                      </div>
                    </div>
                    <AccordionDetails>
                      <Row gutter={[16, 16]}>
                        {module.submodules.map((submodule) => (
                          <Col xs={Math.round(12 / 12 * 24)}>
                            <Card style={{  p: 2  }}>
                              <Typography variant="subtitle2" gutterBottom>
                                {submodule.label}
                              </Typography>
                              <div>
                                {submodule.permissions.map((permission) => (
                                  <Tag
                                    key={permission}
                                    label={permission === 'view' ? 'مشاهده' : 
                                           permission === 'create' ? 'ایجاد' :
                                           permission === 'edit' ? 'ویرایش' :
                                           permission === 'delete' ? 'حذف' : permission}
                                    size="small"
                                    color={permission === 'view' ? 'success' :
                                           permission === 'create' ? 'primary' :
                                           permission === 'edit' ? 'warning' :
                                           permission === 'delete' ? 'error' : 'default'}
                                  />
                                ))}
                              </div>
                            </Card>
                          </Col>
                        ))}
                      </Row>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Edit User Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          ویرایش دسترسی‌های کاربر: {selectedUser?.fullName}
        </div>
        <div>
          {selectedUser && (
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام کامل"
                  value={selectedUser.fullName}
                  disabled
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="ایمیل"
                  value={selectedUser.email}
                  disabled
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>نقش کاربری</span>
                  <Select
                    value={selectedUser.role}
                    label="نقش کاربری"
                  >
                    {userRoles.map((role) => (
                      <MenuItem key={role.id} value={role.id}>
                        {role.label}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>وضعیت</span>
                  <Select
                    value={selectedUser.status}
                    label="وضعیت"
                  >
                    <MenuItem value="active">فعال</Select.Option>
                    <MenuItem value="inactive">غیرفعال</Select.Option>
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Typography variant="subtitle2" gutterBottom>
                  دسترسی به ماژول‌ها:
                </Typography>
                <div style={{  maxHeight: 300, overflow: 'auto'  }}>
                  {allModules.map((module) => (
                    <FormControlLabel
                      key={module.name}
                      control={
                        <Checkbox
                          checked={selectedUser.modules.some((m: any) => m.name === module.name)}
                        />
                      }
                      label={module.label}
                    />
                  ))}
                </div>
              </Col>
            </Row>
          )}
        </div>
        <div>
          <Button onClick={handleCloseDialog}>انصراف</Button>
          <Button variant="contained">
            ذخیره تغییرات
          </Button>
        </div>
      </Modal>
    </div>
  );
}; 