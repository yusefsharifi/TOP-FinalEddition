import React, { useState } from 'react';
import { Alert, Button, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { QualityInspection } from '../../../types/quality';
import { QualityInspectionsTable } from '../../components/quality/QualityInspectionsTable';
import { QualityInspectionForm } from '../../components/quality/QualityInspectionForm';
import { QualityInspectionsExportButtons } from '../../components/quality/QualityInspectionsExportButtons';
import { useCreateQualityInspection, useUpdateQualityInspection } from '../../../api/quality';

export const QualityInspections: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [editInspection, setEditInspection] = useState<QualityInspection | null>(null);
  const [exportData, setExportData] = useState<QualityInspection[]>([]);
  const [snackbar, setSnackbar] = useState<{ 
    open: boolean; 
    message: string; 
    severity: 'success' | 'error' 
  }>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  const createInspection = useCreateQualityInspection();
  const updateInspection = useUpdateQualityInspection();

  const handleEdit = (inspection: QualityInspection | null) => {
    setEditInspection(inspection);
    setFormOpen(true);
  };

  const handleView = (inspection: QualityInspection) => {
    // نمایش جزئیات بازرسی
    console.log('View inspection:', inspection);
  };

  const handleExport = (inspections: QualityInspection[]) => {
    setExportData(inspections);
  };

  const handleSave = async (data: any) => {
    try {
      if (editInspection) {
        await updateInspection.mutateAsync({ id: editInspection.id, ...data });
        setSnackbar({ 
          open: true, 
          message: 'بازرسی کیفیت با موفقیت ویرایش شد.', 
          severity: 'success' 
        });
      } else {
        await createInspection.mutateAsync(data);
        setSnackbar({ 
          open: true, 
          message: 'بازرسی کیفیت جدید با موفقیت ایجاد شد.', 
          severity: 'success' 
        });
      }
      setFormOpen(false);
      setEditInspection(null);
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'خطا در ذخیره بازرسی کیفیت.', 
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
        <Typography.Title level={2}>مدیریت بازرسی‌های کیفیت</Typography.Title>
        <div style={{  display: 'flex', gap: 2  }}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={() => handleEdit(null)}
          >
            افزودن بازرسی جدید
          </Button>
          {exportData.length > 0 && (
            <QualityInspectionsExportButtons inspections={exportData} />
          )}
        </div>
      </div>

      <QualityInspectionsTable
        onEdit={handleEdit}
        onView={handleView}
        onExport={handleExport}
        userRole="admin"
      />

      <QualityInspectionForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditInspection(null);
        }}
        inspection={editInspection}
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