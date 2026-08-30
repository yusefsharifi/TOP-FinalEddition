// HR Module API
import { apiClient } from '../../services/api';
import {
  Employee,
  Department,
  Position,
  Attendance,
  LeaveRequest,
  Payroll,
  PerformanceReview,
  Training,
  TrainingEnrollment,
  Recruitment,
  JobApplication,
  Benefit,
  EmployeeBenefit,
  EmployeeFormData,
  DepartmentFormData,
  PositionFormData,
  LeaveRequestFormData,
  HRFilters,
  AttendanceFilters,
  LeaveFilters,
  HRResponse,
  HRStats
} from '../../types/hr';

// Employees API
export const employeesApi = {
  getAll: (filters?: HRFilters) =>
    apiClient.get<HRResponse<Employee>>('/hr/employees', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Employee>(`/hr/employees/${id}`),
  
  create: (data: EmployeeFormData) =>
    apiClient.post<Employee>('/hr/employees', data),
  
  update: (id: string, data: Partial<EmployeeFormData>) =>
    apiClient.put<Employee>(`/hr/employees/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/employees/${id}`),
  
  getByDepartment: (departmentId: string) =>
    apiClient.get<Employee[]>(`/hr/employees/department/${departmentId}`),
  
  getByPosition: (positionId: string) =>
    apiClient.get<Employee[]>(`/hr/employees/position/${positionId}`),
  
  getByManager: (managerId: string) =>
    apiClient.get<Employee[]>(`/hr/employees/manager/${managerId}`),
  
  export: (filters?: HRFilters) =>
    apiClient.get('/hr/employees/export', { params: filters, responseType: 'blob' }),
};

// Departments API
export const departmentsApi = {
  getAll: (filters?: HRFilters) =>
    apiClient.get<HRResponse<Department>>('/hr/departments', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Department>(`/hr/departments/${id}`),
  
  create: (data: DepartmentFormData) =>
    apiClient.post<Department>('/hr/departments', data),
  
  update: (id: string, data: Partial<DepartmentFormData>) =>
    apiClient.put<Department>(`/hr/departments/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/departments/${id}`),
  
  getTree: () =>
    apiClient.get<Department[]>('/hr/departments/tree'),
  
  getEmployees: (id: string) =>
    apiClient.get<Employee[]>(`/hr/departments/${id}/employees`),
};

// Positions API
export const positionsApi = {
  getAll: (filters?: HRFilters) =>
    apiClient.get<HRResponse<Position>>('/hr/positions', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Position>(`/hr/positions/${id}`),
  
  create: (data: PositionFormData) =>
    apiClient.post<Position>('/hr/positions', data),
  
  update: (id: string, data: Partial<PositionFormData>) =>
    apiClient.put<Position>(`/hr/positions/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/positions/${id}`),
  
  getByDepartment: (departmentId: string) =>
    apiClient.get<Position[]>(`/hr/positions/department/${departmentId}`),
};

// Attendance API
export const attendanceApi = {
  getAll: (filters?: AttendanceFilters) =>
    apiClient.get<HRResponse<Attendance>>('/hr/attendance', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Attendance>(`/hr/attendance/${id}`),
  
  create: (data: any) =>
    apiClient.post<Attendance>('/hr/attendance', data),
  
  update: (id: string, data: Partial<Attendance>) =>
    apiClient.put<Attendance>(`/hr/attendance/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/attendance/${id}`),
  
  checkIn: (employeeId: string) =>
    apiClient.post<Attendance>(`/hr/attendance/${employeeId}/check-in`),
  
  checkOut: (employeeId: string) =>
    apiClient.post<Attendance>(`/hr/attendance/${employeeId}/check-out`),
  
  getByEmployee: (employeeId: string, filters?: AttendanceFilters) =>
    apiClient.get<HRResponse<Attendance>>(`/hr/attendance/employee/${employeeId}`, { params: filters }),
  
  getByDate: (date: string) =>
    apiClient.get<Attendance[]>(`/hr/attendance/date/${date}`),
  
  export: (filters?: AttendanceFilters) =>
    apiClient.get('/hr/attendance/export', { params: filters, responseType: 'blob' }),
};

// Leave Requests API
export const leaveRequestsApi = {
  getAll: (filters?: LeaveFilters) =>
    apiClient.get<HRResponse<LeaveRequest>>('/hr/leave-requests', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<LeaveRequest>(`/hr/leave-requests/${id}`),
  
  create: (data: LeaveRequestFormData) =>
    apiClient.post<LeaveRequest>('/hr/leave-requests', data),
  
  update: (id: string, data: Partial<LeaveRequestFormData>) =>
    apiClient.put<LeaveRequest>(`/hr/leave-requests/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/leave-requests/${id}`),
  
  approve: (id: string) =>
    apiClient.post<LeaveRequest>(`/hr/leave-requests/${id}/approve`),
  
  reject: (id: string, reason: string) =>
    apiClient.post<LeaveRequest>(`/hr/leave-requests/${id}/reject`, { reason }),
  
  getByEmployee: (employeeId: string) =>
    apiClient.get<LeaveRequest[]>(`/hr/leave-requests/employee/${employeeId}`),
  
  getByStatus: (status: string) =>
    apiClient.get<LeaveRequest[]>(`/hr/leave-requests/status/${status}`),
  
  export: (filters?: LeaveFilters) =>
    apiClient.get('/hr/leave-requests/export', { params: filters, responseType: 'blob' }),
};

// Payroll API
export const payrollApi = {
  getAll: (filters?: HRFilters) =>
    apiClient.get<HRResponse<Payroll>>('/hr/payroll', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Payroll>(`/hr/payroll/${id}`),
  
  create: (data: any) =>
    apiClient.post<Payroll>('/hr/payroll', data),
  
  update: (id: string, data: Partial<Payroll>) =>
    apiClient.put<Payroll>(`/hr/payroll/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/payroll/${id}`),
  
  process: (id: string) =>
    apiClient.post<Payroll>(`/hr/payroll/${id}/process`),
  
  pay: (id: string) =>
    apiClient.post<Payroll>(`/hr/payroll/${id}/pay`),
  
  getByEmployee: (employeeId: string) =>
    apiClient.get<Payroll[]>(`/hr/payroll/employee/${employeeId}`),
  
  getByPeriod: (periodStart: string, periodEnd: string) =>
    apiClient.get<Payroll[]>(`/hr/payroll/period`, { params: { period_start: periodStart, period_end: periodEnd } }),
  
  export: (filters?: HRFilters) =>
    apiClient.get('/hr/payroll/export', { params: filters, responseType: 'blob' }),
};

// Performance Reviews API
export const performanceReviewsApi = {
  getAll: (filters?: HRFilters) =>
    apiClient.get<HRResponse<PerformanceReview>>('/hr/performance-reviews', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<PerformanceReview>(`/hr/performance-reviews/${id}`),
  
  create: (data: any) =>
    apiClient.post<PerformanceReview>('/hr/performance-reviews', data),
  
  update: (id: string, data: Partial<PerformanceReview>) =>
    apiClient.put<PerformanceReview>(`/hr/performance-reviews/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/performance-reviews/${id}`),
  
  submit: (id: string) =>
    apiClient.post<PerformanceReview>(`/hr/performance-reviews/${id}/submit`),
  
  approve: (id: string) =>
    apiClient.post<PerformanceReview>(`/hr/performance-reviews/${id}/approve`),
  
  getByEmployee: (employeeId: string) =>
    apiClient.get<PerformanceReview[]>(`/hr/performance-reviews/employee/${employeeId}`),
  
  getByReviewer: (reviewerId: string) =>
    apiClient.get<PerformanceReview[]>(`/hr/performance-reviews/reviewer/${reviewerId}`),
  
  export: (filters?: HRFilters) =>
    apiClient.get('/hr/performance-reviews/export', { params: filters, responseType: 'blob' }),
};

// Training API
export const trainingApi = {
  getAll: (filters?: HRFilters) =>
    apiClient.get<HRResponse<Training>>('/hr/training', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Training>(`/hr/training/${id}`),
  
  create: (data: any) =>
    apiClient.post<Training>('/hr/training', data),
  
  update: (id: string, data: Partial<Training>) =>
    apiClient.put<Training>(`/hr/training/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/training/${id}`),
  
  getEnrollments: (id: string) =>
    apiClient.get<TrainingEnrollment[]>(`/hr/training/${id}/enrollments`),
  
  enroll: (trainingId: string, employeeId: string) =>
    apiClient.post<TrainingEnrollment>(`/hr/training/${trainingId}/enroll`, { employee_id: employeeId }),
  
  export: (filters?: HRFilters) =>
    apiClient.get('/hr/training/export', { params: filters, responseType: 'blob' }),
};

// Recruitment API
export const recruitmentApi = {
  getAll: (filters?: HRFilters) =>
    apiClient.get<HRResponse<Recruitment>>('/hr/recruitment', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Recruitment>(`/hr/recruitment/${id}`),
  
  create: (data: any) =>
    apiClient.post<Recruitment>('/hr/recruitment', data),
  
  update: (id: string, data: Partial<Recruitment>) =>
    apiClient.put<Recruitment>(`/hr/recruitment/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/recruitment/${id}`),
  
  publish: (id: string) =>
    apiClient.post<Recruitment>(`/hr/recruitment/${id}/publish`),
  
  close: (id: string) =>
    apiClient.post<Recruitment>(`/hr/recruitment/${id}/close`),
  
  getApplications: (id: string) =>
    apiClient.get<JobApplication[]>(`/hr/recruitment/${id}/applications`),
  
  export: (filters?: HRFilters) =>
    apiClient.get('/hr/recruitment/export', { params: filters, responseType: 'blob' }),
};

// Job Applications API
export const jobApplicationsApi = {
  getAll: (filters?: HRFilters) =>
    apiClient.get<HRResponse<JobApplication>>('/hr/job-applications', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<JobApplication>(`/hr/job-applications/${id}`),
  
  create: (data: any) =>
    apiClient.post<JobApplication>('/hr/job-applications', data),
  
  update: (id: string, data: Partial<JobApplication>) =>
    apiClient.put<JobApplication>(`/hr/job-applications/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/job-applications/${id}`),
  
  shortlist: (id: string) =>
    apiClient.post<JobApplication>(`/hr/job-applications/${id}/shortlist`),
  
  hire: (id: string) =>
    apiClient.post<JobApplication>(`/hr/job-applications/${id}/hire`),
  
  reject: (id: string, reason: string) =>
    apiClient.post<JobApplication>(`/hr/job-applications/${id}/reject`, { reason }),
  
  export: (filters?: HRFilters) =>
    apiClient.get('/hr/job-applications/export', { params: filters, responseType: 'blob' }),
};

// Benefits API
export const benefitsApi = {
  getAll: (filters?: HRFilters) =>
    apiClient.get<HRResponse<Benefit>>('/hr/benefits', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Benefit>(`/hr/benefits/${id}`),
  
  create: (data: any) =>
    apiClient.post<Benefit>('/hr/benefits', data),
  
  update: (id: string, data: Partial<Benefit>) =>
    apiClient.put<Benefit>(`/hr/benefits/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/hr/benefits/${id}`),
  
  getEmployeeBenefits: (employeeId: string) =>
    apiClient.get<EmployeeBenefit[]>(`/hr/benefits/employee/${employeeId}`),
  
  enroll: (benefitId: string, employeeId: string) =>
    apiClient.post<EmployeeBenefit>(`/hr/benefits/${benefitId}/enroll`, { employee_id: employeeId }),
  
  export: (filters?: HRFilters) =>
    apiClient.get('/hr/benefits/export', { params: filters, responseType: 'blob' }),
};

// HR Statistics API
export const hrStatsApi = {
  getDashboard: () =>
    apiClient.get<HRStats>('/hr/stats/dashboard'),
  
  getDepartmentStats: () =>
    apiClient.get<any[]>('/hr/stats/departments'),
  
  getAttendanceStats: (period: string) =>
    apiClient.get<any[]>('/hr/stats/attendance', { params: { period } }),
  
  getLeaveStats: (period: string) =>
    apiClient.get<any[]>('/hr/stats/leave', { params: { period } }),
  
  getPayrollStats: (period: string) =>
    apiClient.get<any[]>('/hr/stats/payroll', { params: { period } }),
  
  getPerformanceStats: () =>
    apiClient.get<any[]>('/hr/stats/performance'),
  
  getTrainingStats: () =>
    apiClient.get<any[]>('/hr/stats/training'),
  
  getRecruitmentStats: () =>
    apiClient.get<any[]>('/hr/stats/recruitment'),
};

// Export all APIs
export const hrApi = {
  employees: employeesApi,
  departments: departmentsApi,
  positions: positionsApi,
  attendance: attendanceApi,
  leaveRequests: leaveRequestsApi,
  payroll: payrollApi,
  performanceReviews: performanceReviewsApi,
  training: trainingApi,
  recruitment: recruitmentApi,
  jobApplications: jobApplicationsApi,
  benefits: benefitsApi,
  stats: hrStatsApi,
};