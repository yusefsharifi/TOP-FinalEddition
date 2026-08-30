import React, { useState } from 'react';
import { Alert, Button, Card, Col, Divider, Input, InputNumber, Row, Switch, Typography } from 'antd';
import { useForm, Controller } from 'react-hook-form';

interface PurchaseSettings {
  autoApproveRequests: boolean;
  autoGenerateOrders: boolean;
  defaultPaymentTerms: number;
  defaultDeliveryTerms: number;
  maxOrderAmount: number;
  minOrderAmount: number;
  requireApproval: boolean;
  emailNotifications: boolean;
  smsNotifications: boolean;
  defaultCurrency: string;
  taxRate: number;
  discountRate: number;
}

export const PurchaseSettings: React.FC = () => {
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const { control, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<PurchaseSettings>({
    defaultValues: {
      autoApproveRequests: false,
      autoGenerateOrders: false,
      defaultPaymentTerms: 30,
      defaultDeliveryTerms: 14,
      maxOrderAmount: 10000000,
      minOrderAmount: 100000,
      requireApproval: true,
      emailNotifications: true,
      smsNotifications: false,
      defaultCurrency: 'تومان',
      taxRate: 9,
      discountRate: 0
    }
  });

  const onSubmit = async (data: PurchaseSettings) => {
    try {
      // در حالت واقعی باید به API ارسال شود
      console.log('تنظیمات ذخیره شد:', data);
      setSnackbar({
        open: true,
        message: 'تنظیمات با موفقیت ذخیره شد.',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'خطا در ذخیره تنظیمات.',
        severity: 'error'
      });
    }
  };

  const handleReset = () => {
    reset();
    setSnackbar({
      open: true,
      message: 'تنظیمات به حالت پیش‌فرض بازگشت.',
      severity: 'success'
    });
  };

  return (
    <div style={{  p: 3  }}>
      <Typography.Title level={2}>
        تنظیمات تدارکات و خرید
      </Typography.Title>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Row gutter={[16, 16]}>
          {/* تنظیمات عمومی */}
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card>
              <div>
                <Typography.Title level={4}>
                  تنظیمات عمومی
                </Typography.Title>
                <Row gutter={[16, 16]}>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="defaultCurrency"
                      control={control}
                      rules={{ required: 'واحد پول پیش‌فرض الزامی است' }}
                      render={({ field }) => (
                        <Input
                          {...field}
                          label="واحد پول پیش‌فرض"
                          fullWidth
                          error={!!errors.defaultCurrency}
                          helperText={errors.defaultCurrency?.message}
                        />
                      )}
                    />
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="taxRate"
                      control={control}
                      rules={{ 
                        required: 'نرخ مالیات الزامی است',
                        min: { value: 0, message: 'نرخ مالیات باید مثبت باشد' },
                        max: { value: 100, message: 'نرخ مالیات نمی‌تواند بیشتر از 100% باشد' }
                      }}
                      render={({ field }) => (
                        <Input
                          {...field}
                          label="نرخ مالیات (%)"
                          type="number"
                          fullWidth
                          error={!!errors.taxRate}
                          helperText={errors.taxRate?.message}
                        />
                      )}
                    />
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="discountRate"
                      control={control}
                      rules={{ 
                        min: { value: 0, message: 'نرخ تخفیف باید مثبت باشد' },
                        max: { value: 100, message: 'نرخ تخفیف نمی‌تواند بیشتر از 100% باشد' }
                      }}
                      render={({ field }) => (
                        <Input
                          {...field}
                          label="نرخ تخفیف پیش‌فرض (%)"
                          type="number"
                          fullWidth
                          error={!!errors.discountRate}
                          helperText={errors.discountRate?.message}
                        />
                      )}
                    />
                  </Col>
                </Row>
              </div>
            </Card>
          </Col>

          {/* تنظیمات سفارشات */}
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card>
              <div>
                <Typography.Title level={4}>
                  تنظیمات سفارشات
                </Typography.Title>
                <Row gutter={[16, 16]}>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="defaultPaymentTerms"
                      control={control}
                      rules={{ 
                        required: 'شرایط پرداخت پیش‌فرض الزامی است',
                        min: { value: 1, message: 'حداقل 1 روز' }
                      }}
                      render={({ field }) => (
                        <Input
                          {...field}
                          label="شرایط پرداخت پیش‌فرض (روز)"
                          type="number"
                          fullWidth
                          error={!!errors.defaultPaymentTerms}
                          helperText={errors.defaultPaymentTerms?.message}
                        />
                      )}
                    />
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="defaultDeliveryTerms"
                      control={control}
                      rules={{ 
                        required: 'شرایط تحویل پیش‌فرض الزامی است',
                        min: { value: 1, message: 'حداقل 1 روز' }
                      }}
                      render={({ field }) => (
                        <Input
                          {...field}
                          label="شرایط تحویل پیش‌فرض (روز)"
                          type="number"
                          fullWidth
                          error={!!errors.defaultDeliveryTerms}
                          helperText={errors.defaultDeliveryTerms?.message}
                        />
                      )}
                    />
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="maxOrderAmount"
                      control={control}
                      rules={{ 
                        required: 'حداکثر مبلغ سفارش الزامی است',
                        min: { value: 1, message: 'مبلغ باید مثبت باشد' }
                      }}
                      render={({ field }) => (
                        <Input
                          {...field}
                          label="حداکثر مبلغ سفارش (تومان)"
                          type="number"
                          fullWidth
                          error={!!errors.maxOrderAmount}
                          helperText={errors.maxOrderAmount?.message}
                        />
                      )}
                    />
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="minOrderAmount"
                      control={control}
                      rules={{ 
                        required: 'حداقل مبلغ سفارش الزامی است',
                        min: { value: 1, message: 'مبلغ باید مثبت باشد' }
                      }}
                      render={({ field }) => (
                        <Input
                          {...field}
                          label="حداقل مبلغ سفارش (تومان)"
                          type="number"
                          fullWidth
                          error={!!errors.minOrderAmount}
                          helperText={errors.minOrderAmount?.message}
                        />
                      )}
                    />
                  </Col>
                </Row>
              </div>
            </Card>
          </Col>

          {/* تنظیمات خودکار */}
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card>
              <div>
                <Typography.Title level={4}>
                  تنظیمات خودکار
                </Typography.Title>
                <Row gutter={[16, 16]}>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="autoApproveRequests"
                      control={control}
                      render={({ field }) => (
                        <FormControlLabel
                          control={
                            <Switch
                              checked={field.value}
                              onChange={field.onChange}
                            />
                          }
                          label="تأیید خودکار درخواست‌ها"
                        />
                      )}
                    />
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="autoGenerateOrders"
                      control={control}
                      render={({ field }) => (
                        <FormControlLabel
                          control={
                            <Switch
                              checked={field.value}
                              onChange={field.onChange}
                            />
                          }
                          label="ایجاد خودکار سفارشات"
                        />
                      )}
                    />
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="requireApproval"
                      control={control}
                      render={({ field }) => (
                        <FormControlLabel
                          control={
                            <Switch
                              checked={field.value}
                              onChange={field.onChange}
                            />
                          }
                          label="نیاز به تأیید برای سفارشات"
                        />
                      )}
                    />
                  </Col>
                </Row>
              </div>
            </Card>
          </Col>

          {/* تنظیمات اعلان‌ها */}
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card>
              <div>
                <Typography.Title level={4}>
                  تنظیمات اعلان‌ها
                </Typography.Title>
                <Row gutter={[16, 16]}>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="emailNotifications"
                      control={control}
                      render={({ field }) => (
                        <FormControlLabel
                          control={
                            <Switch
                              checked={field.value}
                              onChange={field.onChange}
                            />
                          }
                          label="اعلان‌های ایمیل"
                        />
                      )}
                    />
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="smsNotifications"
                      control={control}
                      render={({ field }) => (
                        <FormControlLabel
                          control={
                            <Switch
                              checked={field.value}
                              onChange={field.onChange}
                            />
                          }
                          label="اعلان‌های پیامک"
                        />
                      )}
                    />
                  </Col>
                </Row>
              </div>
            </Card>
          </Col>
        </Row>

        <div style={{  mt: 3, display: 'flex', gap: 2  }}>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
          </Button>
          <Button
            variant="outlined"
            onClick={handleReset}
            disabled={isSubmitting}
          >
            بازگشت به پیش‌فرض
          </Button>
        </div>
      </form>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </div>
    </div>
  );
}; 