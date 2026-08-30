import React, { useState } from 'react';
import { Alert, Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { BulbOutlined, CheckCircleOutlined, EditOutlined, OptimizationOutlined, RiseOutlined, WarningOutlined } from '@ant-design/icons';

const mockOptimizations = [
  {
    id: 1,
    productName: 'لپ‌تاپ Dell XPS 13',
    sku: 'LAP-001',
    currentStock: 25,
    recommendedStock: 35,
    optimizationType: 'increase',
    reason: 'تقاضای فصلی بالا',
    potentialSavings: 5000000,
    implementationTime: '1 هفته',
    priority: 'high',
    status: 'pending',
  },
  {
    id: 2,
    productName: 'ماوس بی‌سیم Logitech',
    sku: 'MOU-002',
    currentStock: 0,
    recommendedStock: 50,
    optimizationType: 'reorder',
    reason: 'موجودی تمام شده',
    potentialSavings: 2000000,
    implementationTime: '2 هفته',
    priority: 'critical',
    status: 'approved',
  },
  {
    id: 3,
    productName: 'کیف چرمی مردانه',
    sku: 'BAG-003',
    currentStock: 8,
    recommendedStock: 5,
    optimizationType: 'decrease',
    reason: 'موجودی بیش از حد',
    potentialSavings: 3000000,
    implementationTime: '3 روز',
    priority: 'medium',
    status: 'implemented',
  },
];

const optimizationTypes = [
  { value: 'increase', label: 'افزایش موجودی', color: 'success' },
  { value: 'decrease', label: 'کاهش موجودی', color: 'warning' },
  { value: 'reorder', label: 'سفارش مجدد', color: 'error' },
  { value: 'transfer', label: 'انتقال', color: 'info' },
];

const priorityLevels = [
  { value: 'critical', label: 'بحرانی', color: 'error' },
  { value: 'high', label: 'بالا', color: 'warning' },
  { value: 'medium', label: 'متوسط', color: 'info' },
  { value: 'low', label: 'کم', color: 'success' },
];

export const InventoryOptimization: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedOptimization, setSelectedOptimization] = useState<any>(null);
  const [newOptimization, setNewOptimization] = useState({
    productName: '',
    sku: '',
    currentStock: '',
    recommendedStock: '',
    optimizationType: '',
    reason: '',
    potentialSavings: '',
    implementationTime: '',
    priority: '',
    notes: '',
  });

  const handleAddOptimization = () => {
    setSelectedOptimization(null);
    setOpenDialog(true);
  };

  const handleEditOptimization = (optimization: any) => {
    setSelectedOptimization(optimization);
    setNewOptimization({
      productName: optimization.productName,
      sku: optimization.sku,
      currentStock: optimization.currentStock.toString(),
      recommendedStock: optimization.recommendedStock.toString(),
      optimizationType: optimization.optimizationType,
      reason: optimization.reason,
      potentialSavings: optimization.potentialSavings.toString(),
      implementationTime: optimization.implementationTime,
      priority: optimization.priority,
      notes: '',
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedOptimization(null);
    setNewOptimization({
      productName: '',
      sku: '',
      currentStock: '',
      recommendedStock: '',
      optimizationType: '',
      reason: '',
      potentialSavings: '',
      implementationTime: '',
      priority: '',
      notes: '',
    });
  };

  const handleSaveOptimization = () => {
    // در اینجا بهینه‌سازی ذخیره می‌شود
    handleCloseDialog();
  };

  const getOptimizationTypeColor = (type: string) => {
    const optimizationType = optimizationTypes.find(t => t.value === type);
    return optimizationType ? optimizationType.color : 'default';
  };

  const getOptimizationTypeText = (type: string) => {
    const optimizationType = optimizationTypes.find(t => t.value === type);
    return optimizationType ? optimizationType.label : 'نامشخص';
  };

  const getPriorityColor = (priority: string) => {
    const priorityLevel = priorityLevels.find(p => p.value === priority);
    return priorityLevel ? priorityLevel.color : 'default';
  };

  const getPriorityText = (priority: string) => {
    const priorityLevel = priorityLevels.find(p => p.value === priority);
    return priorityLevel ? priorityLevel.label : 'نامشخص';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'pending':
        return 'warning';
      case 'implemented':
        return 'info';
      case 'rejected':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'approved':
        return 'تأیید شده';
      case 'pending':
        return 'در انتظار';
      case 'implemented':
        return 'پیاده‌سازی شده';
      case 'rejected':
        return 'رد شده';
      default:
        return 'نامشخص';
    }
  };

  const totalSavings = mockOptimizations.reduce((sum, opt) => sum + opt.potentialSavings, 0);
  const pendingOptimizations = mockOptimizations.filter(opt => opt.status === 'pending').length;
  const implementedOptimizations = mockOptimizations.filter(opt => opt.status === 'implemented').length;
  const criticalOptimizations = mockOptimizations.filter(opt => opt.priority === 'critical').length;

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <Optimization style={{  mr: 1  }} />
            بهینه‌سازی موجودی
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<AutoFixHigh />}
            onClick={handleAddOptimization}
          >
            بهینه‌سازی جدید
          </Button>
        </div>

        {/* هشدارهای بحرانی */}
        {criticalOptimizations > 0 && (
          <Alert severity="error" style={{  mb: 3  }}>
            {criticalOptimizations} بهینه‌سازی بحرانی نیاز به توجه فوری دارد!
          </Alert>
        )}

        {/* خلاصه آمار */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalSavings.toLocaleString()} تومان
              </Typography.Title>
              <Typography.Text>
                کل صرفه‌جویی بالقوه
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {pendingOptimizations}
              </Typography.Title>
              <Typography.Text>
                در انتظار تأیید
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {implementedOptimizations}
              </Typography.Title>
              <Typography.Text>
                پیاده‌سازی شده
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {criticalOptimizations}
              </Typography.Title>
              <Typography.Text>
                بحرانی
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>محصول</TableCell>
                <TableCell align="right">موجودی فعلی</TableCell>
                <TableCell align="right">موجودی پیشنهادی</TableCell>
                <TableCell>نوع بهینه‌سازی</TableCell>
                <TableCell>دلیل</TableCell>
                <TableCell align="right">صرفه‌جویی</TableCell>
                <TableCell>اولویت</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockOptimizations.map((optimization) => (
                <TableRow key={optimization.id}>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {optimization.productName}
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {optimization.sku}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell align="right">{optimization.currentStock}</TableCell>
                  <TableCell align="right">{optimization.recommendedStock}</TableCell>
                  <TableCell>
                    <Tag
                      label={getOptimizationTypeText(optimization.optimizationType)}
                      color={getOptimizationTypeColor(optimization.optimizationType) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{optimization.reason}</TableCell>
                  <TableCell align="right">
                    {optimization.potentialSavings.toLocaleString()} تومان
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={getPriorityText(optimization.priority)}
                      color={getPriorityColor(optimization.priority) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={getStatusText(optimization.status)}
                      color={getStatusColor(optimization.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleEditOptimization(optimization)}
                      >
                        <Lightbulb />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleEditOptimization(optimization)}
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

        {/* Dialog برای اضافه/ویرایش بهینه‌سازی */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedOptimization ? 'ویرایش بهینه‌سازی' : 'افزودن بهینه‌سازی جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام محصول"
                  value={newOptimization.productName}
                  onChange={(e) => setNewOptimization({ ...newOptimization, productName: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="SKU"
                  value={newOptimization.sku}
                  onChange={(e) => setNewOptimization({ ...newOptimization, sku: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="موجودی فعلی"
                  type="number"
                  value={newOptimization.currentStock}
                  onChange={(e) => setNewOptimization({ ...newOptimization, currentStock: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="موجودی پیشنهادی"
                  type="number"
                  value={newOptimization.recommendedStock}
                  onChange={(e) => setNewOptimization({ ...newOptimization, recommendedStock: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>نوع بهینه‌سازی</span>
                  <Select
                    value={newOptimization.optimizationType}
                    label="نوع بهینه‌سازی"
                    onChange={(e) => setNewOptimization({ ...newOptimization, optimizationType: e.target.value })}
                  >
                    {optimizationTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>اولویت</span>
                  <Select
                    value={newOptimization.priority}
                    label="اولویت"
                    onChange={(e) => setNewOptimization({ ...newOptimization, priority: e.target.value })}
                  >
                    {priorityLevels.map((priority) => (
                      <MenuItem key={priority.value} value={priority.value}>
                        {priority.label}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="صرفه‌جویی بالقوه"
                  type="number"
                  value={newOptimization.potentialSavings}
                  onChange={(e) => setNewOptimization({ ...newOptimization, potentialSavings: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="زمان پیاده‌سازی"
                  value={newOptimization.implementationTime}
                  onChange={(e) => setNewOptimization({ ...newOptimization, implementationTime: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="دلیل بهینه‌سازی"
                  value={newOptimization.reason}
                  onChange={(e) => setNewOptimization({ ...newOptimization, reason: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newOptimization.notes}
                  onChange={(e) => setNewOptimization({ ...newOptimization, notes: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveOptimization} variant="contained">
              {selectedOptimization ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 