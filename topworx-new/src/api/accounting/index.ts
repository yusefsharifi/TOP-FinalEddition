// Accounting & Treasury API
import { apiClient } from '../../services/api';
import {
  ChartOfAccounts,
  JournalEntry,
  JournalEntryLine,
  GeneralLedger,
  TrialBalance,
  FinancialStatement,
  BankAccount,
  BankTransaction,
  BankReconciliation,
  CashFlow,
  Budget,
  BudgetLine,
  TaxCode,
  TaxTransaction,
  FixedAsset,
  AssetDepreciation,
  CostCenter,
  AccountingPeriod,
  AuditTrail,
  ChartOfAccountsFormData,
  JournalEntryFormData,
  BankAccountFormData,
  BankTransactionFormData,
  BudgetFormData,
  FixedAssetFormData,
  AccountingFilters,
  BankTransactionFilters,
  BudgetFilters,
  AccountingResponse,
  AccountingStats
} from '../../types/accounting';

// Chart of Accounts API
export const chartOfAccountsApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<ChartOfAccounts>>('/accounting/chart-of-accounts', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<ChartOfAccounts>(`/accounting/chart-of-accounts/${id}`),
  
  create: (data: ChartOfAccountsFormData) =>
    apiClient.post<ChartOfAccounts>('/accounting/chart-of-accounts', data),
  
  update: (id: string, data: Partial<ChartOfAccountsFormData>) =>
    apiClient.put<ChartOfAccounts>(`/accounting/chart-of-accounts/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/chart-of-accounts/${id}`),
  
  getTree: () =>
    apiClient.get<ChartOfAccounts[]>('/accounting/chart-of-accounts/tree'),
  
  getByType: (type: string) =>
    apiClient.get<ChartOfAccounts[]>(`/accounting/chart-of-accounts/type/${type}`),
};

// Journal Entries API
export const journalEntriesApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<JournalEntry>>('/accounting/journal-entries', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<JournalEntry>(`/accounting/journal-entries/${id}`),
  
  create: (data: JournalEntryFormData) =>
    apiClient.post<JournalEntry>('/accounting/journal-entries', data),
  
  update: (id: string, data: Partial<JournalEntryFormData>) =>
    apiClient.put<JournalEntry>(`/accounting/journal-entries/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/journal-entries/${id}`),
  
  post: (id: string) =>
    apiClient.post<JournalEntry>(`/accounting/journal-entries/${id}/post`),
  
  cancel: (id: string) =>
    apiClient.post<JournalEntry>(`/accounting/journal-entries/${id}/cancel`),
  
  getLines: (id: string) =>
    apiClient.get<JournalEntryLine[]>(`/accounting/journal-entries/${id}/lines`),
  
  getNextNumber: () =>
    apiClient.get<{ next_number: string }>('/accounting/journal-entries/next-number'),
};

// General Ledger API
export const generalLedgerApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<GeneralLedger>>('/accounting/general-ledger', { params: filters }),
  
  getByAccount: (accountId: string, filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<GeneralLedger>>(`/accounting/general-ledger/account/${accountId}`, { params: filters }),
  
  getBalance: (accountId: string, date?: string) =>
    apiClient.get<{ balance: number }>(`/accounting/general-ledger/account/${accountId}/balance`, { params: { date } }),
  
  export: (filters?: AccountingFilters) =>
    apiClient.get('/accounting/general-ledger/export', { params: filters, responseType: 'blob' }),
};

// Trial Balance API
export const trialBalanceApi = {
  get: (date?: string) =>
    apiClient.get<TrialBalance[]>('/accounting/trial-balance', { params: { date } }),
  
  export: (date?: string) =>
    apiClient.get('/accounting/trial-balance/export', { params: { date }, responseType: 'blob' }),
};

// Financial Statements API
export const financialStatementsApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<FinancialStatement>>('/accounting/financial-statements', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<FinancialStatement>(`/accounting/financial-statements/${id}`),
  
  generateBalanceSheet: (periodStart: string, periodEnd: string) =>
    apiClient.post<FinancialStatement>('/accounting/financial-statements/balance-sheet', { period_start: periodStart, period_end: periodEnd }),
  
  generateIncomeStatement: (periodStart: string, periodEnd: string) =>
    apiClient.post<FinancialStatement>('/accounting/financial-statements/income-statement', { period_start: periodStart, period_end: periodEnd }),
  
  generateCashFlow: (periodStart: string, periodEnd: string) =>
    apiClient.post<FinancialStatement>('/accounting/financial-statements/cash-flow', { period_start: periodStart, period_end: periodEnd }),
  
  export: (id: string, format: 'pdf' | 'excel') =>
    apiClient.get(`/accounting/financial-statements/${id}/export`, { params: { format }, responseType: 'blob' }),
};

