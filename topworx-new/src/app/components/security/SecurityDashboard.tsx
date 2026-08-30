import React, { useState, useEffect } from 'react';
import { Alert, Badge, Button, Card, Col, Collapse, Input, InputNumber, Modal, Progress, Rate, Row, Select, Switch, Table, Tag, Typography } from 'antd';
import { BarChartOutlined, BugOutlined, CheckCircleOutlined, CloseCircleOutlined, DownOutlined, EyeInvisibleOutlined, EyeOutlined, FallOutlined, FilterOutlined, HistoryOutlined, KeyOutlined, LockOutlined, PlusOutlined, ReloadOutlined, RiseOutlined, SafetyOutlined, SpeedOutlined, StarOutlined, TeamOutlined, UserOutlined, WarningOutlined } from '@ant-design/icons';

const mockSecurityData = {
  overallScore: 85,
  lastScan: '1402/11/15 14:30',
  totalThreats: 3,
  criticalThreats: 1,
  highThreats: 2,
  mediumThreats: 0,
  lowThreats: 0,
  securityEvents: [
    {
      id: 1,
      type: 'failed_login',
      severity: 'medium',
      user: 'user123',
      ip: '192.168.1.100',
      timestamp: '1402/11/15 14:25',
      description: 'تلاش ناموفق ورود به سیستم',
      status: 'investigating',
    },
    {
      id: 2,
      type: 'suspicious_activity',
      severity: 'high',
      user: 'admin',
      ip: '10.0.0.50',
      timestamp: '1402/11/15 13:45',
      description: 'فعالیت مشکوک در بخش مالی',
      status: 'resolved',
    },
    {
      id: 3,
      type: 'data_access',
      severity: 'low',
      user: 'manager1',
      ip: '172.16.0.25',
      timestamp: '1402/11/15 12:30',
      description: 'دسترسی به داده‌های حساس',
      status: 'normal',
    },
  ],
  moduleAccess: [
    { module: 'Dashboard', users: 150, admins: 5, lastAccess: '1402/11/15 15:00' },
    { module: 'CRM', users: 45, admins: 3, lastAccess: '1402/11/15 14:45' },
    { module: 'Inventory', users: 25, admins: 2, lastAccess: '1402/11/15 14:30' },
    { module: 'Finance', users: 15, admins: 2, lastAccess: '1402/11/15 14:15' },
    { module: 'HR', users: 20, admins: 2, lastAccess: '1402/11/15 14:00' },
    { module: 'Sales', users: 35, admins: 3, lastAccess: '1402/11/15 13:45' },
    { module: 'Purchase', users: 18, admins: 2, lastAccess: '1402/11/15 13:30' },
    { module: 'Procurement', users: 12, admins: 1, lastAccess: '1402/11/15 13:15' },
    { module: 'Quality', users: 15, admins: 2, lastAccess: '1402/11/15 13:00' },
    { module: 'Projects', users: 30, admins: 2, lastAccess: '1402/11/15 12:45' },
    { module: 'BI', users: 8, admins: 2, lastAccess: '1402/11/15 12:30' },
    { module: 'AI', users: 5, admins: 1, lastAccess: '1402/11/15 12:15' },
    { module: 'Reports', users: 25, admins: 3, lastAccess: '1402/11/15 12:00' },
    { module: 'Tasks', users: 40, admins: 2, lastAccess: '1402/11/15 11:45' },
    { module: 'Correspondence', users: 10, admins: 1, lastAccess: '1402/11/15 11:30' },
    { module: 'HSE', users: 12, admins: 2, lastAccess: '1402/11/15 11:15' },
    { module: 'Calendar', users: 60, admins: 2, lastAccess: '1402/11/15 11:00' },
    { module: 'Documents', users: 35, admins: 2, lastAccess: '1402/11/15 10:45' },
    { module: 'Settings', users: 3, admins: 3, lastAccess: '1402/11/15 10:30' },
  ],
  userRoles: [
    { role: 'Super Admin', users: 3, permissions: 'All', lastActivity: '1402/11/15 15:00' },
    { role: 'Module Admin', users: 25, permissions: 'Module Specific', lastActivity: '1402/11/15 14:45' },
    { role: 'Manager', users: 45, permissions: 'Department', lastActivity: '1402/11/15 14:30' },
    { role: 'User', users: 200, permissions: 'Limited', lastActivity: '1402/11/15 14:15' },
    { role: 'Guest', users: 15, permissions: 'Read Only', lastActivity: '1402/11/15 14:00' },
  ],
  securityMetrics: {
    totalUsers: 288,
    activeUsers: 245,
    failedLogins: 12,
    suspiciousActivities: 3,
    dataBreaches: 0,
    systemUptime: 99.8,
  },
};

