import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Progress, Row, Select, Table, Tag, Typography } from 'antd';
import { DatabaseOutlined, DeleteOutlined, EditOutlined, EnvironmentOutlined, PlusOutlined } from '@ant-design/icons';

const mockWarehouses = [
  {
    id: 1,
    name: 'انبار مرکزی',
    location: 'تهران، خیابان ولیعصر',
    capacity: 10000,
    usedCapacity: 7800,
    sections: 15,
    manager: 'علی احمدی',
    status: 'active',
    temperature: '18°C',
    humidity: '45%',
  },
  {
    id: 2,
    name: 'انبار شمال',
    location: 'شمال تهران، جاده چالوس',
    capacity: 5000,
    usedCapacity: 3200,
    sections: 8,
    manager: 'مریم محمدی',
    status: 'active',
    temperature: '20°C',
    humidity: '50%',
  },
  {
    id: 3,
    name: 'انبار جنوب',
    location: 'جنوب تهران، بزرگراه آزادگان',
    capacity: 3000,
    usedCapacity: 2800,
    sections: 6,
    manager: 'حسن رضایی',
    status: 'maintenance',
    temperature: '22°C',
    humidity: '55%',
  },
];

const mockSections = [
  {
    id: 1,
    warehouseId: 1,
    name: 'قفسه A-1',
    capacity: 500,
    usedCapacity: 350,
    category: 'الکترونیک',
    temperature: '18°C',
    humidity: '45%',
    status: 'active',
  },
  {
    id: 2,
    warehouseId: 1,
    name: 'قفسه A-2',
    capacity: 500,
    usedCapacity: 480,
    category: 'پوشاک',
    temperature: '18°C',
    humidity: '45%',
    status: 'active',
  },
  {
    id: 3,
    warehouseId: 2,
    name: 'قفسه B-1',
    capacity: 300,
    usedCapacity: 200,
    category: 'کتاب',
    temperature: '20°C',
    humidity: '50%',
    status: 'active',
  },
];

const warehouseStatuses = [
  'فعال',
  'تعمیر',
  'غیرفعال',
  'توسعه',
];

export const WarehouseManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState<any>(null);
  const [newWarehouse, setNewWarehouse] = useState({
    name: '',
    location: '',
    capacity: '',
    manager: '',
    temperature: '',
    humidity: '',
    description: '',
  });

  const handleAddWarehouse = () => {
    setSelectedWarehouse(null);
    setOpenDialog(true);
  };

  const handleEditWarehouse = (warehouse: any) => {
    setSelectedWarehouse(warehouse);
    setNewWarehouse({
      name: warehouse.name,
      location: warehouse.location,
      capacity: warehouse.capacity.toString(),
      manager: warehouse.manager,
      temperature: warehouse.temperature,
      humidity: warehouse.humidity,
      description: '',
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedWarehouse(null);
    setNewWarehouse({
      name: '',
      location: '',
      capacity: '',
      manager: '',
      temperature: '',
      humidity: '',
      description: '',
    });
  };

  const handleSaveWarehouse = () => {
    // در اینجا انبار ذخیره می‌شود
    handleCloseDialog();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'maintenance':
        return 'warning';
      case 'inactive':
        return 'error';
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
      default:
        return 'نامشخص';
    }
  };

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <Storage style={{  mr: 1  }} />
            مدیریت انبار
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddWarehouse}
          >
            انبار جدید
          </Button>
        </div>

        {/* خلاصه انبارها */}
        <Row gutter={[16, 16]}>
          {mockWarehouses.map((warehouse) => {
            const utilization = (warehouse.usedCapacity / warehouse.capacity) * 100;
            return (
              <Col xs={Math.round(12 / 12 * 24)}>
                <Card style={{  p: 2  }}>
                  <div>
                    <Typography.Title level={4}>{warehouse.name}</Typography.Title>
                    <Tag
                      label={getStatusText(warehouse.status)}
                      color={getStatusColor(warehouse.status) as any}
                      size="small"
                    />
                  </div>
                  <Typography.Text>
                    {warehouse.location}
                  </Typography.Text>
                  <Typography.Text>
                    مدیر: {warehouse.manager}
                  </Typography.Text>
                  <div>
                    <div style={{  width: '100%', mr: 1  }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={utilization} 
                        style={{  height: 8, borderRadius: 4  }}
                        color={utilization > 80 ? 'warning' : 'success'}
                      />
                    </div>
                    <Typography.Text>
                      {utilization.toFixed(1)}%
                    </Typography.Text>
                  </div>
                  <Typography.Text>
                    {warehouse.usedCapacity.toLocaleString()} / {warehouse.capacity.toLocaleString()} متر مربع
                  </Typography.Text>
                </Card>
              </Col>
            );
          })}
        </Row>

        {/* جدول انبارها */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام انبار</TableCell>
                <TableCell>محل</TableCell>
                <TableCell>ظرفیت</TableCell>
                <TableCell>استفاده شده</TableCell>
                <TableCell>مدیر</TableCell>
                <TableCell>دما</TableCell>
                <TableCell>رطوبت</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockWarehouses.map((warehouse) => (
                <TableRow key={warehouse.id}>
                  <TableCell>{warehouse.name}</TableCell>
                  <TableCell>{warehouse.location}</TableCell>
                  <TableCell>{warehouse.capacity.toLocaleString()} متر مربع</TableCell>
                  <TableCell>{warehouse.usedCapacity.toLocaleString()} متر مربع</TableCell>
                  <TableCell>{warehouse.manager}</TableCell>
                  <TableCell>{warehouse.temperature}</TableCell>
                  <TableCell>{warehouse.humidity}</TableCell>
                  <TableCell>
                    <Tag
                      label={getStatusText(warehouse.status)}
                      color={getStatusColor(warehouse.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <div>
                      <Button type="text" size="small" onClick={() => handleEditWarehouse(warehouse)}
                      >
                        <Edit />
                      </Button>
                      <Button type="text" size="small" onClick={() => handleEditWarehouse(warehouse)}
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

        {/* Dialog برای اضافه/ویرایش انبار */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>
            {selectedWarehouse ? 'ویرایش انبار' : 'افزودن انبار جدید'}
          </div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="نام انبار"
                  value={newWarehouse.name}
                  onChange={(e) => setNewWarehouse({ ...newWarehouse, name: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="محل"
                  value={newWarehouse.location}
                  onChange={(e) => setNewWarehouse({ ...newWarehouse, location: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="ظرفیت (متر مربع)"
                  type="number"
                  value={newWarehouse.capacity}
                  onChange={(e) => setNewWarehouse({ ...newWarehouse, capacity: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="مدیر"
                  value={newWarehouse.manager}
                  onChange={(e) => setNewWarehouse({ ...newWarehouse, manager: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="دما"
                  value={newWarehouse.temperature}
                  onChange={(e) => setNewWarehouse({ ...newWarehouse, temperature: e.target.value })}
                  placeholder="مثال: 18°C"
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="رطوبت"
                  value={newWarehouse.humidity}
                  onChange={(e) => setNewWarehouse({ ...newWarehouse, humidity: e.target.value })}
                  placeholder="مثال: 45%"
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="توضیحات"
                  multiline
                  rows={3}
                  value={newWarehouse.description}
                  onChange={(e) => setNewWarehouse({ ...newWarehouse, description: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveWarehouse} variant="contained">
              {selectedWarehouse ? 'ویرایش' : 'ثبت'}
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 