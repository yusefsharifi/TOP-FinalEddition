import React, { useState } from 'react';
import { Alert, Button, Card, Checkbox, Col, Collapse, Divider, Input, InputNumber, List, List.Item, Modal, Progress, Row, Select, Switch, Table, Tag, Typography } from 'antd';
import { CheckCircleOutlined, CloseOutlined, DeleteOutlined, DownOutlined, EditOutlined, EnvironmentOutlined, EyeInvisibleOutlined, EyeOutlined, GuestAccountOutlined, KeyOutlined, LockOutlined, MailOutlined, PhoneOutlined, PlusOutlined, ReadOutlined, SafetyOutlined, SettingOutlined, TeamOutlined, ToolOutlined, UserOutlined, WarningOutlined } from '@ant-design/icons';

// تعریف تمام ماژول‌ها برای دسترسی ادمین
const allSystemModules = [
  { name: 'Dashboard', label: 'داشبورد', icon: 'Dashboard' },
  { name: 'CRM', label: 'مدیریت روابط مشتریان', icon: 'People' },
  { name: 'Inventory', label: 'انبار و کالا', icon: 'Inventory' },
  { name: 'Finance', label: 'مالی و حسابداری', icon: 'AccountBalance' },
  { name: 'Accounting', label: 'حسابداری', icon: 'Book' },
  { name: 'HR', label: 'منابع انسانی', icon: 'Group' },
  { name: 'Sales', label: 'فروش', icon: 'ShoppingCart' },
  { name: 'Purchase', label: 'خرید', icon: 'ShoppingCart' },
  { name: 'Procurement', label: 'تأمین و خرید', icon: 'LocalShipping' },
  { name: 'Quality', label: 'کیفیت', icon: 'Quality' },
  { name: 'Projects', label: 'مدیریت پروژه', icon: 'Assignment' },
  { name: 'BI', label: 'هوش تجاری', icon: 'Analytics' },
  { name: 'AI', label: 'هوش مصنوعی', icon: 'Psychology' },
  { name: 'Reports', label: 'گزارشات', icon: 'Assessment' },
  { name: 'Tasks', label: 'وظایف', icon: 'Assignment' },
  { name: 'Correspondence', label: 'نامه‌نگاری', icon: 'Mail' },
  { name: 'HSE', label: 'سلامت، ایمنی و محیط زیست', icon: 'Security' },
  { name: 'Calendar', label: 'تقویم', icon: 'CalendarToday' },
  { name: 'Documents', label: 'مستندات', icon: 'Description' },
  { name: 'Settings', label: 'تنظیمات', icon: 'Settings' },
];

// تعریف نقش‌های کاربری
const userRoles = [
  {
    id: 'super_admin',
    name: 'Super Admin',
    label: 'مدیر کل سیستم',
    description: 'دسترسی کامل به تمام ماژول‌ها و تنظیمات سیستم',
    permissions: ['all'],
    color: 'error',
  },
  {
    id: 'module_admin',
    name: 'Module Admin',
    label: 'مدیر ماژول',
    description: 'دسترسی کامل به ماژول‌های مشخص شده',
    permissions: ['module_specific'],
    color: 'warning',
  },
  {
    id: 'manager',
    name: 'Manager',
    label: 'مدیر',
    description: 'دسترسی مدیریتی به بخش‌های مشخص شده',
    permissions: ['department'],
    color: 'primary',
  },
  {
    id: 'user',
    name: 'User',
    label: 'کاربر',
    description: 'دسترسی محدود به بخش‌های مشخص شده',
    permissions: ['limited'],
    color: 'success',
  },
  {
    id: 'guest',
    name: 'Guest',
    label: 'مهمان',
    description: 'دسترسی فقط خواندن به بخش‌های مشخص شده',
    permissions: ['read_only'],
    color: 'info',
  },
];

