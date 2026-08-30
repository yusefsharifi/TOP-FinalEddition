import React, { useEffect } from 'react';
import { Button, Col, Input, InputNumber, Modal, Row, Select, Tag, Typography } from 'antd';
import { useForm, Controller } from 'react-hook-form';
import { PurchaseInvoice } from '../../../types/procurement';

interface PurchaseInvoiceFormProps {
  open: boolean;
  onClose: () => void;
  invoice: PurchaseInvoice | null;
  onSave: (data: any) => void;
}

const statusOptions = [
  { value: 'در انتظار پرداخت', label: 'در انتظار پرداخت' },
  { value: 'پرداخت شده', label: 'پرداخت شده' },
  { value: 'تأخیر', label: 'تأخیر' }
];

const paymentMethodOptions = [
  { value: 'نقدی', label: 'نقدی' },
  { value: 'چک', label: 'چک' },
  { value: 'کارت اعتباری', label: 'کارت اعتباری' },
  { value: 'انتقال بانکی', label: 'انتقال بانکی' }
];

export const PurchaseInvoiceForm: React.FC<PurchaseInvoiceFormProps> = ({
  open,
  onClose,
  invoice,
  onSave
}) => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm({
    defaultValues: {
      invoiceNumber: '',
      supplierName: '',
      dueDate: '',
      totalAmount: '',
      status: 'در انتظار پرداخت',
      paymentMethod: 'نقدی',
      notes: ''
    }
  });

  useEffect(() => {
    if (invoice) {
      reset({
        invoiceNumber: invoice.invoiceNumber,
        supplierName: invoice.supplierName,
        dueDate: invoice.dueDate,
        totalAmount: invoice.totalAmount.toString(),
        status: invoice.status,
        paymentMethod: invoice.paymentMethod,
        notes: invoice.notes || ''
      });
    } else {
      reset({
        invoiceNumber: '',
        supplierName: '',
        dueDate: '',
        totalAmount: '',
        status: 'در انتظار پرداخت',
        paymentMethod: 'نقدی',
        notes: ''
      });
    }
  }, [invoice, reset]);

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
          {invoice ? 'ویرایش فاکتور خرید' : 'افزودن فاکتور خرید جدید'}
        </Typography.Title>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="invoiceNumber"
                control={control}
                rules={{ required: 'شماره فاکتور الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="شماره فاکتور"
                    fullWidth
                    error={!!errors.invoiceNumber}
                    helperText={errors.invoiceNumber?.message}
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
                name="dueDate"
                control={control}
                rules={{ required: 'تاریخ سررسید الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ سررسید"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.dueDate}
                    helperText={errors.dueDate?.message}
                  />
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
                                option.value === 'پرداخت شده' ? 'success' :
                                option.value === 'تأخیر' ? 'error' :
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
                name="paymentMethod"
                control={control}
                rules={{ required: 'روش پرداخت الزامی است' }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.paymentMethod}>
                    <InputLabel>روش پرداخت</span>
                    <Select {...field} label="روش پرداخت">
                      {paymentMethodOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.paymentMethod && (
                      <FormHelperText>{errors.paymentMethod.message}</FormHelperText>
                    )}
                  </div>
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
            {isSubmitting ? 'در حال ذخیره...' : (invoice ? 'ویرایش' : 'ذخیره')}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 