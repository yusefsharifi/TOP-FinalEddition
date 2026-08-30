import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Row, Select, Table, Tag, Typography } from 'antd';
import { DeleteOutlined, EditOutlined, EyeOutlined, PlusOutlined, ToolOutlined } from '@ant-design/icons';

const mockAssets = [
  {
    id: 1,
    name: 'کامپیوتر سرور',
    category: 'تجهیزات IT',
    purchaseDate: '2023-01-15',
    purchasePrice: 15000000,
    currentValue: 12000000,
    depreciationRate: 20,
    location: 'اتاق سرور',
    status: 'active',
    condition: 'خوب',
    lastMaintenance: '2024-03-15',
    nextMaintenance: '2024-06-15',
  },
  {
    id: 2,
    name: 'ماشین آلات تولید',
    category: 'تجهیزات تولید',
    purchaseDate: '2022-06-20',
    purchasePrice: 50000000,
    currentValue: 35000000,
    depreciationRate: 15,
    location: 'سالن تولید',
    status: 'active',
    condition: 'متوسط',
    lastMaintenance: '2024-02-10',
    nextMaintenance: '2024-05-10',
  },
  {
    id: 3,
    name: 'میز و صندلی اداری',
    category: 'مبلمان',
    purchaseDate: '2023-03-10',
    purchasePrice: 8000000,
    currentValue: 6000000,
    depreciationRate: 10,
    location: 'دفتر مرکزی',
    status: 'active',
    condition: 'خوب',
    lastMaintenance: '2024-01-20',
    nextMaintenance: '2024-04-20',
  },
  {
    id: 4,
    name: 'خودرو شرکت',
    category: 'وسایل نقلیه',
    purchaseDate: '2021-09-05',
    purchasePrice: 25000000,
    currentValue: 15000000,
    depreciationRate: 25,
    location: 'پارکینگ شرکت',
    status: 'maintenance',
    condition: 'نیاز به تعمیر',
    lastMaintenance: '2024-04-01',
    nextMaintenance: '2024-07-01',
  },
];

const assetCategories = [
  'تجهیزات IT',
  'تجهیزات تولید',
  'مبلمان',
  'وسایل نقلیه',
  'ساختمان',
  'سایر',
];

const assetStatuses = [
  'فعال',
  'تعمیر',
  'غیرفعال',
  'فروخته شده',
];

const assetConditions = [
  'عالی',
  'خوب',
  'متوسط',
  'ضعیف',
  'نیاز به تعمیر',
];

