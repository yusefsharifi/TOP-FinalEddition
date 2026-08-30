import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Account, Transaction, Invoice, Payment, Expense, Budget, FinancialReport } from '../../types/finance';

// --- Accounts ---
export const useAccounts = (filter?: any) =>
  useQuery<Account[]>(['accounts', filter], async () => {
    const { data } = await axios.get('/api/finance/accounts', { params: filter });
    return data;
  });

export const useCreateAccount = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Account>) => axios.post('/api/finance/accounts', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['accounts'])
    }
  );
};

export const useUpdateAccount = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Account>) => axios.put(`/api/finance/accounts/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['accounts'])
    }
  );
};

export const useDeleteAccount = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/finance/accounts/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['accounts'])
    }
  );
};

// --- Transactions ---
export const useTransactions = (filter?: any) =>
  useQuery<Transaction[]>(['transactions', filter], async () => {
    const { data } = await axios.get('/api/finance/transactions', { params: filter });
    return data;
  });

export const useCreateTransaction = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Transaction>) => axios.post('/api/finance/transactions', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['transactions'])
    }
  );
};

export const useUpdateTransaction = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Transaction>) => axios.put(`/api/finance/transactions/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['transactions'])
    }
  );
};

export const useDeleteTransaction = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/finance/transactions/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['transactions'])
    }
  );
};

// --- Invoices ---
export const useInvoices = (filter?: any) =>
  useQuery<Invoice[]>(['invoices', filter], async () => {
    const { data } = await axios.get('/api/finance/invoices', { params: filter });
    return data;
  });

export const useCreateInvoice = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Invoice>) => axios.post('/api/finance/invoices', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['invoices'])
    }
  );
};

export const useUpdateInvoice = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Invoice>) => axios.put(`/api/finance/invoices/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['invoices'])
    }
  );
};

export const useDeleteInvoice = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/finance/invoices/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['invoices'])
    }
  );
};

// --- Payments ---
export const usePayments = (filter?: any) =>
  useQuery<Payment[]>(['payments', filter], async () => {
    const { data } = await axios.get('/api/finance/payments', { params: filter });
    return data;
  });

export const useCreatePayment = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Payment>) => axios.post('/api/finance/payments', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['payments'])
    }
  );
};

export const useUpdatePayment = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Payment>) => axios.put(`/api/finance/payments/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['payments'])
    }
  );
};

export const useDeletePayment = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/finance/payments/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['payments'])
    }
  );
};

// --- Expenses ---
export const useExpenses = (filter?: any) =>
  useQuery<Expense[]>(['expenses', filter], async () => {
    const { data } = await axios.get('/api/finance/expenses', { params: filter });
    return data;
  });

export const useCreateExpense = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Expense>) => axios.post('/api/finance/expenses', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['expenses'])
    }
  );
};

export const useUpdateExpense = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Expense>) => axios.put(`/api/finance/expenses/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['expenses'])
    }
  );
};

export const useDeleteExpense = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/finance/expenses/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['expenses'])
    }
  );
};

// --- Budgets ---
export const useBudgets = (filter?: any) =>
  useQuery<Budget[]>(['budgets', filter], async () => {
    const { data } = await axios.get('/api/finance/budgets', { params: filter });
    return data;
  });

export const useCreateBudget = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Budget>) => axios.post('/api/finance/budgets', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['budgets'])
    }
  );
};

export const useUpdateBudget = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Budget>) => axios.put(`/api/finance/budgets/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['budgets'])
    }
  );
};

export const useDeleteBudget = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/finance/budgets/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['budgets'])
    }
  );
};

// --- Financial Reports ---
export const useFinancialReports = (filter?: any) =>
  useQuery<FinancialReport[]>(['financialReports', filter], async () => {
    const { data } = await axios.get('/api/finance/reports', { params: filter });
    return data;
  });

export const useCreateFinancialReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<FinancialReport>) => axios.post('/api/finance/reports', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['financialReports'])
    }
  );
};

// --- Finance Dashboard ---
export const useFinanceDashboard = () =>
  useQuery(['financeDashboard'], async () => {
    const { data } = await axios.get('/api/finance/dashboard');
    return data;
  }); 