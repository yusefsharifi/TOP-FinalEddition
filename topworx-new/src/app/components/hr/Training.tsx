import React, { useState } from 'react';
import { Alert, Button, Card, Col, Collapse, Input, InputNumber, Modal, Progress, Rate, Row, Select, Table, Tag, Typography } from 'antd';
import { CheckCircleOutlined, CheckSquareOutlined, ClockCircleOutlined, DownOutlined, ReadOutlined, UserOutlined, VideoCameraOutlined } from '@ant-design/icons';

const mockTrainings = [
  {
    id: 1,
    title: 'آموزش React پیشرفته',
    instructor: 'دکتر احمدی',
    type: 'online',
    duration: '20 ساعت',
    startDate: '1402/11/01',
    endDate: '1402/11/15',
    status: 'active',
    enrolledEmployees: 15,
    maxCapacity: 20,
    rating: 4.5,
    description: 'آموزش مفاهیم پیشرفته React و TypeScript',
    modules: [
      { title: 'مفاهیم پایه React', duration: '4 ساعت', completed: true },
      { title: 'Hooks پیشرفته', duration: '6 ساعت', completed: true },
      { title: 'State Management', duration: '5 ساعت', completed: false },
      { title: 'Testing', duration: '5 ساعت', completed: false },
    ],
  },
  {
    id: 2,
    title: 'مدیریت پروژه Agile',
    instructor: 'مهندس محمدی',
    type: 'workshop',
    duration: '16 ساعت',
    startDate: '1402/11/10',
    endDate: '1402/11/12',
    status: 'completed',
    enrolledEmployees: 12,
    maxCapacity: 15,
    rating: 4.8,
    description: 'کارگاه عملی مدیریت پروژه با روش‌های Agile',
    modules: [
      { title: 'مفاهیم Agile', duration: '4 ساعت', completed: true },
      { title: 'Scrum Framework', duration: '6 ساعت', completed: true },
      { title: 'Sprint Planning', duration: '3 ساعت', completed: true },
      { title: 'Retrospective', duration: '3 ساعت', completed: true },
    ],
  },
  {
    id: 3,
    title: 'مهارت‌های ارتباطی',
    instructor: 'خانم رضایی',
    type: 'seminar',
    duration: '8 ساعت',
    startDate: '1402/12/01',
    endDate: '1402/12/01',
    status: 'upcoming',
    enrolledEmployees: 8,
    maxCapacity: 25,
    rating: 0,
    description: 'بهبود مهارت‌های ارتباطی و ارائه',
    modules: [
      { title: 'اصول ارتباط مؤثر', duration: '3 ساعت', completed: false },
      { title: 'ارائه و سخنرانی', duration: '3 ساعت', completed: false },
      { title: 'مذاکره و حل تعارض', duration: '2 ساعت', completed: false },
    ],
  },
];

const trainingTypes = [
  { value: 'online', label: 'آنلاین', color: 'primary' },
  { value: 'workshop', label: 'کارگاه', color: 'secondary' },
  { value: 'seminar', label: 'سمینار', color: 'info' },
  { value: 'certification', label: 'گواهینامه', color: 'success' },
];

const trainingStatuses = [
  { value: 'upcoming', label: 'آینده', color: 'info' },
  { value: 'active', label: 'فعال', color: 'success' },
  { value: 'completed', label: 'تکمیل شده', color: 'default' },
  { value: 'cancelled', label: 'لغو شده', color: 'error' },
];

