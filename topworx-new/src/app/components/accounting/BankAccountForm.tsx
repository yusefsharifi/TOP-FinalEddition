import React from 'react';
import { Button, Col, Input, InputNumber, Modal, Row, Select, Typography } from 'antd';
import { BankOutlined as AccountBalanceIcon, CloseOutlined as CancelIcon, SaveOutlined as SaveIcon } from '@ant-design/icons';
import { useForm, Controller } from 'react-hook-form';
import { BankAccount, BankAccountFormData } from '../../../types/accounting';

interface BankAccountFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: BankAccountFormData) => void;
  account?: BankAccount;
  loading?: boolean;
}

const accountTypes = [
  { value: 'checking', label: 'جاری' },
  { value: 'savings', label: 'پس‌انداز' },
  { value: 'credit', label: 'اعتباری' },
];

const currencies = [
  { value: 'IRR', label: 'ریال ایران' },
  { value: 'USD', label: 'دلار آمریکا' },
  { value: 'EUR', label: 'یورو' },
  { value: 'GBP', label: 'پوند انگلیس' },
  { value: 'AED', label: 'درهم امارات' },
  { value: 'SAR', label: 'ریال عربستان' },
];

export const BankAccountForm: React.FC<BankAccountFormProps> = ({
  open,
  onClose,
  onSubmit,
  account,
  loading = false,
}) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<BankAccountFormData>({
    defaultValues: {
      name: account?.name || '',
      account_number: account?.account_number || '',
      bank_name: account?.bank_name || '',
      branch_name: account?.branch_name || '',
      currency: account?.currency || 'IRR',
      opening_balance: account?.opening_balance || 0,
      account_type: account?.account_type || 'checking',
    },
  });

  React.useEffect(() => {
    if (account) {
      reset({
        name: account.name,
        account_number: account.account_number,
        bank_name: account.bank_name,
        branch_name: account.branch_name || '',
        currency: account.currency,
        opening_balance: account.opening_balance,
        account_type: account.account_type,
      });
    } else {
      reset({
        name: '',
        account_number: '',
        bank_name: '',
        branch_name: '',
        currency: 'IRR',
        opening_balance: 0,
        account_type: 'checking',
      });
    }
  }, [account, reset]);

  const handleFormSubmit = (data: BankAccountFormData) => {
    onSubmit(data);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>
        <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
          <AccountBalanceIcon />
          <Typography.Title level={4}>
            {account ? 'ویرایش حساب بانکی' : 'افزودن حساب بانکی جدید'}
          </Typography.Title>
        </div>
      </div>
      
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="name"
                control={control}
                rules={{
                  required: 'نام حساب الزامی است',
                  minLength: { value: 3, message: 'نام حساب باید حداقل 3 کاراکتر باشد' },
                  maxLength: { value: 100, message: 'نام حساب نمی‌تواند بیش از 100 کاراکتر باشد' }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="نام حساب"
                    fullWidth
                    error={!!errors.name}
                    helperText={errors.name?.message}
                    placeholder="مثال: حساب جاری شرکت"
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="account_number"
                control={control}
                rules={{
                  required: 'شماره حساب الزامی است',
                  minLength: { value: 10, message: 'شماره حساب باید حداقل 10 رقم باشد' },
                  maxLength: { value: 20, message: 'شماره حساب نمی‌تواند بیش از 20 رقم باشد' },
                  pattern: {
                    value: /^[0-9]+$/,
                    message: 'شماره حساب فقط می‌تواند شامل اعداد باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="شماره حساب"
                    fullWidth
                    error={!!errors.account_number}
                    helperText={errors.account_number?.message}
                    placeholder="مثال: 1234567890"
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="bank_name"
                control={control}
                rules={{
                  required: 'نام بانک الزامی است',
                  minLength: { value: 2, message: 'نام بانک باید حداقل 2 کاراکتر باشد' },
                  maxLength: { value: 50, message: 'نام بانک نمی‌تواند بیش از 50 کاراکتر باشد' }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="نام بانک"
                    fullWidth
                    error={!!errors.bank_name}
                    helperText={errors.bank_name?.message}
                    placeholder="مثال: بانک ملی ایران"
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="branch_name"
                control={control}
                rules={{
                  maxLength: { value: 50, message: 'نام شعبه نمی‌تواند بیش از 50 کاراکتر باشد' }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="نام شعبه (اختیاری)"
                    fullWidth
                    error={!!errors.branch_name}
                    helperText={errors.branch_name?.message}
                    placeholder="مثال: شعبه مرکزی"
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="account_type"
                control={control}
                rules={{ required: 'نوع حساب الزامی است' }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.account_type}>
                    <InputLabel>نوع حساب</span>
                    <Select {...field} label="نوع حساب">
                      {accountTypes.map((type) => (
                        <MenuItem key={type.value} value={type.value}>
                          {type.label}
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.account_type && (
                      <FormHelperText>{errors.account_type.message}</FormHelperText>
                    )}
                  </div>
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="currency"
                control={control}
                rules={{ required: 'ارز الزامی است' }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.currency}>
                    <InputLabel>ارز</span>
                    <Select {...field} label="ارز">
                      {currencies.map((currency) => (
                        <MenuItem key={currency.value} value={currency.value}>
                          {currency.label}
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.currency && (
                      <FormHelperText>{errors.currency.message}</FormHelperText>
                    )}
                  </div>
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="opening_balance"
                control={control}
                rules={{
                  required: 'موجودی اولیه الزامی است',
                  min: { value: 0, message: 'موجودی اولیه نمی‌تواند منفی باشد' }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="موجودی اولیه"
                    type="number"
                    fullWidth
                    error={!!errors.opening_balance}
                    helperText={errors.opening_balance?.message}
                    inputProps={{ min: 0, step: 0.01 }}
                    placeholder="0"
                  />
                )}
              />
            </Col>
          </Row>

          {/* Validation Summary */}
          {Object.keys(errors).length > 0 && (
            <div style={{  mt: 2, p: 2, bgcolor: 'error.light', borderRadius: 1  }}>
              <Typography.Text>
                لطفاً خطاهای زیر را برطرف کنید:
              </Typography.Text>
              <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                {Object.values(errors).map((error, index) => (
                  <li key={index}>
                    <Typography.Text>
                      {error?.message}
                    </Typography.Text>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div>
          <Button onClick={handleClose} disabled={loading}>
            انصراف
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
            startIcon={<SaveIcon />}
            style={{  minWidth: 100  }}
          >
            {loading ? 'در حال ذخیره...' : account ? 'ویرایش' : 'افزودن'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 