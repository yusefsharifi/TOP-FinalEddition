import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Spin, Table, Tabs, Tag, Tooltip, Typography } from 'antd';
import { BankOutlined as AccountBalanceIcon, DeleteOutlined as DeleteIcon, DownloadOutlined as DownloadIcon, EditOutlined as EditIcon, EnvironmentOutlined as LocationIcon, EyeOutlined as VisibilityIcon, FallOutlined as TrendingDownIcon, PlusOutlined as AddIcon, ReloadOutlined as RefreshIcon, RiseOutlined as TrendingUpIcon, ToolOutlined as BuildIcon } from '@ant-design/icons';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { FixedAsset, AssetDepreciation } from '../../../types/accounting';
import { accountingApi } from '../../../api/accounting';

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
      id={`assets-tabpanel-${index}`}
      aria-labelledby={`assets-tab-${index}`}
      {...other}
    >
      {value === index && <div style={{  py: 3  }}>{children}</div>}
    </div>
  );
}

export const FixedAssetsManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [assets, setAssets] = useState<FixedAsset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<FixedAsset | null>(null);
  const [assetDepreciations, setAssetDepreciations] = useState<AssetDepreciation[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [depreciationData, setDepreciationData] = useState<any[]>([]);
  const [categoryData, setCategoryData] = useState<any[]>([]);

  const loadAssets = async () => {
    try {
      setLoading(true);
      const response = await accountingApi.fixedAssets.getAll({ limit: 100 });
      setAssets(response.data);

      // Mock data for charts
      setDepreciationData([
        { month: 'فروردین', depreciation: 150000, accumulated: 150000 },
        { month: 'اردیبهشت', depreciation: 150000, accumulated: 300000 },
        { month: 'خرداد', depreciation: 150000, accumulated: 450000 },
        { month: 'تیر', depreciation: 150000, accumulated: 600000 },
        { month: 'مرداد', depreciation: 150000, accumulated: 750000 },
        { month: 'شهریور', depreciation: 150000, accumulated: 900000 },
      ]);

      setCategoryData([
        { category: 'ساختمان', value: 3000000, percentage: 50 },
        { category: 'ماشین‌آلات', value: 1800000, percentage: 30 },
        { category: 'وسایل نقلیه', value: 600000, percentage: 10 },
        { category: 'تجهیزات اداری', value: 300000, percentage: 5 },
        { category: 'سایر', value: 300000, percentage: 5 },
      ]);
    } catch (error) {
      console.error('Error loading assets:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssets();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleViewAsset = async (asset: FixedAsset) => {
    try {
      const depreciationsResponse = await accountingApi.fixedAssets.getDepreciation(asset.id, {});
      setAssetDepreciations(depreciationsResponse.data);
      setSelectedAsset(asset);
      setDialogOpen(true);
    } catch (error) {
      console.error('Error loading asset depreciations:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'disposed': return 'error';
      case 'sold': return 'warning';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'فعال';
      case 'disposed': return 'از رده خارج';
      case 'sold': return 'فروخته شده';
      default: return status;
    }
  };

  const getDepreciationMethodLabel = (method: string) => {
    switch (method) {
      case 'straight_line': return 'خط مستقیم';
      case 'declining_balance': return 'تراز نزولی';
      case 'sum_of_years': return 'مجموع سنوات';
      default: return method;
    }
  };

  const calculateDepreciationRate = (asset: FixedAsset) => {
    return ((asset.purchase_cost - asset.salvage_value) / asset.useful_life) / asset.purchase_cost * 100;
  };

  if (loading) {
    return (
      <div style={{  display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400  }}>
        <Spin />
      </div>
    );
  }

  const totalAssets = assets.reduce((sum, asset) => sum + asset.current_value, 0);
  const totalDepreciation = assets.reduce((sum, asset) => sum + asset.accumulated_depreciation, 0);
  const netAssets = totalAssets - totalDepreciation;

  return (
    <div style={{  p: 3  }}>
      {/* Header */}
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <Typography.Title level={2}>
          مدیریت دارایی‌های ثابت
        </Typography.Title>
        <div style={{  display: 'flex', gap: 1  }}>
          <Tooltip title="بارگذاری مجدد">
            <Button type="text" onClick={loadAssets} disabled={loading}>
              <RefreshIcon />
            </Button>
          </Tooltip>
          <Button variant="contained" startIcon={<AddIcon />}>
            افزودن دارایی جدید
          </Button>
        </div>
      </div>

      {/* Assets Overview Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div style={{  display: 'flex', alignItems: 'center', gap: 2  }}>
                <AccountBalanceIcon style={{  fontSize: 32, color: 'primary.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {assets.length}
                  </Typography.Title>
                  <Typography.Text>
                    کل دارایی‌ها
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
                    {formatCurrency(totalAssets)}
                  </Typography.Title>
                  <Typography.Text>
                    ارزش کل دارایی‌ها
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
                    {formatCurrency(totalDepreciation)}
                  </Typography.Title>
                  <Typography.Text>
                    استهلاک انباشته
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
                <BuildIcon style={{  fontSize: 32, color: 'info.main'  }} />
                <div>
                  <Typography.Title level={2}>
                    {formatCurrency(netAssets)}
                  </Typography.Title>
                  <Typography.Text>
                    ارزش خالص دارایی‌ها
                  </Typography.Text>
                </div>
              </div>
            </div>
          </Card>
      </Col>

      {/* Depreciation Chart */}
      <Card style={{  p: 3, mb: 3  }}>
        <Typography.Title level={4}>
          روند استهلاک
        </Typography.Title>
        <div style={{  height: 400  }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={depreciationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <RechartsTooltip formatter={(value) => formatCurrency(Number(value))} />
              <Legend />
              <Line type="monotone" dataKey="depreciation" stroke="#8884d8" name="استهلاک ماهانه" />
              <Line type="monotone" dataKey="accumulated" stroke="#82ca9d" name="استهلاک انباشته" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Asset Categories Distribution */}
      <Card style={{  p: 3, mb: 3  }}>
        <Typography.Title level={4}>
          توزیع دارایی‌ها بر اساس دسته‌بندی
        </Typography.Title>
        <div style={{  height: 400  }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'][index]} />
                ))}
              </Pie>
              <RechartsTooltip formatter={(value) => formatCurrency(Number(value))} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Tabs */}
      <Card style={{  width: '100%'  }}>
        <div style={{  borderBottom: 1, borderColor: 'divider'  }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="assets tabs">
            <Tab label="لیست دارایی‌ها" />
            <Tab label="گزارش استهلاک" />
          </Tabs>
        </div>

        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>کد</TableCell>
                  <TableCell>نام دارایی</TableCell>
                  <TableCell>دسته‌بندی</TableCell>
                  <TableCell>محل</TableCell>
                  <TableCell align="right">ارزش خرید</TableCell>
                  <TableCell align="right">ارزش فعلی</TableCell>
                  <TableCell align="right">استهلاک انباشته</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell align="center">عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assets.map((asset) => (
                  <TableRow key={asset.id} hover>
                    <TableCell>
                      <Typography.Text>
                        {asset.code}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {asset.name}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag label={asset.category} size="small" />
                    </TableCell>
                    <TableCell>
                      <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
                        <LocationIcon style={{  fontSize: 16, color: 'text.secondary'  }} />
                        <Typography.Text>
                          {asset.location || '-'}
                        </Typography.Text>
                      </div>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(asset.purchase_cost)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(asset.current_value)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(asset.accumulated_depreciation)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Tag
                        label={getStatusLabel(asset.status)}
                        color={getStatusColor(asset.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <div style={{  display: 'flex', gap: 1, justifyContent: 'center'  }}>
                        <Tooltip title="مشاهده جزئیات">
                          <Button type="text" size="small" onClick={() => handleViewAsset(asset)}
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
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>دارایی</TableCell>
                  <TableCell>دوره</TableCell>
                  <TableCell align="right">مبلغ استهلاک</TableCell>
                  <TableCell align="right">استهلاک انباشته</TableCell>
                  <TableCell align="right">ارزش دفتری</TableCell>
                  <TableCell>تاریخ</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assetDepreciations.map((depreciation) => (
                  <TableRow key={depreciation.id} hover>
                    <TableCell>
                      <Typography.Text>
                        {depreciation.asset_name}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {formatDate(depreciation.period_start)} - {formatDate(depreciation.period_end)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(depreciation.depreciation_amount)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(depreciation.accumulated_depreciation)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell align="right">
                      <Typography.Text>
                        {formatCurrency(depreciation.book_value)}
                      </Typography.Text>
                    </TableCell>
                    <TableCell>
                      <Typography.Text>
                        {formatDate(depreciation.created_at)}
                      </Typography.Text>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabPanel>
      </Card>

      {/* Asset Details Dialog */}
      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          <Typography.Title level={4}>
            جزئیات دارایی: {selectedAsset?.name}
          </Typography.Title>
        </div>
        <div>
          {selectedAsset && (
            <div>
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    کد دارایی
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedAsset.code}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    دسته‌بندی
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedAsset.category}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    تاریخ خرید
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatDate(selectedAsset.purchase_date)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    عمر مفید
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedAsset.useful_life} سال
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    ارزش خرید
                  </Typography>
                  <Typography.Title level={4}>
                    {formatCurrency(selectedAsset.purchase_cost)}
                  </Typography.Title>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    ارزش اسقاط
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatCurrency(selectedAsset.salvage_value)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    روش استهلاک
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {getDepreciationMethodLabel(selectedAsset.depreciation_method)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    نرخ استهلاک سالانه
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {calculateDepreciationRate(selectedAsset).toFixed(2)}%
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    ارزش فعلی
                  </Typography>
                  <Typography.Title level={4}>
                    {formatCurrency(selectedAsset.current_value)}
                  </Typography.Title>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    استهلاک انباشته
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {formatCurrency(selectedAsset.accumulated_depreciation)}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    محل
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedAsset.location || 'مشخص نشده'}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    توضیحات
                  </Typography>
                  <Typography variant="body1" style={{  mb: 2  }}>
                    {selectedAsset.description || 'توضیحی ثبت نشده'}
                  </Typography>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Typography variant="subtitle2" color="text.secondary">
                    وضعیت
                  </Typography>
                  <Tag
                    label={getStatusLabel(selectedAsset.status)}
                    color={getStatusColor(selectedAsset.status)}
                    style={{  mb: 2  }}
                  />
                </Col>
              </Row>

              <Divider style={{  my: 2  }} />

              <Typography.Title level={4}>
                جدول استهلاک
              </Typography.Title>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>دوره</TableCell>
                      <TableCell align="right">استهلاک دوره</TableCell>
                      <TableCell align="right">استهلاک انباشته</TableCell>
                      <TableCell align="right">ارزش دفتری</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {assetDepreciations.map((depreciation) => (
                      <TableRow key={depreciation.id}>
                        <TableCell>
                          {formatDate(depreciation.period_start)} - {formatDate(depreciation.period_end)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(depreciation.depreciation_amount)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(depreciation.accumulated_depreciation)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(depreciation.book_value)}
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