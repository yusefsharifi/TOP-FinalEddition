// src/services/hrApi.ts
// ============================================================================
// HR & Payroll API
// ============================================================================

import { apiClient } from './api';
import {
  Employee,
  Department,
  AttendanceRecord,
  LeaveRequest,
  PayrollPeriod,
  PayrollEntry,
} from '../types';

const BASE = '/hr';

export const hrApi = {
  // Employees
  getEmployees: (params?: { department_id?: number; status?: string; search?: string }) =>
    apiClient.get<Employee[]>(`${BASE}/employees`, { params }),
  
  getEmployee: (id: number) => 
    apiClient.get<Employee>(`${BASE}/employees/${id}`),
  
  createEmployee: (data: Partial<Employee>) =>
    apiClient.post<Employee>(`${BASE}/employees`, data),
  
  updateEmployee: (id: number, data: Partial<Employee>) =>
    apiClient.put<Employee>(`${BASE}/employees/${id}`, data),
  
  getEndOfService: (id: number, asOfDate?: string) =>
    apiClient.get(`${BASE}/employees/${id}/end-of-service`, { params: { as_of_date: asOfDate } }),

  // Departments
  getDepartments: () =>
    apiClient.get<Department[]>(`${BASE}/departments`),
  
  createDepartment: (data: Partial<Department>) =>
    apiClient.post<Department>(`${BASE}/departments`, data),
  
  getDepartmentCosts: (id: number, year: number, month: number) =>
    apiClient.get(`${BASE}/departments/${id}/costs`, { params: { year, month } }),

  // Attendance
  checkIn: (data: { employeeId: number; recordDate: string; checkInTime: string }) =>
    apiClient.post<AttendanceRecord>(`${BASE}/attendance/check-in`, {
      employee_id: data.employeeId,
      record_date: data.recordDate,
      check_in_time: data.checkInTime,
    }),
  
  checkOut: (data: { employeeId: number; recordDate: string; checkOutTime: string }) =>
    apiClient.post<AttendanceRecord>(`${BASE}/attendance/check-out`, {
      employee_id: data.employeeId,
      record_date: data.recordDate,
      check_out_time: data.checkOutTime,
    }),
  
  getAttendanceSummary: (params?: { employee_id?: number; year?: number; month?: number }) =>
    apiClient.get(`${BASE}/attendance/summary`, { params }),
  
  approveOvertime: (recordId: number) =>
    apiClient.put<AttendanceRecord>(`${BASE}/attendance/${recordId}/approve`),

  // Leave
  getLeaves: (params?: { employee_id?: number; status?: string }) =>
    apiClient.get<LeaveRequest[]>(`${BASE}/leaves`, { params }),
  
  submitLeave: (data: Partial<LeaveRequest>) =>
    apiClient.post<LeaveRequest>(`${BASE}/leaves`, data),
  
  approveLeave: (id: number, notes?: string) =>
    apiClient.post<LeaveRequest>(`${BASE}/leaves/${id}/approve`, { notes }),
  
  rejectLeave: (id: number, reason: string) =>
    apiClient.post<LeaveRequest>(`${BASE}/leaves/${id}/reject`, { reason }),
  
  getLeaveBalance: (employeeId: number) =>
    apiClient.get(`${BASE}/leaves/balance/${employeeId}`),

  // Payroll
  getPayrollPeriods: () =>
    apiClient.get<PayrollPeriod[]>(`${BASE}/payroll/periods`),
  
  createPayrollPeriod: (data: { year: number; month: number; startDate: string; endDate: string }) =>
    apiClient.post<PayrollPeriod>(`${BASE}/payroll/periods`, data),
  
  calculatePayroll: (periodId: number) =>
    apiClient.post<PayrollPeriod>(`${BASE}/payroll/periods/${periodId}/calculate`),
  
  getPayrollEntries: (periodId: number) =>
    apiClient.get<PayrollEntry[]>(`${BASE}/payroll/periods/${periodId}/entries`),
  
  adjustPayrollEntry: (entryId: number, data: Partial<PayrollEntry>) =>
    apiClient.put<PayrollEntry>(`${BASE}/payroll/entries/${entryId}`, data),
  
  approvePayroll: (periodId: number) =>
    apiClient.post<PayrollPeriod>(`${BASE}/payroll/periods/${periodId}/approve`),
  
  payPayroll: (periodId: number, bankCode?: string) =>
    apiClient.post<PayrollPeriod>(`${BASE}/payroll/periods/${periodId}/pay`, null, { 
      params: { bank_account_code: bankCode } 
    }),
  
  downloadPayslip: (entryId: number) =>
    apiClient.get(`${BASE}/payroll/payslips/${entryId}/pdf`, { responseType: 'blob' }),

  // Reports
  getHeadcount: () =>
    apiClient.get(`${BASE}/reports/headcount`),
  
  getPayrollSummary: (year: number, month: number) =>
    apiClient.get(`${BASE}/reports/payroll-summary`, { params: { year, month } }),
  
  getTaxWithholding: (year: number, month: number) =>
    apiClient.get(`${BASE}/reports/tax-withholding`, { params: { year, month } }),
  
  getInsuranceSummary: (year: number, month: number) =>
    apiClient.get(`${BASE}/reports/insurance-summary`, { params: { year, month } }),
};