const severityLevels = [
  { value: 'critical', label: 'بحرانی', color: 'error' },
  { value: 'high', label: 'بالا', color: 'warning' },
  { value: 'medium', label: 'متوسط', color: 'info' },
  { value: 'low', label: 'کم', color: 'success' },
];

const eventTypes = [
  { value: 'failed_login', label: 'ورود ناموفق', color: 'warning' },
  { value: 'suspicious_activity', label: 'فعالیت مشکوک', color: 'error' },
  { value: 'data_access', label: 'دسترسی به داده', color: 'info' },
  { value: 'system_change', label: 'تغییر سیستم', color: 'primary' },
];

export const SecurityDashboard: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('day');
  const [openDialog, setOpenDialog] = useState(false);

  const getSeverityColor = (severity: string) => {
    const severityLevel = severityLevels.find(s => s.value === severity);
    return severityLevel ? severityLevel.color : 'default';
  };

  const getSeverityText = (severity: string) => {
    const severityLevel = severityLevels.find(s => s.value === severity);
    return severityLevel ? severityLevel.label : 'نامشخص';
  };

  const getEventTypeColor = (type: string) => {
    const eventType = eventTypes.find(t => t.value === type);
    return eventType ? eventType.color : 'default';
  };

  const getEventTypeText = (type: string) => {
    const eventType = eventTypes.find(t => t.value === type);
    return eventType ? eventType.label : 'نامشخص';
  };

  const getSecurityScoreColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'primary';
    if (score >= 50) return 'warning';
    return 'error';
  };

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          داشبورد امنیت
        </Typography.Title>
        <div>
          <FormControl size="small" style={{  minWidth: 120  }}>
            <InputLabel>دوره</span>
            <Select
              value={selectedPeriod}
              label="دوره"
              onChange={(e) => setSelectedPeriod(e.target.value)}
            >
              <MenuItem value="hour">ساعت</Select.Option>
              <MenuItem value="day">روز</Select.Option>
              <MenuItem value="week">هفته</Select.Option>
              <MenuItem value="month">ماه</Select.Option>
            </Select>
          </div>
          <Button type="text">
            <Refresh />
          </Button>
          <Button variant="contained" startIcon={<Shield />}>
            اسکن امنیتی
          </Button>
        </div>
      </div>

      {/* Key Security Metrics */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography.Title level={2}>
                    {mockSecurityData.overallScore}%
                  </Typography.Title>
                  <Typography.Text>
                    امتیاز امنیتی
                  </Typography.Text>
                </div>
                <Security style={{  fontSize: 40, color: getSecurityScoreColor(mockSecurityData.overallScore) + '.main'  }} />
              </div>
              <div>
                <TrendingUp color="success" style={{  mr: 0.5  }} />
                <Typography.Text>
                  +5% نسبت به هفته قبل
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography.Title level={2}>
                    {mockSecurityData.totalThreats}
                  </Typography.Title>
                  <Typography.Text>
                    تهدیدات شناسایی شده
                  </Typography.Text>
                </div>
                <Warning style={{  fontSize: 40, color: 'error'  }} />
              </div>
              <div>
                <Typography.Text>
                  {mockSecurityData.criticalThreats} بحرانی
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography.Title level={2}>
                    {mockSecurityData.securityMetrics.activeUsers}
                  </Typography.Title>
                  <Typography.Text>
                    کاربران فعال
                  </Typography.Text>
                </div>
                <Person style={{  fontSize: 40, color: 'success.main'  }} />
              </div>
              <div>
                <Typography.Text>
                  از {mockSecurityData.securityMetrics.totalUsers} کاربر کل
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography.Title level={2}>
                    {mockSecurityData.securityMetrics.systemUptime}%
                  </Typography.Title>
                  <Typography.Text>
                    در دسترس بودن سیستم
                  </Typography.Text>
                </div>
                <CheckCircle style={{  fontSize: 40, color: 'info.main'  }} />
              </div>
              <div>
                <Typography.Text>
                  بدون قطعی در 30 روز گذشته
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Security Alerts */}
      {mockSecurityData.criticalThreats > 0 && (
        <Alert severity="error" style={{  mb: 3  }}>
          {mockSecurityData.criticalThreats} تهدید بحرانی شناسایی شده که نیاز به بررسی فوری دارد!
        </Alert>
      )}

      {/* Security Events and Module Access */}
      <Row gutter={[16, 16]}>
        {/* Security Events */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <Typography.Title level={4}>
                  رویدادهای امنیتی
                </Typography.Title>
                <Button size="small" startIcon={<Add />}>
                  مشاهده همه
                </Button>
              </div>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>نوع</TableCell>
                      <TableCell>کاربر</TableCell>
                      <TableCell>شدت</TableCell>
                      <TableCell>وضعیت</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockSecurityData.securityEvents.map((event) => (
                      <TableRow key={event.id}>
                        <TableCell>
                          <Typography.Text>
                            {getEventTypeText(event.type)}
                          </Typography.Text>
                          <Typography variant="caption" color="textSecondary">
                            {event.timestamp}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography.Text>{event.user}</Typography.Text>
                          <Typography variant="caption" color="textSecondary">
                            {event.ip}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Tag
                            label={getSeverityText(event.severity)}
                            color={getSeverityColor(event.severity) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Tag
                            label={event.status === 'resolved' ? 'حل شده' : event.status === 'investigating' ? 'در حال بررسی' : 'عادی'}
                            color={event.status === 'resolved' ? 'success' : event.status === 'investigating' ? 'warning' : 'info'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </Card>
        </Col>

        {/* Module Access Overview */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography.Title level={4}>
                دسترسی به ماژول‌ها
              </Typography.Title>
              <div>
                {mockSecurityData.moduleAccess.slice(0, 8).map((module, index) => (
                  <div>
                    <div>
                      <Typography.Text>
                        {module.module}
                      </Typography.Text>
                      <Typography.Text>
                        {module.users + module.admins} کاربر
                      </Typography.Text>
                    </div>
                    <LinearProgress
                      variant="determinate"
                      value={((module.users + module.admins) / mockSecurityData.securityMetrics.totalUsers) * 100}
                      style={{  height: 6, borderRadius: 3  }}
                    />
                    <div>
                      <Typography variant="caption" color="textSecondary">
                        {module.admins} ادمین
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {module.lastAccess}
                      </Typography>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* User Roles and Permissions */}
      <div style={{  mt: 3  }}>
        <Typography.Title level={4}>
          نقش‌های کاربری و دسترسی‌ها
        </Typography.Title>
        <Row gutter={[16, 16]}>
          {mockSecurityData.userRoles.map((role, index) => (
            <Col xs={Math.round(12 / 12 * 24)}>
              <Card style={{  p: 2  }}>
                <div>
                  <Typography.Title level={4}>
                    {role.role}
                  </Typography.Title>
                  <Tag label={`${role.users} کاربر`} size="small" color="primary" />
                </div>
                <Typography.Text>
                  دسترسی: {role.permissions}
                </Typography.Text>
                <Typography variant="caption" color="textSecondary">
                  آخرین فعالیت: {role.lastActivity}
                </Typography>
                <div style={{  mt: 2  }}>
                  <Button variant="outlined" size="small" fullWidth>
                    مدیریت دسترسی‌ها
                  </Button>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </div>

      {/* Security Metrics Details */}
      <div style={{  mt: 3  }}>
        <Typography.Title level={4}>
          آمار امنیتی
        </Typography.Title>
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {mockSecurityData.securityMetrics.failedLogins}
              </Typography.Title>
              <Typography.Text>
                ورودهای ناموفق
              </Typography.Text>
              <LinearProgress
                variant="determinate"
                value={(mockSecurityData.securityMetrics.failedLogins / mockSecurityData.securityMetrics.totalUsers) * 100}
                style={{  height: 6, borderRadius: 3  }}
              />
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {mockSecurityData.securityMetrics.suspiciousActivities}
              </Typography.Title>
              <Typography.Text>
                فعالیت‌های مشکوک
              </Typography.Text>
              <LinearProgress
                variant="determinate"
                value={(mockSecurityData.securityMetrics.suspiciousActivities / mockSecurityData.securityMetrics.totalUsers) * 100}
                style={{  height: 6, borderRadius: 3  }}
              />
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {mockSecurityData.securityMetrics.dataBreaches}
              </Typography.Title>
              <Typography.Text>
                نقض داده‌ها
              </Typography.Text>
              <LinearProgress
                variant="determinate"
                value={0}
                style={{  height: 6, borderRadius: 3  }}
              />
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {mockSecurityData.securityMetrics.systemUptime}%
              </Typography.Title>
              <Typography.Text>
                در دسترس بودن
              </Typography.Text>
              <LinearProgress
                variant="determinate"
                value={mockSecurityData.securityMetrics.systemUptime}
                style={{  height: 6, borderRadius: 3  }}
              />
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
}; 