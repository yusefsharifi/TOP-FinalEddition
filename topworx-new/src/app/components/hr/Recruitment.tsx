import React, { useState } from 'react';
import { Alert, Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { CheckCircleOutlined, CheckSquareOutlined, ClockCircleOutlined, CloseOutlined, InterviewOutlined, ToolOutlined, UserAddOutlined } from '@ant-design/icons';

const mockCandidates = [
  {
    id: 1,
    name: 'علی احمدی',
    position: 'برنامه‌نویس React',
    email: 'ali.ahmadi@example.com',
    phone: '09123456789',
    experience: '3 سال',
    education: 'کارشناسی مهندسی نرم‌افزار',
    status: 'interview',
    appliedDate: '1402/10/15',
    interviewDate: '1402/10/20',
    skills: ['React', 'TypeScript', 'Node.js'],
    rating: 4.2,
    notes: 'تجربه خوب در پروژه‌های مشابه',
  },
  {
    id: 2,
    name: 'فاطمه محمدی',
    position: 'طراح UI/UX',
    email: 'fateme.mohammadi@example.com',
    phone: '09187654321',
    experience: '2 سال',
    education: 'کارشناسی طراحی گرافیک',
    status: 'hired',
    appliedDate: '1402/10/10',
    interviewDate: '1402/10/18',
    skills: ['Figma', 'Adobe XD', 'Photoshop'],
    rating: 4.5,
    notes: 'نمونه کارهای عالی',
  },
  {
    id: 3,
    name: 'محمد رضایی',
    position: 'مدیر پروژه',
    email: 'mohammad.rezaei@example.com',
    phone: '09111111111',
    experience: '5 سال',
    education: 'کارشناسی ارشد مدیریت',
    status: 'rejected',
    appliedDate: '1402/10/12',
    interviewDate: '1402/10/22',
    skills: ['PMP', 'Agile', 'Scrum'],
    rating: 3.8,
    notes: 'تجربه کافی ندارد',
  },
];

const jobPositions = [
  { value: 'react-developer', label: 'برنامه‌نویس React' },
  { value: 'ui-ux-designer', label: 'طراح UI/UX' },
  { value: 'project-manager', label: 'مدیر پروژه' },
  { value: 'devops-engineer', label: 'مهندس DevOps' },
  { value: 'data-scientist', label: 'دانشمند داده' },
  { value: 'sales-manager', label: 'مدیر فروش' },
];

const candidateStatuses = [
  { value: 'applied', label: 'درخواست شده', color: 'info' },
  { value: 'screening', label: 'بررسی اولیه', color: 'warning' },
  { value: 'interview', label: 'مصاحبه', color: 'primary' },
  { value: 'technical', label: 'تست فنی', color: 'secondary' },
  { value: 'final', label: 'مصاحبه نهایی', color: 'info' },
  { value: 'hired', label: 'استخدام شده', color: 'success' },
  { value: 'rejected', label: 'رد شده', color: 'error' },
];

const recruitmentSteps = [
  'درخواست',
  'بررسی اولیه',
  'مصاحبه',
  'تست فنی',
  'مصاحبه نهایی',
  'استخدام',
];

export const Recruitment: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [newCandidate, setNewCandidate] = useState({
    name: '',
    position: '',
    email: '',
    phone: '',
    experience: '',
    education: '',
    skills: '',
    notes: '',
  });

  const handleAddCandidate = () => {
    setSelectedCandidate(null);
    setOpenDialog(true);
  };

  const handleEditCandidate = (candidate: any) => {
    setSelectedCandidate(candidate);
    setNewCandidate({
      name: candidate.name,
      position: candidate.position,
      email: candidate.email,
      phone: candidate.phone,
      experience: candidate.experience,
      education: candidate.education,
      skills: candidate.skills.join(', '),
      notes: candidate.notes,
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedCandidate(null);
    setNewCandidate({
      name: '',
      position: '',
      email: '',
      phone: '',
      experience: '',
      education: '',
      skills: '',
      notes: '',
    });
  };

  const handleSaveCandidate = () => {
    // در اینجا کاندید ذخیره می‌شود
    handleCloseDialog();
  };

  const getStatusColor = (status: string) => {
    const candidateStatus = candidateStatuses.find(s => s.value === status);
    return candidateStatus ? candidateStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const candidateStatus = candidateStatuses.find(s => s.value === status);
    return candidateStatus ? candidateStatus.label : 'نامشخص';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'hired':
        return <CheckCircle color="success" />;
      case 'rejected':
        return <Cancel color="error" />;
      case 'interview':
        return <Interview color="primary" />;
      default:
        return <Pending color="warning" />;
    }
  };

  const getStepIndex = (status: string) => {
    switch (status) {
      case 'applied':
        return 0;
      case 'screening':
        return 1;
      case 'interview':
        return 2;
      case 'technical':
        return 3;
      case 'final':
        return 4;
      case 'hired':
        return 5;
      default:
        return 0;
    }
  };

  const totalCandidates = mockCandidates.length;
  const hiredCandidates = mockCandidates.filter(c => c.status === 'hired').length;
  const interviewCandidates = mockCandidates.filter(c => c.status === 'interview').length;
  const rejectedCandidates = mockCandidates.filter(c => c.status === 'rejected').length;
  const averageRating = mockCandidates.reduce((sum, c) => sum + c.rating, 0) / totalCandidates;

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <PersonAdd style={{  mr: 1  }} />
            مدیریت استخدام
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<PersonAdd />}
            onClick={handleAddCandidate}
          >
            کاندید جدید
          </Button>
        </div>

        {/* خلاصه آمار */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalCandidates}
              </Typography.Title>
              <Typography.Text>
                کل کاندیدها
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {hiredCandidates}
              </Typography.Title>
              <Typography.Text>
                استخدام شده
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {interviewCandidates}
              </Typography.Title>
              <Typography.Text>
                در حال مصاحبه
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

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام</TableCell>
                <TableCell>موقعیت</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>امتیاز</TableCell>
                <TableCell>تاریخ درخواست</TableCell>
                <TableCell>مهارت‌ها</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockCandidates.map((candidate) => (
                <TableRow key={candidate.id}>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {candidate.name}
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {candidate.email}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell>{candidate.position}</TableCell>
                  <TableCell>
                    <div>
                      {getStatusIcon(candidate.status)}
                      <Tag
                        label={getStatusText(candidate.status)}
                        color={getStatusColor(candidate.status) as any}
                        size="small"
                      />
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {candidate.rating}/5
                      </Typography.Text>
                      <LinearProgress
                        variant="determinate"
                        value={candidate.rating * 20}
                        style={{  width: 50  }}
                      />
                    </div>
                  </TableCell>
                  <TableCell>{candidate.appliedDate}</TableCell>
                  <TableCell>
                    <div>
                      {candidate.skills.slice(0, 2).map((skill, index) => (
                        <Tag
                          key={index}
                          label={skill}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                      {candidate.skills.length > 2 && (
                        <Tag
                          label={`+${candidate.skills.length - 2}`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleEditCandidate(candidate)}
                      >
                        <Assignment />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleEditCandidate(candidate)}
                      >
                        <CheckCircle />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* نمایش روند استخدام */}
        <div style={{  mt: 3  }}>
          <Typography.Title level={4}>
            روند استخدام
          </Typography.Title>
          <Stepper activeStep={2} orientation="horizontal">
            {recruitmentSteps.map((step, index) => (
              <Step key={step}>
                <StepLabel>{step}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </div>

        {/* Dialog برای اضافه/ویرایش کاندید */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedCandidate ? 'ویرایش کاندید' : 'افزودن کاندید جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام و نام خانوادگی"
                  value={newCandidate.name}
                  onChange={(e) => setNewCandidate({ ...newCandidate, name: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>موقعیت شغلی</span>
                  <Select
                    value={newCandidate.position}
                    label="موقعیت شغلی"
                    onChange={(e) => setNewCandidate({ ...newCandidate, position: e.target.value })}
                  >
                    {jobPositions.map((position) => (
                      <MenuItem key={position.value} value={position.value}>
                        {position.label}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="ایمیل"
                  type="email"
                  value={newCandidate.email}
                  onChange={(e) => setNewCandidate({ ...newCandidate, email: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="شماره تماس"
                  value={newCandidate.phone}
                  onChange={(e) => setNewCandidate({ ...newCandidate, phone: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="سابقه کاری"
                  value={newCandidate.experience}
                  onChange={(e) => setNewCandidate({ ...newCandidate, experience: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تحصیلات"
                  value={newCandidate.education}
                  onChange={(e) => setNewCandidate({ ...newCandidate, education: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="مهارت‌ها (با کاما جدا کنید)"
                  value={newCandidate.skills}
                  onChange={(e) => setNewCandidate({ ...newCandidate, skills: e.target.value })}
                  helperText="مثال: React, TypeScript, Node.js"
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="یادداشت‌ها"
                  multiline
                  rows={3}
                  value={newCandidate.notes}
                  onChange={(e) => setNewCandidate({ ...newCandidate, notes: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveCandidate} variant="contained">
              {selectedCandidate ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 