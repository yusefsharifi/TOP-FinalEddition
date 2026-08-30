import React, { useState } from 'react';
import { Alert, Button, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { PurchaseInvoice } from '../../../types/procurement';
import { PurchaseInvoicesTable } from '../../components/purchase/PurchaseInvoicesTable';
import { PurchaseInvoiceForm } from '../../components/purchase/PurchaseInvoiceForm';
import { PurchaseInvoiceDetails } from '../../components/purchase/PurchaseInvoiceDetails';
import { PurchaseInvoicesExportButtons } from '../../components/purchase/PurchaseInvoicesExportButtons';
import { useCreatePurchaseInvoice, useUpdatePurchaseInvoice } from '../../../api/procurement';

export const PurchaseInvoices: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [editInvoice, setEditInvoice] = useState<PurchaseInvoice | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<PurchaseInvoice | null>(null);
  const [exportData, setExportData] = useState<PurchaseInvoice[]>([]);
  const [snackbar, setSnackbar] = useState<{ 
    open: boolean; 
    message: string; 
    severity: 'success' | 'error' 
  }>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  const createInvoice = useCreatePurchaseInvoice();
  const updateInvoice = useUpdatePurchaseInvoice();

  const handleEdit = (invoice: PurchaseInvoice | null) => {
    setEditInvoice(invoice);
    setFormOpen(true);
  };

  const handleView = (invoice: PurchaseInvoice) => {
    setSelectedInvoice(invoice);
    setDetailsOpen(true);
  };

  const handleExport = (invoices: PurchaseInvoice[]) => {
    setExportData(invoices);
  };

  const handleSave = async (data: any) => {
    try {
      if (editInvoice) {
        await updateInvoice.mutateAsync({ id: editInvoice.id, ...data });
        setSnackbar({ 
          open: true, 
          message: 'فاکتور با موفقیت ویرایش شد.', 
          severity: 'success' 
        });
      } else {
        await createInvoice.mutateAsync(data);
        setSnackbar({ 
          open: true, 
          message: 'فاکتور جدید با موفقیت ایجاد شد.', 
          severity: 'success' 
        });
      }
      setFormOpen(false);
      setEditInvoice(null);
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'خطا در ذخیره فاکتور.', 
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
        <Typography.Title level={2}>مدیریت فاکتورهای خرید</Typography.Title>
        <div style={{  display: 'flex', gap: 2  }}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={() => handleEdit(null)}
          >
            افزودن فاکتور جدید
          </Button>
          {exportData.length > 0 && (
            <PurchaseInvoicesExportButtons invoices={exportData} />
          )}
        </div>
      </div>

      <PurchaseInvoicesTable
        onEdit={handleEdit}
        onView={handleView}
        onExport={handleExport}
        userRole="admin"
      />

      <PurchaseInvoiceForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditInvoice(null);
        }}
        invoice={editInvoice}
        onSave={handleSave}
      />

      <PurchaseInvoiceDetails
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        invoice={selectedInvoice}
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