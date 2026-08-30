// Accounting & Treasury Module Types

export interface ChartOfAccounts {
  id: string;
  code: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
  parent_id?: string;
  level: number;
  is_active: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface JournalEntry {
  id: string;
  entry_number: string;
  date: string;
  reference: string;
  description: string;
  total_debit: number;
  total_credit: number;
  status: 'draft' | 'posted' | 'cancelled';
  posted_by?: string;
  posted_at?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface JournalEntryLine {
  id: string;
  journal_entry_id: string;
  account_id: string;
  account_code: string;
  account_name: string;
  debit_amount: number;
  credit_amount: number;
  description: string;
  line_number: number;
}

export interface GeneralLedger {
  id: string;
  account_id: string;
  account_code: string;
  account_name: string;
  date: string;
  entry_id: string;
  entry_number: string;
  reference: string;
  description: string;
  debit_amount: number;
  credit_amount: number;
  balance: number;
  created_at: string;
}

export interface TrialBalance {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  opening_debit: number;
  opening_credit: number;
  period_debit: number;
  period_credit: number;
  closing_debit: number;
  closing_credit: number;
}

export interface FinancialStatement {
  id: string;
  name: string;
  type: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'equity_statement';
  period_start: string;
  period_end: string;
  currency: string;
  total_assets: number;
  total_liabilities: number;
  total_equity: number;
  net_income: number;
  created_at: string;
}

export interface BankAccount {
  id: string;
  name: string;
  account_number: string;
  bank_name: string;
  branch_name?: string;
  currency: string;
  opening_balance: number;
  current_balance: number;
  is_active: boolean;
  account_type: 'checking' | 'savings' | 'credit';
  created_at: string;
  updated_at: string;
}

export interface BankTransaction {
  id: string;
  bank_account_id: string;
  bank_account_name: string;
  transaction_date: string;
  value_date: string;
  reference: string;
  description: string;
  amount: number;
  type: 'deposit' | 'withdrawal' | 'transfer' | 'fee' | 'interest';
  status: 'pending' | 'completed' | 'cancelled';
  reconciled: boolean;
  reconciled_at?: string;
  reconciled_by?: string;
  created_at: string;
  updated_at: string;
}

export interface BankReconciliation {
  id: string;
  bank_account_id: string;
  bank_account_name: string;
  period_start: string;
  period_end: string;
  opening_balance: number;
  closing_balance: number;
  book_balance: number;
  bank_balance: number;
  difference: number;
  status: 'draft' | 'completed';
  completed_at?: string;
  completed_by?: string;
  created_at: string;
  updated_at: string;
}

export interface CashFlow {
  id: string;
  period_start: string;
  period_end: string;
  operating_activities: number;
  investing_activities: number;
  financing_activities: number;
  net_cash_flow: number;
  opening_cash_balance: number;
  closing_cash_balance: number;
  created_at: string;
}

export interface Budget {
  id: string;
  name: string;
  fiscal_year: string;
  period_start: string;
  period_end: string;
  total_budget: number;
  actual_amount: number;
  variance: number;
  variance_percentage: number;
  status: 'draft' | 'approved' | 'active' | 'closed';
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface BudgetLine {
  id: string;
  budget_id: string;
  account_id: string;
  account_code: string;
  account_name: string;
  budget_amount: number;
  actual_amount: number;
  variance: number;
  variance_percentage: number;
}

export interface TaxCode {
  id: string;
  code: string;
  name: string;
  rate: number;
  type: 'sales_tax' | 'purchase_tax' | 'withholding_tax';
  is_active: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface TaxTransaction {
  id: string;
  tax_code_id: string;
  tax_code_name: string;
  transaction_date: string;
  reference: string;
  description: string;
  taxable_amount: number;
  tax_amount: number;
  type: 'input' | 'output';
  status: 'pending' | 'paid' | 'refunded';
  due_date: string;
  paid_date?: string;
  created_at: string;
  updated_at: string;
}

export interface FixedAsset {
  id: string;
  code: string;
  name: string;
  category: string;
  purchase_date: string;
  purchase_cost: number;
  salvage_value: number;
  useful_life: number;
  depreciation_method: 'straight_line' | 'declining_balance' | 'sum_of_years';
  current_value: number;
  accumulated_depreciation: number;
  status: 'active' | 'disposed' | 'sold';
  location?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface AssetDepreciation {
  id: string;
  asset_id: string;
  asset_name: string;
  period_start: string;
  period_end: string;
  depreciation_amount: number;
  accumulated_depreciation: number;
  book_value: number;
  created_at: string;
}

export interface CostCenter {
  id: string;
  code: string;
  name: string;
  parent_id?: string;
  manager_id?: string;
  budget_amount: number;
  actual_amount: number;
  is_active: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface AccountingPeriod {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: 'open' | 'closed' | 'locked';
  closed_at?: string;
  closed_by?: string;
  created_at: string;
  updated_at: string;
}

export interface AuditTrail {
  id: string;
  table_name: string;
  record_id: string;
  action: 'create' | 'update' | 'delete';
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  user_id: string;
  user_name: string;
  ip_address: string;
  created_at: string;
}

// Form Types
export interface ChartOfAccountsFormData {
  code: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
  parent_id?: string;
  description?: string;
}

export interface JournalEntryFormData {
  date: string;
  reference: string;
  description: string;
  lines: JournalEntryLineFormData[];
}

export interface JournalEntryLineFormData {
  account_id: string;
  debit_amount: number;
  credit_amount: number;
  description: string;
}

export interface BankAccountFormData {
  name: string;
  account_number: string;
  bank_name: string;
  branch_name?: string;
  currency: string;
  opening_balance: number;
  account_type: 'checking' | 'savings' | 'credit';
}

export interface BankTransactionFormData {
  bank_account_id: string;
  transaction_date: string;
  value_date: string;
  reference: string;
  description: string;
  amount: number;
  type: 'deposit' | 'withdrawal' | 'transfer' | 'fee' | 'interest';
}

export interface BudgetFormData {
  name: string;
  fiscal_year: string;
  period_start: string;
  period_end: string;
  total_budget: number;
}

export interface FixedAssetFormData {
  code: string;
  name: string;
  category: string;
  purchase_date: string;
  purchase_cost: number;
  salvage_value: number;
  useful_life: number;
  depreciation_method: 'straight_line' | 'declining_balance' | 'sum_of_years';
  location?: string;
  description?: string;
}

// Filter Types
export interface AccountingFilters {
  date_from?: string;
  date_to?: string;
  account_type?: string;
  status?: string;
  created_by?: string;
  search?: string;
}

export interface BankTransactionFilters {
  bank_account_id?: string;
  date_from?: string;
  date_to?: string;
  type?: string;
  status?: string;
  reconciled?: boolean;
  search?: string;
}

export interface BudgetFilters {
  fiscal_year?: string;
  status?: string;
  search?: string;
}

// Response Types
export interface AccountingResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface AccountingStats {
  total_assets: number;
  total_liabilities: number;
  total_equity: number;
  net_income: number;
  cash_balance: number;
  accounts_receivable: number;
  accounts_payable: number;
} 