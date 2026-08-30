import React from "react";
import { Button, Col, Input, InputNumber, Modal, Row } from 'antd';
import { useForm } from "react-hook-form";
import { createCustomer, updateCustomer } from "../../api/crm/customers";

export const CustomerForm: React.FC<{
  open: boolean;
  onClose: () => void;
  customer?: any;
  onSaved: (msg: string) => void;
  onError: (msg: string) => void;
}> = ({ open, onClose, customer, onSaved, onError }) => {
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: customer || {},
  });

  React.useEffect(() => {
    reset(customer || {});
  }, [customer, reset]);

  const onSubmit = async (data: any) => {
    try {
      if (customer) {
        await updateCustomer(customer.id, data);
        onSaved("مشتری با موفقیت ویرایش شد.");
      } else {
        await createCustomer(data);
        onSaved("مشتری جدید با موفقیت افزوده شد.");
      }
    } catch (e: any) {
      onError(e.message || "خطا در ذخیره‌سازی اطلاعات");
    }
  };

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{customer ? "ویرایش مشتری" : "افزودن مشتری جدید"}</div>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                label="نام"
                fullWidth
                {...register("name", { required: "نام الزامی است" })}
                error={!!errors.name}
                helperText={errors.name?.message}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                label="ایمیل"
                fullWidth
                {...register("email", { required: "ایمیل الزامی است" })}
                error={!!errors.email}
                helperText={errors.email?.message}
              />
            </Col>
            {/* سایر فیلدها */}
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