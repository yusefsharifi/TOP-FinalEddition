import React, { useState, useEffect } from 'react';
import { Alert, AutoComplete, Button, Card, Col, Divider, Input, InputNumber, Modal, Row, Select, Table, Tag, Typography } from 'antd';
import { CloseOutlined as CancelIcon, DeleteOutlined as DeleteIcon, FileTextOutlined as ReceiptIcon, PlusOutlined as AddIcon, SaveOutlined as SaveIcon } from '@ant-design/icons';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { JournalEntry, JournalEntryFormData, JournalEntryLineFormData, ChartOfAccounts } from '../../../types/accounting';

interface JournalEntryFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: JournalEntryFormData) => void;
  entry?: JournalEntry;
  accounts: ChartOfAccounts[];
  loading?: boolean;
  nextNumber?: string;
}

export const JournalEntryForm: React.FC<JournalEntryFormProps> = ({
  open,
  onClose,
  onSubmit,
  entry,
  accounts,
  loading = false,
  nextNumber,
}) => {
  const [totalDebit, setTotalDebit] = useState(0);
  const [totalCredit, setTotalCredit] = useState(0);
  const [isBalanced, setIsBalanced] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
    setValue,
  } = useForm<JournalEntryFormData>({
    defaultValues: {
      date: new Date().toISOString().split('T')[0],
      reference: '',
      description: '',
      lines: [
        { account_id: '', debit_amount: 0, credit_amount: 0, description: '' },
        { account_id: '', debit_amount: 0, credit_amount: 0, description: '' },
      ],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'lines',
  });

  const watchedLines = watch('lines');

  useEffect(() => {
    if (entry) {
      reset({
        date: entry.date.split('T')[0],
        reference: entry.reference,
        description: entry.description,
        lines: [], // Will be populated from API
      });
    } else {
      reset({
        date: new Date().toISOString().split('T')[0],
        reference: '',
        description: '',
        lines: [
          { account_id: '', debit_amount: 0, credit_amount: 0, description: '' },
          { account_id: '', debit_amount: 0, credit_amount: 0, description: '' },
        ],
      });
    }
  }, [entry, reset]);

  // Calculate totals when lines change
  useEffect(() => {
    const debitTotal = watchedLines.reduce((sum, line) => sum + (line.debit_amount || 0), 0);
    const creditTotal = watchedLines.reduce((sum, line) => sum + (line.credit_amount || 0), 0);
    
    setTotalDebit(debitTotal);
    setTotalCredit(creditTotal);
    setIsBalanced(Math.abs(debitTotal - creditTotal) < 0.01);
  }, [watchedLines]);

  const handleFormSubmit = (data: JournalEntryFormData) => {
    if (!isBalanced) {
      alert('جمع بدهکار و بستانکار باید برابر باشد');
      return;
    }
    onSubmit(data);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const addLine = () => {
    append({ account_id: '', debit_amount: 0, credit_amount: 0, description: '' });
  };

  const removeLine = (index: number) => {
    if (fields.length > 2) {
      remove(index);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount);
  };

  const getAccountLabel = (accountId: string) => {
    const account = accounts.find(acc => acc.id === accountId);
    return account ? `${account.code} - ${account.name}` : '';
  };

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>
        <div style={{  display: 'flex', alignItems: 'center', gap: 1  }}>
          <ReceiptIcon />
          <Typography.Title level={4}>
            {entry ? 'ویرایش سند حسابداری' : 'افزودن سند حسابداری جدید'}
          </Typography.Title>
        </div>
      </div>
      
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            {/* Header Information */}
            <Col xs={Math.round(12 / 12 * 24)}>
              <div style={{  p: 2, bgcolor: 'grey.50', borderRadius: 1, mb: 2  }}>
                <Row gutter={[16, 16]}>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Controller
                      name="date"
                      control={control}
                      rules={{ required: 'تاریخ الزامی است' }}
                      render={({ field }) => (
                        <Input
                          {...field}
                          label="تاریخ سند"
                          type="date"
                          fullWidth
                          error={!!errors.date}
                          helperText={errors.date?.message}
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
                          placeholder="شماره فاکتور، شماره چک و..."
                        />
                      )}
                    />
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Input
                      label="شماره سند"
                      value={nextNumber || 'خودکار'}
                      fullWidth
                      disabled
                      helperText="شماره سند به صورت خودکار تولید می‌شود"
                    />
                  </Col>
                </Row>
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
                        label="توضیحات سند"
                        fullWidth
                        multiline
                        rows={2}
                        error={!!errors.description}
                        helperText={errors.description?.message}
                        placeholder="توضیحات کلی سند..."
                      />
                    )}
                  />
                </Col>
              </div>
            </Col>

            {/* Lines Section */}
            <Col xs={Math.round(12 / 12 * 24)}>
              <div style={{  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2  }}>
                <Typography.Title level={4}>ردیف‌های سند</Typography.Title>
                <Button
                  startIcon={<AddIcon />}
                  onClick={addLine}
                  variant="outlined"
                  size="small"
                >
                  افزودن ردیف
                </Button>
              </div>

              <TableContainer component={Paper} style={{  maxHeight: 400  }}>
                <Table stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>ردیف</TableCell>
                      <TableCell>حساب</TableCell>
                      <TableCell align="right">بدهکار</TableCell>
                      <TableCell align="right">بستانکار</TableCell>
                      <TableCell>توضیحات</TableCell>
                      <TableCell align="center">عملیات</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {fields.map((field, index) => (
                      <TableRow key={field.id}>
                        <TableCell>{index + 1}</TableCell>
                        <TableCell>
                          <Controller
                            name={`lines.${index}.account_id`}
                            control={control}
                            rules={{ required: 'حساب الزامی است' }}
                            render={({ field }) => (
                              <Autocomplete
                                {...field}
                                options={accounts}
                                getOptionLabel={(option) => `${option.code} - ${option.name}`}
                                isOptionEqualToValue={(option, value) => option.id === value.id}
                                onChange={(_, newValue) => field.onChange(newValue?.id || '')}
                                renderInput={(params) => (
                                  <Input
                                    {...params}
                                    size="small"
                                    error={!!errors.lines?.[index]?.account_id}
                                    helperText={errors.lines?.[index]?.account_id?.message}
                                    placeholder="انتخاب حساب"
                                  />
                                )}
                                noOptionsText="هیچ حسابی یافت نشد"
                                clearOnBlur
                                clearOnEscape
                              />
                            )}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Controller
                            name={`lines.${index}.debit_amount`}
                            control={control}
                            rules={{ min: { value: 0, message: 'مبلغ نمی‌تواند منفی باشد' } }}
                            render={({ field }) => (
                              <Input
                                {...field}
                                type="number"
                                size="small"
                                inputProps={{ min: 0, step: 0.01 }}
                                error={!!errors.lines?.[index]?.debit_amount}
                                helperText={errors.lines?.[index]?.debit_amount?.message}
                                onChange={(e) => {
                                  const value = parseFloat(e.target.value) || 0;
                                  field.onChange(value);
                                  // Clear credit amount when debit is entered
                                  if (value > 0) {
                                    setValue(`lines.${index}.credit_amount`, 0);
                                  }
                                }}
                              />
                            )}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Controller
                            name={`lines.${index}.credit_amount`}
                            control={control}
                            rules={{ min: { value: 0, message: 'مبلغ نمی‌تواند منفی باشد' } }}
                            render={({ field }) => (
                              <Input
                                {...field}
                                type="number"
                                size="small"
                                inputProps={{ min: 0, step: 0.01 }}
                                error={!!errors.lines?.[index]?.credit_amount}
                                helperText={errors.lines?.[index]?.credit_amount?.message}
                                onChange={(e) => {
                                  const value = parseFloat(e.target.value) || 0;
                                  field.onChange(value);
                                  // Clear debit amount when credit is entered
                                  if (value > 0) {
                                    setValue(`lines.${index}.debit_amount`, 0);
                                  }
                                }}
                              />
                            )}
                          />
                        </TableCell>
                        <TableCell>
                          <Controller
                            name={`lines.${index}.description`}
                            control={control}
                            rules={{ maxLength: { value: 100, message: 'توضیحات نمی‌تواند بیش از 100 کاراکتر باشد' } }}
                            render={({ field }) => (
                              <Input
                                {...field}
                                size="small"
                                fullWidth
                                error={!!errors.lines?.[index]?.description}
                                helperText={errors.lines?.[index]?.description?.message}
                                placeholder="توضیحات ردیف..."
                              />
                            )}
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Button type="text" size="small" onClick={() => removeLine(index)}
                            disabled={fields.length <= 2}
                          >
                            <DeleteIcon />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </Col>

            {/* Totals Section */}
            <Col xs={Math.round(12 / 12 * 24)}>
              <div style={{  p: 2, bgcolor: 'grey.50', borderRadius: 1  }}>
                <Row gutter={[16, 16]}>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Typography.Title level={4}>
                      جمع بدهکار: {formatCurrency(totalDebit)}
                    </Typography.Title>
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Typography.Title level={4}>
                      جمع بستانکار: {formatCurrency(totalCredit)}
                    </Typography.Title>
                  </Col>
                  <Col xs={Math.round(12 / 12 * 24)}>
                    <Tag
                      label={isBalanced ? 'متوازن' : 'نامتوازن'}
                      color={isBalanced ? 'success' : 'error'}
                      variant="outlined"
                    />
                  </Col>
                </Row>
                
                {!isBalanced && (
                  <Alert severity="error" style={{  mt: 2  }}>
                    جمع بدهکار و بستانکار باید برابر باشد. تفاوت: {formatCurrency(Math.abs(totalDebit - totalCredit))}
                  </Alert>
                )}
              </div>
            </Col>
          </Row>
        </div>

        <div>
          <Button onClick={handleClose} disabled={loading}>
            انصراف
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !isBalanced}
            startIcon={<SaveIcon />}
            style={{  minWidth: 120  }}
          >
            {loading ? 'در حال ذخیره...' : entry ? 'ویرایش' : 'ذخیره'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 