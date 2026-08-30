import React, { useState, useMemo } from "react";
import { Alert, Button, Card, Input, InputNumber, Pagination, Table, Tag, Tooltip, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { CustomerForm, Customer } from "../../components/crm/CustomerForm";
import { CustomerDetails } from "../../components/crm/CustomerDetails";

const mockCustomers: Customer[] = [
  { id: 1, name: "John Doe", email: "john@example.com", phone: "123-456-7890", company: "ABC Corp", status: "Active" },
  { id: 2, name: "Jane Smith", email: "jane@example.com", phone: "098-765-4321", company: "XYZ Ltd", status: "Active" },
  { id: 3, name: "Ali Rezaei", email: "ali@example.com", phone: "0912-1234567", company: "Pars Co", status: "Inactive" },
  { id: 4, name: "Sara Ahmadi", email: "sara@example.com", phone: "0935-9876543", company: "IranTech", status: "Active" },
  { id: 5, name: "Mohammad Karimi", email: "mohammad@example.com", phone: "0910-5555555", company: "Asia Ltd", status: "Inactive" },
];

const USER_ROLE = "admin"; // برای تست RBAC

export const Customers: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>(mockCustomers);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [formOpen, setFormOpen] = useState(false);
  const [editCustomer, setEditCustomer] = useState<Customer | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });
  const theme = useTheme();

  const filtered = useMemo(() =>
    customers.filter(c =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.email.toLowerCase().includes(search.toLowerCase()) ||
      c.phone.includes(search) ||
      c.company.toLowerCase().includes(search.toLowerCase())
    ), [customers, search]);

  const paged = useMemo(() =>
    filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filtered, page, rowsPerPage]);

  const handleAdd = () => {
    setEditCustomer(null);
    setFormOpen(true);
  };
  const handleEdit = (customer: Customer) => {
    setEditCustomer(customer);
    setFormOpen(true);
  };
  const handleDelete = (id?: number) => {
    setCustomers(prev => prev.filter(c => c.id !== id));
    setSnackbar({ open: true, message: "مشتری حذف شد.", severity: "success" });
  };
  const handleSave = (data: Customer) => {
    if (editCustomer) {
      setCustomers(prev => prev.map(c => c.id === editCustomer.id ? { ...data, id: editCustomer.id } : c));
      setSnackbar({ open: true, message: "مشتری ویرایش شد.", severity: "success" });
    } else {
      setCustomers(prev => [...prev, { ...data, id: Math.max(...prev.map(c => c.id || 0)) + 1 }]);
      setSnackbar({ open: true, message: "مشتری جدید اضافه شد.", severity: "success" });
    }
  };
  const handleDetails = (customer: Customer) => {
    setSelectedCustomer(customer);
    setDetailsOpen(true);
  };

  // RBAC: فقط ادمین می‌تواند افزودن/ویرایش/حذف کند
  const canEdit = USER_ROLE === "admin";

  return (
    <div>
      <Typography.Title level={2}>
        مدیریت مشتریان
      </Typography.Title>
      <Toolbar style={{  px: 0, mb: 2  }}>
        <Input
          label="جستجو"
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{  width: 250, ml: 2  }}
          size="small"
        />
        {canEdit && (
          <Tooltip title="افزودن مشتری جدید">
            <Button type="text" onClick={handleAdd} style={{  ml: 1  }}>
              <AddIcon />
            </Button>
          </Tooltip>
        )}
      </Toolbar>
      <TableContainer component={Paper} style={{  boxShadow: 2, borderRadius: 3  }}>
        <Table size="small">
          <TableHead>
            <TableRow style={{  bgcolor: theme.palette.mode === "dark" ? "grey.900" : "grey.100"  }}>
              <TableCell>نام</TableCell>
              <TableCell>ایمیل</TableCell>
              <TableCell>تلفن</TableCell>
              <TableCell>شرکت</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell align="center">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paged.map((customer) => (
              <TableRow key={customer.id} hover>
                <TableCell>{customer.name}</TableCell>
                <TableCell>{customer.email}</TableCell>
                <TableCell>{customer.phone}</TableCell>
                <TableCell>{customer.company}</TableCell>
                <TableCell>
                  <Tag
                    label={customer.status === "Active" ? "فعال" : "غیرفعال"}
                    color={customer.status === "Active" ? "success" : "default"}
                    size="small"
                  />
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="مشاهده جزئیات">
                    <Button type="text" onClick={() => handleDetails(customer)}>
                      <VisibilityIcon />
                    </Button>
                  </Tooltip>
                  {canEdit && (
                    <>
                      <Tooltip title="ویرایش">
                        <Button type="text" onClick={() => handleEdit(customer)}>
                          <EditIcon />
                        </Button>
                      </Tooltip>
                      <Tooltip title="حذف">
                        <Button type="text" onClick={() => handleDelete(customer.id)}>
                          <DeleteIcon color="error" />
                        </Button>
                      </Tooltip>
                    </>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={filtered.length}
          page={page}
          onPageChange={(_, p) => setPage(p)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={e => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
          rowsPerPageOptions={[5, 10, 25]}
          labelRowsPerPage="تعداد در صفحه"
        />
      </div>
      <CustomerForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        customer={editCustomer}
        onSave={handleSave}
      />
      <CustomerDetails
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        customer={selectedCustomer}
      />
      <Snackbar open={snackbar.open} autoHideDuration={3000} onClose={() => setSnackbar(s => ({ ...s, open: false }))}>
        <Alert severity={snackbar.severity} style={{  width: '100%'  }}>{snackbar.message}</Alert>
      </div>
    </div>
  );
}; 