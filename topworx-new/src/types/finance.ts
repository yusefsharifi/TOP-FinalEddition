// Finance Module Types

export interface FinancialAccount {
  id: string;
  account_number: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
  category: string;
  parent_id?: string;
  parent_name?: string;
  balance: number;
  currency: string;
  is_active: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface FinancialTransaction {
  id: string;
  transaction_number: string;
  account_id: string;
  account_name: string;
  transaction_date: string;
  reference: string;
  description: string;
  amount: number;
  type: 'debit' | 'credit';
  category: string;
  status: 'pending' | 'posted' | 'cancelled';
  posted_by?: string;
  posted_at?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface FinancialBudget {
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

export interface FinancialReport {
  id: string;
  name: string;
  type: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'budget_variance' | 'custom';
  period_start: string;
  period_end: string;
  currency: string;
  parameters: Record<string, any>;
  generated_at: string;
  generated_by: string;
  file_url?: string;
  created_at: string;
  updated_at: string;
}

export interface FinancialForecast {
  id: string;
  name: string;
  type: 'revenue' | 'expense' | 'cash_flow' | 'profit';
  period_start: string;
  period_end: string;
  forecast_amount: number;
  actual_amount?: number;
  variance?: number;
  confidence_level: number;
  assumptions: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface FinancialKPI {
  id: string;
  name: string;
  description: string;
  category: 'profitability' | 'liquidity' | 'efficiency' | 'growth';
  formula: string;
  target_value: number;
  current_value: number;
  unit: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  last_calculated: string;
  created_at: string;
  updated_at: string;
}

export interface FinancialDocument {
  id: string;
  document_number: string;
  type: 'invoice' | 'receipt' | 'payment' | 'expense' | 'other';
  title: string;
  description: string;
  amount: number;
  currency: string;
  document_date: string;
  due_date?: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  file_url?: string;
  tags: string[];
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface FinancialAudit {
  id: string;
  audit_number: string;
  title: string;
  description: string;
  audit_type: 'internal' | 'external' | 'compliance' | 'operational';
  auditor: string;
  audit_date: string;
  findings: string;
  recommendations: string;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  score?: number;
  created_at: string;
  updated_at: string;
}

export interface FinancialRisk {
  id: string;
  name: string;
  description: string;
  category: 'market' | 'credit' | 'operational' | 'liquidity' | 'compliance';
  probability: number;
  impact: number;
  risk_score: number;
  mitigation_strategy: string;
  owner: string;
  status: 'active' | 'mitigated' | 'accepted' | 'closed';
  created_at: string;
  updated_at: string;
}

export interface FinancialCompliance {
  id: string;
  regulation_name: string;
  description: string;
  category: 'tax' | 'accounting' | 'reporting' | 'internal_control';
  requirement: string;
  deadline: string;
  responsible_party: string;
  status: 'compliant' | 'non_compliant' | 'in_progress' | 'pending';
  last_review: string;
  next_review: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

// Form Types
export interface FinancialAccountFormData {
  account_number: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
  category: string;
  parent_id?: string;
  balance: number;
  currency: string;
  description?: string;
}

export interface FinancialTransactionFormData {
  account_id: string;
  transaction_date: string;
  reference: string;
  description: string;
  amount: number;
  type: 'debit' | 'credit';
  category: string;
}

export interface FinancialBudgetFormData {
  name: string;
  fiscal_year: string;
  period_start: string;
  period_end: string;
  total_budget: number;
}

export interface FinancialReportFormData {
  name: string;
  type: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'budget_variance' | 'custom';
  period_start: string;
  period_end: string;
  currency: string;
  parameters: Record<string, any>;
}

// Filter Types
export interface FinanceFilters {
  date_from?: string;
  date_to?: string;
  account_type?: string;
  category?: string;
  status?: string;
  search?: string;
}

export interface TransactionFilters {
  account_id?: string;
  date_from?: string;
  date_to?: string;
  type?: string;
  category?: string;
  status?: string;
  search?: string;
}

export interface BudgetFilters {
  fiscal_year?: string;
  status?: string;
  search?: string;
}

// Response Types
export interface FinanceResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface FinanceStats {
  total_assets: number;
  total_liabilities: number;
  total_equity: number;
  net_income: number;
  cash_flow: number;
  budget_variance: number;
  profit_margin: number;
  return_on_equity: number;
  current_ratio: number;
  debt_to_equity: number;
} 