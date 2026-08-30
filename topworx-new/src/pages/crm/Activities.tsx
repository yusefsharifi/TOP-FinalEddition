import React, { useState } from "react";
import { Alert, Button, Typography } from 'antd';
import { Activity } from "../../../types/crm";
import { ActivitiesTable } from "../../app/components/crm/ActivitiesTable";
import { ActivityForm } from "../../app/components/crm/ActivityForm";

const mockActivities: Activity[] = [
  { id: 1, type: "تماس", relatedType: "customer", relatedId: 1, subject: "تماس با شرکت الف", description: "پیگیری اولیه", date: new Date(), ownerId: 1, ownerName: "علی رضایی", status: "برنامه‌ریزی شده" },
  { id: 2, type: "جلسه", relatedType: "opportunity", relatedId: 2, subject: "جلسه با شرکت ب", description: "ارائه پیشنهاد", date: new Date(), ownerId: 2, ownerName: "مریم محمدی", status: "انجام شده" },
  { id: 3, type: "ایمیل", relatedType: "order", relatedId: 3, subject: "ارسال فاکتور به شرکت ج", description: "ارسال فاکتور نهایی", date: new Date(), ownerId: 1, ownerName: "علی رضایی", status: "لغو شده" },
];

export const Activities: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>(mockActivities);
  const [formOpen, setFormOpen] = useState(false);
  const [editActivity, setEditActivity] = useState<Activity | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const handleAdd = () => {
    setEditActivity(null);
    setFormOpen(true);
  };
  const handleEdit = (activity: Activity) => {
    setEditActivity(activity);
    setFormOpen(true);
  };
  const handleDelete = (id: number) => {
    setActivities(acts => acts.filter(a => a.id !== id));
    setSnackbar({ open: true, message: "فعالیت حذف شد.", severity: "success" });
  };
  const handleSave = (data: Activity) => {
    if (editActivity) {
      setActivities(acts => acts.map(a => a.id === editActivity.id ? { ...data, id: editActivity.id } : a));
      setSnackbar({ open: true, message: "فعالیت ویرایش شد.", severity: "success" });
    } else {
      setActivities(acts => [...acts, { ...data, id: Math.max(...acts.map(a => a.id || 0)) + 1 }]);
      setSnackbar({ open: true, message: "فعالیت جدید اضافه شد.", severity: "success" });
    }
    setFormOpen(false);
  };
  const handleView = (activity: Activity) => {
    setEditActivity(activity);
    setFormOpen(true);
  };

  return (
    <div>
      <div>
        <Typography.Title level={3}>فعالیت‌ها و پیگیری‌ها</Typography.Title>
        <Button variant="contained" color="primary" onClick={handleAdd}>افزودن فعالیت</Button>
      </div>
      <ActivitiesTable
        activities={activities}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={handleView}
      />
      <ActivityForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        activity={editActivity}
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