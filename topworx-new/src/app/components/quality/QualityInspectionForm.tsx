import React, { useEffect } from 'react';
import { Button, Card, Col, Divider, Input, InputNumber, Modal, Row, Select, Tag, Typography } from 'antd';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { PlusOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { QualityInspection, QualityStatus, InspectionType } from '../../../types/quality';

interface QualityInspectionFormProps {
  open: boolean;
  onClose: () => void;
  inspection: QualityInspection | null;
  onSave: (data: any) => void;
}

const inspectionTypeOptions: { value: InspectionType; label: string }[] = [
  { value: 'incoming', label: 'بازرسی ورودی' },
  { value: 'in_process', label: 'بازرسی فرآیند' },
  { value: 'final', label: 'بازرسی نهایی' },
  { value: 'random', label: 'بازرسی تصادفی' },
  { value: 'special', label: 'بازرسی ویژه' }
];

const statusOptions: { value: QualityStatus; label: string }[] = [
  { value: 'pending', label: 'در انتظار' },
  { value: 'in_progress', label: 'در حال انجام' },
  { value: 'passed', label: 'قبول' },
  { value: 'failed', label: 'رد' },
  { value: 'conditional', label: 'مشروط' },
  { value: 'cancelled', label: 'لغو شده' }
];

export const QualityInspectionForm: React.FC<QualityInspectionFormProps> = ({
  open,
  onClose,
  inspection,
  onSave
}) => {
  const {
    control,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting }
  } = useForm({
    defaultValues: {
      inspectionNumber: '',
      type: 'incoming' as InspectionType,
      productId: '',
      productName: '',
      batchNumber: '',
      lotNumber: '',
      quantity: '',
      inspectedQuantity: '',
      passedQuantity: '',
      failedQuantity: '',
      status: 'pending' as QualityStatus,
      inspectorId: '',
      inspectorName: '',
      inspectionDate: '',
      nextInspectionDate: '',
      specifications: [{
        parameter: '',
        specification: '',
        unit: '',
        minValue: '',
        maxValue: '',
        targetValue: '',
        actualValue: '',
        isConforming: true,
        remarks: ''
      }],
      notes: ''
    }
  });

  const { fields: specFields, append: appendSpec, remove: removeSpec } = useFieldArray({
    control,
    name: 'specifications'
  });

  const watchedSpecs = watch('specifications');

  useEffect(() => {
    if (inspection) {
      reset({
        inspectionNumber: inspection.inspectionNumber,
        type: inspection.type,
        productId: inspection.productId?.toString() || '',
        productName: inspection.productName || '',
        batchNumber: inspection.batchNumber || '',
        lotNumber: inspection.lotNumber || '',
        quantity: inspection.quantity.toString(),
        inspectedQuantity: inspection.inspectedQuantity.toString(),
        passedQuantity: inspection.passedQuantity.toString(),
        failedQuantity: inspection.failedQuantity.toString(),
        status: inspection.status,
        inspectorId: inspection.inspectorId.toString(),
        inspectorName: inspection.inspectorName,
        inspectionDate: inspection.inspectionDate,
        nextInspectionDate: inspection.nextInspectionDate || '',
        specifications: inspection.specifications.length > 0 ? inspection.specifications.map(spec => ({
          parameter: spec.parameter,
          specification: spec.specification,
          unit: spec.unit,
          minValue: spec.minValue?.toString() || '',
          maxValue: spec.maxValue?.toString() || '',
          targetValue: spec.targetValue?.toString() || '',
          actualValue: spec.actualValue?.toString() || '',
          isConforming: spec.isConforming,
          remarks: spec.remarks || ''
        })) : [{
          parameter: '',
          specification: '',
          unit: '',
          minValue: '',
          maxValue: '',
          targetValue: '',
          actualValue: '',
          isConforming: true,
          remarks: ''
        }],
        notes: inspection.notes || ''
      });
    } else {
      reset({
        inspectionNumber: '',
        type: 'incoming',
        productId: '',
        productName: '',
        batchNumber: '',
        lotNumber: '',
        quantity: '',
        inspectedQuantity: '',
        passedQuantity: '',
        failedQuantity: '',
        status: 'pending',
        inspectorId: '',
        inspectorName: '',
        inspectionDate: '',
        nextInspectionDate: '',
        specifications: [{
          parameter: '',
          specification: '',
          unit: '',
          minValue: '',
          maxValue: '',
          targetValue: '',
          actualValue: '',
          isConforming: true,
          remarks: ''
        }],
        notes: ''
      });
    }
  }, [inspection, reset]);

  const onSubmit = (data: any) => {
    onSave({
      ...data,
      quantity: parseInt(data.quantity),
      inspectedQuantity: parseInt(data.inspectedQuantity),
      passedQuantity: parseInt(data.passedQuantity),
      failedQuantity: parseInt(data.failedQuantity),
      inspectorId: parseInt(data.inspectorId),
      specifications: data.specifications.map((spec: any) => ({
        ...spec,
        minValue: spec.minValue ? parseFloat(spec.minValue) : undefined,
        maxValue: spec.maxValue ? parseFloat(spec.maxValue) : undefined,
        targetValue: spec.targetValue ? parseFloat(spec.targetValue) : undefined,
        actualValue: spec.actualValue ? parseFloat(spec.actualValue) : undefined
      }))
    });
  };

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>
        <Typography.Title level={4}>
          {inspection ? 'ویرایش بازرسی کیفیت' : 'افزودن بازرسی کیفیت جدید'}
        </Typography.Title>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            {/* اطلاعات اصلی */}
            <Col xs={Math.round(12 / 12 * 24)}>
              <Typography.Title level={4}>اطلاعات اصلی</Typography.Title>
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="inspectionNumber"
                control={control}
                rules={{ required: 'شماره بازرسی الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="شماره بازرسی"
                    fullWidth
                    error={!!errors.inspectionNumber}
                    helperText={errors.inspectionNumber?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="type"
                control={control}
                rules={{ required: 'نوع بازرسی الزامی است' }}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.type}>
                    <InputLabel>نوع بازرسی</span>
                    <Select {...field} label="نوع بازرسی">
                      {inspectionTypeOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          <div>
                            <Tag 
                              label={option.label} 
                              size="small"
                              color={
                                option.value === 'incoming' ? 'primary' :
                                option.value === 'in_process' ? 'info' :
                                option.value === 'final' ? 'success' :
                                option.value === 'random' ? 'warning' :
                                'secondary'
                              }
                            />
                          </div>
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
                name="productName"
                control={control}
                rules={{ required: 'نام محصول/خدمت الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="محصول/خدمت"
                    fullWidth
                    error={!!errors.productName}
                    helperText={errors.productName?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="batchNumber"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="شماره دسته"
                    fullWidth
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="quantity"
                control={control}
                rules={{ 
                  required: 'تعداد کل الزامی است',
                  pattern: {
                    value: /^\d+$/,
                    message: 'تعداد باید عدد صحیح باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تعداد کل"
                    type="number"
                    fullWidth
                    error={!!errors.quantity}
                    helperText={errors.quantity?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="inspectedQuantity"
                control={control}
                rules={{ 
                  required: 'تعداد بازرسی شده الزامی است',
                  pattern: {
                    value: /^\d+$/,
                    message: 'تعداد باید عدد صحیح باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تعداد بازرسی شده"
                    type="number"
                    fullWidth
                    error={!!errors.inspectedQuantity}
                    helperText={errors.inspectedQuantity?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="passedQuantity"
                control={control}
                rules={{ 
                  required: 'تعداد قبول الزامی است',
                  pattern: {
                    value: /^\d+$/,
                    message: 'تعداد باید عدد صحیح باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تعداد قبول"
                    type="number"
                    fullWidth
                    error={!!errors.passedQuantity}
                    helperText={errors.passedQuantity?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="failedQuantity"
                control={control}
                rules={{ 
                  required: 'تعداد رد الزامی است',
                  pattern: {
                    value: /^\d+$/,
                    message: 'تعداد باید عدد صحیح باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تعداد رد"
                    type="number"
                    fullWidth
                    error={!!errors.failedQuantity}
                    helperText={errors.failedQuantity?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="inspectorName"
                control={control}
                rules={{ required: 'نام بازرس الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="نام بازرس"
                    fullWidth
                    error={!!errors.inspectorName}
                    helperText={errors.inspectorName?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="inspectionDate"
                control={control}
                rules={{ required: 'تاریخ بازرسی الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ بازرسی"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.inspectionDate}
                    helperText={errors.inspectionDate?.message}
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
                                option.value === 'passed' ? 'success' :
                                option.value === 'failed' ? 'error' :
                                option.value === 'conditional' ? 'warning' :
                                option.value === 'in_progress' ? 'info' :
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
              <Divider style={{  my: 2  }} />
              <Typography.Title level={4}>مشخصات فنی</Typography.Title>
            </Col>

            {specFields.map((field, index) => (
              <Col xs={Math.round(12 / 12 * 24)}>
                <Card variant="outlined">
                  <div>
                    <div>
                      <Typography.Title level={5}>مشخصه {index + 1}</Typography.Title>
                      <Button type="text" 
                        onClick={() => removeSpec(index)} 
                        color="error" 
                        size="small"
                        disabled={specFields.length === 1}
                      >
                        <DeleteIcon />
                      </Button>
                    </div>
                    
                    <Row gutter={[16, 16]}>
                      <Col xs={Math.round(12 / 12 * 24)}>
                        <Controller
                          name={`specifications.${index}.parameter`}
                          control={control}
                          rules={{ required: 'پارامتر الزامی است' }}
                          render={({ field }) => (
                            <Input
                              {...field}
                              label="پارامتر"
                              fullWidth
                              error={!!errors.specifications?.[index]?.parameter}
                              helperText={errors.specifications?.[index]?.parameter?.message}
                            />
                          )}
                        />
                      </Col>
                      
                      <Col xs={Math.round(12 / 12 * 24)}>
                        <Controller
                          name={`specifications.${index}.specification`}
                          control={control}
                          rules={{ required: 'مشخصه الزامی است' }}
                          render={({ field }) => (
                            <Input
                              {...field}
                              label="مشخصه"
                              fullWidth
                              error={!!errors.specifications?.[index]?.specification}
                              helperText={errors.specifications?.[index]?.specification?.message}
                            />
                          )}
                        />
                      </Col>
                      
                      <Col xs={Math.round(12 / 12 * 24)}>
                        <Controller
                          name={`specifications.${index}.unit`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              {...field}
                              label="واحد"
                              fullWidth
                            />
                          )}
                        />
                      </Col>
                      
                      <Col xs={Math.round(12 / 12 * 24)}>
                        <Controller
                          name={`specifications.${index}.minValue`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              {...field}
                              label="حداقل"
                              type="number"
                              fullWidth
                            />
                          )}
                        />
                      </Col>
                      
                      <Col xs={Math.round(12 / 12 * 24)}>
                        <Controller
                          name={`specifications.${index}.maxValue`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              {...field}
                              label="حداکثر"
                              type="number"
                              fullWidth
                            />
                          )}
                        />
                      </Col>
                      
                      <Col xs={Math.round(12 / 12 * 24)}>
                        <Controller
                          name={`specifications.${index}.actualValue`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              {...field}
                              label="مقدار واقعی"
                              type="number"
                              fullWidth
                            />
                          )}
                        />
                      </Col>
                      
                      <Col xs={Math.round(12 / 12 * 24)}>
                        <Controller
                          name={`specifications.${index}.remarks`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              {...field}
                              label="توضیحات"
                              multiline
                              rows={2}
                              fullWidth
                            />
                          )}
                        />
                      </Col>
                    </Row>
                  </div>
                </Card>
              </Col>
            ))}

            <Col xs={Math.round(12 / 12 * 24)}>
              <Button
                startIcon={<AddIcon />}
                onClick={() => appendSpec({
                  parameter: '',
                  specification: '',
                  unit: '',
                  minValue: '',
                  maxValue: '',
                  targetValue: '',
                  actualValue: '',
                  isConforming: true,
                  remarks: ''
                })}
                variant="outlined"
              >
                افزودن مشخصه جدید
              </Button>
            </Col>

            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="notes"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="یادداشت‌ها"
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
            {isSubmitting ? 'در حال ذخیره...' : (inspection ? 'ویرایش' : 'ذخیره')}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 