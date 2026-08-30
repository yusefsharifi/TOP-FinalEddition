import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Col, Divider, Row, Spin, Tabs, Tag, Tooltip, Typography } from 'antd';
import { BankOutlined as BusinessIcon, BarChartOutlined as AssessmentIcon, ClockCircleOutlined as ScheduleIcon, CreditCardOutlined as PaymentIcon, DownloadOutlined as DownloadIcon, EyeOutlined as VisibilityIcon, FallOutlined as TrendingDownIcon, PlusOutlined as AddIcon, ReloadOutlined as RefreshIcon, RiseOutlined as TrendingUpIcon, TeamOutlined as PeopleIcon, ToolOutlined as WorkIcon } from '@ant-design/icons';
import { EmployeesTable } from '../../components/hr/EmployeesTable';
import { Recruitment } from '../../components/hr/Recruitment';
import { Training } from '../../components/hr/Training';
import { Performance } from '../../components/hr/Performance';
import { Attendance } from '../../components/hr/Attendance';
import { Benefits } from '../../components/hr/Benefits';
import { 
  Employee, 
  HRStats,
  HRFilters
} from '../../../types/hr';
import { hrApi } from '../../../api/hr';
import { useAuth } from '../../../core/auth/AuthContext';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`hr-tabpanel-${index}`}
      aria-labelledby={`hr-tab-${index}`}
      {...other}
    >
      {value === index && <div style={{  py: 3  }}>{children}</div>}
    </div>
  );
}