// کاربران نمونه
const mockUsers = [
  {
    id: 1,
    username: 'superadmin',
    fullName: 'مدیر کل سیستم',
    email: 'superadmin@topworx.com',
    phone: '09123456789',
    department: 'IT',
    role: 'super_admin',
    status: 'active',
    lastLogin: '1402/11/15 15:00',
    createdDate: '1402/01/01',
    modules: allSystemModules.map(m => ({ name: m.name, permissions: ['all'] })),
    profile: {
      avatar: '/avatars/admin.jpg',
      bio: 'مدیر کل سیستم با دسترسی کامل به تمام ماژول‌ها',
      skills: ['System Administration', 'Security', 'Database Management'],
      education: 'کارشناسی ارشد مهندسی نرم‌افزار',
      experience: '10 سال',
    },
  },
  {
    id: 2,
    username: 'crm_admin',
    fullName: 'مدیر CRM',
    email: 'crm.admin@topworx.com',
    phone: '09187654321',
    department: 'Sales',
    role: 'module_admin',
    status: 'active',
    lastLogin: '1402/11/15 14:45',
    createdDate: '1402/03/15',
    modules: [
      { name: 'CRM', permissions: ['all'] },
      { name: 'Sales', permissions: ['view', 'create', 'edit'] },
      { name: 'Reports', permissions: ['view', 'create'] },
    ],
    profile: {
      avatar: '/avatars/crm-admin.jpg',
      bio: 'مدیر بخش CRM و فروش',
      skills: ['CRM Management', 'Sales', 'Customer Relations'],
      education: 'کارشناسی مدیریت بازرگانی',
      experience: '5 سال',
    },
  },
  {
    id: 3,
    username: 'finance_admin',
    fullName: 'مدیر مالی',
    email: 'finance.admin@topworx.com',
    phone: '09111111111',
    department: 'Finance',
    role: 'module_admin',
    status: 'active',
    lastLogin: '1402/11/15 14:30',
    createdDate: '1402/02/20',
    modules: [
      { name: 'Finance', permissions: ['all'] },
      { name: 'Accounting', permissions: ['all'] },
      { name: 'Reports', permissions: ['view', 'create'] },
    ],
    profile: {
      avatar: '/avatars/finance-admin.jpg',
      bio: 'مدیر بخش مالی و حسابداری',
      skills: ['Financial Management', 'Accounting', 'Budgeting'],
      education: 'کارشناسی ارشد حسابداری',
      experience: '8 سال',
    },
  },
  {
    id: 4,
    username: 'hr_admin',
    fullName: 'مدیر منابع انسانی',
    email: 'hr.admin@topworx.com',
    phone: '09122222222',
    department: 'HR',
    role: 'module_admin',
    status: 'active',
    lastLogin: '1402/11/15 14:15',
    createdDate: '1402/04/10',
    modules: [
      { name: 'HR', permissions: ['all'] },
      { name: 'Reports', permissions: ['view', 'create'] },
    ],
    profile: {
      avatar: '/avatars/hr-admin.jpg',
      bio: 'مدیر بخش منابع انسانی',
      skills: ['HR Management', 'Recruitment', 'Performance Management'],
      education: 'کارشناسی مدیریت منابع انسانی',
      experience: '6 سال',
    },
  },
  {
    id: 5,
    username: 'inventory_admin',
    fullName: 'مدیر انبار',
    email: 'inventory.admin@topworx.com',
    phone: '09133333333',
    department: 'Operations',
    role: 'module_admin',
    status: 'active',
    lastLogin: '1402/11/15 14:00',
    createdDate: '1402/05/05',
    modules: [
      { name: 'Inventory', permissions: ['all'] },
      { name: 'Purchase', permissions: ['view', 'create', 'edit'] },
      { name: 'Procurement', permissions: ['view', 'edit'] },
    ],
    profile: {
      avatar: '/avatars/inventory-admin.jpg',
      bio: 'مدیر بخش انبار و تدارکات',
      skills: ['Inventory Management', 'Supply Chain', 'Logistics'],
      education: 'کارشناسی مهندسی صنایع',
      experience: '7 سال',
    },
  },
];

