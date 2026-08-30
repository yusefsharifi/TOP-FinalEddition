import React, { useEffect } from 'react';
import { Button, Col, Input, InputNumber, Modal, Row, Select, Tag, Typography } from 'antd';
import { useForm, Controller } from 'react-hook-form';
import { PurchaseRequest, PurchaseRequestStatus, PurchaseRequestPriority } from '../../../types/procurement';

interface PurchaseRequestFormProps {
  open: boolean;
  onClose: () => void;
  request: PurchaseRequest | null;
  onSave: (data: any) => void;
}

const statusOptions: { value: PurchaseRequestStatus; label: string }[] = [
  { value: 'در انتظار بررسی', label: 'در انتظار بررسی' },
  { value: 'تأیید شده', label: 'تأیید شده' },
  { value: 'رد شده', label: 'رد شده' },
  { value: 'در حال خرید', label: 'در حال خرید' },
  { value: 'تکمیل شده', label: 'تکمیل شده' }
];

const priorityOptions: { value: PurchaseRequestPriority; label: string }[] = [
  { value: 'کم', label: 'کم' },
  { value: 'متوسط', label: 'متوسط' },
  { value: 'زیاد', label: 'زیاد' },
  { value: 'فوری', label: 'فوری' }
];

export const PurchaseRequestForm: React.FC<PurchaseRequestFormProps> = ({
  open,
  onClose,
  request,
  onSave
}) => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm({
    defaultValues: {
      requestNumber: '',
      department: '',
      requestDate: '',
      requiredDate: '',
      priority: 'متوسط' as PurchaseRequestPriority,
      status: 'در انتظار بررسی' as PurchaseRequestStatus,
      description: '',
      estimatedCost: '',
      notes: ''
    }
  });

  useEffect(() => {
    if (request) {
      reset({
        requestNumber: request.requestNumber,
        department: request.department,
        requestDate: request.requestDate,
        requiredDate: request.requiredDate,
        priority: request.priority,
        status: request.status,
        description: request.description,
        estimatedCost: request.estimatedCost.toString(),
        notes: request.notes || ''
      });
    } else {
      reset({
        requestNumber: '',
        department: '',
        requestDate: '',
        requiredDate: '',
        priority: 'متوسط',
        status: 'در انتظار بررسی',
        description: '',
        estimatedCost: '',
        notes: ''
      });
    }
  }, [request, reset]);

  const onSubmit = (data: any) => {
    onSave({
      ...data,
      estimatedCost: parseFloat(data.estimatedCost)
    });
  };

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>
        <Typography.Title level={4}>
          {request ? 'ویرایش درخواست خرید' : 'افزودن درخواست خرید جدید'}
        </Typography.Title>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="requestNumber"
                control={control}
                rules={{ required: 'شماره درخواست الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="شماره درخواست"
                    fullWidth
                    error={!!errors.requestNumber}
                    helperText={errors.requestNumber?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="department"
                control={control}
                rules={{ required: 'دپارتمان الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="دپارتمان"
                    fullWidth
                    error={!!errors.department}
                    helperText={errors.department?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="requestDate"
                control={control}
                rules={{ required: 'تاریخ درخواست الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ درخواست"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.requestDate}
                    helperText={errors.requestDate?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="requiredDate"
                control={control}
                rules={{ required: 'تاریخ مورد نیاز الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ مورد نیاز"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.requiredDate}
                    helperText={errors.requiredDate?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="priority"
                control={control}
                rules={{ required: 'اولویت الزامی است' }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.priority}>
                    <InputLabel>اولویت</span>
                    <Select {...field} label="اولویت">
                      {priorityOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          <div>
                            <Tag 
                              label={option.label} 
                              size="small"
                              color={
                                option.value === 'فوری' ? 'error' :
                                option.value === 'زیاد' ? 'warning' :
                                option.value === 'متوسط' ? 'primary' :
                                'default'
                              }
                            />
                          </div>
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.priority && (
                      <FormHelperText>{errors.priority.message}</FormHelperText>
                    )}
                  </div>
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
                                option.value === 'تکمیل شده' ? 'success' :
                                option.value === 'رد شده' ? 'error' :
                                option.value === 'تأیید شده' ? 'primary' :
                                'default'
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
                name="estimatedCost"
                control={control}
                rules={{ 
                  required: 'هزینه تخمینی الزامی است',
                  pattern: {
                    value: /^\d+(\.\d{1,2})?$/,
                    message: 'هزینه باید عدد معتبر باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="هزینه تخمینی (تومان)"
                    fullWidth
                    error={!!errors.estimatedCost}
                    helperText={errors.estimatedCost?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="description"
                control={control}
                rules={{ required: 'توضیحات الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="توضیحات"
                    multiline
                    rows={3}
                    fullWidth
                    error={!!errors.description}
                    helperText={errors.description?.message}
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
            {isSubmitting ? 'در حال ذخیره...' : (request ? 'ویرایش' : 'ذخیره')}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 