import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row, Select } from 'antd';
import { useForm, Controller, useFieldArray } from "react-hook-form";
import { Payroll, PayrollItem } from "../../api/payroll/types";

const itemTypes = [
  { value: "base", label: "حقوق پایه" },
  { value: "bonus", label: "پاداش" },
  { value: "overtime", label: "اضافه‌کاری" },
  { value: "loan", label: "وام" },
  { value: "insurance", label: "بیمه" },
  { value: "tax", label: "مالیات" },
  { value: "deduction", label: "کسورات" },
  { value: "custom", label: "سفارشی" },
];

export const PayrollForm: React.FC<{
  open: boolean;
  onClose: () => void;
  payroll?: Payroll;
  onSave: (data: any) => void;
  employees: { id: string; name: string }[];
}> = ({ open, onClose, payroll, onSave, employees }) => {
  const { control, handleSubmit, reset } = useForm({
    defaultValues: payroll || {
      employeeId: "",
      month: new Date().getMonth() + 1,
      year: new Date().getFullYear(),
      items: [],
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: "items" });

  useEffect(() => {
    reset(payroll || {
      employeeId: "",
      month: new Date().getMonth() + 1,
      year: new Date().getFullYear(),
      items: [],
    });
  }, [payroll, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{payroll ? "ویرایش فیش حقوقی" : "ثبت فیش حقوقی جدید"}</div>
      <form onSubmit={handleSubmit(onSave)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(4 / 12 * 24)}>
              <Controller
                name="employeeId"
                control={control}
                rules={{ required: "انتخاب پرسنل الزامی است" }}
                render={({ field, fieldState }) => (
                  <FormControl fullWidth>
                    <InputLabel>پرسنل</span>
                    <Select {...field} label="پرسنل" error={!!fieldState.error}>
                      {employees.map(e => <MenuItem key={e.id} value={e.id}>{e.name}</Select.Option>)}
                    </Select>
                  </div>
                )}
              />
            </Col>
            <Col xs={Math.round(4 / 12 * 24)}>
              <Controller
                name="month"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="ماه" type="number" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(4 / 12 * 24)}>
              <Controller
                name="year"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="سال" type="number" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Button variant="outlined" onClick={() => append({ type: "base", title: "", amount: 0 })}>افزودن آیتم حقوقی</Button>
            </Col>
            {fields.map((item, idx) => (
              <React.Fragment key={item.id}>
                <Col xs={Math.round(3 / 12 * 24)}>
                  <Controller
                    name={`items.${idx}.type`}
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth>
                        <InputLabel>نوع</span>
                        <Select {...field} label="نوع">
                          {itemTypes.map(t => <MenuItem key={t.value} value={t.value}>{t.label}</Select.Option>)}
                        </Select>
                      </div>
                    )}
                  />
                </Col>
                <Col xs={Math.round(5 / 12 * 24)}>
                  <Controller
                    name={`items.${idx}.title`}
                    control={control}
                    render={({ field }) => (
                      <Input {...field} label="شرح" fullWidth />
                    )}
                  />
                </Col>
                <Col xs={Math.round(3 / 12 * 24)}>
                  <Controller
                    name={`items.${idx}.amount`}
                    control={control}
                    render={({ field }) => (
                      <Input {...field} label="مبلغ" type="number" fullWidth />
                    )}
                  />
                </Col>
                <Col xs={Math.round(1 / 12 * 24)}>
                  <Button color="error" onClick={() => remove(idx)}>حذف</Button>
                </Col>
              </React.Fragment>
            ))}
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