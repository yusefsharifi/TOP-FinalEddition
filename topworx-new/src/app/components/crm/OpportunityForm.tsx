import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { Opportunity, OpportunityStage, OpportunityStatus } from "../../../types/crm";

export interface OpportunityFormProps {
  open: boolean;
  onClose: () => void;
  opportunity?: Opportunity | null;
  onSave: (data: Opportunity) => void;
}

const stages: OpportunityStage[] = ["سرنخ", "مذاکره", "پیشنهاد", "توافق", "برنده", "باخته"];
const statuses: OpportunityStatus[] = ["در انتظار", "فعال", "برنده", "باخته", "آرشیو"];

export const OpportunityForm: React.FC<OpportunityFormProps> = ({ open, onClose, opportunity, onSave }) => {
  const { control, handleSubmit, reset } = useForm<Opportunity>({
    defaultValues: opportunity || {
      title: "",
      customerId: 0,
      customerName: "",
      ownerId: 0,
      ownerName: "",
      stage: "سرنخ",
      amount: 0,
      currency: "تومان",
      probability: 0,
      status: "در انتظار",
      expectedCloseDate: new Date(),
      notes: "",
    },
  });

  useEffect(() => {
    if (opportunity) reset(opportunity);
    else reset({
      title: "",
      customerId: 0,
      customerName: "",
      ownerId: 0,
      ownerName: "",
      stage: "سرنخ",
      amount: 0,
      currency: "تومان",
      probability: 0,
      status: "در انتظار",
      expectedCloseDate: new Date(),
      notes: "",
    });
  }, [opportunity, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{opportunity ? "ویرایش فرصت فروش" : "افزودن فرصت فروش"}</div>
      <form onSubmit={handleSubmit(onSave)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="title"
                control={control}
                rules={{ required: "عنوان الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="عنوان فرصت" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="customerName"
                control={control}
                rules={{ required: "نام مشتری الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="نام مشتری" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="ownerName"
                control={control}
                rules={{ required: "کارشناس فروش الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="کارشناس فروش" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="stage"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="مرحله فرصت" select fullWidth>
                    {stages.map((s) => (
                      <MenuItem key={s} value={s}>{s}</Select.Option>
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
                name="amount"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="مبلغ" type="number" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="currency"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="واحد پول" select fullWidth>
                    <MenuItem value="تومان">تومان</Select.Option>
                    <MenuItem value="دلار">دلار</Select.Option>
                    <MenuItem value="یورو">یورو</Select.Option>
                  </Input>
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="probability"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="درصد احتمال" type="number" fullWidth inputProps={{ min: 0, max: 100 }} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="expectedCloseDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ پیش‌بینی پایان" type="date" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="notes"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="یادداشت" fullWidth multiline rows={2} />
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