export const Training: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTraining, setSelectedTraining] = useState<any>(null);
  const [newTraining, setNewTraining] = useState({
    title: '',
    instructor: '',
    type: '',
    duration: '',
    startDate: '',
    endDate: '',
    maxCapacity: '',
    description: '',
  });

  const handleAddTraining = () => {
    setSelectedTraining(null);
    setOpenDialog(true);
  };

  const handleEditTraining = (training: any) => {
    setSelectedTraining(training);
    setNewTraining({
      title: training.title,
      instructor: training.instructor,
      type: training.type,
      duration: training.duration,
      startDate: training.startDate,
      endDate: training.endDate,
      maxCapacity: training.maxCapacity.toString(),
      description: training.description,
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedTraining(null);
    setNewTraining({
      title: '',
      instructor: '',
      type: '',
      duration: '',
      startDate: '',
      endDate: '',
      maxCapacity: '',
      description: '',
    });
  };

  const handleSaveTraining = () => {
    // در اینجا آموزش ذخیره می‌شود
    handleCloseDialog();
  };

  const getTypeColor = (type: string) => {
    const trainingType = trainingTypes.find(t => t.value === type);
    return trainingType ? trainingType.color : 'default';
  };

  const getTypeText = (type: string) => {
    const trainingType = trainingTypes.find(t => t.value === type);
    return trainingType ? trainingType.label : 'نامشخص';
  };

  const getStatusColor = (status: string) => {
    const trainingStatus = trainingStatuses.find(s => s.value === status);
    return trainingStatus ? trainingStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const trainingStatus = trainingStatuses.find(s => s.value === status);
    return trainingStatus ? trainingStatus.label : 'نامشخص';
  };

  const getProgressPercentage = (training: any) => {
    const completedModules = training.modules.filter((m: any) => m.completed).length;
    return (completedModules / training.modules.length) * 100;
  };

  const totalTrainings = mockTrainings.length;
  const activeTrainings = mockTrainings.filter(t => t.status === 'active').length;
  const completedTrainings = mockTrainings.filter(t => t.status === 'completed').length;
  const totalEnrolled = mockTrainings.reduce((sum, t) => sum + t.enrolledEmployees, 0);
  const averageRating = mockTrainings
    .filter(t => t.rating > 0)
    .reduce((sum, t) => sum + t.rating, 0) / mockTrainings.filter(t => t.rating > 0).length;

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <School style={{  mr: 1  }} />
            مدیریت آموزش
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<School />}
            onClick={handleAddTraining}
          >
            دوره جدید
          </Button>
        </div>

        {/* خلاصه آمار */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalTrainings}
              </Typography.Title>
              <Typography.Text>
                کل دوره‌ها
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {activeTrainings}
              </Typography.Title>
              <Typography.Text>
                دوره‌های فعال
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalEnrolled}
              </Typography.Title>
              <Typography.Text>
                شرکت‌کنندگان
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {averageRating.toFixed(1)}
              </Typography.Title>
              <Typography.Text>
                میانگین امتیاز
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        {/* لیست دوره‌های آموزشی */}
        {mockTrainings.map((training) => (
          <Accordion key={training.id} style={{  mb: 2  }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <div>
                <div>
                  <Typography.Title level={4}>{training.title}</Typography.Title>
                  <Typography.Text>
                    {training.instructor} • {training.duration}
                  </Typography.Text>
                </div>
                <div>
                  <Tag
                    label={getTypeText(training.type)}
                    color={getTypeColor(training.type) as any}
                    size="small"
                  />
                  <Tag
                    label={getStatusText(training.status)}
                    color={getStatusColor(training.status) as any}
                    size="small"
                  />
                  {training.rating > 0 && (
                    <Rating value={training.rating} readOnly size="small" />
                  )}
                </div>
              </div>
            </div>
            <AccordionDetails>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography.Text>
                    {training.description}
                  </Typography.Text>
                  
                  {/* پیشرفت دوره */}
                  <div style={{  mb: 2  }}>
                    <div>
                      <Typography.Text>پیشرفت دوره</Typography.Text>
                      <Typography.Text>
                        {getProgressPercentage(training).toFixed(0)}%
                      </Typography.Text>
                    </div>
                    <LinearProgress
                      variant="determinate"
                      value={getProgressPercentage(training)}
                      style={{  height: 8, borderRadius: 4  }}
                    />
                  </div>

                  {/* ماژول‌های دوره */}
                  <Typography variant="subtitle2" gutterBottom>
                    ماژول‌های دوره:
                  </Typography>
                  <div>
                    {training.modules.map((module: any, index: number) => (
                      <div>
                        <div>
                          {module.completed ? (
                            <CheckCircle color="success" fontSize="small" />
                          ) : (
                            <Assignment color="action" fontSize="small" />
                          )}
                          <Typography.Text>{module.title}</Typography.Text>
                        </div>
                        <Typography variant="caption" color="textSecondary">
                          {module.duration}
                        </Typography>
                      </div>
                    ))}
                  </div>
                </Col>
                
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Card style={{  p: 2  }}>
                    <Typography variant="subtitle2" gutterBottom>
                      اطلاعات دوره
                    </Typography>
                    <div>
                      <div>
                        <Typography.Text>شروع:</Typography.Text>
                        <Typography.Text>{training.startDate}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>پایان:</Typography.Text>
                        <Typography.Text>{training.endDate}</Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>ظرفیت:</Typography.Text>
                        <Typography.Text>
                          {training.enrolledEmployees}/{training.maxCapacity}
                        </Typography.Text>
                      </div>
                      <div>
                        <Typography.Text>نوع:</Typography.Text>
                        <Typography.Text>{getTypeText(training.type)}</Typography.Text>
                      </div>
                    </div>
                    
                    <div style={{  mt: 2  }}>
                      <Button
                        variant="outlined"
                        size="small"
                        fullWidth
                        onClick={() => handleEditTraining(training)}
                      >
                        ویرایش دوره
                      </Button>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
          </div>
        ))}

        {/* Dialog برای اضافه/ویرایش دوره */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedTraining ? 'ویرایش دوره' : 'افزودن دوره جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="عنوان دوره"
                  value={newTraining.title}
                  onChange={(e) => setNewTraining({ ...newTraining, title: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="مدرس"
                  value={newTraining.instructor}
                  onChange={(e) => setNewTraining({ ...newTraining, instructor: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>نوع دوره</span>
                  <Select
                    value={newTraining.type}
                    label="نوع دوره"
                    onChange={(e) => setNewTraining({ ...newTraining, type: e.target.value })}
                  >
                    {trainingTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="مدت زمان"
                  value={newTraining.duration}
                  onChange={(e) => setNewTraining({ ...newTraining, duration: e.target.value })}
                  helperText="مثال: 20 ساعت"
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ شروع"
                  value={newTraining.startDate}
                  onChange={(e) => setNewTraining({ ...newTraining, startDate: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ پایان"
                  value={newTraining.endDate}
                  onChange={(e) => setNewTraining({ ...newTraining, endDate: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="ظرفیت حداکثر"
                  type="number"
                  value={newTraining.maxCapacity}
                  onChange={(e) => setNewTraining({ ...newTraining, maxCapacity: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات دوره"
                  multiline
                  rows={3}
                  value={newTraining.description}
                  onChange={(e) => setNewTraining({ ...newTraining, description: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveTraining} variant="contained">
              {selectedTraining ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 