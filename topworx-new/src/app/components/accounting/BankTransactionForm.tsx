import React from 'react';
import { AutoComplete, Button, Col, Input, InputNumber, Modal, Row, Select, Typography } from 'antd';
import { CloseOutlined as CancelIcon, FileTextOutlined as ReceiptIcon, SaveOutlined as SaveIcon } from '@ant-design/icons';
import { useForm, Controller } from 'react-hook-form';
import { BankTransaction, BankTransactionFormData, BankAccount } from '../../../types/accounting';

interface BankTransactionFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: BankTransactionFormData) => void;
  transaction?: BankTransaction;
  bankAccounts: BankAccount[];
  loading?: boolean;
}

const transactionTypes = [
  { value: 'deposit', label: 'واریز' },
  { value: 'withdrawal', label: 'برداشت' },
  { value: 'transfer', label: 'انتقال' },
  { value: 'fee', label: 'کارمزد' },
  { value: 'interest', label: 'سود' },
];

export const BankTransactionForm: React.FC<BankTransactionFormProps> = ({
  open,
  onClose,
  onSubmit,
  transaction,
  bankAccounts,
  loading = false,
}) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<BankTransactionFormData>({
    defaultValues: {
      bank_account_id: transaction?.bank_account_id || '',
      transaction_date: transaction?.transaction_date || new Date().toISOString().split('T')[0],
      value_date: transaction?.value_date || new Date().toISOString().split('T')[0],
      reference: transaction?.reference || '',
      description: transaction?.description || '',
      amount: transaction?.amount || 0,
      type: transaction?.type || 'deposit',
    },
  });

  React.useEffect(() => {
    if (transaction) {
      reset({
        bank_account_id: transaction.bank_account_id,
        transaction_date: transaction.transaction_date.split('T')[0],
        value_date: transaction.value_date.split('T')[0],
        reference: transaction.reference,
        description: transaction.description,
        amount: transaction.amount,
        type: transaction.type,
      });
    } else {
      reset({
        bank_account_id: '',
        transaction_date: new Date().toISOString().split('T')[0],
        value_date: new Date().toISOString().split('T')[0],
        reference: '',
        description: '',
        amount: 0,
        type: 'deposit',
      });
    }
  }, [transaction, reset]);

  const handleFormSubmit = (data: BankTransactionFormData) => {
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
          <ReceiptIcon />
          <Typography.Title level={4}>
            {transaction ? 'ویرایش تراکنش بانکی' : 'افزودن تراکنش بانکی جدید'}
          </Typography.Title>
        </div>
      </div>
      
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="bank_account_id"
                control={control}
                rules={{ required: 'حساب بانکی الزامی است' }}
                render={({ field }) => (
                  <Autocomplete
                    {...field}
                    options={bankAccounts}
                    getOptionLabel={(option) => `${option.name} - ${option.account_number}`}
                    isOptionEqualToValue={(option, value) => option.id === value.id}
                    onChange={(_, newValue) => field.onChange(newValue?.id || '')}
                    renderInput={(params) => (
                      <Input
                        {...params}
                        label="حساب بانکی"
                        error={!!errors.bank_account_id}
                        helperText={errors.bank_account_id?.message}
                        placeholder="انتخاب حساب بانکی"
                      />
                    )}
                    noOptionsText="هیچ حساب بانکی یافت نشد"
                    clearOnBlur
                    clearOnEscape
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="type"
                control={control}
                rules={{ required: 'نوع تراکنش الزامی است' }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.type}>
                    <InputLabel>نوع تراکنش</span>
                    <Select {...field} label="نوع تراکنش">
                      {transactionTypes.map((type) => (
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
                name="transaction_date"
                control={control}
                rules={{ required: 'تاریخ تراکنش الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ تراکنش"
                    type="date"
                    fullWidth
                    error={!!errors.transaction_date}
                    helperText={errors.transaction_date?.message}
                    InputLabelProps={{ shrink: true }}
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="value_date"
                control={control}
                rules={{ required: 'تاریخ ارزش الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ ارزش"
                    type="date"
                    fullWidth
                    error={!!errors.value_date}
                    helperText={errors.value_date?.message}
                    InputLabelProps={{ shrink: true }}
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="reference"
                control={control}
                rules={{
                  required: 'مرجع الزامی است',
                  maxLength: { value: 50, message: 'مرجع نمی‌تواند بیش از 50 کاراکتر باشد' }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="مرجع"
                    fullWidth
                    error={!!errors.reference}
                    helperText={errors.reference?.message}
                    placeholder="شماره چک، شماره فیش و..."
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="amount"
                control={control}
                rules={{
                  required: 'مبلغ الزامی است',
                  min: { value: 0.01, message: 'مبلغ باید بزرگتر از صفر باشد' }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="مبلغ"
                    type="number"
                    fullWidth
                    error={!!errors.amount}
                    helperText={errors.amount?.message}
                    inputProps={{ min: 0.01, step: 0.01 }}
                    placeholder="0"
                  />
                )}
              />
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="description"
                control={control}
                rules={{
                  required: 'توضیحات الزامی است',
                  maxLength: { value: 200, message: 'توضیحات نمی‌تواند بیش از 200 کاراکتر باشد' }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="توضیحات"
                    fullWidth
                    multiline
                    rows={3}
                    error={!!errors.description}
                    helperText={errors.description?.message}
                    placeholder="توضیحات مربوط به تراکنش..."
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
            {loading ? 'در حال ذخیره...' : transaction ? 'ویرایش' : 'افزودن'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 