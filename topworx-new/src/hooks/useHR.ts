// src/hooks/useHR.ts
// ============================================================================
// HR & Payroll Hooks
// ============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { hrApi } from '../services/hrApi';
import { Employee, Department, LeaveRequest, PayrollPeriod, PayrollEntry } from '../types';

const KEYS = {
  employees: (params?: object) => ['hr', 'employees', params],
  employee: (id: number) => ['hr', 'employees', id],
  departments: ['hr', 'departments'],
  leaves: (params?: object) => ['hr', 'leaves', params],
  payrollPeriods: ['hr', 'payroll', 'periods'],
  payrollEntries: (periodId: number) => ['hr', 'payroll', 'entries', periodId],
};

export function useEmployees(params?: Parameters<typeof hrApi.getEmployees>[0]) {
  return useQuery<Employee[], Error>({
    queryKey: KEYS.employees(params),
    queryFn: async () => {
      const response = await hrApi.getEmployees(params);
      return response.data;
    },
  });
}

export function useEmployee(id: number) {
  return useQuery<Employee, Error>({
    queryKey: KEYS.employee(id),
    queryFn: async () => {
      const response = await hrApi.getEmployee(id);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useDepartments() {
  return useQuery<Department[], Error>({
    queryKey: KEYS.departments,
    queryFn: async () => {
      const response = await hrApi.getDepartments();
      return response.data;
    },
  });
}

export function useLeaves(params?: Parameters<typeof hrApi.getLeaves>[0]) {
  return useQuery<LeaveRequest[], Error>({
    queryKey: KEYS.leaves(params),
    queryFn: async () => {
      const response = await hrApi.getLeaves(params);
      return response.data;
    },
  });
}

export function useApproveLeave() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, notes }: { id: number; notes?: string }) => {
      const response = await hrApi.approveLeave(id, notes);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hr', 'leaves'] });
    },
  });
}

export function usePayrollPeriods() {
  return useQuery<PayrollPeriod[], Error>({
    queryKey: KEYS.payrollPeriods,
    queryFn: async () => {
      const response = await hrApi.getPayrollPeriods();
      return response.data;
    },
  });
}

export function usePayrollEntries(periodId: number) {
  return useQuery<PayrollEntry[], Error>({
    queryKey: KEYS.payrollEntries(periodId),
    queryFn: async () => {
      const response = await hrApi.getPayrollEntries(periodId);
      return response.data;
    },
    enabled: !!periodId,
  });
}

export function useCalculatePayroll() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (periodId: number) => {
      const response = await hrApi.calculatePayroll(periodId);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['hr', 'payroll', 'periods'] });
      queryClient.invalidateQueries({ queryKey: ['hr', 'payroll', 'entries', data.id] });
    },
  });
}

export function useApprovePayroll() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (periodId: number) => {
      const response = await hrApi.approvePayroll(periodId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hr', 'payroll'] });
    },
  });
}