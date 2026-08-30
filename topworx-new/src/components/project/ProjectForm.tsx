import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row, Select, Tag } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { Project, ProjectStatus, ProjectMember } from "../../api/projects/types";
import { PaperClipOutlined } from '@ant-design/icons';
<Col xs={Math.round(12 / 12 * 24)}>
  <Button component="label" startIcon={<AttachFileIcon />}>
    انتخاب فایل پیوست
    <input type="file" hidden onChange={e => setFile(e.target.files?.[0] || null)} />
  </Button>
  {file && <Typography fontSize={13}>{file.name}</Typography>}
</Col>

const statusOptions: { value: ProjectStatus; label: string }[] = [
  { value: "active", label: "در حال انجام" },
  { value: "completed", label: "تکمیل شده" },
  { value: "paused", label: "متوقف" },
  { value: "cancelled", label: "لغو شده" },
];

export const ProjectForm: React.FC<{
  open: boolean;
  onClose: () => void;
  project?: Project;
  onSave: (data: any) => void;
  users: { id: string; name: string }[];
}> = ({ open, onClose, project, onSave, users }) => {
  const { control, handleSubmit, reset } = useForm({
    defaultValues: project || {
      title: "",
      description: "",
      status: "active",
      startDate: "",
      endDate: "",
      members: [],
    },
  });

  useEffect(() => {
    reset(project || {
      title: "",
      description: "",
      status: "active",
      startDate: "",
      endDate: "",
      members: [],
    });
  }, [project, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{project ? "ویرایش پروژه" : "افزودن پروژه جدید"}</div>
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
                name="status"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>وضعیت</span>
                    <Select {...field} label="وضعیت">
                      {statusOptions.map((s) => (
                        <MenuItem key={s.value} value={s.value}>{s.label}</Select.Option>
                      ))}
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="members"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>اعضا</span>
                    <Select {...field} label="اعضا" multiple renderValue={(selected) => (
                      <div style={{  display: 'flex', flexWrap: 'wrap', gap: 0.5  }}>
                        {(selected as string[]).map((id) => {
                          const user = users.find(u => u.id === id);
                          return <Tag key={id} label={user?.name || id} />;
                        })}
                      </div>
                    )}>
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
                name="startDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ شروع" type="date" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="endDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ پایان" type="date" fullWidth InputLabelProps={{ shrink: true }} />
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