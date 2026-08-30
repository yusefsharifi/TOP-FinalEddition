import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row, Select } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { Task, TaskPriority, TaskStatus } from "../../api/tasks/types";

export const TaskForm: React.FC<{
  open: boolean;
  onClose: () => void;
  task?: Task;
  onSave: (data: any) => void;
  users: { id: string; name: string }[];
}> = ({ open, onClose, task, onSave, users }) => {
  const { control, handleSubmit, reset } = useForm({
    defaultValues: task || {
      title: "",
      description: "",
      status: "todo",
      priority: "medium",
      assignee: "",
      dueDate: "",
    },
  });

  useEffect(() => {
    reset(task || {
      title: "",
      description: "",
      status: "todo",
      priority: "medium",
      assignee: "",
      dueDate: "",
    });
  }, [task, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{task ? "ویرایش وظیفه" : "افزودن وظیفه جدید"}</div>
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
                  <Input {...field} label="توضیحات" fullWidth multiline rows={3} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="status"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>وضعیت</span>
                    <Select {...field} label="وضعیت">
                      <MenuItem value="todo">در انتظار</Select.Option>
                      <MenuItem value="in_progress">در حال انجام</Select.Option>
                      <MenuItem value="done">انجام شده</Select.Option>
                      <MenuItem value="cancelled">لغو شده</Select.Option>
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="priority"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>اولویت</span>
                    <Select {...field} label="اولویت">
                      <MenuItem value="low">کم</Select.Option>
                      <MenuItem value="medium">متوسط</Select.Option>
                      <MenuItem value="high">زیاد</Select.Option>
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="assignee"
                control={control}
                rules={{ required: "انتخاب مسئول الزامی است" }}
                render={({ field, fieldState }) => (
                  <FormControl fullWidth>
                    <InputLabel>مسئول</span>
                    <Select {...field} label="مسئول" error={!!fieldState.error}>
                      {users.map((u) => (
                        <MenuItem key={u.id} value={u.id}>{u.name}</Select.Option>
                      ))}
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="dueDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ سررسید" type="date" fullWidth InputLabelProps={{ shrink: true }} />
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