// Bank Accounts API
export const bankAccountsApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<BankAccount>>('/accounting/bank-accounts', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<BankAccount>(`/accounting/bank-accounts/${id}`),
  
  create: (data: BankAccountFormData) =>
    apiClient.post<BankAccount>('/accounting/bank-accounts', data),
  
  update: (id: string, data: Partial<BankAccountFormData>) =>
    apiClient.put<BankAccount>(`/accounting/bank-accounts/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/bank-accounts/${id}`),
  
  getBalance: (id: string) =>
    apiClient.get<{ balance: number }>(`/accounting/bank-accounts/${id}/balance`),
  
  getTransactions: (id: string, filters?: BankTransactionFilters) =>
    apiClient.get<AccountingResponse<BankTransaction>>(`/accounting/bank-accounts/${id}/transactions`, { params: filters }),
};

// Bank Transactions API
export const bankTransactionsApi = {
  getAll: (filters?: BankTransactionFilters) =>
    apiClient.get<AccountingResponse<BankTransaction>>('/accounting/bank-transactions', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<BankTransaction>(`/accounting/bank-transactions/${id}`),
  
  create: (data: BankTransactionFormData) =>
    apiClient.post<BankTransaction>('/accounting/bank-transactions', data),
  
  update: (id: string, data: Partial<BankTransactionFormData>) =>
    apiClient.put<BankTransaction>(`/accounting/bank-transactions/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/bank-transactions/${id}`),
  
  reconcile: (id: string) =>
    apiClient.post<BankTransaction>(`/accounting/bank-transactions/${id}/reconcile`),
  
  bulkReconcile: (ids: string[]) =>
    apiClient.post<BankTransaction[]>('/accounting/bank-transactions/bulk-reconcile', { ids }),
  
  import: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<BankTransaction[]>('/accounting/bank-transactions/import', formData);
  },
  
  export: (filters?: BankTransactionFilters) =>
    apiClient.get('/accounting/bank-transactions/export', { params: filters, responseType: 'blob' }),
};

