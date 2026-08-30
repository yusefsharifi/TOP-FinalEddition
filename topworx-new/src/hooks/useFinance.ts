// src/hooks/useFinance.ts
// ============================================================================
// Finance Hooks
// ============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { financeApi } from '../services/financeApi';
import {
  FiscalPeriod,
  AccountWithBalance,
  JournalEntry,
  TrialBalance,
  IncomeStatement,
  BalanceSheet,
  CreateJournalEntry,
} from '../types';

const KEYS = {
  periods: ['finance', 'periods'],
  accounts: (params?: object) => ['finance', 'accounts', params],
  accountTree: ['finance', 'accounts', 'tree'],
  account: (id: number) => ['finance', 'accounts', id],
  journalEntries: (params?: object) => ['finance', 'journal-entries', params],
  journalEntry: (id: number) => ['finance', 'journal-entries', id],
  trialBalance: (date: string) => ['finance', 'reports', 'trial-balance', date],
  incomeStatement: (periodId: number) => ['finance', 'reports', 'income-statement', periodId],
  balanceSheet: (date: string) => ['finance', 'reports', 'balance-sheet', date],
};

export function useFiscalPeriods(year?: number) {
  return useQuery<FiscalPeriod[], Error>({
    queryKey: KEYS.periods,
    queryFn: async () => {
      const response = await financeApi.getPeriods(year);
      return response.data;
    },
  });
}

export function useAccountTree() {
  return useQuery<AccountWithBalance[], Error>({
    queryKey: KEYS.accountTree,
    queryFn: async () => {
      const response = await financeApi.getAccountTree();
      return response.data;
    },
  });
}

export function useJournalEntries(params?: Parameters<typeof financeApi.getJournalEntries>[0]) {
  return useQuery<JournalEntry[], Error>({
    queryKey: KEYS.journalEntries(params),
    queryFn: async () => {
      const response = await financeApi.getJournalEntries(params);
      return response.data;
    },
  });
}

export function useJournalEntry(id: number) {
  return useQuery<JournalEntry, Error>({
    queryKey: KEYS.journalEntry(id),
    queryFn: async () => {
      const response = await financeApi.getJournalEntry(id);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useTrialBalance(asOfDate: string) {
  return useQuery<TrialBalance, Error>({
    queryKey: KEYS.trialBalance(asOfDate),
    queryFn: async () => {
      const response = await financeApi.getTrialBalance(asOfDate);
      return response.data;
    },
    enabled: !!asOfDate,
  });
}

export function useBalanceSheet(asOfDate: string) {
  return useQuery<BalanceSheet, Error>({
    queryKey: KEYS.balanceSheet(asOfDate),
    queryFn: async () => {
      const response = await financeApi.getBalanceSheet(asOfDate);
      return response.data;
    },
    enabled: !!asOfDate,
  });
}

export function useIncomeStatement(periodId: number) {
  return useQuery<IncomeStatement, Error>({
    queryKey: KEYS.incomeStatement(periodId),
    queryFn: async () => {
      const response = await financeApi.getIncomeStatement(periodId);
      return response.data;
    },
    enabled: !!periodId,
  });
}

export function useCreateJournalEntry() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CreateJournalEntry) => {
      const response = await financeApi.createJournalEntry(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'journal-entries'] });
    },
  });
}

export function usePostJournalEntry() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await financeApi.postJournalEntry(id);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'journal-entries'] });
      queryClient.invalidateQueries({ queryKey: ['finance', 'reports'] });
      queryClient.invalidateQueries({ queryKey: ['finance', 'accounts'] });
    },
  });
}

export function useReverseJournalEntry() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, reversalDate }: { id: number; reversalDate: string }) => {
      const response = await financeApi.reverseJournalEntry(id, reversalDate);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'journal-entries'] });
    },
  });
}