export const UserManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [newUser, setNewUser] = useState({
    username: '',
    fullName: '',
    email: '',
    phone: '',
    department: '',
    role: 'user',
    status: 'active',
    password: '',
    confirmPassword: '',
    selectedModules: [],
  });

  const steps = [
    'اطلاعات پایه',
    'نقش و دسترسی‌ها',
    'تنظیمات امنیتی',
    'تأیید نهایی',
  ];

  const handleCreateAdmin = () => {
    setSelectedUser(null);
    setNewUser({
      username: '',
      fullName: '',
      email: '',
      phone: '',
      department: '',
      role: 'super_admin',
      status: 'active',
      password: '',
      confirmPassword: '',
      selectedModules: allSystemModules.map(m => m.name),
    });
    setOpenDialog(true);
  };

  const handleEditUser = (user: any) => {
    setSelectedUser(user);
    setNewUser({
      username: user.username,
      fullName: user.fullName,
      email: user.email,
      phone: user.phone,
      department: user.department,
      role: user.role,
      status: user.status,
      password: '',
      confirmPassword: '',
      selectedModules: user.modules.map((m: any) => m.name),
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedUser(null);
    setActiveStep(0);
    setNewUser({
      username: '',
      fullName: '',
      email: '',
      phone: '',
      department: '',
      role: 'user',
      status: 'active',
      password: '',
      confirmPassword: '',
      selectedModules: [],
    });
  };

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSaveUser = () => {
    // در اینجا کاربر ذخیره می‌شود
    handleCloseDialog();
  };

  const getRoleColor = (role: string) => {
    const roleObj = userRoles.find(r => r.id === role);
    return roleObj ? roleObj.color : 'default';
  };

  const getRoleText = (role: string) => {
    const roleObj = userRoles.find(r => r.id === role);
    return roleObj ? roleObj.label : 'نامشخص';
  };

  const getStatusColor = (status: string) => {
    return status === 'active' ? 'success' : 'error';
  };

  const departments = [
    'IT',
    'Sales',
    'Finance',
    'HR',
    'Operations',
    'Marketing',
    'Customer Service',
    'Research & Development',
  ];

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          مدیریت کاربران
        </Typography.Title>
        <div>
          <Button variant="outlined" startIcon={<Security />}>
            تنظیمات امنیتی
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreateAdmin}>
            ایجاد کاربر ادمین
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
              {mockUsers.filter(u => u.role === 'super_admin' || u.role === 'module_admin').length}
            </Typography.Title>
            <Typography.Text>
              کاربران ادمین
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

      {/* Users Table */}
      <Card>
        <div>
          <Typography.Title level={4}>
            لیست کاربران
          </Typography.Title>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>کاربر</TableCell>
                  <TableCell>نقش</TableCell>
                  <TableCell>بخش</TableCell>
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
                        <AccountCircle />
                        <div>
                          <Typography.Text>
                            {user.fullName}
                          </Typography.Text>
                          <Typography variant="caption" color="textSecondary">
                            {user.email}
                          </Typography>
                        </div>
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
                      <Typography.Text>{user.department}</Typography.Text>
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
      </Card>

      {/* User Roles Overview */}
      <div style={{  mt: 3  }}>
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
                  <Tag
                    label={`${mockUsers.filter(u => u.role === role.id).length} کاربر`}
                    size="small"
                    color={role.color as any}
                  />
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

      {/* Create/Edit User Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          {selectedUser ? 'ویرایش کاربر' : 'ایجاد کاربر ادمین جدید'}
        </div>
        <div>
          <Stepper activeStep={activeStep} style={{  mb: 3  }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {activeStep === 0 && (
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام کاربری"
                  value={newUser.username}
                  onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام کامل"
                  value={newUser.fullName}
                  onChange={(e) => setNewUser({ ...newUser, fullName: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="ایمیل"
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="شماره تماس"
                  value={newUser.phone}
                  onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>بخش</span>
                  <Select
                    value={newUser.department}
                    label="بخش"
                    onChange={(e) => setNewUser({ ...newUser, department: e.target.value })}
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
                <FormControl fullWidth>
                  <InputLabel>وضعیت</span>
                  <Select
                    value={newUser.status}
                    label="وضعیت"
                    onChange={(e) => setNewUser({ ...newUser, status: e.target.value })}
                  >
                    <MenuItem value="active">فعال</Select.Option>
                    <MenuItem value="inactive">غیرفعال</Select.Option>
                  </Select>
                </div>
              </Col>
            </Row>
          )}

          {activeStep === 1 && (
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>نقش کاربری</span>
                  <Select
                    value={newUser.role}
                    label="نقش کاربری"
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
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
                <Typography variant="subtitle2" gutterBottom>
                  دسترسی به ماژول‌ها:
                </Typography>
                <div style={{  maxHeight: 300, overflow: 'auto'  }}>
                  {allSystemModules.map((module) => (
                    <FormControlLabel
                      key={module.name}
                      control={
                        <Checkbox
                          checked={newUser.selectedModules.includes(module.name)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setNewUser({
                                ...newUser,
                                selectedModules: [...newUser.selectedModules, module.name]
                              });
                            } else {
                              setNewUser({
                                ...newUser,
                                selectedModules: newUser.selectedModules.filter(m => m !== module.name)
                              });
                            }
                          }}
                        />
                      }
                      label={module.label}
                    />
                  ))}
                </div>
              </Col>
            </Row>
          )}

          {activeStep === 2 && (
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="رمز عبور"
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تأیید رمز عبور"
                  type="password"
                  value={newUser.confirmPassword}
                  onChange={(e) => setNewUser({ ...newUser, confirmPassword: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="فعال‌سازی احراز هویت دو مرحله‌ای"
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="ارسال ایمیل تأیید"
                />
              </Col>
            </Row>
          )}

          {activeStep === 3 && (
            <div>
              <Typography.Title level={4}>
                خلاصه اطلاعات کاربر
              </Typography.Title>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography.Text>
                    <strong>نام کاربری:</strong> {newUser.username}
                  </Typography.Text>
                  <Typography.Text>
                    <strong>نام کامل:</strong> {newUser.fullName}
                  </Typography.Text>
                  <Typography.Text>
                    <strong>ایمیل:</strong> {newUser.email}
                  </Typography.Text>
                  <Typography.Text>
                    <strong>نقش:</strong> {getRoleText(newUser.role)}
                  </Typography.Text>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography.Text>
                    <strong>بخش:</strong> {newUser.department}
                  </Typography.Text>
                  <Typography.Text>
                    <strong>وضعیت:</strong> {newUser.status === 'active' ? 'فعال' : 'غیرفعال'}
                  </Typography.Text>
                  <Typography.Text>
                    <strong>تعداد ماژول‌ها:</strong> {newUser.selectedModules.length}
                  </Typography.Text>
                </Col>
              </Row>
            </div>
          )}
        </div>
        <div>
          <Button onClick={handleCloseDialog}>انصراف</Button>
          {activeStep !== 0 && (
            <Button onClick={handleBack}>قبلی</Button>
          )}
          {activeStep === steps.length - 1 ? (
            <Button onClick={handleSaveUser} variant="contained">
              {selectedUser ? 'ویرایش' : 'ایجاد'}
            </Button>
          ) : (
            <Button onClick={handleNext} variant="contained">
              بعدی
            </Button>
          )}
        </div>
      </Modal>
    </div>
  );
}; 