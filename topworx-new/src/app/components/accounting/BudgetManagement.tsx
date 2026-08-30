import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Col, Divider, Input, InputNumber, Modal, Progress, Row, Select, Spin, Table, Tag, Tooltip, Typography } from 'antd';
import { BankOutlined as AccountBalanceIcon, DeleteOutlined as DeleteIcon, DownloadOutlined as DownloadIcon, EditOutlined as EditIcon, EyeOutlined as VisibilityIcon, FallOutlined as TrendingDownIcon, PlusOutlined as AddIcon, ReloadOutlined as RefreshIcon, RiseOutlined as TrendingUpIcon } from '@ant-design/icons';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Budget, BudgetLine } from '../../../types/accounting';
import { accountingApi } from '../../../api/accounting';

export const BudgetManagement: React.FC = () => {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [selectedBudget, setSelectedBudget] = useState<Budget | null>(null);
  const [budgetLines, setBudgetLines] = useState<BudgetLine[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [budgetData, setBudgetData] = useState<any[]>([]);
  const [varianceData, setVarianceData] = useState<any[]>([]);

  const loadBudgets = async () => {
    try {
      setLoading(true);
      const response = await accountingApi.budgets.getAll({ limit: 100 });
      setBudgets(response.data);
      
      // Mock data for charts
      setBudgetData([
        { month: 'فروردین', budget: 1500000, actual: 1400000, variance: -100000 },
        { month: 'اردیبهشت', budget: 1600000, actual: 1650000, variance: 50000 },
        { month: 'خرداد', budget: 1400000, actual: 1350000, variance: -50000 },
        { month: 'تیر', budget: 1700000, actual: 1750000, variance: 50000 },
        { month: 'مرداد', budget: 1500000, actual: 1450000, variance: -50000 },
        { month: 'شهریور', budget: 1600000, actual: 1700000, variance: 100000 },
      ]);

      setVarianceData([
        { category: 'هزینه‌های عملیاتی', budget: 800000, actual: 750000, variance: -50000 },
        { category: 'هزینه‌های اداری', budget: 400000, actual: 420000, variance: 20000 },
        { category: 'هزینه‌های فروش', budget: 300000, actual: 280000, variance: -20000 },
        { category: 'هزینه‌های مالی', budget: 100000, actual: 95000, variance: -5000 },
      ]);
    } catch (error) {
      console.error('Error loading budgets:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBudgets();
  }, []);

  const handleViewBudget = async (budget: Budget) => {
    try {
      const linesResponse = await accountingApi.budgets.getLines(budget.id);
      setBudgetLines(linesResponse.data);
      setSelectedBudget(budget);
      setDialogOpen(true);
    } catch (error) {
      console.error('Error loading budget lines:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const getVarianceColor = (variance: number) => {
    if (variance < 0) return 'error';
    if (variance > 0) return 'warning';
    return 'success';
  };

  const getVarianceIcon = (variance: number) => {
    if (variance < 0) return <TrendingDownIcon />;
    if (variance > 0) return <TrendingUpIcon />;
    return null;
  };

  if (loading) {
    return (
      <div style={{  display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400  }}>
        <Spin />
      </div>
    );
  }

  return (
    <div style={{  p: 3  }}>
      {/* Header */}
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <Typography.Title level={2}>
          مدیریت بودجه
        </Typography.Title>
        <div style={{  display: 'flex', gap: 1  }}>
          <Tooltip title="بارگذاری مجدد">
            <Button type="text" onClick={loadBudgets} disabled={loading}>
              <RefreshIcon />
            </Button>
          </Tooltip>
          <Button variant="contained" startIcon={<AddIcon />}>
            افزودن بودجه جدید
          </Button>
        </div>
      </div>

      {/* Budget Overview Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <AccountBalanceIcon style={{  fontSize: 32, color: 'primary.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {budgets.length}
                  </Typography.Title>
                  <Typography.Text>
                    کل بودجه‌ها
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
                    {budgets.filter(b => b.status === 'active').length}
                  </Typography.Title>
                  <Typography.Text>
                    بودجه‌های فعال
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
                <TrendingDownIcon style={{  fontSize: 32, color: 'warning.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {budgets.filter(b => b.status === 'approved').length}
                  </Typography.Title>
                  <Typography.Text>
                    بودجه‌های تأیید شده
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
                <AccountBalanceIcon style={{  fontSize: 32, color: 'info.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {formatCurrency(budgets.reduce((sum, b) => sum + b.total_budget, 0))}
                  </Typography.Title>
                  <Typography.Text>
                    کل بودجه
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
      </Col>

      {/* Budget vs Actual Chart */}
      <Card style={{  p: 3, mb: 3  }}>
        <Typography.Title level={4}>
          مقایسه بودجه و عملکرد واقعی
        </Typography.Title>
        <div style={{  height: 400  }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={budgetData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <RechartsTooltip formatter={(value) => formatCurrency(Number(value))} />
              <Legend />
              <Line type="monotone" dataKey="budget" stroke="#8884d8" name="بودجه" />
              <Line type="monotone" dataKey="actual" stroke="#82ca9d" name="عملکرد واقعی" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Variance Analysis */}
      <Card style={{  p: 3, mb: 3  }}>
        <Typography.Title level={4}>
          تحلیل انحراف بودجه
        </Typography.Title>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>دسته‌بندی</TableCell>
                <TableCell align="right">بودجه</TableCell>
                <TableCell align="right">عملکرد واقعی</TableCell>
                <TableCell align="right">انحراف</TableCell>
                <TableCell align="right">درصد انحراف</TableCell>
                <TableCell>وضعیت</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {varianceData.map((row) => (
                <TableRow key={row.category}>
                  <TableCell>{row.category}</TableCell>
                  <TableCell align="right">{formatCurrency(row.budget)}</TableCell>
                  <TableCell align="right">{formatCurrency(row.actual)}</TableCell>
                  <TableCell align="right">
                    <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                      {getVarianceIcon(row.variance)}
                      <Typography
                        color={getVarianceColor(row.variance)}
                        fontFamily="monospace"
                      >
                        {formatCurrency(row.variance)}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell align="right">
                    {formatPercentage((row.variance / row.budget) * 100)}
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={row.variance < 0 ? 'کمتر از بودجه' : row.variance > 0 ? 'بیشتر از بودجه' : 'مطابق بودجه'}
                      color={getVarianceColor(row.variance)}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* Budget List */}
      <Card style={{  p: 3  }}>
        <Typography.Title level={4}>
          لیست بودجه‌ها
        </Typography.Title>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام بودجه</TableCell>
                <TableCell>سال مالی</TableCell>
                <TableCell align="right">کل بودجه</TableCell>
                <TableCell align="right">عملکرد واقعی</TableCell>
                <TableCell align="right">انحراف</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell align="center">عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {budgets.map((budget) => (
                <TableRow key={budget.id} hover>
                  <TableCell>
                    <Typography.Text>
                      {budget.name}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>{budget.fiscal_year}</TableCell>
                  <TableCell align="right">
                    <Typography.Text>
                      {formatCurrency(budget.total_budget)}
                    </Typography.Text>
                  </TableCell>
                  <TableCell align="right">
                    <Typography.Text>
                      {formatCurrency(budget.actual_amount)}
                    </Typography.Text>
                  </TableCell>
                  <TableCell align="right">
                    <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                      {getVarianceIcon(budget.variance)}
                      <Typography
                        color={getVarianceColor(budget.variance)}
                        fontFamily="monospace"
                      >
                        {formatCurrency(budget.variance)}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={budget.status === 'active' ? 'فعال' : budget.status === 'approved' ? 'تأیید شده' : 'پیش‌نویس'}
                      color={budget.status === 'active' ? 'success' : budget.status === 'approved' ? 'primary' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                      <Tooltip title="مشاهده جزئیات">
                        <Button type="text" size="small" onClick={() => handleViewBudget(budget)}
                        >
                          <VisibilityIcon />
                        </Button>
                      </Tooltip>
                      <Tooltip title="ویرایش">
                        <Button type="text" size="small" color="primary">
                          <EditIcon />
                        </Button>
                      </Tooltip>
                      <Tooltip title="حذف">
                        <Button type="text" size="small" color="error">
                          <DeleteIcon />
                        </Button>
                      </Tooltip>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* Budget Details Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          <Typography.Title level={4}>
            جزئیات بودجه: {selectedBudget?.name}
          </Typography.Title>
        </div>
        <div>
          {selectedBudget && (
            <div>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    سال مالی
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedBudget.fiscal_year}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    وضعیت
                  </Typography>
                  <Tag
                    label={selectedBudget.status === 'active' ? 'فعال' : 'تأیید شده'}
                    color={selectedBudget.status === 'active' ? 'success' : 'primary'}
                    style={{  mb: 2  }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    کل بودجه
                  </Typography>
                  <Typography.Title level={4}>
                    {formatCurrency(selectedBudget.total_budget)}
                  </Typography.Title>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    عملکرد واقعی
                  </Typography>
                  <Typography.Title level={4}>
                    {formatCurrency(selectedBudget.actual_amount)}
                  </Typography.Title>
                </Col>
              </Row>

              <Divider style={{  my: 2  }} />

              <Typography.Title level={4}>
                ردیف‌های بودجه
              </Typography.Title>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>حساب</TableCell>
                      <TableCell align="right">بودجه</TableCell>
                      <TableCell align="right">عملکرد واقعی</TableCell>
                      <TableCell align="right">انحراف</TableCell>
                      <TableCell align="right">درصد انحراف</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {budgetLines.map((line) => (
                      <TableRow key={line.id}>
                        <TableCell>{line.account_name}</TableCell>
                        <TableCell align="right">{formatCurrency(line.budget_amount)}</TableCell>
                        <TableCell align="right">{formatCurrency(line.actual_amount)}</TableCell>
                        <TableCell align="right">
                          <Typography
                            color={getVarianceColor(line.variance)}
                            fontFamily="monospace"
                          >
                            {formatCurrency(line.variance)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          {formatPercentage(line.variance_percentage)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </div>
        <div>
          <Button onClick={() => setDialogOpen(false)}>
            بستن
          </Button>
        </div>
      </Modal>
    </div>
  );
}; 