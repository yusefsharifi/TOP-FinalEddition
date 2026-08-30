import React, { useState } from 'react';
import { Alert, Button, Card, Col, Collapse, Input, InputNumber, Modal, Progress, Rate, Row, Select, Slider, Table, Tag, Typography } from 'antd';
import { BarChartOutlined, CheckCircleOutlined, DownOutlined, RiseOutlined, StarOutlined, TrophyOutlined, UserOutlined, WarningOutlined } from '@ant-design/icons';

const mockEmployees = [
  {
    id: 1,
    name: 'علی احمدی',
    position: 'برنامه‌نویس ارشد',
    department: 'توسعه نرم‌افزار',
    manager: 'مهندس محمدی',
    overallScore: 4.2,
    lastReview: '1402/09/15',
    nextReview: '1402/12/15',
    status: 'excellent',
    goals: [
      { title: 'توسعه ویژگی‌های جدید', completed: 85, target: 100 },
      { title: 'بهبود عملکرد کد', completed: 90, target: 100 },
      { title: 'مشارکت در تیم', completed: 95, target: 100 },
    ],
    skills: [
      { name: 'React', level: 4.5 },
      { name: 'TypeScript', level: 4.0 },
      { name: 'Node.js', level: 3.8 },
      { name: 'Database Design', level: 4.2 },
    ],
    feedback: 'کارمند بسیار متعهد و با استعداد. عملکرد عالی در پروژه‌های اخیر.',
  },
  {
    id: 2,
    name: 'فاطمه محمدی',
    position: 'طراح UI/UX',
    department: 'طراحی',
    manager: 'خانم رضایی',
    overallScore: 3.8,
    lastReview: '1402/09/20',
    nextReview: '1402/12/20',
    status: 'good',
    goals: [
      { title: 'طراحی رابط کاربری جدید', completed: 70, target: 100 },
      { title: 'بهبود تجربه کاربری', completed: 80, target: 100 },
      { title: 'آموزش همکاران', completed: 60, target: 100 },
    ],
    skills: [
      { name: 'Figma', level: 4.2 },
      { name: 'Adobe XD', level: 3.8 },
      { name: 'Photoshop', level: 4.0 },
      { name: 'User Research', level: 3.5 },
    ],
    feedback: 'طراح خلاق و با استعداد. نیاز به بهبود در مدیریت زمان دارد.',
  },
  {
    id: 3,
    name: 'محمد رضایی',
    position: 'مدیر پروژه',
    department: 'مدیریت',
    manager: 'دکتر احمدی',
    overallScore: 4.5,
    lastReview: '1402/09/10',
    nextReview: '1402/12/10',
    status: 'excellent',
    goals: [
      { title: 'تحویل پروژه‌ها در موعد', completed: 95, target: 100 },
      { title: 'بهبود رضایت تیم', completed: 90, target: 100 },
      { title: 'کاهش هزینه‌ها', completed: 85, target: 100 },
    ],
    skills: [
      { name: 'Project Management', level: 4.8 },
      { name: 'Agile/Scrum', level: 4.5 },
      { name: 'Team Leadership', level: 4.3 },
      { name: 'Risk Management', level: 4.0 },
    ],
    feedback: 'مدیر عالی با مهارت‌های رهبری برجسته. عملکرد استثنایی در مدیریت تیم.',
  },
];

const performanceStatuses = [
  { value: 'excellent', label: 'عالی', color: 'success' },
  { value: 'good', label: 'خوب', color: 'primary' },
  { value: 'average', label: 'متوسط', color: 'warning' },
  { value: 'poor', label: 'ضعیف', color: 'error' },
];

const departments = [
  'توسعه نرم‌افزار',
  'طراحی',
  'مدیریت',
  'فروش',
  'پشتیبانی',
  'مالی',
];

