// HR Module Types

export interface Employee {
  id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  hire_date: string;
  department_id: string;
  department_name: string;
  position_id: string;
  position_name: string;
  manager_id?: string;
  manager_name?: string;
  salary: number;
  currency: string;
  employment_type: 'full_time' | 'part_time' | 'contract' | 'intern';
  status: 'active' | 'inactive' | 'terminated' | 'resigned';
  address: string;
  city: string;
  country: string;
  postal_code: string;
  emergency_contact: string;
  emergency_phone: string;
  created_at: string;
  updated_at: string;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  description: string;
  manager_id?: string;
  manager_name?: string;
  parent_id?: string;
  parent_name?: string;
  budget: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Position {
  id: string;
  title: string;
  code: string;
  description: string;
  department_id: string;
  department_name: string;
  level: number;
  min_salary: number;
  max_salary: number;
  requirements: string;
  responsibilities: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Attendance {
  id: string;
  employee_id: string;
  employee_name: string;
  date: string;
  check_in: string;
  check_out?: string;
  total_hours?: number;
  overtime_hours?: number;
  status: 'present' | 'absent' | 'late' | 'half_day' | 'leave';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface LeaveRequest {
  id: string;
  employee_id: string;
  employee_name: string;
  leave_type: 'annual' | 'sick' | 'personal' | 'maternity' | 'paternity' | 'unpaid';
  start_date: string;
  end_date: string;
  days_requested: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface Payroll {
  id: string;
  employee_id: string;
  employee_name: string;
  period_start: string;
  period_end: string;
  basic_salary: number;
  allowances: number;
  deductions: number;
  overtime_pay: number;
  bonus: number;
  gross_salary: number;
  net_salary: number;
  tax_amount: number;
  insurance_amount: number;
  status: 'draft' | 'processed' | 'paid' | 'cancelled';
  payment_date?: string;
  created_at: string;
  updated_at: string;
}

export interface PerformanceReview {
  id: string;
  employee_id: string;
  employee_name: string;
  reviewer_id: string;
  reviewer_name: string;
  review_period: string;
  review_date: string;
  overall_rating: number;
  goals_achieved: number;
  goals_total: number;
  strengths: string;
  areas_for_improvement: string;
  recommendations: string;
  employee_comments?: string;
  status: 'draft' | 'submitted' | 'approved' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface Training {
  id: string;
  title: string;
  description: string;
  type: 'internal' | 'external' | 'online' | 'workshop';
  provider: string;
  duration: number; // in hours
  cost: number;
  max_participants: number;
  start_date: string;
  end_date: string;
  location: string;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface TrainingEnrollment {
  id: string;
  training_id: string;
  training_title: string;
  employee_id: string;
  employee_name: string;
  enrollment_date: string;
  status: 'enrolled' | 'attended' | 'completed' | 'dropped';
  completion_date?: string;
  certificate_issued?: boolean;
  certificate_number?: string;
  feedback_rating?: number;
  feedback_comments?: string;
  created_at: string;
  updated_at: string;
}

export interface Recruitment {
  id: string;
  position_id: string;
  position_title: string;
  department_id: string;
  department_name: string;
  title: string;
  description: string;
  requirements: string;
  responsibilities: string;
  min_experience: number;
  max_experience: number;
  min_salary: number;
  max_salary: number;
  positions_available: number;
  status: 'draft' | 'published' | 'closed' | 'cancelled';
  publish_date?: string;
  close_date?: string;
  created_at: string;
  updated_at: string;
}

export interface JobApplication {
  id: string;
  recruitment_id: string;
  recruitment_title: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  resume_url: string;
  cover_letter?: string;
  experience_years: number;
  expected_salary: number;
  status: 'applied' | 'screening' | 'interview' | 'shortlisted' | 'hired' | 'rejected';
  screening_score?: number;
  interview_score?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Benefit {
  id: string;
  name: string;
  description: string;
  type: 'health' | 'dental' | 'vision' | 'life' | 'disability' | 'retirement' | 'other';
  provider: string;
  cost_per_employee: number;
  employer_contribution: number;
  employee_contribution: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmployeeBenefit {
  id: string;
  employee_id: string;
  employee_name: string;
  benefit_id: string;
  benefit_name: string;
  enrollment_date: string;
  coverage_start_date: string;
  coverage_end_date?: string;
  status: 'active' | 'inactive' | 'terminated';
  created_at: string;
  updated_at: string;
}

// Form Types
export interface EmployeeFormData {
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  hire_date: string;
  department_id: string;
  position_id: string;
  manager_id?: string;
  salary: number;
  currency: string;
  employment_type: 'full_time' | 'part_time' | 'contract' | 'intern';
  address: string;
  city: string;
  country: string;
  postal_code: string;
  emergency_contact: string;
  emergency_phone: string;
}

export interface DepartmentFormData {
  name: string;
  code: string;
  description: string;
  manager_id?: string;
  parent_id?: string;
  budget: number;
}

export interface PositionFormData {
  title: string;
  code: string;
  description: string;
  department_id: string;
  level: number;
  min_salary: number;
  max_salary: number;
  requirements: string;
  responsibilities: string;
}

export interface LeaveRequestFormData {
  employee_id: string;
  leave_type: 'annual' | 'sick' | 'personal' | 'maternity' | 'paternity' | 'unpaid';
  start_date: string;
  end_date: string;
  reason: string;
}

// Filter Types
export interface HRFilters {
  department_id?: string;
  status?: string;
  employment_type?: string;
  search?: string;
}

export interface AttendanceFilters {
  employee_id?: string;
  date_from?: string;
  date_to?: string;
  status?: string;
}

export interface LeaveFilters {
  employee_id?: string;
  leave_type?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}

// Response Types
export interface HRResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface HRStats {
  total_employees: number;
  active_employees: number;
  new_hires_this_month: number;
  turnover_rate: number;
  average_salary: number;
  total_departments: number;
  total_positions: number;
  attendance_rate: number;
} 