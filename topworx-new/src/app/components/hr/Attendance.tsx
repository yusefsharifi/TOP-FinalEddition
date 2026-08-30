import React, { useState } from 'react';
import { Alert, Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { CheckCircleOutlined, ClockCircleOutlined, CloseOutlined, EditOutlined, PlusOutlined, UserOutlined, WarningOutlined } from '@ant-design/icons';

const mockAttendance = [
  {
    id: 1,
    employeeName: 'علی احمدی',
    employeeId: 'EMP001',
    date: '1402/11/15',
    checkIn: '08:30',
    checkOut: '17:30',
    totalHours: 9,
    status: 'present',
    overtime: 1,
    lateMinutes: 0,
    earlyLeave: 0,
    notes: '',
  },
  {
    id: 2,
    employeeName: 'فاطمه محمدی',
    employeeId: 'EMP002',
    date: '1402/11/15',
    checkIn: '08:45',
    checkOut: '17:15',
    totalHours: 8.5,
    status: 'present',
    overtime: 0,
    lateMinutes: 15,
    earlyLeave: 15,
    notes: 'تأخیر به دلیل ترافیک',
  },
  {
    id: 3,
    employeeName: 'محمد رضایی',
    employeeId: 'EMP003',
    date: '1402/11/15',
    checkIn: '09:00',
    checkOut: '18:00',
    totalHours: 9,
    status: 'present',
    overtime: 1,
    lateMinutes: 30,
    earlyLeave: 0,
    notes: '',
  },
  {
    id: 4,
    employeeName: 'زهرا کریمی',
    employeeId: 'EMP004',
    date: '1402/11/15',
    checkIn: '',
    checkOut: '',
    totalHours: 0,
    status: 'absent',
    overtime: 0,
    lateMinutes: 0,
    earlyLeave: 0,
    notes: 'مرخصی استعلاجی',
  },
];

const attendanceStatuses = [
  { value: 'present', label: 'حاضر', color: 'success' },
  { value: 'absent', label: 'غایب', color: 'error' },
  { value: 'late', label: 'تأخیر', color: 'warning' },
  { value: 'half-day', label: 'نیم روز', color: 'info' },
  { value: 'leave', label: 'مرخصی', color: 'default' },
];

const departments = [
  'توسعه نرم‌افزار',
  'طراحی',
  'مدیریت',
  'فروش',
  'پشتیبانی',
  'مالی',
];

export const Attendance: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<any>(null);
  const [newRecord, setNewRecord] = useState({
    employeeId: '',
    date: '',
    checkIn: '',
    checkOut: '',
    status: '',
    notes: '',
  });

  const handleAddRecord = () => {
    setSelectedRecord(null);
    setOpenDialog(true);
  };

  const handleEditRecord = (record: any) => {
    setSelectedRecord(record);
    setNewRecord({
      employeeId: record.employeeId,
      date: record.date,
      checkIn: record.checkIn,
      checkOut: record.checkOut,
      status: record.status,
      notes: record.notes,
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedRecord(null);
    setNewRecord({
      employeeId: '',
      date: '',
      checkIn: '',
      checkOut: '',
      status: '',
      notes: '',
    });
  };

  const handleSaveRecord = () => {
    // در اینجا رکورد حضور ذخیره می‌شود
    handleCloseDialog();
  };

  const getStatusColor = (status: string) => {
    const attendanceStatus = attendanceStatuses.find(s => s.value === status);
    return attendanceStatus ? attendanceStatus.color : 'default';
  };

  const getStatusText = (status: string) => {
    const attendanceStatus = attendanceStatuses.find(s => s.value === status);
    return attendanceStatus ? attendanceStatus.label : 'نامشخص';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'present':
        return <CheckCircle color="success" />;
      case 'absent':
        return <Cancel color="error" />;
      case 'late':
        return <Warning color="warning" />;
      case 'half-day':
        return <Schedule color="info" />;
      default:
        return <Person color="action" />;
    }
  };

  const totalEmployees = mockAttendance.length;
  const presentEmployees = mockAttendance.filter(a => a.status === 'present').length;
  const absentEmployees = mockAttendance.filter(a => a.status === 'absent').length;
  const lateEmployees = mockAttendance.filter(a => a.lateMinutes > 0).length;
  const totalOvertime = mockAttendance.reduce((sum, a) => sum + a.overtime, 0);

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <AccessTime style={{  mr: 1  }} />
            مدیریت حضور و غیاب
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddRecord}
          >
            ثبت حضور جدید
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
                {presentEmployees}
              </Typography.Title>
              <Typography.Text>
                حاضر
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {absentEmployees}
              </Typography.Title>
              <Typography.Text>
                غایب
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalOvertime}
              </Typography.Title>
              <Typography.Text>
                ساعت اضافه‌کاری
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        {/* هشدار تأخیر */}
        {lateEmployees > 0 && (
          <Alert severity="warning" style={{  mb: 3  }}>
            {lateEmployees} کارمند امروز تأخیر داشته‌اند.
          </Alert>
        )}

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>کارمند</TableCell>
                <TableCell>تاریخ</TableCell>
                <TableCell>ورود</TableCell>
                <TableCell>خروج</TableCell>
                <TableCell>ساعت کاری</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>تأخیر/زودترک</TableCell>
                <TableCell>اضافه‌کاری</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockAttendance.map((record) => (
                <TableRow key={record.id}>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {record.employeeName}
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {record.employeeId}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell>{record.date}</TableCell>
                  <TableCell>
                    {record.checkIn ? (
                      <Typography.Text>
                        {record.checkIn}
                      </Typography.Text>
                    ) : (
                      <Typography.Text>
                        -
                      </Typography.Text>
                    )}
                  </TableCell>
                  <TableCell>
                    {record.checkOut ? (
                      <Typography.Text>
                        {record.checkOut}
                      </Typography.Text>
                    ) : (
                      <Typography.Text>
                        -
                      </Typography.Text>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {record.totalHours} ساعت
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <div>
                      {getStatusIcon(record.status)}
                      <Tag
                        label={getStatusText(record.status)}
                        color={getStatusColor(record.status) as any}
                        size="small"
                      />
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      {record.lateMinutes > 0 && (
                        <Typography variant="caption" color="warning.main" display="block">
                          تأخیر: {record.lateMinutes} دقیقه
                        </Typography>
                      )}
                      {record.earlyLeave > 0 && (
                        <Typography variant="caption" color="info.main" display="block">
                          زودترک: {record.earlyLeave} دقیقه
                        </Typography>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    {record.overtime > 0 ? (
                      <Typography.Text>
                        {record.overtime} ساعت
                      </Typography.Text>
                    ) : (
                      <Typography.Text>
                        -
                      </Typography.Text>
                    )}
                  </TableCell>
                  <TableCell>
                    <Button type="text" size="small" onClick={() => handleEditRecord(record)}
                    >
                      <Edit />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* تقویم حضور */}
        <div style={{  mt: 3  }}>
          <Typography.Title level={4}>
            تقویم حضور
          </Typography.Title>
          <Card style={{  p: 2  }}>
            <Typography.Text>
              تقویم تعاملی برای مشاهده حضور کارکنان در روزهای مختلف
            </Typography.Text>
            {/* در اینجا می‌توان تقویم تعاملی اضافه کرد */}
          </Card>
        </div>

        {/* Dialog برای اضافه/ویرایش رکورد حضور */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedRecord ? 'ویرایش حضور' : 'ثبت حضور جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="کد کارمند"
                  value={newRecord.employeeId}
                  onChange={(e) => setNewRecord({ ...newRecord, employeeId: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ"
                  type="date"
                  value={newRecord.date}
                  onChange={(e) => setNewRecord({ ...newRecord, date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="ساعت ورود"
                  type="time"
                  value={newRecord.checkIn}
                  onChange={(e) => setNewRecord({ ...newRecord, checkIn: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="ساعت خروج"
                  type="time"
                  value={newRecord.checkOut}
                  onChange={(e) => setNewRecord({ ...newRecord, checkOut: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>وضعیت</span>
                  <Select
                    value={newRecord.status}
                    label="وضعیت"
                    onChange={(e) => setNewRecord({ ...newRecord, status: e.target.value })}
                  >
                    {attendanceStatuses.map((status) => (
                      <MenuItem key={status.value} value={status.value}>
                        {status.label}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="یادداشت"
                  multiline
                  rows={3}
                  value={newRecord.notes}
                  onChange={(e) => setNewRecord({ ...newRecord, notes: e.target.value })}
                  placeholder="توضیحات اضافی..."
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveRecord} variant="contained">
              {selectedRecord ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 