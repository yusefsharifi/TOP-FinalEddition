import React, { useEffect } from 'react';
import { Button, Col, Divider, Input, InputNumber, Modal, Row, Select, Tag, Typography } from 'antd';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { PlusOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { Employee, EmployeeStatus, EmployeeType, Gender, MaritalStatus } from '../../../types/hr';

interface EmployeeFormProps {
  open: boolean;
  onClose: () => void;
  employee: Employee | null;
  onSave: (data: any) => void;
}

const statusOptions: { value: EmployeeStatus; label: string }[] = [
  { value: 'active', label: 'فعال' },
  { value: 'inactive', label: 'غیرفعال' },
  { value: 'on_leave', label: 'مرخصی' },
  { value: 'terminated', label: 'فسخ شده' },
  { value: 'retired', label: 'بازنشسته' }
];

const employeeTypeOptions: { value: EmployeeType; label: string }[] = [
  { value: 'full_time', label: 'تمام وقت' },
  { value: 'part_time', label: 'نیمه وقت' },
  { value: 'contract', label: 'قراردادی' },
  { value: 'intern', label: 'کارآموز' }
];

const genderOptions: { value: Gender; label: string }[] = [
  { value: 'male', label: 'مرد' },
  { value: 'female', label: 'زن' },
  { value: 'other', label: 'سایر' }
];

const maritalStatusOptions: { value: MaritalStatus; label: string }[] = [
  { value: 'single', label: 'مجرد' },
  { value: 'married', label: 'متأهل' },
  { value: 'divorced', label: 'مطلقه' },
  { value: 'widowed', label: 'بیوه' }
];

export const EmployeeForm: React.FC<EmployeeFormProps> = ({
  open,
  onClose,
  employee,
  onSave
}) => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm({
    defaultValues: {
      employeeCode: '',
      firstName: '',
      lastName: '',
      nationalId: '',
      birthDate: '',
      gender: 'male' as Gender,
      maritalStatus: 'single' as MaritalStatus,
      email: '',
      phone: '',
      address: '',
      emergencyContact: {
        name: '',
        phone: '',
        relationship: ''
      },
      department: '',
      position: '',
      employeeType: 'full_time' as EmployeeType,
      status: 'active' as EmployeeStatus,
      hireDate: '',
      contractEndDate: '',
      salary: '',
      bankAccount: {
        bankName: '',
        accountNumber: '',
        cardNumber: ''
      },
      skills: [''],
      education: [{
        degree: '',
        field: '',
        university: '',
        graduationYear: ''
      }],
      workExperience: [{
        company: '',
        position: '',
        startDate: '',
        endDate: '',
        description: ''
      }],
      performance: {
        rating: 3,
        lastReviewDate: '',
        nextReviewDate: '',
        comments: ''
      }
    }
  });

  const { fields: skillFields, append: appendSkill, remove: removeSkill } = useFieldArray({
    control,
    name: 'skills'
  });

  const { fields: educationFields, append: appendEducation, remove: removeEducation } = useFieldArray({
    control,
    name: 'education'
  });

  const { fields: experienceFields, append: appendExperience, remove: removeExperience } = useFieldArray({
    control,
    name: 'workExperience'
  });

  useEffect(() => {
    if (employee) {
      reset({
        employeeCode: employee.employeeCode,
        firstName: employee.firstName,
        lastName: employee.lastName,
        nationalId: employee.nationalId,
        birthDate: employee.birthDate,
        gender: employee.gender,
        maritalStatus: employee.maritalStatus,
        email: employee.email,
        phone: employee.phone,
        address: employee.address,
        emergencyContact: employee.emergencyContact,
        department: employee.department,
        position: employee.position,
        employeeType: employee.employeeType,
        status: employee.status,
        hireDate: employee.hireDate,
        contractEndDate: employee.contractEndDate || '',
        salary: employee.salary.toString(),
        bankAccount: employee.bankAccount,
        skills: employee.skills.length > 0 ? employee.skills : [''],
        education: employee.education.length > 0 ? employee.education.map(edu => ({
          ...edu,
          graduationYear: edu.graduationYear.toString()
        })) : [{
          degree: '',
          field: '',
          university: '',
          graduationYear: ''
        }],
        workExperience: employee.workExperience.length > 0 ? employee.workExperience : [{
          company: '',
          position: '',
          startDate: '',
          endDate: '',
          description: ''
        }],
        performance: employee.performance
      });
    } else {
      reset({
        employeeCode: '',
        firstName: '',
        lastName: '',
        nationalId: '',
        birthDate: '',
        gender: 'male',
        maritalStatus: 'single',
        email: '',
        phone: '',
        address: '',
        emergencyContact: {
          name: '',
          phone: '',
          relationship: ''
        },
        department: '',
        position: '',
        employeeType: 'full_time',
        status: 'active',
        hireDate: '',
        contractEndDate: '',
        salary: '',
        bankAccount: {
          bankName: '',
          accountNumber: '',
          cardNumber: ''
        },
        skills: [''],
        education: [{
          degree: '',
          field: '',
          university: '',
          graduationYear: ''
        }],
        workExperience: [{
          company: '',
          position: '',
          startDate: '',
          endDate: '',
          description: ''
        }],
        performance: {
          rating: 3,
          lastReviewDate: '',
          nextReviewDate: '',
          comments: ''
        }
      });
    }
  }, [employee, reset]);

  const onSubmit = (data: any) => {
    onSave({
      ...data,
      salary: parseFloat(data.salary),
      education: data.education.map((edu: any) => ({
        ...edu,
        graduationYear: parseInt(edu.graduationYear)
      }))
    });
  };

  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>
        <Typography.Title level={4}>
          {employee ? 'ویرایش کارمند' : 'افزودن کارمند جدید'}
        </Typography.Title>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            {/* اطلاعات شخصی */}
            <Col xs={Math.round(12 / 12 * 24)}>
              <Typography.Title level={4}>اطلاعات شخصی</Typography.Title>
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="employeeCode"
                control={control}
                rules={{ required: 'کد پرسنلی الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="کد پرسنلی"
                    fullWidth
                    error={!!errors.employeeCode}
                    helperText={errors.employeeCode?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="nationalId"
                control={control}
                rules={{ 
                  required: 'کد ملی الزامی است',
                  pattern: {
                    value: /^\d{10}$/,
                    message: 'کد ملی باید 10 رقم باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="کد ملی"
                    fullWidth
                    error={!!errors.nationalId}
                    helperText={errors.nationalId?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="firstName"
                control={control}
                rules={{ required: 'نام الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="نام"
                    fullWidth
                    error={!!errors.firstName}
                    helperText={errors.firstName?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="lastName"
                control={control}
                rules={{ required: 'نام خانوادگی الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="نام خانوادگی"
                    fullWidth
                    error={!!errors.lastName}
                    helperText={errors.lastName?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="birthDate"
                control={control}
                rules={{ required: 'تاریخ تولد الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ تولد"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.birthDate}
                    helperText={errors.birthDate?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="gender"
                control={control}
                rules={{ required: 'جنسیت الزامی است' }}
                render={({ field }) => (
                  <div fullWidth error={!!errors.gender}>
                    <span>جنسیت</span>
                    <Select {...field} label="جنسیت">
                      {genderOptions.map((option) => (
                        <Select.Option key={option.value} value={option.value}>
                          {option.label}
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.gender && (
                      <span>{errors.gender.message}</span>
                    )}
                  </div>
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="maritalStatus"
                control={control}
                rules={{ required: 'وضعیت تأهل الزامی است' }}
                render={({ field }) => (
                  <div fullWidth error={!!errors.maritalStatus}>
                    <span>وضعیت تأهل</span>
                    <Select {...field} label="وضعیت تأهل">
                      {maritalStatusOptions.map((option) => (
                        <Select.Option key={option.value} value={option.value}>
                          {option.label}
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.maritalStatus && (
                      <span>{errors.maritalStatus.message}</span>
                    )}
                  </div>
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
              <Divider style={{  my: 2  }} />
              <Typography.Title level={4}>اطلاعات شغلی</Typography.Title>
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
                name="position"
                control={control}
                rules={{ required: 'سمت الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="سمت"
                    fullWidth
                    error={!!errors.position}
                    helperText={errors.position?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="employeeType"
                control={control}
                rules={{ required: 'نوع استخدام الزامی است' }}
                render={({ field }) => (
                  <div fullWidth error={!!errors.employeeType}>
                    <span>نوع استخدام</span>
                    <Select {...field} label="نوع استخدام">
                      {employeeTypeOptions.map((option) => (
                        <Select.Option key={option.value} value={option.value}>
                          {option.label}
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.employeeType && (
                      <span>{errors.employeeType.message}</span>
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
                  <div fullWidth error={!!errors.status}>
                    <span>وضعیت</span>
                    <Select {...field} label="وضعیت">
                      {statusOptions.map((option) => (
                        <Select.Option key={option.value} value={option.value}>
                          <div>
                            <Tag 
                              label={option.label} 
                              size="small"
                              color={
                                option.value === 'active' ? 'success' :
                                option.value === 'inactive' ? 'error' :
                                option.value === 'on_leave' ? 'warning' :
                                'default'
                              }
                            />
                          </div>
                        </Select.Option>
                      ))}
                    </Select>
                    {errors.status && (
                      <span>{errors.status.message}</span>
                    )}
                  </div>
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="hireDate"
                control={control}
                rules={{ required: 'تاریخ استخدام الزامی است' }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ استخدام"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.hireDate}
                    helperText={errors.hireDate?.message}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="contractEndDate"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="تاریخ پایان قرارداد"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                  />
                )}
              />
            </Col>
            
            <Col xs={Math.round(12 / 12 * 24)}>
              <Controller
                name="salary"
                control={control}
                rules={{ 
                  required: 'حقوق الزامی است',
                  pattern: {
                    value: /^\d+(\.\d{1,2})?$/,
                    message: 'مبلغ باید عدد معتبر باشد'
                  }
                }}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="حقوق (تومان)"
                    fullWidth
                    error={!!errors.salary}
                    helperText={errors.salary?.message}
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
            {isSubmitting ? 'در حال ذخیره...' : (employee ? 'ویرایش' : 'ذخیره')}
          </Button>
        </div>
      </form>
    </Modal>
  );
}; 