import React, { useState, useEffect } from 'react';
import { Alert, Badge, Button, Card, Col, Collapse, Input, InputNumber, Modal, Progress, Rate, Row, Select, Table, Tag, Typography } from 'antd';
import { BarChartOutlined, BugOutlined, CheckCircleOutlined, CloseCircleOutlined, DownOutlined, FallOutlined, FilterOutlined, PlusOutlined, QualityOutlined, ReloadOutlined, RiseOutlined, SafetyOutlined, SpeedOutlined, StarOutlined, WarningOutlined } from '@ant-design/icons';

const mockQualityData = {
  totalInspections: 1250,
  passedInspections: 1180,
  failedInspections: 70,
  qualityScore: 94.4,
  defectRate: 5.6,
  topIssues: [
    { name: 'نقص در بسته‌بندی', count: 25, severity: 'medium' },
    { name: 'مشکل در رنگ‌آمیزی', count: 18, severity: 'high' },
    { name: 'عدم تطابق اندازه', count: 12, severity: 'low' },
    { name: 'نقص در عملکرد', count: 8, severity: 'critical' },
  ],
  qualityByDepartment: [
    { department: 'تولید', score: 96.2, inspections: 450 },
    { department: 'مونتاژ', score: 93.8, inspections: 320 },
    { department: 'بسته‌بندی', score: 91.5, inspections: 280 },
    { department: 'کنترل کیفیت', score: 98.1, inspections: 200 },
  ],
  recentInspections: [
    {
      id: 'INS-001',
      product: 'لپ‌تاپ Dell XPS 13',
      inspector: 'علی احمدی',
      result: 'passed',
      score: 95,
      date: '1402/11/15',
      notes: 'کیفیت عالی، تمام تست‌ها موفق',
    },
    {
      id: 'INS-002',
      product: 'ماوس بی‌سیم Logitech',
      inspector: 'فاطمه محمدی',
      result: 'failed',
      score: 65,
      date: '1402/11/14',
      notes: 'مشکل در عملکرد دکمه‌ها',
    },
    {
      id: 'INS-003',
      product: 'کیف چرمی مردانه',
      inspector: 'محمد رضایی',
      result: 'passed',
      score: 92,
      date: '1402/11/13',
      notes: 'کیفیت خوب، نیاز به بهبود جزئی',
    },
  ],
  qualityTrend: [
    { month: 'مهر', score: 91.5 },
    { month: 'آبان', score: 93.2 },
    { month: 'آذر', score: 92.8 },
    { month: 'دی', score: 94.1 },
    { month: 'بهمن', score: 94.4 },
    { month: 'اسفند', score: 95.2 },
  ],
  defectCategories: [
    { category: 'ظاهری', count: 35, percentage: 50 },
    { category: 'عملکردی', count: 20, percentage: 28.6 },
    { category: 'بسته‌بندی', count: 10, percentage: 14.3 },
    { category: 'سایر', count: 5, percentage: 7.1 },
  ],
};

const inspectionResults = [
  { value: 'passed', label: 'تأیید شده', color: 'success' },
  { value: 'failed', label: 'رد شده', color: 'error' },
  { value: 'conditional', label: 'مشروط', color: 'warning' },
  { value: 'pending', label: 'در انتظار', color: 'info' },
];

const severityLevels = [
  { value: 'critical', label: 'بحرانی', color: 'error' },
  { value: 'high', label: 'بالا', color: 'warning' },
  { value: 'medium', label: 'متوسط', color: 'info' },
  { value: 'low', label: 'کم', color: 'success' },
];

