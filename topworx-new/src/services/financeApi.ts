// src/services/financeApi.ts
// ============================================================================
// Finance Module API
// ============================================================================

import { apiClient } from './api';
import {
  FiscalPeriod,
  Account,
  AccountWithBalance,
  JournalEntry,
  TrialBalance,
  IncomeStatement,
  BalanceSheet,
  InventoryValuation,
  CreateJournalEntry,
} from '../types';

const BASE = '/finance';

export const financeApi = {
  // Fiscal periods
  getPeriods: (year?: number) =>
    apiClient.get<FiscalPeriod[]>(`${BASE}/periods`, { params: { year } }),
  
  createPeriod: (data: Partial<FiscalPeriod>) =>
    apiClient.post<FiscalPeriod>(`${BASE}/periods`, data),
  
  closePeriod: (id: number) =>
    apiClient.post<FiscalPeriod>(`${BASE}/periods/${id}/close`),

  // Accounts
  getAccounts: (params?: { type?: string; is_active?: boolean }) =>
    apiClient.get<Account[]>(`${BASE}/accounts`, { params }),
  
  getAccountTree: () =>
    apiClient.get<AccountWithBalance[]>(`${BASE}/accounts/tree`),
  
  getAccount: (id: number, asOfDate?: string) =>
    apiClient.get<AccountWithBalance>(`${BASE}/accounts/${id}`, { params: { as_of_date: asOfDate } }),
  
  createAccount: (data: Partial<Account>) =>
    apiClient.post<Account>(`${BASE}/accounts`, data),
  
  updateAccount: (id: number, data: Partial<Account>) =>
    apiClient.put<Account>(`${BASE}/accounts/${id}`, data),

  // Journal entries
  getJournalEntries: (params?: {
    period_id?: number;
    status?: string;
    account_id?: number;
    date_from?: string;
    date_to?: string;
  }) => apiClient.get<JournalEntry[]>(`${BASE}/journal-entries`, { params }),
  
  getJournalEntry: (id: number) =>
    apiClient.get<JournalEntry>(`${BASE}/journal-entries/${id}`),
  
  createJournalEntry: (data: CreateJournalEntry) =>
    apiClient.post<JournalEntry>(`${BASE}/journal-entries`, data),
  
  updateJournalEntry: (id: number, data: Partial<CreateJournalEntry>) =>
    apiClient.put<JournalEntry>(`${BASE}/journal-entries/${id}`, data),
  
  deleteJournalEntry: (id: number) =>
    apiClient.delete(`${BASE}/journal-entries/${id}`),
  
  postJournalEntry: (id: number) =>
    apiClient.post<JournalEntry>(`${BASE}/journal-entries/${id}/post`),
  
  reverseJournalEntry: (id: number, reversalDate: string) =>
    apiClient.post<JournalEntry>(`${BASE}/journal-entries/${id}/reverse`, null, {
      params: { reversal_date: reversalDate },
    }),

  // Reports
  getTrialBalance: (asOfDate: string) =>
    apiClient.get<TrialBalance>(`${BASE}/reports/trial-balance`, { params: { as_of_date: asOfDate } }),
  
  getIncomeStatement: (periodId: number) =>
    apiClient.get<IncomeStatement>(`${BASE}/reports/income-statement`, { params: { period_id: periodId } }),
  
  getBalanceSheet: (asOfDate: string) =>
    apiClient.get<BalanceSheet>(`${BASE}/reports/balance-sheet`, { params: { as_of_date: asOfDate } }),
  
  getInventoryValuation: (asOfDate: string) =>
    apiClient.get<InventoryValuation>(`${BASE}/reports/inventory-valuation`, { params: { as_of_date: asOfDate } }),
  
  getAgingReceivable: (asOfDate: string) =>
    apiClient.get(`${BASE}/reports/aging-receivable`, { params: { as_of_date: asOfDate } }),
  
  getAgingPayable: (asOfDate: string) =>
    apiClient.get(`${BASE}/reports/aging-payable`, { params: { as_of_date: asOfDate } }),
};