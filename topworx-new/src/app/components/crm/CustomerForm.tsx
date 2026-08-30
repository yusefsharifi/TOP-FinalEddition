import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row, Select } from 'antd';
import { useForm } from "react-hook-form";

export interface Customer {
  id?: number;
  name: string;
  email: string;
  phone: string;
  company: string;
  status: "Active" | "Inactive";
}

interface CustomerFormProps {
  open: boolean;
  onClose: () => void;
  customer?: Customer | null;
  onSave: (data: Customer) => void;
}

export const CustomerForm: React.FC<CustomerFormProps> = ({ open, onClose, customer, onSave }) => {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<Customer>({
    defaultValues: customer || { name: "", email: "", phone: "", company: "", status: "Active" },
  });

  useEffect(() => {
    reset(customer || { name: "", email: "", phone: "", company: "", status: "Active" });
  }, [customer, reset]);

  const onSubmit = (data: Customer) => {
    onSave(data);
    onClose();
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
                {...register("email", { required: "ایمیل الزامی است", pattern: { value: /.+@.+\..+/, message: "ایمیل معتبر نیست" } })}
                error={!!errors.email}
                helperText={errors.email?.message}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                label="تلفن"
                fullWidth
                {...register("phone", { required: "تلفن الزامی است" })}
                error={!!errors.phone}
                helperText={errors.phone?.message}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                label="شرکت"
                fullWidth
                {...register("company", { required: "شرکت الزامی است" })}
                error={!!errors.company}
                helperText={errors.company?.message}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                select
                label="وضعیت"
                fullWidth
                {...register("status", { required: true })}
                defaultValue={customer?.status || "Active"}
              >
                <Select.Option value="Active">فعال</Select.Option>
                <Select.Option value="Inactive">غیرفعال</Select.Option>
              </Input>
            </Col>
          </Row>
        </div>
        <div>
          <Button onClick={onClose}>انصراف</Button>
          <Button type="submit" variant="contained">{customer ? "ذخیره" : "افزودن"}</Button>
        </div>
      </form>
    </Modal>
  );
}; 