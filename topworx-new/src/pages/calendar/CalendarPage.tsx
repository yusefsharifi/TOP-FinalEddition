import React, { useState } from "react";
import { Alert, Button, Card } from 'antd';
import { useCalendarEvents, useCreateEvent, useUpdateEvent, useDeleteEvent } from "../../api/calendar";
import { CalendarView } from "../../components/calendar/CalendarView";
import { EventForm } from "../../components/calendar/EventForm";
import { useEffect } from "react";
import { useNotificationSnackbar } from "../../core/notifications/NotificationSnackbarProvider";

const { showNotification } = useNotificationSnackbar();

const handleEventDrop = async (event, start, end) => {
  try {
    await updateEvent.mutateAsync({ id: event.id, start, end });
    setSnackbar({ open: true, message: "رویداد جابجا شد.", severity: "success" });
    refetch();
  } catch (e: any) {
    setSnackbar({ open: true, message: "خطا در جابجایی رویداد", severity: "error" });
  }
};

useEffect(() => {
  data.forEach(event => {
    const start = new Date(event.start).getTime();
    const now = Date.now();
    // اگر رویداد در ۲۴ ساعت آینده است و هنوز شروع نشده
    if (start - now < 24 * 60 * 60 * 1000 && start > now) {
      showNotification(`رویداد "${event.title}" تا ۲۴ ساعت دیگر شروع می‌شود!`, "info");
    }
  });
}, [data]);

// فرض: لیست کاربران را از API یا Context بگیر
const users = [
  { id: "1", name: "مدیر" },
  { id: "2", name: "کاربر نمونه" },
];

export const CalendarPage: React.FC = () => {
  const { data = [], isLoading, refetch } = useCalendarEvents();
  const createEvent = useCreateEvent();
  const updateEvent = useUpdateEvent();
  const deleteEvent = useDeleteEvent();

  const [openForm, setOpenForm] = useState(false);
  const [selected, setSelected] = useState<any>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const handleSelectEvent = (event: any) => {
    setSelected(event);
    setOpenForm(true);
  };

  const handleSelectSlot = (slot: { start: Date; end: Date }) => {
    setSelected({ start: slot.start.toISOString(), end: slot.end.toISOString() });
    setOpenForm(true);
  };

  const handleSave = async (data: any) => {
    try {
      if (selected && selected.id) {
        await updateEvent.mutateAsync({ id: selected.id, ...data });
        setSnackbar({ open: true, message: "رویداد با موفقیت ویرایش شد.", severity: "success" });
      } else {
        await createEvent.mutateAsync(data);
        setSnackbar({ open: true, message: "رویداد جدید با موفقیت افزوده شد.", severity: "success" });
      }
      setOpenForm(false);
      refetch();
    } catch (e: any) {
      setSnackbar({ open: true, message: e.message || "خطا در ذخیره‌سازی اطلاعات", severity: "error" });
    }
  };

  return (
    <Card style={{  p: 3  }}>
      <div>
        <Button variant="contained" onClick={() => { setSelected(null); setOpenForm(true); }}>افزودن رویداد جدید</Button>
      </div>
      <CalendarView
        events={data}
        onSelectEvent={handleSelectEvent}
        onSelectSlot={handleSelectSlot}
      />
      <EventForm
        open={openForm}
        onClose={() => setOpenForm(false)}
        event={selected}
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