export const AssetManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<any>(null);
  const [newAsset, setNewAsset] = useState({
    name: '',
    category: '',
    purchaseDate: '',
    purchasePrice: '',
    depreciationRate: '',
    location: '',
    condition: '',
    description: '',
  });

  const handleAddAsset = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedAsset(null);
    setNewAsset({
      name: '',
      category: '',
      purchaseDate: '',
      purchasePrice: '',
      depreciationRate: '',
      location: '',
      condition: '',
      description: '',
    });
  };

  const handleSaveAsset = () => {
    // در اینجا دارایی جدید ذخیره می‌شود
    handleCloseDialog();
  };

  const handleViewAsset = (asset: any) => {
    setSelectedAsset(asset);
    setOpenDialog(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'maintenance':
        return 'warning';
      case 'inactive':
        return 'error';
      case 'sold':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'فعال';
      case 'maintenance':
        return 'تعمیر';
      case 'inactive':
        return 'غیرفعال';
      case 'sold':
        return 'فروخته شده';
      default:
        return 'نامشخص';
    }
  };

  const totalAssets = mockAssets.reduce((sum, asset) => sum + asset.purchasePrice, 0);
  const currentValue = mockAssets.reduce((sum, asset) => sum + asset.currentValue, 0);
  const totalDepreciation = totalAssets - currentValue;
  const activeAssets = mockAssets.filter(asset => asset.status === 'active').length;

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <Build style={{  mr: 1  }} />
            مدیریت دارایی‌ها
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddAsset}
          >
            دارایی جدید
          </Button>
        </div>

        {/* خلاصه دارایی‌ها */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                ارزش کل دارایی‌ها
              </Typography.Title>
              <Typography.Title level={2}>
                {totalAssets.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                ارزش فعلی
              </Typography.Title>
              <Typography.Title level={2}>
                {currentValue.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                کل استهلاک
              </Typography.Title>
              <Typography.Title level={2}>
                {totalDepreciation.toLocaleString()} تومان
              </Typography.Title>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center'  }}>
              <Typography.Title level={4}>
                دارایی‌های فعال
              </Typography.Title>
              <Typography.Title level={2}>
                {activeAssets}
              </Typography.Title>
            </Card>
          </Col>
        </Row>

        {/* جدول دارایی‌ها */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام دارایی</TableCell>
                <TableCell>دسته‌بندی</TableCell>
                <TableCell>محل</TableCell>
                <TableCell align="right">قیمت خرید</TableCell>
                <TableCell align="right">ارزش فعلی</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>شرایط</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockAssets.map((asset) => (
                <TableRow key={asset.id}>
                  <TableCell>{asset.name}</TableCell>
                  <TableCell>{asset.category}</TableCell>
                  <TableCell>{asset.location}</TableCell>
                  <TableCell align="right">
                    {asset.purchasePrice.toLocaleString()} تومان
                  </TableCell>
                  <TableCell align="right">
                    {asset.currentValue.toLocaleString()} تومان
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={getStatusText(asset.status)}
                      color={getStatusColor(asset.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tag
                      label={asset.condition}
                      color={asset.condition === 'نیاز به تعمیر' ? 'error' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleViewAsset(asset)}
                      >
                        <Visibility />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleViewAsset(asset)}
                      >
                        <Edit />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleViewAsset(asset)}
                      >
                        <Delete />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Dialog برای مشاهده/ویرایش دارایی */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedAsset ? 'جزئیات دارایی' : 'افزودن دارایی جدید'}
          </div>
          <div>
            {selectedAsset ? (
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="نام دارایی"
                    value={selectedAsset.name}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="دسته‌بندی"
                    value={selectedAsset.category}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="تاریخ خرید"
                    value={selectedAsset.purchaseDate}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="قیمت خرید"
                    value={selectedAsset.purchasePrice.toLocaleString()}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="ارزش فعلی"
                    value={selectedAsset.currentValue.toLocaleString()}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="نرخ استهلاک"
                    value={`${selectedAsset.depreciationRate}%`}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="محل"
                    value={selectedAsset.location}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="آخرین تعمیر"
                    value={selectedAsset.lastMaintenance}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="تعمیر بعدی"
                    value={selectedAsset.nextMaintenance}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="وضعیت"
                    value={getStatusText(selectedAsset.status)}
                    InputProps={{ readOnly: true }}
                  />
                </Col>
              </Row>
            ) : (
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="نام دارایی"
                    value={newAsset.name}
                    onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <FormControl fullWidth>
                    <InputLabel>دسته‌بندی</span>
                    <Select
                      value={newAsset.category}
                      label="دسته‌بندی"
                      onChange={(e) => setNewAsset({ ...newAsset, category: e.target.value })}
                    >
                      {assetCategories.map((category) => (
                        <MenuItem key={category} value={category}>
                          {category}
                        </Select.Option>
                      ))}
                    </Select>
                  </div>
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="تاریخ خرید"
                    type="date"
                    value={newAsset.purchaseDate}
                    onChange={(e) => setNewAsset({ ...newAsset, purchaseDate: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="قیمت خرید"
                    type="number"
                    value={newAsset.purchasePrice}
                    onChange={(e) => setNewAsset({ ...newAsset, purchasePrice: e.target.value })}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="نرخ استهلاک (%)"
                    type="number"
                    value={newAsset.depreciationRate}
                    onChange={(e) => setNewAsset({ ...newAsset, depreciationRate: e.target.value })}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <Input
                    fullWidth
                    label="محل"
                    value={newAsset.location}
                    onChange={(e) => setNewAsset({ ...newAsset, location: e.target.value })}
                  />
                </Col>
                <Col xs={Math.round(12 / 12 * 24)}>
                  <FormControl fullWidth>
                    <InputLabel>شرایط</span>
                    <Select
                      value={newAsset.condition}
                      label="شرایط"
                      onChange={(e) => setNewAsset({ ...newAsset, condition: e.target.value })}
                    >
                      {assetConditions.map((condition) => (
                        <MenuItem key={condition} value={condition}>
                          {condition}
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
                    value={newAsset.description}
                    onChange={(e) => setNewAsset({ ...newAsset, description: e.target.value })}
                  />
                </Col>
              </Row>
            )}
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            {!selectedAsset && (
              <Button onClick={handleSaveAsset} variant="contained">
                ثبت دارایی
              </Button>
            )}
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 