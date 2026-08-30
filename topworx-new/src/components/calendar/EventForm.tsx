import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row, Select } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { CalendarEvent, EventType } from "../../api/calendar/types";

const eventTypes: { value: EventType; label: string }[] = [
  { value: "meeting", label: "جلسه" },
  { value: "reminder", label: "یادآوری" },
  { value: "holiday", label: "تعطیلی" },
  { value: "birthday", label: "تولد" },
  { value: "task", label: "وظیفه" },
  { value: "custom", label: "سفارشی" },
];

export const EventForm: React.FC<{
  open: boolean;
  onClose: () => void;
  event?: CalendarEvent;
  onSave: (data: any) => void;
  users: { id: string; name: string }[];
}> = ({ open, onClose, event, onSave, users }) => {
  const { control, handleSubmit, reset } = useForm({
    defaultValues: event || {
      title: "",
      description: "",
      type: "meeting",
      start: "",
      end: "",
      participants: [],
      allDay: false,
    },
  });

  useEffect(() => {
    reset(event || {
      title: "",
      description: "",
      type: "meeting",
      start: "",
      end: "",
      participants: [],
      allDay: false,
    });
  }, [event, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{event ? "ویرایش رویداد" : "افزودن رویداد جدید"}</div>
      <form onSubmit={handleSubmit(onSave)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="title"
                control={control}
                rules={{ required: "عنوان الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="عنوان" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="توضیحات" fullWidth multiline rows={2} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="type"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>نوع رویداد</span>
                    <Select {...field} label="نوع رویداد">
                      {eventTypes.map((t) => (
                        <MenuItem key={t.value} value={t.value}>{t.label}</Select.Option>
                      ))}
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="allDay"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>تمام روز</span>
                    <Select {...field} label="تمام روز">
                      <MenuItem value={true}>بله</Select.Option>
                      <MenuItem value={false}>خیر</Select.Option>
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="start"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="شروع" type="datetime-local" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="end"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="پایان" type="datetime-local" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="participants"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>شرکت‌کنندگان</span>
                    <Select {...field} label="شرکت‌کنندگان" multiple>
                      {users.map((u) => (
                        <MenuItem key={u.id} value={u.id}>{u.name}</Select.Option>
                      ))}
                    </Select>
                  </div>
                )}
              />
            </Col>
          </Row>
        </div>
        <div>
          <Button onClick={onClose}>انصراف</Button>
          <Button type="submit" variant="contained">ذخیره</Button>
        </div>
      </form>
    </Modal>
  );
};