export const Performance: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<any>(null);
  const [newReview, setNewReview] = useState({
    overallScore: 3,
    feedback: '',
    goals: '',
    recommendations: '',
  });

  const handleAddReview = () => {
    setSelectedEmployee(null);
    setOpenDialog(true);
  };

  const handleEditReview = (employee: any) => {
    setSelectedEmployee(employee);
    setNewReview({
      overallScore: employee.overallScore,
      feedback: employee.feedback,
      goals: '',
      recommendations: '',
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedEmployee(null);
    setNewReview({
      overallScore: 3,
      feedback: '',
      goals: '',
      recommendations: '',
    });
  };

  const handleSaveReview = () => {
    // در اینجا ارزیابی ذخیره می‌شود
    handleCloseDialog();
  };

  const getStatusColor = (status: string) => {
    const performanceStatus = performanceStatuses.find(s => s.value === status);
    return performanceStatus ? performanceStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const performanceStatus = performanceStatuses.find(s => s.value === status);
    return performanceStatus ? performanceStatus.label : 'نامشخص';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
        return <EmojiEvents color="success" />;
      case 'good':
        return <CheckCircle color="primary" />;
      case 'average':
        return <TrendingUp color="warning" />;
      case 'poor':
        return <Warning color="error" />;
      default:
        return <Person color="action" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 4.5) return 'success';
    if (score >= 3.5) return 'primary';
    if (score >= 2.5) return 'warning';
    return 'error';
  };

  const totalEmployees = mockEmployees.length;
  const excellentEmployees = mockEmployees.filter(e => e.status === 'excellent').length;
  const goodEmployees = mockEmployees.filter(e => e.status === 'good').length;
  const averageScore = mockEmployees.reduce((sum, e) => sum + e.overallScore, 0) / totalEmployees;

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <Assessment style={{  mr: 1  }} />
            ارزیابی عملکرد
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Assessment />}
            onClick={handleAddReview}
          >
            ارزیابی جدید
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
                {excellentEmployees}
              </Typography.Title>
              <Typography.Text>
                عملکرد عالی
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {goodEmployees}
              </Typography.Title>
              <Typography.Text>
                عملکرد خوب
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {averageScore.toFixed(1)}
              </Typography.Title>
              <Typography.Text>
                میانگین امتیاز
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        {/* لیست ارزیابی‌های عملکرد */}
        {mockEmployees.map((employee) => (
          <Accordion key={employee.id} style={{  mb: 2  }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <div>
                <div>
                  <Typography.Title level={4}>{employee.name}</Typography.Title>
                  <Typography.Text>
                    {employee.position} • {employee.department}
                  </Typography.Text>
                </div>
                <div>
                  {getStatusIcon(employee.status)}
                  <Tag
                    label={getStatusText(employee.status)}
                    color={getStatusColor(employee.status) as any}
                    size="small"
                  />
                  <Rating value={employee.overallScore} readOnly size="small" />
                </div>
              </div>
            </div>
            <AccordionDetails>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  {/* اهداف و پیشرفت */}
                  <Typography variant="subtitle2" gutterBottom>
                    اهداف و پیشرفت:
                  </Typography>
                  <div>
                    {employee.goals.map((goal, index) => (
                      <div>
                        <div>
                          <Typography.Text>{goal.title}</Typography.Text>
                          <Typography.Text>
                            {goal.completed}/{goal.target} ({((goal.completed / goal.target) * 100).toFixed(0)}%)
                          </Typography.Text>
                        </div>
                        <LinearProgress
                          variant="determinate"
                          value={(goal.completed / goal.target) * 100}
                          style={{  height: 8, borderRadius: 4  }}
                        />
                      </div>
                    ))}
                  </div>

                  {/* مهارت‌ها */}
                  <Typography variant="subtitle2" gutterBottom>
                    مهارت‌ها:
                  </Typography>
                  <div>
                    {employee.skills.map((skill, index) => (
                      <Tag
                        key={index}
                        label={`${skill.name}: ${skill.level}/5`}
                        variant="outlined"
                        size="small"
                        color={getScoreColor(skill.level) as any}
                      />
                    ))}
                  </div>

                  {/* بازخورد */}
                  <Typography variant="subtitle2" gutterBottom>
                    بازخورد:
                  </Typography>
                  <Typography.Text>
                    {employee.feedback}
                  </Typography.Text>
                </Col>
                
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Card style={{  p: 2  }}>
                    <Typography variant="subtitle2" gutterBottom>
                      اطلاعات ارزیابی
                    </Typography>
                    <div>
                      <div>
                        <Typography.Text>مدیر:</Typography.Text>
                        <Typography.Text>{employee.manager}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>آخرین ارزیابی:</Typography.Text>
                        <Typography.Text>{employee.lastReview}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>ارزیابی بعدی:</Typography.Text>
                        <Typography.Text>{employee.nextReview}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>امتیاز کلی:</Typography.Text>
                        <Typography.Text>
                          {employee.overallScore}/5
                        </Typography.Text>
                      </div>
                    </div>
                    
                    <div style={{  mt: 2  }}>
                      <Button
                        variant="outlined"
                        size="small"
                        fullWidth
                        onClick={() => handleEditReview(employee)}
                      >
                        ویرایش ارزیابی
                      </Button>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
          </div>
        ))}

        {/* Dialog برای اضافه/ویرایش ارزیابی */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedEmployee ? `ارزیابی ${selectedEmployee.name}` : 'ارزیابی جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Typography variant="subtitle2" gutterBottom>
                  امتیاز کلی:
                </Typography>
                <div>
                  <Rating
                    value={newReview.overallScore}
                    onChange={(_, value) => setNewReview({ ...newReview, overallScore: value || 0 })}
                    size="large"
                  />
                  <Typography.Text>
                    {newReview.overallScore}/5
                  </Typography.Text>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="بازخورد"
                  multiline
                  rows={4}
                  value={newReview.feedback}
                  onChange={(e) => setNewReview({ ...newReview, feedback: e.target.value })}
                  placeholder="نظرات و بازخورد خود را در مورد عملکرد کارمند بنویسید..."
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="اهداف آینده"
                  multiline
                  rows={3}
                  value={newReview.goals}
                  onChange={(e) => setNewReview({ ...newReview, goals: e.target.value })}
                  placeholder="اهداف و انتظارات برای دوره بعدی..."
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توصیه‌ها"
                  multiline
                  rows={3}
                  value={newReview.recommendations}
                  onChange={(e) => setNewReview({ ...newReview, recommendations: e.target.value })}
                  placeholder="توصیه‌های بهبود و توسعه..."
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveReview} variant="contained">
              {selectedEmployee ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 