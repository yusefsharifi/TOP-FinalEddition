import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { SalesInvoice, PaymentStatus } from "../../../types/crm";

export interface SalesInvoiceFormProps {
  open: boolean;
  onClose: () => void;
  invoice?: SalesInvoice | null;
  onSave: (data: SalesInvoice) => void;
}

const paymentStatuses: PaymentStatus[] = ["پرداخت نشده", "نیمه پرداخت", "پرداخت شده"];

export const SalesInvoiceForm: React.FC<SalesInvoiceFormProps> = ({ open, onClose, invoice, onSave }) => {
  const { control, handleSubmit, reset } = useForm<SalesInvoice>({
    defaultValues: invoice || {
      invoiceNumber: "",
      orderId: 0,
      customerId: 0,
      customerName: "",
      invoiceDate: new Date(),
      dueDate: new Date(),
      amount: 0,
      taxAmount: 0,
      totalAmount: 0,
      currency: "تومان",
      status: "پرداخت نشده",
      paymentMethod: undefined,
      paymentDate: undefined,
      attachment: undefined,
      notes: "",
    },
  });

  useEffect(() => {
    if (invoice) reset(invoice);
    else reset({
      invoiceNumber: "",
      orderId: 0,
      customerId: 0,
      customerName: "",
      invoiceDate: new Date(),
      dueDate: new Date(),
      amount: 0,
      taxAmount: 0,
      totalAmount: 0,
      currency: "تومان",
      status: "پرداخت نشده",
      paymentMethod: undefined,
      paymentDate: undefined,
      attachment: undefined,
      notes: "",
    });
  }, [invoice, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{invoice ? "ویرایش فاکتور فروش" : "افزودن فاکتور فروش"}</div>
      <form onSubmit={handleSubmit(onSave)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="invoiceNumber"
                control={control}
                rules={{ required: "شماره فاکتور الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="شماره فاکتور" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
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
                name="invoiceDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ فاکتور" type="date" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="dueDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ سررسید" type="date" fullWidth InputLabelProps={{ shrink: true }} />
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
                name="taxAmount"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="مالیات" type="number" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="totalAmount"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="جمع کل" type="number" fullWidth />
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
                name="status"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="وضعیت پرداخت" select fullWidth>
                    {paymentStatuses.map((s) => (
                      <MenuItem key={s} value={s}>{s}</Select.Option>
                    ))}
                  </Input>
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