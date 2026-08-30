import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row, Select } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { Budget, BudgetType } from "../../api/budget/types";
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

const typeOptions: { value: BudgetType; label: string }[] = [
  { value: "annual", label: "سالانه" },
  { value: "monthly", label: "ماهانه" },
  { value: "project", label: "پروژه‌ای" },
];

export const BudgetForm: React.FC<{
  open: boolean;
  onClose: () => void;
  budget?: Budget;
  onSave: (data: any) => void;
  allocations: { id: string; name: string; type: string }[];
}> = ({ open, onClose, budget, onSave, allocations }) => {
  const { control, handleSubmit, reset, watch } = useForm({
    defaultValues: budget || {
      title: "",
      type: "annual",
      year: new Date().getFullYear(),
      month: undefined,
      amount: 0,
      allocatedTo: "",
    },
  });

  const type = watch("type");

  useEffect(() => {
    reset(budget || {
      title: "",
      type: "annual",
      year: new Date().getFullYear(),
      month: undefined,
      amount: 0,
      allocatedTo: "",
    });
  }, [budget, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{budget ? "ویرایش بودجه" : "ثبت بودجه جدید"}</div>
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
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="type"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>نوع بودجه</span>
                    <Select {...field} label="نوع بودجه">
                      {typeOptions.map(t => <MenuItem key={t.value} value={t.value}>{t.label}</Select.Option>)}
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="allocatedTo"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>تخصیص به</span>
                    <Select {...field} label="تخصیص به">
                      {allocations.map(a => <MenuItem key={a.id} value={a.id}>{a.name}</Select.Option>)}
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="year"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="سال" type="number" fullWidth />
                )}
              />
            </Col>
            {type === "monthly" && (
              <Col xs={Math.round(6 / 12 * 24)}>
                <Controller
                  name="month"
                  control={control}
                  render={({ field }) => (
                    <Input {...field} label="ماه" type="number" fullWidth />
                  )}
                />
              </Col>
            )}
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="amount"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="مبلغ بودجه" type="number" fullWidth />
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