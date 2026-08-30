import React, { useState } from 'react';
import { Alert, Button, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { PurchaseRequest } from '../../../types/procurement';
import { PurchaseRequestsTable } from '../../components/purchase/PurchaseRequestsTable';
import { PurchaseRequestForm } from '../../components/purchase/PurchaseRequestForm';
import { PurchaseRequestsExportButtons } from '../../components/purchase/PurchaseRequestsExportButtons';
import { useCreatePurchaseRequest, useUpdatePurchaseRequest } from '../../../api/procurement';

export const PurchaseRequests: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [editRequest, setEditRequest] = useState<PurchaseRequest | null>(null);
  const [exportData, setExportData] = useState<PurchaseRequest[]>([]);
  const [snackbar, setSnackbar] = useState<{ 
    open: boolean; 
    message: string; 
    severity: 'success' | 'error' 
  }>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  const createRequest = useCreatePurchaseRequest();
  const updateRequest = useUpdatePurchaseRequest();

  const handleEdit = (request: PurchaseRequest | null) => {
    setEditRequest(request);
    setFormOpen(true);
  };

  const handleExport = (requests: PurchaseRequest[]) => {
    setExportData(requests);
  };

  const handleSave = async (data: any) => {
    try {
      if (editRequest) {
        await updateRequest.mutateAsync({ id: editRequest.id, ...data });
        setSnackbar({ 
          open: true, 
          message: 'درخواست با موفقیت ویرایش شد.', 
          severity: 'success' 
        });
      } else {
        await createRequest.mutateAsync(data);
        setSnackbar({ 
          open: true, 
          message: 'درخواست جدید با موفقیت ایجاد شد.', 
          severity: 'success' 
        });
      }
      setFormOpen(false);
      setEditRequest(null);
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'خطا در ذخیره درخواست.', 
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
        <Typography.Title level={2}>مدیریت درخواست‌های خرید</Typography.Title>
        <div style={{  display: 'flex', gap: 2  }}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={() => handleEdit(null)}
          >
            افزودن درخواست جدید
          </Button>
          {exportData.length > 0 && (
            <PurchaseRequestsExportButtons requests={exportData} />
          )}
        </div>
      </div>

      <PurchaseRequestsTable
        onEdit={handleEdit}
        onExport={handleExport}
        userRole="admin"
      />

      <PurchaseRequestForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditRequest(null);
        }}
        request={editRequest}
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