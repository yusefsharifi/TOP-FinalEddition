import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row, Select } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { Asset, AssetCategory } from "../../api/assets/types";
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
      <MenuItem value="it"><Checkbox checked={roles.includes("it")} /> <ListItemText primary="فناوری اطلاعات" /></Select.Option>
      {/* ... */}
    </Select>
  </div>
)}

<Button onClick={() => archiveAsset(asset.id)}>آرشیو</Button>

{asset.projectId && (
  <Button onClick={() => navigate(`/projects/${asset.projectId}`)} size="small" color="primary">
    مشاهده پروژه
  </Button>
)}

const categoryOptions: { value: AssetCategory; label: string }[] = [
  { value: "fixed", label: "اموال ثابت" },
  { value: "equipment", label: "تجهیزات" },
  { value: "vehicle", label: "وسایل نقلیه" },
  { value: "it", label: "فناوری اطلاعات" },
  { value: "other", label: "سایر" },
];

export const AssetForm: React.FC<{
  open: boolean;
  onClose: () => void;
  asset?: Asset;
  onSave: (data: any) => void;
  managers: { id: string; name: string }[];
}> = ({ open, onClose, asset, onSave, managers }) => {
  const { control, handleSubmit, reset } = useForm({
    defaultValues: asset || {
      code: "",
      name: "",
      category: "fixed",
      location: "",
      manager: "",
      value: 0,
      purchaseDate: "",
      warrantyEnd: "",
      insuranceEnd: "",
      status: "active",
    },
  });

  useEffect(() => {
    reset(asset || {
      code: "",
      name: "",
      category: "fixed",
      location: "",
      manager: "",
      value: 0,
      purchaseDate: "",
      warrantyEnd: "",
      insuranceEnd: "",
      status: "active",
    });
  }, [asset, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{asset ? "ویرایش دارایی" : "ثبت دارایی جدید"}</div>
      <form onSubmit={handleSubmit(onSave)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="code"
                control={control}
                rules={{ required: "کد دارایی الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="کد دارایی" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="name"
                control={control}
                rules={{ required: "نام دارایی الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="نام دارایی" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="category"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>دسته‌بندی</span>
                    <Select {...field} label="دسته‌بندی">
                      {categoryOptions.map(c => <MenuItem key={c.value} value={c.value}>{c.label}</Select.Option>)}
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="manager"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>مسئول</span>
                    <Select {...field} label="مسئول">
                      {managers.map(m => <MenuItem key={m.id} value={m.id}>{m.name}</Select.Option>)}
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="location"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="محل نگهداری" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="value"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="ارزش" type="number" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="purchaseDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ خرید" type="date" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="warrantyEnd"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="پایان گارانتی" type="date" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="insuranceEnd"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="پایان بیمه" type="date" fullWidth InputLabelProps={{ shrink: true }} />
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
                      <MenuItem value="active">فعال</Select.Option>
                      <MenuItem value="inactive">غیرفعال</Select.Option>
                      <MenuItem value="maintenance">در تعمیر</Select.Option>
                      <MenuItem value="disposed">خارج شده</Select.Option>
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