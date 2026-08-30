import React, { useState } from "react";
import { Alert, Button, Input, InputNumber, Modal, Tabs, Typography } from 'antd';
import { Opportunity, OpportunityStage } from "../../../types/crm";
import { OpportunitiesTable } from "../../app/components/crm/OpportunitiesTable";
import { OpportunityForm } from "../../app/components/crm/OpportunityForm";
import { OpportunitiesKanban } from "../../app/components/crm/OpportunitiesKanban";
import { ArchiveOutlined } from '@ant-design/icons';
import { UploadOutlined } from '@ant-design/icons';
import { SearchOutlined } from '@ant-design/icons';

const mockOpportunities: Opportunity[] = [
  { id: 1, title: "قرارداد شرکت الف", customerId: 1, customerName: "شرکت الف", ownerId: 1, ownerName: "علی رضایی", stage: "مذاکره", amount: 1200000, currency: "تومان", probability: 60, status: "فعال", expectedCloseDate: new Date(), notes: "", archived: false },
  { id: 2, title: "پروژه شرکت ب", customerId: 2, customerName: "شرکت ب", ownerId: 2, ownerName: "مریم محمدی", stage: "پیشنهاد", amount: 850000, currency: "تومان", probability: 40, status: "در انتظار", expectedCloseDate: new Date(), notes: "", archived: false },
  { id: 3, title: "فروش به شرکت ج", customerId: 3, customerName: "شرکت ج", ownerId: 1, ownerName: "علی رضایی", stage: "سرنخ", amount: 500000, currency: "تومان", probability: 20, status: "در انتظار", expectedCloseDate: new Date(), notes: "", archived: false },
  { id: 4, title: "قرارداد شرکت د", customerId: 4, customerName: "شرکت د", ownerId: 3, ownerName: "سارا احمدی", stage: "برنده", amount: 2000000, currency: "تومان", probability: 100, status: "برنده", expectedCloseDate: new Date(), notes: "", archived: false },
];

export const Opportunities: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>(mockOpportunities);
  const [formOpen, setFormOpen] = useState(false);
  const [editOpportunity, setEditOpportunity] = useState<Opportunity | null>(null);
  const [kanbanView, setKanbanView] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });
  const [tab, setTab] = useState(0); // 0: فعال، 1: آرشیو
  const [search, setSearch] = useState("");

  const handleAdd = () => {
    setEditOpportunity(null);
    setFormOpen(true);
  };
  const handleEdit = (op: Opportunity) => {
    setEditOpportunity(op);
    setFormOpen(true);
  };
  const handleDelete = (id: number) => {
    setOpportunities(ops => ops.filter(o => o.id !== id));
    setSnackbar({ open: true, message: "فرصت حذف شد.", severity: "success" });
  };
  const handleSave = (data: Opportunity) => {
    if (editOpportunity) {
      setOpportunities(ops => ops.map(o => o.id === editOpportunity.id ? { ...data, id: editOpportunity.id } : o));
      setSnackbar({ open: true, message: "فرصت ویرایش شد.", severity: "success" });
    } else {
      setOpportunities(ops => [...ops, { ...data, id: Math.max(...ops.map(o => o.id || 0)) + 1 }]);
      setSnackbar({ open: true, message: "فرصت جدید اضافه شد.", severity: "success" });
    }
    setFormOpen(false);
  };
  const handleView = (op: Opportunity) => {
    setEditOpportunity(op);
    setFormOpen(true);
  };
  const handleStageChange = (id: number, newStage: OpportunityStage) => {
    setOpportunities(ops => ops.map(o => o.id === id ? { ...o, stage: newStage } : o));
    setSnackbar({ open: true, message: "مرحله فرصت تغییر کرد.", severity: "success" });
  };
  const handleArchive = (id: number) => {
    setOpportunities(ops => ops.map(o => o.id === id ? { ...o, archived: !o.archived } : o));
    setSnackbar({ open: true, message: "وضعیت آرشیو تغییر کرد.", severity: "success" });
  };

  const filtered = opportunities.filter(o => {
    const matchesTab = tab === 0 ? !o.archived : !!o.archived;
    const matchesSearch =
      o.title.toLowerCase().includes(search.toLowerCase()) ||
      o.customerName.toLowerCase().includes(search.toLowerCase()) ||
      o.ownerName.toLowerCase().includes(search.toLowerCase());
    return matchesTab && matchesSearch;
  });

  return (
    <div>
      <div>
        <Typography.Title level={3}>فرصت‌های فروش</Typography.Title>
        <div>
          <Button variant={kanbanView ? "outlined" : "contained"} onClick={() => setKanbanView(false)}>جدول</Button>
          <Button variant={kanbanView ? "contained" : "outlined"} onClick={() => setKanbanView(true)}>Kanban</Button>
          <Button variant="contained" color="primary" onClick={handleAdd}>افزودن فرصت</Button>
        </div>
      </div>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} style={{  mb: 2  }}>
        <Tab label="فعال" />
        <Tab label="آرشیو" />
      </Tabs>
            <Input
        value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="جستجو ترکیبی..."
        size="small"
        style={{  mb: 2, width: 250  }}
        InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment> }}
      />
      {kanbanView ? (
        <OpportunitiesKanban
          opportunities={filtered}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={handleView}
          onStageChange={handleStageChange}
        />
      ) : (
        <OpportunitiesTable
          opportunities={filtered}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={handleView}
          renderActions={op => (
            <Button
              size="small"
              startIcon={op.archived ? <UnarchiveIcon /> : <ArchiveIcon />}
              onClick={() => handleArchive(op.id!)}
            >
              {op.archived ? "بازگردانی" : "آرشیو"}
            </Button>
          )}
        />
      )}
      <OpportunityForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        opportunity={editOpportunity}
        onSave={handleSave}
      />
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar(s => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </div>
    </div>
  );
};