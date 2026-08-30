import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { Activity, ActivityType, ActivityStatus } from "../../../types/crm";

export interface ActivityFormProps {
  open: boolean;
  onClose: () => void;
  activity?: Activity | null;
  onSave: (data: Activity) => void;
}

const types: ActivityType[] = ["تماس", "جلسه", "ایمیل", "یادداشت", "وظیفه"];
const statuses: ActivityStatus[] = ["برنامه‌ریزی شده", "انجام شده", "لغو شده"];

export const ActivityForm: React.FC<ActivityFormProps> = ({ open, onClose, activity, onSave }) => {
  const { control, handleSubmit, reset } = useForm<Activity>({
    defaultValues: activity || {
      type: "تماس",
      relatedType: "customer",
      relatedId: 0,
      subject: "",
      description: "",
      date: new Date(),
      ownerId: 0,
      ownerName: "",
      status: "برنامه‌ریزی شده",
    },
  });

  useEffect(() => {
    if (activity) reset(activity);
    else reset({
      type: "تماس",
      relatedType: "customer",
      relatedId: 0,
      subject: "",
      description: "",
      date: new Date(),
      ownerId: 0,
      ownerName: "",
      status: "برنامه‌ریزی شده",
    });
  }, [activity, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{activity ? "ویرایش فعالیت/پیگیری" : "افزودن فعالیت/پیگیری"}</div>
      <form onSubmit={handleSubmit(onSave)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="type"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="نوع فعالیت" select fullWidth>
                    {types.map((t) => (
                      <MenuItem key={t} value={t}>{t}</Select.Option>
                    ))}
                  </Input>
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="status"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="وضعیت" select fullWidth>
                    {statuses.map((s) => (
                      <MenuItem key={s} value={s}>{s}</Select.Option>
                    ))}
                  </Input>
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="subject"
                control={control}
                rules={{ required: "موضوع الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="موضوع" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
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
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="date"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ" type="date" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="ownerName"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="مسئول" fullWidth />
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