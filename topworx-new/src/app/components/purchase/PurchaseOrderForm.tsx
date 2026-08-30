import React, { useEffect } from 'react';
import { Button, Col, Input, InputNumber, Modal, Row, Select, Tag, Typography } from 'antd';
import { useForm, Controller } from 'react-hook-form';
import { PurchaseOrder, PurchaseOrderStatus } from '../../../types/procurement';

interface PurchaseOrderFormProps {
  open: boolean;
  onClose: () => void;
  order: PurchaseOrder | null;
  onSave: (data: any) => void;
}

const statusOptions: { value: PurchaseOrderStatus; label: string }[] = [
  { value: 'در انتظار تأیید', label: 'در انتظار تأیید' },
  { value: 'تأیید شده', label: 'تأیید شده' },
  { value: 'ارسال شده', label: 'ارسال شده' },
  { value: 'دریافت شده', label: 'دریافت شده' },
  { value: 'لغو شده', label: 'لغو شده' }
];

export const PurchaseOrderForm: React.FC<PurchaseOrderFormProps> = ({
  open,
  onClose,
  order,
  onSave
}) => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm({
    defaultValues: {
      orderNumber: '',
      supplierName: '',
      orderDate: '',
      expectedDeliveryDate: '',
      status: 'در انتظار تأیید' as PurchaseOrderStatus,
      totalAmount: '',
      notes: ''
    }
  });

  useEffect(() => {
    if (order) {
      reset({
        orderNumber: order.orderNumber,
        supplierName: order.supplierName,
        orderDate: order.orderDate,
        expectedDeliveryDate: order.expectedDeliveryDate,
        status: order.status,
        totalAmount: order.totalAmount.toString(),
        notes: order.notes || ''
      });
    } else {
      reset({
        orderNumber: '',
        supplierName: '',
        orderDate: '',
        expectedDeliveryDate: '',
        status: 'در انتظار تأیید',
        totalAmount: '',
        notes: ''
      });
    }
  }, [order, reset]);

  const onSubmit = (data: any) => {
    onSave({
      ...data,
      totalAmount: parseFloat(data.totalAmount)
    });
  };

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>
        <Typography.Title level={4}>
          {order ? 'ویرایش سفارش خرید' : 'افزودن سفارش خرید جدید'}
        </Typography.Title>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="orderNumber"
                control={control}
                rules={{ required: 'شماره سفارش الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="شماره سفارش"
                    fullWidth
                    error={!!errors.orderNumber}
                    helperText={errors.orderNumber?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="supplierName"
                control={control}
                rules={{ required: 'نام تأمین‌کننده الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="نام تأمین‌کننده"
                    fullWidth
                    error={!!errors.supplierName}
                    helperText={errors.supplierName?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="orderDate"
                control={control}
                rules={{ required: 'تاریخ سفارش الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ سفارش"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.orderDate}
                    helperText={errors.orderDate?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="expectedDeliveryDate"
                control={control}
                rules={{ required: 'تاریخ تحویل مورد انتظار الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ تحویل مورد انتظار"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.expectedDeliveryDate}
                    helperText={errors.expectedDeliveryDate?.message}
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
                                option.value === 'دریافت شده' ? 'success' :
                                option.value === 'لغو شده' ? 'error' :
                                option.value === 'ارسال شده' ? 'primary' :
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
                name="totalAmount"
                control={control}
                rules={{ 
                  required: 'مبلغ کل الزامی است',
                  pattern: {
                    value: /^\d+(\.\d{1,2})?$/,
                    message: 'مبلغ باید عدد معتبر باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="مبلغ کل (تومان)"
                    fullWidth
                    error={!!errors.totalAmount}
                    helperText={errors.totalAmount?.message}
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
                    rows={3}
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
            {isSubmitting ? 'در حال ذخیره...' : (order ? 'ویرایش' : 'ذخیره')}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 