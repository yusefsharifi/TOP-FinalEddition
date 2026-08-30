import React, { useState } from 'react';
import { Alert, Button, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { Supplier } from '../../../types/procurement';
import { SuppliersTable } from '../../components/purchase/SuppliersTable';
import { SupplierForm } from '../../components/purchase/SupplierForm';
import { SuppliersExportButtons } from '../../components/purchase/SuppliersExportButtons';
import { useCreateSupplier, useUpdateSupplier } from '../../../api/procurement';

export const Suppliers: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [editSupplier, setEditSupplier] = useState<Supplier | null>(null);
  const [exportData, setExportData] = useState<Supplier[]>([]);
  const [snackbar, setSnackbar] = useState<{ 
    open: boolean; 
    message: string; 
    severity: 'success' | 'error' 
  }>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  const createSupplier = useCreateSupplier();
  const updateSupplier = useUpdateSupplier();

  const handleEdit = (supplier: Supplier | null) => {
    setEditSupplier(supplier);
    setFormOpen(true);
  };

  const handleExport = (suppliers: Supplier[]) => {
    setExportData(suppliers);
  };

  const handleSave = async (data: any) => {
    try {
      if (editSupplier) {
        await updateSupplier.mutateAsync({ id: editSupplier.id, ...data });
        setSnackbar({ 
          open: true, 
          message: 'تأمین‌کننده با موفقیت ویرایش شد.', 
          severity: 'success' 
        });
      } else {
        await createSupplier.mutateAsync(data);
        setSnackbar({ 
          open: true, 
          message: 'تأمین‌کننده جدید با موفقیت ایجاد شد.', 
          severity: 'success' 
        });
      }
      setFormOpen(false);
      setEditSupplier(null);
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'خطا در ذخیره تأمین‌کننده.', 
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
        <Typography.Title level={2}>مدیریت تأمین‌کنندگان</Typography.Title>
        <div style={{  display: 'flex', gap: 2  }}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={() => handleEdit(null)}
          >
            افزودن تأمین‌کننده جدید
          </Button>
          {exportData.length > 0 && (
            <SuppliersExportButtons suppliers={exportData} />
          )}
        </div>
      </div>

      <SuppliersTable
        onEdit={handleEdit}
        onExport={handleExport}
        userRole="admin"
      />

      <SupplierForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditSupplier(null);
        }}
        supplier={editSupplier}
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