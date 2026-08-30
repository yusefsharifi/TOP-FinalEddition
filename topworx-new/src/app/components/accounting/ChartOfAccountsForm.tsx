import React from 'react';
import { AutoComplete, Button, Col, Input, InputNumber, Modal, Row, Select, Typography } from 'antd';
import { useForm, Controller } from 'react-hook-form';
import { ChartOfAccounts, ChartOfAccountsFormData } from '../../../types/accounting';

interface ChartOfAccountsFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: ChartOfAccountsFormData) => void;
  account?: ChartOfAccounts;
  parentAccounts?: ChartOfAccounts[];
  loading?: boolean;
}

const accountTypes = [
  { value: 'asset', label: 'دارایی' },
  { value: 'liability', label: 'بدهی' },
  { value: 'equity', label: 'سرمایه' },
  { value: 'revenue', label: 'درآمد' },
  { value: 'expense', label: 'هزینه' },
];

export const ChartOfAccountsForm: React.FC<ChartOfAccountsFormProps> = ({
  open,
  onClose,
  onSubmit,
  account,
  parentAccounts = [],
  loading = false,
}) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<ChartOfAccountsFormData>({
    defaultValues: {
      code: account?.code || '',
      name: account?.name || '',
      type: account?.type || 'asset',
      parent_id: account?.parent_id || '',
      description: account?.description || '',
    },
  });

  const selectedType = watch('type');

  React.useEffect(() => {
    if (account) {
      reset({
        code: account.code,
        name: account.name,
        type: account.type,
        parent_id: account.parent_id || '',
        description: account.description || '',
      });
    } else {
      reset({
        code: '',
        name: '',
        type: 'asset',
        parent_id: '',
        description: '',
      });
    }
  }, [account, reset]);

  const handleFormSubmit = (data: ChartOfAccountsFormData) => {
    onSubmit(data);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  // Filter parent accounts based on selected type
  const filteredParentAccounts = parentAccounts.filter(
    (parent) => parent.type === selectedType && parent.id !== account?.id
  );

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>
        <Typography.Title level={4}>
          {account ? 'ویرایش حساب کل' : 'افزودن حساب کل جدید'}
        </Typography.Title>
      </div>
      
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="code"
                control={control}
                rules={{
                  required: 'کد حساب الزامی است',
                  minLength: { value: 2, message: 'کد حساب باید حداقل 2 کاراکتر باشد' },
                  maxLength: { value: 20, message: 'کد حساب نمی‌تواند بیش از 20 کاراکتر باشد' },
                  pattern: {
                    value: /^[0-9A-Za-z\-_]+$/,
                    message: 'کد حساب فقط می‌تواند شامل حروف، اعداد، خط تیره و زیرخط باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="کد حساب"
                    fullWidth
                    error={!!errors.code}
                    helperText={errors.code?.message}
                    placeholder="مثال: 1000"
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="type"
                control={control}
                rules={{ required: 'نوع حساب الزامی است' }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.type}>
                    <InputLabel>نوع حساب</span>
                    <Select {...field} label="نوع حساب">
                      {accountTypes.map((type) => (
                        <MenuItem key={type.value} value={type.value}>
                          {type.label}
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.type && (
                      <FormHelperText>{errors.type.message}</FormHelperText>
                    )}
                  </div>
                )}
              />
            </Col>

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
                    placeholder="مثال: موجودی نقدی"
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="parent_id"
                control={control}
                render={({ field }) => (
                  <Autocomplete
                    {...field}
                    options={filteredParentAccounts}
                    getOptionLabel={(option) => `${option.code} - ${option.name}`}
                    isOptionEqualToValue={(option, value) => option.id === value.id}
                    onChange={(_, newValue) => field.onChange(newValue?.id || '')}
                    renderInput={(params) => (
                      <Input
                        {...params}
                        label="حساب والد (اختیاری)"
                        placeholder="انتخاب حساب والد"
                      />
                    )}
                    noOptionsText="هیچ حسابی یافت نشد"
                    clearOnBlur
                    clearOnEscape
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="description"
                control={control}
                rules={{
                  maxLength: { value: 500, message: 'توضیحات نمی‌تواند بیش از 500 کاراکتر باشد' }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="توضیحات (اختیاری)"
                    fullWidth
                    multiline
                    rows={3}
                    error={!!errors.description}
                    helperText={errors.description?.message}
                    placeholder="توضیحات مربوط به این حساب..."
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
            style={{  minWidth: 100  }}
          >
            {loading ? 'در حال ذخیره...' : account ? 'ویرایش' : 'افزودن'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 