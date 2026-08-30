import React, { useEffect } from "react";
import { Button, Col, Input, InputNumber, Modal, Row, Select } from 'antd';
import { useForm, Controller } from "react-hook-form";
import { Employee, EmployeeStatus } from "../../api/hr/types";
import React from "react";
import { Button, List, List.Item, Typography } from 'antd';

export const EmployeeDocuments: React.FC<{
  documents: { id: string; name: string; url: string }[];
  onUpload: (file: File) => void;
}> = ({ documents, onUpload }) => (
  <div>
    <Typography.Title level={4}>مدارک پرسنلی</Typography.Title>
    <List>
      {documents.map(d => (
        <ListItem key={d.id}>
          <ListItemText
            primary={d.name}
            secondary={<a href={d.url} target="_blank" rel="noopener noreferrer">مشاهده/دانلود</a>}
          />
        </ListItem>
      ))}
    </List>
    <Button variant="outlined" size="small" style={{  mt: 1  }} component="label">
      بارگذاری مدرک جدید
      <input type="file" hidden onChange={e => e.target.files && onUpload(e.target.files[0])} />
    </Button>
  </div>
);

const statusOptions: { value: EmployeeStatus; label: string }[] = [
  { value: "active", label: "فعال" },
  { value: "inactive", label: "غیرفعال" },
  { value: "on_leave", label: "مرخصی" },
  { value: "retired", label: "بازنشسته" },
];

export const EmployeeForm: React.FC<{
  open: boolean;
  onClose: () => void;
  employee?: Employee;
  onSave: (data: any) => void;
}> = ({ open, onClose, employee, onSave }) => {
  const { control, handleSubmit, reset } = useForm({
    defaultValues: employee || {
      code: "",
      firstName: "",
      lastName: "",
      nationalId: "",
      position: "",
      department: "",
      status: "active",
      hireDate: "",
      contractType: "",
      phone: "",
      email: "",
      address: "",
      roles: [],
    },
  });

  useEffect(() => {
    reset(employee || {
      code: "",
      firstName: "",
      lastName: "",
      nationalId: "",
      position: "",
      department: "",
      status: "active",
      hireDate: "",
      contractType: "",
      phone: "",
      email: "",
      address: "",
      roles: [],
    });
  }, [employee, reset]);

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{employee ? "ویرایش پرسنل" : "افزودن پرسنل جدید"}</div>
      <form onSubmit={handleSubmit(onSave)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="code"
                control={control}
                rules={{ required: "کد پرسنلی الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="کد پرسنلی" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="nationalId"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="کد ملی" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="firstName"
                control={control}
                rules={{ required: "نام الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="نام" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="lastName"
                control={control}
                rules={{ required: "نام خانوادگی الزامی است" }}
                render={({ field, fieldState }) => (
                  <Input {...field} label="نام خانوادگی" fullWidth error={!!fieldState.error} helperText={fieldState.error?.message} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="position"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="سمت" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="department"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="دپارتمان" fullWidth />
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
                name="hireDate"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تاریخ استخدام" type="date" fullWidth InputLabelProps={{ shrink: true }} />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="contractType"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="نوع قرارداد" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="phone"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="تلفن" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(6 / 12 * 24)}>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="ایمیل" fullWidth />
                )}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="address"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="آدرس" fullWidth multiline rows={2} />
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