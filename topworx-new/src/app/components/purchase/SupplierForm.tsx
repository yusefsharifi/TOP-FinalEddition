import React, { useEffect } from 'react';
import { Button, Col, Input, InputNumber, Modal, Row, Select, Tag, Typography } from 'antd';
import { useForm, Controller } from 'react-hook-form';
import { Supplier, SupplierStatus } from '../../../types/procurement';

interface SupplierFormProps {
  open: boolean;
  onClose: () => void;
  supplier: Supplier | null;
  onSave: (data: any) => void;
}

const statusOptions: { value: SupplierStatus; label: string }[] = [
  { value: 'فعال', label: 'فعال' },
  { value: 'غیرفعال', label: 'غیرفعال' },
  { value: 'معلق', label: 'معلق' }
];

export const SupplierForm: React.FC<SupplierFormProps> = ({
  open,
  onClose,
  supplier,
  onSave
}) => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm({
    defaultValues: {
      code: '',
      name: '',
      contactPerson: '',
      phone: '',
      email: '',
      address: '',
      status: 'فعال' as SupplierStatus,
      rating: 5,
      notes: ''
    }
  });

  useEffect(() => {
    if (supplier) {
      reset({
        code: supplier.code,
        name: supplier.name,
        contactPerson: supplier.contactPerson,
        phone: supplier.phone,
        email: supplier.email,
        address: supplier.address,
        status: supplier.status,
        rating: supplier.rating,
        notes: supplier.notes || ''
      });
    } else {
      reset({
        code: '',
        name: '',
        contactPerson: '',
        phone: '',
        email: '',
        address: '',
        status: 'فعال',
        rating: 5,
        notes: ''
      });
    }
  }, [supplier, reset]);

  const onSubmit = (data: any) => {
    onSave({
      ...data,
      rating: parseInt(data.rating)
    });
  };

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>
        <Typography.Title level={4}>
          {supplier ? 'ویرایش تأمین‌کننده' : 'افزودن تأمین‌کننده جدید'}
        </Typography.Title>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="code"
                control={control}
                rules={{ required: 'کد تأمین‌کننده الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="کد تأمین‌کننده"
                    fullWidth
                    error={!!errors.code}
                    helperText={errors.code?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="name"
                control={control}
                rules={{ required: 'نام تأمین‌کننده الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="نام تأمین‌کننده"
                    fullWidth
                    error={!!errors.name}
                    helperText={errors.name?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="contactPerson"
                control={control}
                rules={{ required: 'شخص تماس الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="شخص تماس"
                    fullWidth
                    error={!!errors.contactPerson}
                    helperText={errors.contactPerson?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="phone"
                control={control}
                rules={{ 
                  required: 'شماره تلفن الزامی است',
                  pattern: {
                    value: /^[\d\-\+\(\)\s]+$/,
                    message: 'شماره تلفن معتبر نیست'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="شماره تلفن"
                    fullWidth
                    error={!!errors.phone}
                    helperText={errors.phone?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="email"
                control={control}
                rules={{ 
                  required: 'ایمیل الزامی است',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'ایمیل معتبر نیست'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="ایمیل"
                    type="email"
                    fullWidth
                    error={!!errors.email}
                    helperText={errors.email?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="status"
                control={control}
                rules={{ required: 'وضعیت الزامی است' }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.status}>
                    <InputLabel>وضعیت</span>
                    <Select {...field} label="وضعیت">
                      {statusOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          <div>
                            <Tag 
                              label={option.label} 
                              size="small"
                              color={
                                option.value === 'فعال' ? 'success' :
                                option.value === 'غیرفعال' ? 'error' :
                                'warning'
                              }
                            />
                          </div>
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.status && (
                      <FormHelperText>{errors.status.message}</FormHelperText>
                    )}
                  </div>
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="rating"
                control={control}
                rules={{ 
                  required: 'امتیاز الزامی است',
                  min: { value: 1, message: 'امتیاز باید بین 1 تا 5 باشد' },
                  max: { value: 5, message: 'امتیاز باید بین 1 تا 5 باشد' }
                }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.rating}>
                    <InputLabel>امتیاز</span>
                    <Select {...field} label="امتیاز">
                      {[1, 2, 3, 4, 5].map((rating) => (
                        <MenuItem key={rating} value={rating}>
                          <div>
                            <Tag 
                              label={`${rating} ستاره`} 
                              size="small"
                              color={
                                rating >= 4 ? 'success' :
                                rating >= 3 ? 'primary' :
                                rating >= 2 ? 'warning' :
                                'error'
                              }
                            />
                          </div>
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.rating && (
                      <FormHelperText>{errors.rating.message}</FormHelperText>
                    )}
                  </div>
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="address"
                control={control}
                rules={{ required: 'آدرس الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="آدرس"
                    multiline
                    rows={2}
                    fullWidth
                    error={!!errors.address}
                    helperText={errors.address?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="notes"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="یادداشت"
                    multiline
                    rows={2}
                    fullWidth
                  />
                )}
              />
            </Col>
          </Row>
        </div>
        
        <div>
          <Button onClick={onClose} disabled={isSubmitting}>
            انصراف
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            disabled={isSubmitting}
          >
            {isSubmitting ? 'در حال ذخیره...' : (supplier ? 'ویرایش' : 'ذخیره')}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 