export const QualityDashboard: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [openDialog, setOpenDialog] = useState(false);

  const getResultColor = (result: string) => {
    const inspectionResult = inspectionResults.find(r => r.value === result);
    return inspectionResult ? inspectionResult.color : 'default';
  };

  const getResultText = (result: string) => {
    const inspectionResult = inspectionResults.find(r => r.value === result);
    return inspectionResult ? inspectionResult.label : 'نامشخص';
  };

  const getSeverityColor = (severity: string) => {
    const severityLevel = severityLevels.find(s => s.value === severity);
    return severityLevel ? severityLevel.color : 'default';
  };

  const getSeverityText = (severity: string) => {
    const severityLevel = severityLevels.find(s => s.value === severity);
    return severityLevel ? severityLevel.label : 'نامشخص';
  };

  const formatPercentage = (value: number) => {
    return value.toFixed(1) + '%';
  };

  const getQualityColor = (score: number) => {
    if (score >= 95) return 'success';
    if (score >= 85) return 'primary';
    if (score >= 75) return 'warning';
    return 'error';
  };

  return (
    <div>
      {/* Header */}
      <div>
        <Typography.Title level={3}>
          داشبورد کیفیت
        </Typography.Title>
        <div>
          <FormControl size="small" style={{  minWidth: 120  }}>
            <InputLabel>دوره</span>
            <Select
              value={selectedPeriod}
              label="دوره"
              onChange={(e) => setSelectedPeriod(e.target.value)}
            >
              <MenuItem value="week">هفته</Select.Option>
              <MenuItem value="month">ماه</Select.Option>
              <MenuItem value="quarter">فصل</Select.Option>
              <MenuItem value="year">سال</Select.Option>
            </Select>
          </div>
          <Button type="text">
            <Refresh />
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography.Title level={2}>
                    {mockQualityData.qualityScore}%
                  </Typography.Title>
                  <Typography.Text>
                    امتیاز کیفیت
                  </Typography.Text>
                </div>
                <Quality style={{  fontSize: 40, color: 'primary.main'  }} />
              </div>
              <div>
                <TrendingUp color="success" style={{  mr: 0.5  }} />
                <Typography.Text>
                  +2.1% نسبت به ماه قبل
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
                    {mockQualityData.passedInspections}
                  </Typography.Title>
                  <Typography.Text>
                    بازرسی‌های موفق
                  </Typography.Text>
                </div>
                <CheckCircle style={{  fontSize: 40, color: 'success.main'  }} />
              </div>
              <div>
                <Typography.Text>
                  {formatPercentage((mockQualityData.passedInspections / mockQualityData.totalInspections) * 100)} موفقیت
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
                    {mockQualityData.failedInspections}
                  </Typography.Title>
                  <Typography.Text>
                    بازرسی‌های ناموفق
                  </Typography.Text>
                </div>
                <Error style={{  fontSize: 40, color: 'error'  }} />
              </div>
              <div>
                <Typography.Text>
                  {formatPercentage(mockQualityData.defectRate)} نرخ نقص
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
                    {mockQualityData.totalInspections}
                  </Typography.Title>
                  <Typography.Text>
                    کل بازرسی‌ها
                  </Typography.Text>
                </div>
                <Assessment style={{  fontSize: 40, color: 'info.main'  }} />
              </div>
              <div>
                <Typography.Text>
                  این ماه
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Quality Alerts */}
      {mockQualityData.failedInspections > 50 && (
        <Alert severity="warning" style={{  mb: 3  }}>
          {mockQualityData.failedInspections} بازرسی ناموفق وجود دارد که نیاز به بررسی فوری دارد!
        </Alert>
      )}

      {/* Charts Section */}
      <Row gutter={[16, 16]}>
        {/* Quality Trend Chart */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <Typography.Title level={4}>
                  روند کیفیت
                </Typography.Title>
                <Button type="text" size="small">
                  <TrendingUp />
                </Button>
              </div>
              <div style={{  height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center'  }}>
                <Typography.Text>
                  نمودار روند کیفیت در 6 ماه گذشته
                </Typography.Text>
              </div>
            </div>
          </Card>
        </Col>

        {/* Quality by Department */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <Typography.Title level={4}>
                کیفیت بر اساس بخش
              </Typography.Title>
              <div>
                {mockQualityData.qualityByDepartment.map((dept, index) => (
                  <div>
                    <div>
                      <Typography.Text>{dept.department}</Typography.Text>
                      <Typography.Text>
                        {dept.score}%
                      </Typography.Text>
                    </div>
                    <LinearProgress
                      variant="determinate"
                      value={dept.score}
                      color={getQualityColor(dept.score) as any}
                      style={{  height: 8, borderRadius: 4  }}
                    />
                    <Typography variant="caption" color="textSecondary">
                      {dept.inspections} بازرسی
                    </Typography>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Top Issues and Recent Inspections */}
      <Row gutter={[16, 16]}>
        {/* Top Issues */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <Typography.Title level={4}>
                  مشکلات برتر
                </Typography.Title>
                <Button size="small" startIcon={<Add />}>
                  مشاهده همه
                </Button>
              </div>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>مشکل</TableCell>
                      <TableCell align="right">تعداد</TableCell>
                      <TableCell>شدت</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockQualityData.topIssues.map((issue, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography.Text>
                            {issue.name}
                          </Typography.Text>
                        </TableCell>
                        <TableCell align="right">
                          <Tag label={issue.count} size="small" color="primary" />
                        </TableCell>
                        <TableCell>
                          <Tag
                            label={getSeverityText(issue.severity)}
                            color={getSeverityColor(issue.severity) as any}
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

        {/* Recent Inspections */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <Typography.Title level={4}>
                  بازرسی‌های اخیر
                </Typography.Title>
                <Button size="small" startIcon={<Add />}>
                  مشاهده همه
                </Button>
              </div>
              <div>
                {mockQualityData.recentInspections.map((inspection, index) => (
                  <div>
                    <div>
                      <Typography.Text>
                        {inspection.id}
                      </Typography.Text>
                      <Tag
                        label={getResultText(inspection.result)}
                        color={getResultColor(inspection.result) as any}
                        size="small"
                      />
                    </div>
                    <Typography.Text>
                      {inspection.product} - {inspection.inspector}
                    </Typography.Text>
                    <div>
                      <div>
                        <Rating value={inspection.score / 20} readOnly size="small" />
                        <Typography.Text>
                          {inspection.score}/100
                        </Typography.Text>
                      </div>
                      <Typography variant="caption" color="textSecondary">
                        {inspection.date}
                      </Typography>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Defect Categories */}
      <div style={{  mt: 3  }}>
        <Typography.Title level={4}>
          دسته‌بندی نقص‌ها
        </Typography.Title>
        <Row gutter={[16, 16]}>
          {mockQualityData.defectCategories.map((category, index) => (
            <Col xs={Math.round(12 / 12 * 24)}>
              <Card style={{  p: 2, textAlign: 'center'  }}>
                <Typography.Title level={4}>
                  {category.count}
                </Typography.Title>
                <Typography.Text>
                  {category.category}
                </Typography.Text>
                <LinearProgress
                  variant="determinate"
                  value={category.percentage}
                  style={{  height: 8, borderRadius: 4  }}
                />
                <Typography variant="caption" color="textSecondary">
                  {formatPercentage(category.percentage)}
                </Typography>
              </Card>
            </Col>
          ))}
        </Row>
      </div>
    </div>
  );
}; 