// Bank Reconciliation API
export const bankReconciliationApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<BankReconciliation>>('/accounting/bank-reconciliations', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<BankReconciliation>(`/accounting/bank-reconciliations/${id}`),
  
  create: (data: { bank_account_id: string; period_start: string; period_end: string }) =>
    apiClient.post<BankReconciliation>('/accounting/bank-reconciliations', data),
  
  update: (id: string, data: Partial<BankReconciliation>) =>
    apiClient.put<BankReconciliation>(`/accounting/bank-reconciliations/${id}`, data),
  
  complete: (id: string) =>
    apiClient.post<BankReconciliation>(`/accounting/bank-reconciliations/${id}/complete`),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/bank-reconciliations/${id}`),
  
  getUnreconciledTransactions: (bankAccountId: string) =>
    apiClient.get<BankTransaction[]>(`/accounting/bank-reconciliations/unreconciled/${bankAccountId}`),
};

// Cash Flow API
export const cashFlowApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<CashFlow>>('/accounting/cash-flow', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<CashFlow>(`/accounting/cash-flow/${id}`),
  
  generate: (periodStart: string, periodEnd: string) =>
    apiClient.post<CashFlow>('/accounting/cash-flow/generate', { period_start: periodStart, period_end: periodEnd }),
  
  export: (id: string, format: 'pdf' | 'excel') =>
    apiClient.get(`/accounting/cash-flow/${id}/export`, { params: { format }, responseType: 'blob' }),
};

// Budgets API
export const budgetsApi = {
  getAll: (filters?: BudgetFilters) =>
    apiClient.get<AccountingResponse<Budget>>('/accounting/budgets', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<Budget>(`/accounting/budgets/${id}`),
  
  create: (data: BudgetFormData) =>
    apiClient.post<Budget>('/accounting/budgets', data),
  
  update: (id: string, data: Partial<BudgetFormData>) =>
    apiClient.put<Budget>(`/accounting/budgets/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/budgets/${id}`),
  
  approve: (id: string) =>
    apiClient.post<Budget>(`/accounting/budgets/${id}/approve`),
  
  close: (id: string) =>
    apiClient.post<Budget>(`/accounting/budgets/${id}/close`),
  
  getLines: (id: string) =>
    apiClient.get<BudgetLine[]>(`/accounting/budgets/${id}/lines`),
  
  updateLines: (id: string, lines: BudgetLine[]) =>
    apiClient.put<BudgetLine[]>(`/accounting/budgets/${id}/lines`, { lines }),
  
  getVariance: (id: string) =>
    apiClient.get<{ variance: number; variance_percentage: number }>(`/accounting/budgets/${id}/variance`),
};

// Tax Codes API
export const taxCodesApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<TaxCode>>('/accounting/tax-codes', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<TaxCode>(`/accounting/tax-codes/${id}`),
  
  create: (data: { code: string; name: string; rate: number; type: string; description?: string }) =>
    apiClient.post<TaxCode>('/accounting/tax-codes', data),
  
  update: (id: string, data: Partial<TaxCode>) =>
    apiClient.put<TaxCode>(`/accounting/tax-codes/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/tax-codes/${id}`),
  
  getByType: (type: string) =>
    apiClient.get<TaxCode[]>(`/accounting/tax-codes/type/${type}`),
};

// Tax Transactions API
export const taxTransactionsApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<TaxTransaction>>('/accounting/tax-transactions', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<TaxTransaction>(`/accounting/tax-transactions/${id}`),
  
  create: (data: { tax_code_id: string; transaction_date: string; reference: string; description: string; taxable_amount: number; due_date: string }) =>
    apiClient.post<TaxTransaction>('/accounting/tax-transactions', data),
  
  update: (id: string, data: Partial<TaxTransaction>) =>
    apiClient.put<TaxTransaction>(`/accounting/tax-transactions/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/tax-transactions/${id}`),
  
  pay: (id: string, paidDate: string) =>
    apiClient.post<TaxTransaction>(`/accounting/tax-transactions/${id}/pay`, { paid_date: paidDate }),
  
  getPayable: () =>
    apiClient.get<TaxTransaction[]>('/accounting/tax-transactions/payable'),
  
  getReceivable: () =>
    apiClient.get<TaxTransaction[]>('/accounting/tax-transactions/receivable'),
};

// Fixed Assets API
export const fixedAssetsApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<FixedAsset>>('/accounting/fixed-assets', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<FixedAsset>(`/accounting/fixed-assets/${id}`),
  
  create: (data: FixedAssetFormData) =>
    apiClient.post<FixedAsset>('/accounting/fixed-assets', data),
  
  update: (id: string, data: Partial<FixedAssetFormData>) =>
    apiClient.put<FixedAsset>(`/accounting/fixed-assets/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/fixed-assets/${id}`),
  
  dispose: (id: string, data: { disposal_date: string; disposal_amount: number; disposal_reason: string }) =>
    apiClient.post<FixedAsset>(`/accounting/fixed-assets/${id}/dispose`, data),
  
  getDepreciation: (id: string, filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<AssetDepreciation>>(`/accounting/fixed-assets/${id}/depreciation`, { params: filters }),
  
  calculateDepreciation: (id: string, periodStart: string, periodEnd: string) =>
    apiClient.post<AssetDepreciation>(`/accounting/fixed-assets/${id}/calculate-depreciation`, { period_start: periodStart, period_end: periodEnd }),
  
  getByCategory: (category: string) =>
    apiClient.get<FixedAsset[]>(`/accounting/fixed-assets/category/${category}`),
  
  getTotalValue: () =>
    apiClient.get<{ total_value: number; total_depreciation: number; net_value: number }>('/accounting/fixed-assets/total-value'),
};

// Cost Centers API
export const costCentersApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<CostCenter>>('/accounting/cost-centers', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<CostCenter>(`/accounting/cost-centers/${id}`),
  
  create: (data: { code: string; name: string; parent_id?: string; manager_id?: string; budget_amount: number; description?: string }) =>
    apiClient.post<CostCenter>('/accounting/cost-centers', data),
  
  update: (id: string, data: Partial<CostCenter>) =>
    apiClient.put<CostCenter>(`/accounting/cost-centers/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/cost-centers/${id}`),
  
  getTree: () =>
    apiClient.get<CostCenter[]>('/accounting/cost-centers/tree'),
  
  getBudget: (id: string) =>
    apiClient.get<{ budget_amount: number; actual_amount: number; variance: number }>(`/accounting/cost-centers/${id}/budget`),
};

// Accounting Periods API
export const accountingPeriodsApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<AccountingPeriod>>('/accounting/periods', { params: filters }),
  
  getById: (id: string) =>
    apiClient.get<AccountingPeriod>(`/accounting/periods/${id}`),
  
  create: (data: { name: string; start_date: string; end_date: string }) =>
    apiClient.post<AccountingPeriod>('/accounting/periods', data),
  
  update: (id: string, data: Partial<AccountingPeriod>) =>
    apiClient.put<AccountingPeriod>(`/accounting/periods/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/accounting/periods/${id}`),
  
  close: (id: string) =>
    apiClient.post<AccountingPeriod>(`/accounting/periods/${id}/close`),
  
  lock: (id: string) =>
    apiClient.post<AccountingPeriod>(`/accounting/periods/${id}/lock`),
  
  getCurrent: () =>
    apiClient.get<AccountingPeriod>('/accounting/periods/current'),
  
  getOpen: () =>
    apiClient.get<AccountingPeriod[]>('/accounting/periods/open'),
};

// Audit Trail API
export const auditTrailApi = {
  getAll: (filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<AuditTrail>>('/accounting/audit-trail', { params: filters }),
  
  getByTable: (tableName: string, recordId: string) =>
    apiClient.get<AuditTrail[]>(`/accounting/audit-trail/${tableName}/${recordId}`),
  
  getByUser: (userId: string, filters?: AccountingFilters) =>
    apiClient.get<AccountingResponse<AuditTrail>>(`/accounting/audit-trail/user/${userId}`, { params: filters }),
  
  export: (filters?: AccountingFilters) =>
    apiClient.get('/accounting/audit-trail/export', { params: filters, responseType: 'blob' }),
};

// Accounting Statistics API
export const accountingStatsApi = {
  getDashboard: () =>
    apiClient.get<AccountingStats>('/accounting/stats/dashboard'),
  
  getBalanceSheet: (date?: string) =>
    apiClient.get<{ assets: any[]; liabilities: any[]; equity: any[] }>('/accounting/stats/balance-sheet', { params: { date } }),
  
  getIncomeStatement: (periodStart: string, periodEnd: string) =>
    apiClient.get<{ revenue: any[]; expenses: any[]; net_income: number }>('/accounting/stats/income-statement', { params: { period_start: periodStart, period_end: periodEnd } }),
  
  getCashFlow: (periodStart: string, periodEnd: string) =>
    apiClient.get<{ operating: number; investing: number; financing: number; net_flow: number }>('/accounting/stats/cash-flow', { params: { period_start: periodStart, period_end: periodEnd } }),
  
  getBudgetVariance: (fiscalYear: string) =>
    apiClient.get<{ budget: number; actual: number; variance: number; variance_percentage: number }>('/accounting/stats/budget-variance', { params: { fiscal_year: fiscalYear } }),
  
  getTaxSummary: (periodStart: string, periodEnd: string) =>
    apiClient.get<{ payable: number; receivable: number; net_tax: number }>('/accounting/stats/tax-summary', { params: { period_start: periodStart, period_end: periodEnd } }),
};

// Export all APIs
export const accountingApi = {
  chartOfAccounts: chartOfAccountsApi,
  journalEntries: journalEntriesApi,
  generalLedger: generalLedgerApi,
  trialBalance: trialBalanceApi,
  financialStatements: financialStatementsApi,
  bankAccounts: bankAccountsApi,
  bankTransactions: bankTransactionsApi,
  bankReconciliation: bankReconciliationApi,
  cashFlow: cashFlowApi,
  budgets: budgetsApi,
  taxCodes: taxCodesApi,
  taxTransactions: taxTransactionsApi,
  fixedAssets: fixedAssetsApi,
  costCenters: costCentersApi,
  accountingPeriods: accountingPeriodsApi,
  auditTrail: auditTrailApi,
  stats: accountingStatsApi,
}; 