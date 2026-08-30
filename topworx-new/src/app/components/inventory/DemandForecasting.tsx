import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { FieldTimeOutlined, LineChartOutlined, PieChartOutlined, RiseOutlined } from '@ant-design/icons';

const mockForecasts = [
  {
    id: 1,
    productName: 'لپ‌تاپ Dell XPS 13',
    sku: 'LAP-001',
    currentStock: 25,
    forecastedDemand: 35,
    confidence: 85,
    nextMonth: 40,
    nextQuarter: 120,
    seasonality: 'high',
    trend: 'increasing',
    lastUpdated: '2024-04-22',
  },
  {
    id: 2,
    productName: 'ماوس بی‌سیم Logitech',
    sku: 'MOU-002',
    currentStock: 0,
    forecastedDemand: 50,
    confidence: 92,
    nextMonth: 60,
    nextQuarter: 180,
    seasonality: 'medium',
    trend: 'stable',
    lastUpdated: '2024-04-22',
  },
  {
    id: 3,
    productName: 'کیف چرمی مردانه',
    sku: 'BAG-003',
    currentStock: 8,
    forecastedDemand: 15,
    confidence: 78,
    nextMonth: 18,
    nextQuarter: 45,
    seasonality: 'low',
    trend: 'decreasing',
    lastUpdated: '2024-04-22',
  },
];

const forecastPeriods = [
  '1 ماه',
  '3 ماه',
  '6 ماه',
  '1 سال',
];

const confidenceLevels = [
  'کم (60-70%)',
  'متوسط (70-80%)',
  'بالا (80-90%)',
  'خیلی بالا (90%+)',
];

export const DemandForecasting: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedForecast, setSelectedForecast] = useState<any>(null);
  const [newForecast, setNewForecast] = useState({
    productName: '',
    sku: '',
    currentStock: '',
    forecastedDemand: '',
    confidence: '',
    period: '',
    notes: '',
  });

  const handleAddForecast = () => {
    setSelectedForecast(null);
    setOpenDialog(true);
  };

  const handleEditForecast = (forecast: any) => {
    setSelectedForecast(forecast);
    setNewForecast({
      productName: forecast.productName,
      sku: forecast.sku,
      currentStock: forecast.currentStock.toString(),
      forecastedDemand: forecast.forecastedDemand.toString(),
      confidence: forecast.confidence.toString(),
      period: '1 ماه',
      notes: '',
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedForecast(null);
    setNewForecast({
      productName: '',
      sku: '',
      currentStock: '',
      forecastedDemand: '',
      confidence: '',
      period: '',
      notes: '',
    });
  };

  const handleSaveForecast = () => {
    // در اینجا پیش‌بینی ذخیره می‌شود
    handleCloseDialog();
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return 'success';
      case 'stable':
        return 'info';
      case 'decreasing':
        return 'error';
      default:
        return 'default';
    }
  };

  const getTrendText = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return 'صعودی';
      case 'stable':
        return 'ثابت';
      case 'decreasing':
        return 'نزولی';
      default:
        return 'نامشخص';
    }
  };

  const getSeasonalityColor = (seasonality: string) => {
    switch (seasonality) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getSeasonalityText = (seasonality: string) => {
    switch (seasonality) {
      case 'high':
        return 'زیاد';
      case 'medium':
        return 'متوسط';
      case 'low':
        return 'کم';
      default:
        return 'نامشخص';
    }
  };

  const totalForecasted = mockForecasts.reduce((sum, f) => sum + f.forecastedDemand, 0);
  const averageConfidence = mockForecasts.reduce((sum, f) => sum + f.confidence, 0) / mockForecasts.length;
  const highConfidenceForecasts = mockForecasts.filter(f => f.confidence >= 80).length;

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <Analytics style={{  mr: 1  }} />
            پیش‌بینی تقاضا
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<TrendingUp />}
            onClick={handleAddForecast}
          >
            پیش‌بینی جدید
          </Button>
        </div>

        {/* خلاصه آمار */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {totalForecasted}
              </Typography.Title>
              <Typography.Text>
                کل تقاضای پیش‌بینی شده
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {averageConfidence.toFixed(1)}%
              </Typography.Title>
              <Typography.Text>
                میانگین اطمینان
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {highConfidenceForecasts}
              </Typography.Title>
              <Typography.Text>
                پیش‌بینی‌های با اطمینان بالا
              </Typography.Text>
            </Card>
          </Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                {mockForecasts.length}
              </Typography.Title>
              <Typography.Text>
                محصولات تحت پوشش
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
                <TableCell align="right">تقاضای پیش‌بینی شده</TableCell>
                <TableCell>اطمینان</TableCell>
                <TableCell>روند</TableCell>
                <TableCell>فصلی بودن</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockForecasts.map((forecast) => (
                <TableRow key={forecast.id}>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {forecast.productName}
                      </Typography.Text>
                      <Typography variant="caption" color="textSecondary">
                        {forecast.sku}
                      </Typography>
                    </div>
                  </TableCell>
                  <TableCell align="right">{forecast.currentStock}</TableCell>
                  <TableCell align="right">{forecast.forecastedDemand}</TableCell>
                  <TableCell>
                    <div>
                      <div style={{  width: '100%', mr: 1  }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={forecast.confidence} 
                          style={{  height: 6, borderRadius: 3  }}
                          color={forecast.confidence >= 80 ? 'success' : forecast.confidence >= 70 ? 'warning' : 'error'}
                        />
                      </div>
                      <Typography.Text>
                        {forecast.confidence}%
                      </Typography.Text>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={getTrendText(forecast.trend)}
                      color={getTrendColor(forecast.trend) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={getSeasonalityText(forecast.seasonality)}
                      color={getSeasonalityColor(forecast.seasonality) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <div>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleEditForecast(forecast)}
                      >
                        <ShowChart style={{  fontSize: 16  }} />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Dialog برای اضافه/ویرایش پیش‌بینی */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedForecast ? 'ویرایش پیش‌بینی' : 'افزودن پیش‌بینی جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام محصول"
                  value={newForecast.productName}
                  onChange={(e) => setNewForecast({ ...newForecast, productName: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="SKU"
                  value={newForecast.sku}
                  onChange={(e) => setNewForecast({ ...newForecast, sku: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="موجودی فعلی"
                  type="number"
                  value={newForecast.currentStock}
                  onChange={(e) => setNewForecast({ ...newForecast, currentStock: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تقاضای پیش‌بینی شده"
                  type="number"
                  value={newForecast.forecastedDemand}
                  onChange={(e) => setNewForecast({ ...newForecast, forecastedDemand: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="سطح اطمینان (%)"
                  type="number"
                  value={newForecast.confidence}
                  onChange={(e) => setNewForecast({ ...newForecast, confidence: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>دوره پیش‌بینی</span>
                  <Select
                    value={newForecast.period}
                    label="دوره پیش‌بینی"
                    onChange={(e) => setNewForecast({ ...newForecast, period: e.target.value })}
                  >
                    {forecastPeriods.map((period) => (
                      <MenuItem key={period} value={period}>
                        {period}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newForecast.notes}
                  onChange={(e) => setNewForecast({ ...newForecast, notes: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveForecast} variant="contained">
              {selectedForecast ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 