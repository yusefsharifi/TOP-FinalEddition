import React, { useState } from "react";
import { Alert, Button, Card, Typography } from 'antd';
import { CustomerTable } from "../../components/crm/CustomerTable";
import { CustomerForm } from "../../components/crm/CustomerForm";
import { useCustomers } from "../../api/crm/customers";
import { PlusOutlined } from '@ant-design/icons';

export const Customers: React.FC = () => {
  const { data, isLoading, refetch } = useCustomers();
  const [openForm, setOpenForm] = useState(false);
  const [selected, setSelected] = useState(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const handleEdit = (customer: any) => {
    setSelected(customer);
    setOpenForm(true);
  };

  const handleAdd = () => {
    setSelected(null);
    setOpenForm(true);
  };

  const handleSaved = (msg: string) => {
    setSnackbar({ open: true, message: msg, severity: "success" });
    setOpenForm(false);
    refetch();
  };

  const handleError = (msg: string) => {
    setSnackbar({ open: true, message: msg, severity: "error" });
  };

  return (
    <Card style={{  p: 3  }}>
      <div>
        <Typography.Title level={3}>مدیریت مشتریان</Typography.Title>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>
          افزودن مشتری جدید
        </Button>
      </div>
      <CustomerTable
        data={data}
        loading={isLoading}
        onEdit={handleEdit}
        onDelete={refetch}
        onError={handleError}
      />
      <CustomerForm
        open={openForm}
        onClose={() => setOpenForm(false)}
        customer={selected}
        onSaved={handleSaved}
        onError={handleError}
      />
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </div>
    </Card>
  );
};