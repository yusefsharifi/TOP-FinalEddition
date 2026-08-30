import React, { useState } from 'react';
import { Avatar, Button, Card, Input, InputNumber, Menu, Modal, Pagination, Table, Tag, Typography } from 'antd';
import { DeleteOutlined as DeleteIcon, EditOutlined as EditIcon, EllipsisOutlined as MoreVertIcon, PlusOutlined as AddIcon, SearchOutlined as SearchIcon, UserOutlined as PersonIcon } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

interface Employee {
  id: string;
  code: string;
  name: string;
  department: string;
  position: string;
  phone: string;
  email: string;
  status: string;
  joinDate: string;
}

const Employees: React.FC = () => {
  const { t } = useTranslation();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [openDialog, setOpenDialog] = useState(false);

  // Mock data
  const employees: Employee[] = [
    {
      id: '1',
      code: 'EMP001',
      name: 'علی محمدی',
      department: 'فروش',
      position: 'مدیر فروش',
      phone: '۰۹۱۲۳۴۵۶۷۸۹',
      email: 'ali@example.com',
      status: 'فعال',
      joinDate: '۱۴۰۲/۰۱/۱۵',
    },
    {
      id: '2',
      code: 'EMP002',
      name: 'مریم احمدی',
      department: 'حسابداری',
      position: 'کارشناس حسابداری',
      phone: '۰۹۱۲۳۴۵۶۷۹۰',
      email: 'maryam@example.com',
      status: 'فعال',
      joinDate: '۱۴۰۲/۰۲/۲۰',
    },
    // Add more mock data as needed
  ];

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, employee: Employee) => {
    setAnchorEl(event.currentTarget);
    setSelectedEmployee(employee);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedEmployee(null);
  };

  const handleEdit = () => {
    setOpenDialog(true);
    handleMenuClose();
  };

  const handleDelete = () => {
    // Add delete logic here
    handleMenuClose();
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'فعال':
        return 'success';
      case 'غیرفعال':
        return 'error';
      default:
        return 'default';
    }
  };

  const filteredEmployees = employees.filter((employee) =>
    employee.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    employee.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div>
      <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3  }}>
        <Typography.Title level={2}>
          {t('employees.title')}
        </Typography.Title>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          {t('employees.addEmployee')}
        </Button>
      </div>

      <Card style={{  mb: 3  }}>
        <Input
          fullWidth
          variant="outlined"
          placeholder={t('employees.searchPlaceholder')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Card>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('employees.code')}</TableCell>
              <TableCell>{t('employees.name')}</TableCell>
              <TableCell>{t('employees.department')}</TableCell>
              <TableCell>{t('employees.position')}</TableCell>
              <TableCell>{t('employees.phone')}</TableCell>
              <TableCell>{t('employees.email')}</TableCell>
              <TableCell>{t('employees.joinDate')}</TableCell>
              <TableCell>{t('employees.status')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredEmployees
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((employee) => (
                <TableRow key={employee.id}>
                  <TableCell>{employee.code}</TableCell>
                  <TableCell>
                    <div style={{  display: 'flex', alignItems: 'center'  }}>
                      <Avatar style={{  width: 32, height: 32, mr: 1  }}>
                        <PersonIcon />
                      </Avatar>
                      {employee.name}
                    </div>
                  </TableCell>
                  <TableCell>{employee.department}</TableCell>
                  <TableCell>{employee.position}</TableCell>
                  <TableCell>{employee.phone}</TableCell>
                  <TableCell>{employee.email}</TableCell>
                  <TableCell>{employee.joinDate}</TableCell>
                  <TableCell>
                    <Tag
                      label={employee.status}
                      color={getStatusColor(employee.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Button type="text" onClick={(e) => handleMenuClick(e, employee)}>
                      <MoreVertIcon />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredEmployees.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </div>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEdit}>
          <EditIcon style={{  mr: 1  }} /> {t('common.edit')}
        </Select.Option>
        <MenuItem onClick={handleDelete}>
          <DeleteIcon style={{  mr: 1  }} /> {t('common.delete')}
        </Select.Option>
      </Menu>

      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          {selectedEmployee ? t('employees.editEmployee') : t('employees.addEmployee')}
        </div>
        <div>
          {/* Add form fields here */}
          <div style={{  mt: 2  }}>
            <Typography color="text.secondary">
              {t('employees.formPlaceholder')}
            </Typography>
          </div>
        </div>
        <div>
          <Button onClick={handleDialogClose}>{t('common.cancel')}</Button>
          <Button variant="contained" onClick={handleDialogClose}>
            {t('common.save')}
          </Button>
        </div>
      </Modal>
    </div>
  );
};

export default Employees; 