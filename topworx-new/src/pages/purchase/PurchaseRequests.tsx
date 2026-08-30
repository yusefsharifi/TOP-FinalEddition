import React, { useState, useMemo } from "react";
import { Alert, Button, Card, Input, InputNumber, Pagination, Table, Tabs, Tag, Tooltip, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { ArchiveOutlined } from '@ant-design/icons';
import { UploadOutlined } from '@ant-design/icons';
import { PurchaseRequest } from "../../types/procurement";
// import { PurchaseRequestForm } from "../../app/components/procurement/PurchaseRequestForm";
// import { PurchaseRequestDetails } from "../../app/components/procurement/PurchaseRequestDetails";

const mockRequests: PurchaseRequest[] = [
  {
    id: 1,
    requestNumber: "PR-1001",
    requesterId: 1,
    requesterName: "علی رضایی",
    department: "مالی",
    requestDate: new Date(),
    requiredDate: new Date(),
    priority: "زیاد",
    status: "در انتظار",
    totalAmount: 1200000,
    currency: "تومان",
    description: "درخواست خرید لپ‌تاپ",
    items: [],
    isArchived: false,
  },
  {
    id: 2,
    requestNumber: "PR-1002",
    requesterId: 2,
    requesterName: "مریم محمدی",
    department: "فناوری اطلاعات",
    requestDate: new Date(),
    requiredDate: new Date(),
    priority: "متوسط",
    status: "تأیید شده",
    totalAmount: 850000,
    currency: "تومان",
    description: "درخواست خرید پرینتر",
    items: [],
    isArchived: false,
  },
  {
    id: 3,
    requestNumber: "PR-1003",
    requesterId: 3,
    requesterName: "سارا احمدی",
    department: "انبار",
    requestDate: new Date(),
    requiredDate: new Date(),
    priority: "کم",
    status: "لغو شده",
    totalAmount: 500000,
    currency: "تومان",
    description: "درخواست خرید کاغذ",
    items: [],
    isArchived: true,
  },
];

const USER_ROLE = "admin";

export const PurchaseRequests: React.FC = () => {
  const [requests, setRequests] = useState<PurchaseRequest[]>(mockRequests);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [tab, setTab] = useState(0); // 0: فعال، 1: آرشیو
  const [formOpen, setFormOpen] = useState(false);
  const [editRequest, setEditRequest] = useState<PurchaseRequest | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<PurchaseRequest | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });
  const theme = useTheme();

  const filtered = useMemo(() =>
    requests.filter(r => {
      const matchesTab = tab === 0 ? !r.isArchived : !!r.isArchived;
      const matchesSearch =
        r.requestNumber.toLowerCase().includes(search.toLowerCase()) ||
        r.requesterName.toLowerCase().includes(search.toLowerCase()) ||
        r.department.toLowerCase().includes(search.toLowerCase()) ||
        r.description.toLowerCase().includes(search.toLowerCase());
      return matchesTab && matchesSearch;
    }), [requests, search, tab]);

  const paged = useMemo(() =>
    filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filtered, page, rowsPerPage]);

  const handleAdd = () => {
    setEditRequest(null);
    setFormOpen(true);
  };
  const handleEdit = (request: PurchaseRequest) => {
    setEditRequest(request);
    setFormOpen(true);
  };
  const handleDelete = (id?: number) => {
    setRequests(prev => prev.filter(r => r.id !== id));
    setSnackbar({ open: true, message: "درخواست حذف شد.", severity: "success" });
  };
  const handleSave = (data: PurchaseRequest) => {
    if (editRequest) {
      setRequests(prev => prev.map(r => r.id === editRequest.id ? { ...data, id: editRequest.id } : r));
      setSnackbar({ open: true, message: "درخواست ویرایش شد.", severity: "success" });
    } else {
      setRequests(prev => [...prev, { ...data, id: Math.max(...prev.map(r => r.id || 0)) + 1 }]);
      setSnackbar({ open: true, message: "درخواست جدید اضافه شد.", severity: "success" });
    }
    setFormOpen(false);
  };
  const handleDetails = (request: PurchaseRequest) => {
    setSelectedRequest(request);
    setDetailsOpen(true);
  };
  const handleArchive = (id?: number) => {
    setRequests(prev => prev.map(r => r.id === id ? { ...r, isArchived: !r.isArchived } : r));
    setSnackbar({ open: true, message: "وضعیت آرشیو تغییر کرد.", severity: "success" });
  };

  const canEdit = USER_ROLE === "admin";

  return (
    <div>
      <Typography.Title level={2}>
        مدیریت درخواست‌های خرید
      </Typography.Title>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} style={{  mb: 2  }}>
        <Tab label="فعال" />
        <Tab label="آرشیو/لغو شده" />
      </Tabs>
      <Toolbar style={{  px: 0, mb: 2  }}>
        <Input
          label="جستجو"
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{  width: 250, ml: 2  }}
          size="small"
        />
        {canEdit && (
          <Tooltip title="افزودن درخواست جدید">
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
              <TableCell>شماره درخواست</TableCell>
              <TableCell>درخواست‌دهنده</TableCell>
              <TableCell>دپارتمان</TableCell>
              <TableCell>تاریخ درخواست</TableCell>
              <TableCell>تاریخ موردنیاز</TableCell>
              <TableCell>اولویت</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell>مبلغ کل</TableCell>
              <TableCell align="center">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paged.map((request) => (
              <TableRow key={request.id} hover>
                <TableCell>{request.requestNumber}</TableCell>
                <TableCell>{request.requesterName}</TableCell>
                <TableCell>{request.department}</TableCell>
                <TableCell>{request.requestDate ? new Date(request.requestDate).toLocaleDateString() : ""}</TableCell>
                <TableCell>{request.requiredDate ? new Date(request.requiredDate).toLocaleDateString() : ""}</TableCell>
                <TableCell>{request.priority}</TableCell>
                <TableCell>
                  <Tag label={request.status} color={request.status === "تأیید شده" ? "success" : request.status === "رد شده" ? "error" : "default"} size="small" />
                </TableCell>
                <TableCell>{request.totalAmount.toLocaleString()} {request.currency}</TableCell>
                <TableCell align="center">
                  <Tooltip title="مشاهده جزئیات">
                    <Button type="text" onClick={() => handleDetails(request)}>
                      <VisibilityIcon />
                    </Button>
                  </Tooltip>
                  {canEdit && (
                    <>
                      <Tooltip title="ویرایش">
                        <Button type="text" onClick={() => handleEdit(request)}>
                          <EditIcon />
                        </Button>
                      </Tooltip>
                      <Tooltip title="حذف">
                        <Button type="text" onClick={() => handleDelete(request.id)}><DeleteIcon color="error" /></Button>
                      </Tooltip>
                      <Tooltip title={request.isArchived ? "بازگردانی" : "آرشیو"}>
                        <Button type="text" onClick={() => handleArchive(request.id)}>
                          {request.isArchived ? <UnarchiveIcon /> : <ArchiveIcon />}
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
      {/*
      <PurchaseRequestForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        request={editRequest}
        onSave={handleSave}
      />
      <PurchaseRequestDetails
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        request={selectedRequest}
      />
      */}
      <Snackbar open={snackbar.open} autoHideDuration={3000} onClose={() => setSnackbar(s => ({ ...s, open: false }))}>
        <Alert severity={snackbar.severity} style={{  width: '100%'  }}>{snackbar.message}</Alert>
      </div>
    </div>
  );
};
