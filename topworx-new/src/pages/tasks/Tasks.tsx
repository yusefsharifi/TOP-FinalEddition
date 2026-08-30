import React, { useState } from "react";
import { Alert, Button, Card } from 'antd';
import { useTasks, useCreateTask, useUpdateTask, useDeleteTask } from "../../api/tasks";
import { TaskTable } from "../../components/tasks/TaskTable";
import { TaskForm } from "../../components/tasks/TaskForm";
import { useNotificationSnackbar } from "../../core/notifications/NotificationSnackbarProvider";
import { Col, Input, InputNumber, Row } from 'antd';
import React, { useState } from "react";

const [search, setSearch] = useState("");
const [status, setStatus] = useState("");
const [priority, setPriority] = useState("");

const filtered = data.filter(task =>
  (!search || task.title.includes(search)) &&
  (!status || task.status === status) &&
  (!priority || task.priority === priority)
);

const { showNotification } = useNotificationSnackbar();

const handleStatusChange = async (taskId: string, newStatus: Task["status"]) => {
  try {
    await updateTask.mutateAsync({ id: taskId, status: newStatus });
    showNotification("وضعیت وظیفه تغییر کرد", "info");
    refetch();
  } catch (e: any) {
    showNotification("خطا در تغییر وضعیت", "error");
  }
};

export type TaskStatus = "todo" | "in_progress" | "done" | "cancelled";
export type TaskPriority = "low" | "medium" | "high";

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee: { id: string; name: string };
  creator: { id: string; name: string };
  dueDate: string;
  createdAt: string;
  updatedAt: string;
}
const users = [
  { id: "1", name: "مدیر" },
  { id: "2", name: "کاربر نمونه" },
];

export const Tasks: React.FC = () => {
  const { data = [], isLoading, refetch } = useTasks();
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();

  const [openForm, setOpenForm] = useState(false);
  const [selected, setSelected] = useState<any>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const handleEdit = (task: any) => {
    setSelected(task);
    setOpenForm(true);
  };

  const handleAdd = () => {
    setSelected(null);
    setOpenForm(true);
  };

  const handleSave = async (data: any) => {
    try {
      if (selected) {
        await updateTask.mutateAsync({ id: selected.id, ...data });
        setSnackbar({ open: true, message: "وظیفه با موفقیت ویرایش شد.", severity: "success" });
      } else {
        await createTask.mutateAsync(data);
        setSnackbar({ open: true, message: "وظیفه جدید با موفقیت افزوده شد.", severity: "success" });
      }
      setOpenForm(false);
      refetch();
    } catch (e: any) {
      setSnackbar({ open: true, message: e.message || "خطا در ذخیره‌سازی اطلاعات", severity: "error" });
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteTask.mutateAsync(id);
      setSnackbar({ open: true, message: "وظیفه حذف شد.", severity: "success" });
      refetch();
    } catch (e: any) {
      setSnackbar({ open: true, message: e.message || "خطا در حذف وظیفه", severity: "error" });
    }
  };

  return (
    <Card style={{  p: 3  }}>
      <div>
        <Button variant="contained" onClick={handleAdd}>افزودن وظیفه جدید</Button>
      </div>
      <TaskTable data={data} onEdit={handleEdit} onDelete={handleDelete} />
      <TaskForm
        open={openForm}
        onClose={() => setOpenForm(false)}
        task={selected}
        onSave={handleSave}
        users={users}
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