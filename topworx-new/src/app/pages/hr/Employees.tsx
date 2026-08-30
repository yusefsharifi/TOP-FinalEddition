import React, { useState } from 'react';
import { Alert, Button, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { Employee } from '../../../types/hr';
import { EmployeesTable } from '../../components/hr/EmployeesTable';
import { EmployeeForm } from '../../components/hr/EmployeeForm';
import { EmployeesExportButtons } from '../../components/hr/EmployeesExportButtons';
import { useCreateEmployee, useUpdateEmployee } from '../../../api/hr';

export const Employees: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [editEmployee, setEditEmployee] = useState<Employee | null>(null);
  const [exportData, setExportData] = useState<Employee[]>([]);
  const [snackbar, setSnackbar] = useState<{ 
    open: boolean; 
    message: string; 
    severity: 'success' | 'error' 
  }>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  const createEmployee = useCreateEmployee();
  const updateEmployee = useUpdateEmployee();

  const handleEdit = (employee: Employee | null) => {
    setEditEmployee(employee);
    setFormOpen(true);
  };

  const handleView = (employee: Employee) => {
    // نمایش جزئیات کارمند
    console.log('View employee:', employee);
  };

  const handleExport = (employees: Employee[]) => {
    setExportData(employees);
  };

  const handleSave = async (data: any) => {
    try {
      if (editEmployee) {
        await updateEmployee.mutateAsync({ id: editEmployee.id, ...data });
        setSnackbar({ 
          open: true, 
          message: 'کارمند با موفقیت ویرایش شد.', 
          severity: 'success' 
        });
      } else {
        await createEmployee.mutateAsync(data);
        setSnackbar({ 
          open: true, 
          message: 'کارمند جدید با موفقیت ایجاد شد.', 
          severity: 'success' 
        });
      }
      setFormOpen(false);
      setEditEmployee(null);
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'خطا در ذخیره کارمند.', 
        severity: 'error' 
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  return (
    <div style={{  p: 3  }}>
      <div style={{  mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center'  }}>
        <Typography.Title level={2}>مدیریت کارمندان</Typography.Title>
        <div style={{  display: 'flex', gap: 2  }}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={() => handleEdit(null)}
          >
            افزودن کارمند جدید
          </Button>
          {exportData.length > 0 && (
            <EmployeesExportButtons employees={exportData} />
          )}
        </div>
      </div>

      <EmployeesTable
        onEdit={handleEdit}
        onView={handleView}
        onExport={handleExport}
        userRole="admin"
      />

      <EmployeeForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditEmployee(null);
        }}
        employee={editEmployee}
        onSave={handleSave}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </div>
    </div>
  );
}; 