export const HRManagement: React.FC = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<HRStats>({
    total_employees: 0,
    active_employees: 0,
    new_hires_this_month: 0,
    turnover_rate: 0,
    average_salary: 0,
    total_departments: 0,
    total_positions: 0,
    attendance_rate: 0,
  });
  const [filters, setFilters] = useState<HRFilters>({});
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(25);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  const loadEmployees = async () => {
    try {
      setLoading(true);
      const response = await hrApi.employees.getAll({
        ...filters,
        page: page + 1,
        limit,
      });
      setEmployees(response.data);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading employees:', error);
      showSnackbar('خطا در بارگذاری کارمندان', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await hrApi.stats.getDashboard();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  useEffect(() => {
    if (tabValue === 0) {
      loadEmployees();
    }
    loadStats();
  }, [tabValue, page, limit, filters]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setPage(0);
  };

  const handleEmployeeEdit = (employee: Employee) => {
    showSnackbar(`ویرایش کارمند: ${employee.first_name} ${employee.last_name}`, 'info');
  };

  const handleEmployeeDelete = async (employee: Employee) => {
    if (!confirm(`آیا از حذف کارمند "${employee.first_name} ${employee.last_name}" اطمینان دارید؟`)) {
      return;
    }

    try {
      await hrApi.employees.delete(employee.id);
      showSnackbar('کارمند با موفقیت حذف شد', 'success');
      loadEmployees();
      loadStats();
    } catch (error) {
      console.error('Error deleting employee:', error);
      showSnackbar('خطا در حذف کارمند', 'error');
    }
  };

  const handleEmployeeView = (employee: Employee) => {
    showSnackbar(`مشاهده کارمند: ${employee.first_name} ${employee.last_name}`, 'info');
  };

  const handleEmployeeAdd = () => {
    showSnackbar('افزودن کارمند جدید', 'info');
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleLimitChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(0);
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleRefresh = () => {
    if (tabValue === 0) {
      loadEmployees();
    }
    loadStats();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  return (
    <div style={{  p: 3  }}>
      {/* Header */}
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
          <PeopleIcon style={{  fontSize: 32, color: 'primary.main'  }} />
          <div>
            <Typography.Title level={2}>
              مدیریت منابع انسانی
            </Typography.Title>
            <Typography.Text>
              مدیریت کارمندان، بخش‌ها، حضور و غیاب و حقوق
            </Typography.Text>
          </div>
        </div>
        <div style={{  display: 'flex', gap: 1  }}>
          <Tooltip title="بارگذاری مجدد">
            <Button type="text" onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </Button>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleEmployeeAdd}
            disabled={loading}
          >
            افزودن کارمند
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <PeopleIcon style={{  fontSize: 32, color: 'primary.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.total_employees}
                  </Typography.Title>
                  <Typography.Text>
                    کل کارمندان
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <TrendingUpIcon style={{  fontSize: 32, color: 'success.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {stats.active_employees}
                  </Typography.Title>
                  <Typography.Text>
                    کارمندان فعال
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <AssessmentIcon style={{  fontSize: 32, color: 'info.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {formatPercentage(stats.attendance_rate)}
                  </Typography.Title>
                  <Typography.Text>
                    نرخ حضور
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <PaymentIcon style={{  fontSize: 32, color: 'warning.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {formatCurrency(stats.average_salary)}
                  </Typography.Title>
                  <Typography.Text>
                    متوسط حقوق
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
      </Col>

      {/* HR Summary */}
      <Card style={{  p: 2, mb: 3  }}>
        <Typography.Title level={4}>
          خلاصه منابع انسانی
        </Typography.Title>
        <div style={{  display: 'flex', gap: 2, flexWrap: 'wrap'  }}>
          <Tag
            label={`کارمندان جدید این ماه: ${stats.new_hires_this_month}`}
            color="success"
            variant="outlined"
          />
          <Tag
            label={`نرخ جابجایی: ${formatPercentage(stats.turnover_rate)}`}
            color="warning"
            variant="outlined"
          />
          <Tag
            label={`تعداد بخش‌ها: ${stats.total_departments}`}
            color="primary"
            variant="outlined"
          />
          <Tag
            label={`تعداد سمت‌ها: ${stats.total_positions}`}
            color="info"
            variant="outlined"
          />
        </div>
      </Card>

      {/* Tabs */}
      <Card style={{  width: '100%'  }}>
        <div style={{  borderBottom: 1, borderColor: 'divider'  }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="hr tabs">
            <Tab label="کارمندان" />
            <Tab label="بخش‌ها" />
            <Tab label="سمت‌ها" />
            <Tab label="حضور و غیاب" />
            <Tab label="مرخصی‌ها" />
            <Tab label="حقوق" />
            <Tab label="ارزیابی عملکرد" />
            <Tab label="آموزش" />
            <Tab label="استخدام" />
          </Tabs>
        </div>

        <TabPanel value={tabValue} index={0}>
          <EmployeesTable
            employees={employees}
            loading={loading}
            onEdit={handleEmployeeEdit}
            onDelete={handleEmployeeDelete}
            onView={handleEmployeeView}
            onAdd={handleEmployeeAdd}
            onFiltersChange={setFilters}
            total={total}
            page={page}
            limit={limit}
            onPageChange={handlePageChange}
            onLimitChange={handleLimitChange}
            userRole={user?.role}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <div style={{  p: 3, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              مدیریت بخش‌ها
            </Typography.Title>
            <Typography.Text>
              این بخش در حال توسعه است...
            </Typography.Text>
          </div>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <div style={{  p: 3, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              مدیریت سمت‌ها
            </Typography.Title>
            <Typography.Text>
              این بخش در حال توسعه است...
            </Typography.Text>
          </div>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Attendance />
        </TabPanel>

        <TabPanel value={tabValue} index={4}>
          <div style={{  p: 3, textAlign: 'center'  }}>
            <Typography.Title level={4}>
              مدیریت مرخصی‌ها
            </Typography.Title>
            <Typography.Text>
              این بخش در حال توسعه است...
            </Typography.Text>
          </div>
        </TabPanel>

        <TabPanel value={tabValue} index={5}>
          <Benefits />
        </TabPanel>

        <TabPanel value={tabValue} index={6}>
          <Performance />
        </TabPanel>

        <TabPanel value={tabValue} index={7}>
          <Training />
        </TabPanel>

        <TabPanel value={tabValue} index={8}>
          <Recruitment />
        </TabPanel>
      </Card>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          style={{  width: '100%'  }}
        >
          {snackbar.message}
        </Alert>
      </div>
    </div>
  );
}; 