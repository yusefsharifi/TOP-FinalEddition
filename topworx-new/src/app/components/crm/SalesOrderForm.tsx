import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row } from 'antd';
import { useForm, Controller, useFieldArray } from "react-hook-form";
import { SalesOrder, SalesOrderStatus, PaymentStatus, SalesOrderItem } from "../../../types/crm";
import { PlusOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';

export interface SalesOrderFormProps {
  open: boolean;
  onClose: () => void;
  order?: SalesOrder | null;
  onSave: (data: SalesOrder) => void;
}

const statuses: SalesOrderStatus[] = ["در انتظار", "ارسال شده", "پرداخت شده", "لغو شده", "آرشیو"];
const paymentStatuses: PaymentStatus[] = ["پرداخت نشده", "نیمه پرداخت", "پرداخت شده"];

export const SalesOrderForm: React.FC<SalesOrderFormProps> = ({ open, onClose, order, onSave }) => {
  const { control, handleSubmit, reset } = useForm<SalesOrder>({
    defaultValues: order || {
      orderNumber: "",
      customerId: 0,
      customerName: "",
      opportunityId: undefined,
      status: "در انتظار",
      orderDate: new Date(),
      deliveryDate: undefined,
      totalAmount: 0,
      currency: "تومان",
      paymentStatus: "پرداخت نشده",
      items: [],
      createdBy: 0,
      notes: "",
    },
  });
  const { fields, append, remove } = useFieldArray({ control, name: "items" });

  useEffect(() => {
    if (order) reset(order);
    else reset({
      orderNumber: "",
      customerId: 0,
      customerName: "",
      opportunityId: undefined,
      status: "در انتظار",
      orderDate: new Date(),
      deliveryDate: undefined,
      totalAmount: 0,
      currency: "تومان",
      paymentStatus: "پرداخت نشده",
      items: [],
      createdBy: 0,
      notes: "",
    });
  }, [order, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{order ? "ویرایش سفارش فروش" : "افزودن سفارش فروش"}</div>
      <form onSubmit={handleSubmit(onSave)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="orderNumber"
                control={control}
                rules={{ required: "شماره سفارش الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="شماره سفارش" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
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
                name="status"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="وضعیت سفارش" select fullWidth>
                    {statuses.map((s) => (
                      <MenuItem key={s} value={s}>{s}</Select.Option>
                    ))}
                  </Input>
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="paymentStatus"
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
                name="orderDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ سفارش" type="date" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="deliveryDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ تحویل" type="date" fullWidth InputLabelProps={{ shrink: true }} />
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
          <div>
            <div>
              <span>آیتم‌های سفارش</span>
              <Button startIcon={<AddIcon />} onClick={() => append({ productId: 0, productName: "", quantity: 1, unit: "عدد", unitPrice: 0, totalPrice: 0 })}>
                افزودن آیتم
              </Button>
            </div>
            {fields.map((item, idx) => (
              <Row gutter={[16, 16]}>
                <Col xs={Math.round(3 / 12 * 24)}>
                  <Controller
                    name={`items.${idx}.productName` as const}
                    control={control}
                    render={({ field }) => (
                      <Input {...field} label="نام محصول" fullWidth />
                    )}
                  />
                </Col>
                <Col xs={Math.round(2 / 12 * 24)}>
                  <Controller
                    name={`items.${idx}.quantity` as const}
                    control={control}
                    render={({ field }) => (
                      <Input {...field} label="تعداد" type="number" fullWidth />
                    )}
                  />
                </Col>
                <Col xs={Math.round(2 / 12 * 24)}>
                  <Controller
                    name={`items.${idx}.unit` as const}
                    control={control}
                    render={({ field }) => (
                      <Input {...field} label="واحد" fullWidth />
                    )}
                  />
                </Col>
                <Col xs={Math.round(2 / 12 * 24)}>
                  <Controller
                    name={`items.${idx}.unitPrice` as const}
                    control={control}
                    render={({ field }) => (
                      <Input {...field} label="قیمت واحد" type="number" fullWidth />
                    )}
                  />
                </Col>
                <Col xs={Math.round(2 / 12 * 24)}>
                  <Controller
                    name={`items.${idx}.totalPrice` as const}
                    control={control}
                    render={({ field }) => (
                      <Input {...field} label="قیمت کل" type="number" fullWidth />
                    )}
                  />
                </Col>
                <Col xs={Math.round(1 / 12 * 24)}>
                  <Button type="text" onClick={() => remove(idx)} color="error"><DeleteIcon /></Button>
                </Col>
              </Row>
            ))}
          </div>
        </div>
        <div>
          <Button onClick={onClose}>انصراف</Button>
          <Button type="submit" variant="contained">ذخیره</Button>
        </div>
      </form>
    </Modal>
  );
}; 