import React, { useEffect, useState } from "react";
import { Button, Col, Input, InputNumber, Modal, Row, Select } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { Contract, ContractStatus } from "../../api/contracts/types";
import { Checkbox, Select } from 'antd';

const [access, setAccess] = useState<"public" | "private" | "role">("private");
const [roles, setRoles] = useState<string[]>([]);

<FormControl>
  <InputLabel>دسترسی</span>
  <Select value={access} onChange={e => setAccess(e.target.value)} label="دسترسی">
    <MenuItem value="public">عمومی</Select.Option>
    <MenuItem value="private">خصوصی</Select.Option>
    <MenuItem value="role">نقش‌محور</Select.Option>
  </Select>
</div>
{access === "role" && (
  <FormControl>
    <InputLabel>نقش‌ها</span>
    <Select
      multiple
      value={roles}
      onChange={e => setRoles(e.target.value as string[])}
      renderValue={selected => (selected as string[]).join(", ")}
    >
      <MenuItem value="admin"><Checkbox checked={roles.includes("admin")} /> <ListItemText primary="مدیر" /></Select.Option>
      <MenuItem value="finance"><Checkbox checked={roles.includes("finance")} /> <ListItemText primary="مالی" /></Select.Option>
      <MenuItem value="hr"><Checkbox checked={roles.includes("hr")} /> <ListItemText primary="منابع انسانی" /></Select.Option>
      {/* ... */}
    </Select>
  </div>
)}

<FormControl>
  <InputLabel>پروژه مرتبط</span>
  <Select value={relatedProjectId} onChange={e => setRelatedProjectId(e.target.value)} label="پروژه مرتبط">
    <MenuItem value="">بدون پروژه</Select.Option>
    {projects.map(p => <MenuItem key={p.id} value={p.id}>{p.title}</Select.Option>)}
  </Select>
</div>

const statusOptions: { value: ContractStatus; label: string }[] = [
  { value: "active", label: "فعال" },
  { value: "expired", label: "منقضی" },
  { value: "terminated", label: "فسخ‌شده" },
  { value: "renewed", label: "تمدیدشده" },
];

export const ContractForm: React.FC<{
  open: boolean;
  onClose: () => void;
  contract?: Contract;
  onSave: (formData: FormData) => void;
  parties: { id: string; name: string; type: string }[];
}> = ({ open, onClose, contract, onSave, parties }) => {
  const { control, handleSubmit, reset } = useForm({
    defaultValues: contract || {
      title: "",
      type: "",
      party: "",
      status: "active",
      startDate: "",
      endDate: "",
    },
  });
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    reset(contract || {
      title: "",
      type: "",
      party: "",
      status: "active",
      startDate: "",
      endDate: "",
    });
    setFile(null);
  }, [contract, reset]);

  const handleSave = (data: any) => {
    const formData = new FormData();
    Object.entries(data).forEach(([k, v]) => formData.append(k, v));
    if (file) formData.append("file", file);
    onSave(formData);
  };

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{contract ? "ویرایش قرارداد" : "ثبت قرارداد جدید"}</div>
      <form onSubmit={handleSubmit(handleSave)}>
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
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="type"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="نوع قرارداد" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="party"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>طرف قرارداد</span>
                    <Select {...field} label="طرف قرارداد">
                      {parties.map(p => <MenuItem key={p.id} value={p.id}>{p.name}</Select.Option>)}
                    </Select>
                  </div>
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
                      {statusOptions.map(s => <MenuItem key={s.value} value={s.value}>{s.label}</Select.Option>)}
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
            <Col xs={Math.round(12 / 12 * 24)}>
              <Button component="label" variant="outlined">
                انتخاب فایل قرارداد
                <input type="file" hidden onChange={e => setFile(e.target.files?.[0] || null)} />
              </Button>
              {file && <span style={{ marginRight: 8 }}>{file.name}</span>}
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