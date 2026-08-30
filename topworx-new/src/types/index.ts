// src/types/index.ts
// ============================================================================
// TOP WorX ERP - Combined Type Definitions
// ============================================================================

// ─────────────────────────────────────────────────────────────────────────────
// BI Dashboard Types
// ─────────────────────────────────────────────────────────────────────────────

export type AlertCondition = 'above' | 'below' | 'equal' | 'change_percent_above' | 'change_percent_below';
export type AlertSeverity = 'info' | 'warning' | 'critical';
export type KPIHealth = 'good' | 'warning' | 'critical' | 'neutral';

export interface KPIData {
  name: string;
  value: number;
  unit: string;
  label: string;
  health: KPIHealth;
  changePct: number | null;
  previousValue: number | null;
  metadata?: Record<string, unknown>;
}

export interface RevenuePoint {
  period: string;
  jalaliYear: number;
  jalaliMonth: number;
  revenue: number;
}

export interface ExpenseSlice {
  label: string;
  subtype: string;
  value: number;
}

export interface CashFlowEvent {
  date: string;
  inflow: number;
  outflow: number;
}

export interface CEODashboardData {
  kpis: Record<string, KPIData>;
  revenueTrend: RevenuePoint[];
  expenseBreakdown: ExpenseSlice[];
  cashFlowForecast: CashFlowEvent[];
  generatedAt: string;
}

export interface AlertRule {
  id: number;
  name: string;
  metric: string;
  condition: AlertCondition;
  threshold: number;
  severity: AlertSeverity;
  isActive: boolean;
  lastTriggered: string | null;
  cooldownMinutes: number;
}

export interface AlertEvent {
  id: number;
  ruleId: number;
  triggeredAt: string;
  metricValue: number;
  thresholdValue: number;
  message: string;
  acknowledged: boolean;
}

export interface ReportConfig {
  baseTable: string;
  dimensions: string[];
  measures: string[];
  filters: Record<string, unknown>;
  sortBy?: string[];
  limit?: number;
}

export interface ReportTemplate {
  id: string | number;
  name: string;
  config: ReportConfig;
  isSystem: boolean;
  runCount?: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Finance Types
// ─────────────────────────────────────────────────────────────────────────────

export type AccountType = 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
export type AccountSubtype =
  | 'cash' | 'bank' | 'accounts_receivable' | 'inventory' | 'prepaid'
  | 'fixed_asset' | 'accumulated_depreciation' | 'other_asset'
  | 'accounts_payable' | 'accrued_expense' | 'tax_payable' | 'other_liability'
  | 'capital' | 'retained_earnings'
  | 'sales' | 'other_income'
  | 'cogs' | 'salary' | 'rent' | 'utilities' | 'depreciation_exp'
  | 'other_expense' | 'inventory_adjustment';

export type JournalEntryStatus = 'draft' | 'posted' | 'reversed';
export type FiscalPeriodStatus = 'open' | 'closed' | 'adjusting';
export type ReferenceType = 'inventory' | 'invoice' | 'payment' | 'manual' | 'payroll' | 'depreciation' | 'period_close';

export interface FiscalPeriod {
  id: number;
  name: string;
  nameFa: string | null;
  startDate: string;
  endDate: string;
  year: number;
  quarter: number | null;
  status: FiscalPeriodStatus;
}

export interface Account {
  id: number;
  code: string;
  name: string;
  nameFa: string | null;
  type: AccountType;
  subtype: AccountSubtype | null;
  parentId: number | null;
  path: string | null;
  depth: number;
  isBankAccount: boolean;
  allowDirectPosting: boolean;
  isActive: boolean;
  currency: string;
}

export interface AccountWithBalance extends Account {
  totalDebit: string;
  totalCredit: string;
  balance: string;
  children?: AccountWithBalance[];
}

export interface JournalEntryLine {
  id: number;
  journalEntryId: number;
  accountId: number;
  accountCode?: string;
  accountName?: string;
  debit: string | null;
  credit: string | null;
  description: string | null;
  costCenter: string | null;
  contactId: number | null;
  contactType: 'customer' | 'vendor' | null;
}

export interface JournalEntry {
  id: number;
  entryNumber: string;
  entryDate: string;
  periodId: number;
  referenceType: ReferenceType;
  referenceId: number | null;
  description: string;
  descriptionFa: string | null;
  totalDebit: string;
  totalCredit: string;
  status: JournalEntryStatus;
  isReversingEntry: boolean;
  reversedEntryId: number | null;
  postedById: number | null;
  postedAt: string | null;
  lines: JournalEntryLine[];
}

export interface TrialBalance {
  asOfDate: string;
  rows: AccountBalance[];
  grandTotalDebit: string;
  grandTotalCredit: string;
  isBalanced: boolean;
}

export interface AccountBalance {
  accountId: number;
  code: string;
  name: string;
  nameFa: string | null;
  type: AccountType;
  depth: number;
  totalDebit: string;
  totalCredit: string;
  balance: string;
}

export interface IncomeStatement {
  periodStart: string;
  periodEnd: string;
  revenue: IncomeStatementRow[];
  cogs: IncomeStatementRow[];
  operatingExpenses: IncomeStatementRow[];
  totalRevenue: string;
  totalCogs: string;
  grossProfit: string;
  totalOperatingExpenses: string;
  netIncome: string;
}

export interface IncomeStatementRow {
  accountId: number;
  code: string;
  name: string;
  nameFa: string | null;
  amount: string;
}

export interface BalanceSheet {
  asOfDate: string;
  assets: BalanceSheetSection;
  liabilities: BalanceSheetSection;
  equity: BalanceSheetSection;
  totalAssets: string;
  totalLiabilitiesAndEquity: string;
  isBalanced: boolean;
}

export interface BalanceSheetSection {
  accounts: AccountBalance[];
  total: string;
}

export interface InventoryValuation {
  asOfDate: string;
  items: InventoryValuationRow[];
  totalPhysicalValue: string;
  glAccountBalance: string;
  variance: string;
  isReconciled: boolean;
}

export interface InventoryValuationRow {
  itemId: number;
  sku: string;
  itemName: string;
  quantityOnHand: string;
  unitCost: string;
  totalValue: string;
}

export interface CreateJournalEntryLine {
  accountId: number;
  debit?: string;
  credit?: string;
  description?: string;
  costCenter?: string;
}

export interface CreateJournalEntry {
  entryDate: string;
  periodId: number;
  referenceType?: ReferenceType;
  description: string;
  descriptionFa?: string;
  lines: CreateJournalEntryLine[];
}

// ─────────────────────────────────────────────────────────────────────────────
// HR Types
// ─────────────────────────────────────────────────────────────────────────────

export type Gender = 'male' | 'female';
export type MaritalStatus = 'single' | 'married' | 'divorced' | 'widowed';
export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'intern';
export type EmployeeStatus = 'active' | 'on_leave' | 'suspended' | 'terminated';
export type LeaveType = 'annual' | 'sick' | 'unpaid' | 'marriage' | 'bereavement' | 'maternity' | 'paternity' | 'hajj' | 'other';
export type LeaveStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';
export type PayrollPeriodStatus = 'draft' | 'processing' | 'approved' | 'paid' | 'closed';
export type PayrollEntryStatus = 'draft' | 'approved' | 'paid';

export interface Department {
  id: number;
  code: string;
  name: string;
  nameFa: string | null;
  parentId: number | null;
  managerId: number | null;
  costCenterCode: string | null;
  isActive: boolean;
  children: Department[];
}

export interface Employee {
  id: number;
  employeeCode: string;
  firstName: string;
  lastName: string;
  firstNameFa: string | null;
  lastNameFa: string | null;
  nationalId: string;
  birthDate: string | null;
  gender: Gender;
  maritalStatus: MaritalStatus;
  departmentId: number | null;
  jobTitle: string | null;
  employmentType: EmploymentType;
  joinDate: string;
  leaveDate: string | null;
  status: EmployeeStatus;
  baseSalary: string;
  salaryBankAccount: string | null;
  bankName: string | null;
  insuranceExempt: boolean;
  taxExempt: boolean;
  childrenCount: number;
  defaultCostCenter: string | null;
  annualLeaveBalance: number;
  sickLeaveBalance: number;
}

export interface AttendanceRecord {
  id: number;
  employeeId: number;
  recordDate: string;
  checkIn: string | null;
  checkOut: string | null;
  workHours: string;
  overtimeHours: string;
  nightHours: string;
  status: string;
  approvedById: number | null;
}

export interface LeaveRequest {
  id: number;
  employeeId: number;
  leaveType: LeaveType;
  startDate: string;
  endDate: string;
  daysRequested: number;
  status: LeaveStatus;
  approverId: number | null;
  approvedAt: string | null;
  balanceAfter: number | null;
  createdAt: string;
}

export interface PayrollEntry {
  id: number;
  periodId: number;
  employeeId: number;
  baseSalary: string;
  overtimePay: string;
  housingAllowance: string;
  foodAllowance: string;
  childcareAllowance: string;
  bonus: string;
  otherEarnings: string;
  totalEarnings: string;
  workingDays: number;
  overtimeHours: string;
  absentDays: number;
  insuranceEmployee: string;
  insuranceEmployer: string;
  tax: string;
  advanceDeduction: string;
  loanDeduction: string;
  otherDeductions: string;
  totalDeductions: string;
  netSalary: string;
  costCenter: string | null;
  status: PayrollEntryStatus;
  paymentReference: string | null;
  paidAt: string | null;
}

export interface PayrollPeriod {
  id: number;
  year: number;
  month: number;
  startDate: string;
  endDate: string;
  status: PayrollPeriodStatus;
  totalEmployees: number;
  totalGross: string;
  totalNet: string;
  totalTax: string;
  totalInsuranceEmployee: string;
  totalInsuranceEmployer: string;
  journalEntryId: number | null;
  paymentBatchId: string | null;
  approvedAt: string | null;
  paidAt: string | null;
}

// ─────────────────────────────────────────────────────────────────────────────
// Inventory Types
// ─────────────────────────────────────────────────────────────────────────────

export type MovementType = 'inbound' | 'outbound' | 'transfer' | 'adjustment' | 'return' | 'scrap';
export type MovementStatus = 'pending' | 'completed' | 'cancelled';

export interface InventoryCategory {
  id: number;
  name: string;
  code: string;
  description: string | null;
  parent_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Supplier {
  id: number;
  name: string;
  code: string;
  contact_name: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  tax_number: string | null;
  payment_terms_days: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InventoryItem {
  id: number;
  sku: string;
  name: string;
  description: string | null;
  barcode: string | null;
  qr_code: string | null;
  unit_of_measure: string;
  category_id: number | null;
  default_supplier_id: number | null;
  standard_cost: string;
  selling_price: string | null;
  global_reorder_point: string;
  global_max_stock: string | null;
  lead_time_days: number;
  is_active: boolean;
  allow_negative_stock: boolean;
  created_at: string;
  updated_at: string;
  created_by: number | null;
}

export interface InventoryItemDetail extends InventoryItem {
  category: InventoryCategory | null;
  default_supplier: Supplier | null;
  stock_levels: StockLevel[];
}

export interface InventoryLocation {
  id: number;
  code: string;
  name: string;
  warehouse: string;
  zone: string | null;
  aisle: string | null;
  bin: string | null;
  capacity: string | null;
  is_active: boolean;
  is_pickable: boolean;
  is_receivable: boolean;
  created_at: string;
  updated_at: string;
}

export interface StockLevel {
  id: number;
  item_id: number;
  location_id: number;
  quantity_on_hand: string;
  quantity_reserved: string;
  quantity_available: string;
  reorder_point: string | null;
  max_stock: string | null;
  is_below_reorder: boolean;
  location: InventoryLocation | null;
  updated_at: string;
}

export interface InventoryMovement {
  id: number;
  reference_number: string;
  item_id: number;
  from_location_id: number | null;
  to_location_id: number | null;
  supplier_id: number | null;
  movement_type: MovementType;
  status: MovementStatus;
  quantity: string;
  unit_cost: string | null;
  quantity_before: string;
  quantity_after: string;
  movement_date: string;
  reason: string | null;
  notes: string | null;
  external_reference: string | null;
  created_at: string;
  created_by: number | null;
}

export interface LowStockItem {
  item_id: number;
  sku: string;
  item_name: string;
  location_id: number;
  location_code: string;
  quantity_on_hand: string;
  quantity_available: string;
  reorder_point: string;
  shortage: string;
}

export interface CreateItemRequest {
  sku?: string;
  name: string;
  description?: string;
  unit_of_measure: string;
  category_id?: number;
  default_supplier_id?: number;
  standard_cost?: string;
  selling_price?: string;
  global_reorder_point?: string;
  global_max_stock?: string;
  lead_time_days?: number;
  allow_negative_stock?: boolean;
}

export interface InboundMovementRequest {
  item_id: number;
  to_location_id: number;
  quantity: string;
  unit_cost?: string;
  supplier_id?: number;
  reason?: string;
  notes?: string;
  external_reference?: string;
}

export interface OutboundMovementRequest {
  item_id: number;
  from_location_id: number;
  quantity: string;
  reason?: string;
  notes?: string;
  external_reference?: string;
}

export interface StockTransferRequest {
  item_id: number;
  from_location_id: number;
  to_location_id: number;
  quantity: string;
  reason?: string;
}

export interface StockAdjustRequest {
  item_id: number;
  location_id: number;
  new_quantity?: string;
  quantity_delta?: string;
  reason: string;
  notes?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Procurement Types
// ─────────────────────────────────────────────────────────────────────────────

export type VendorCategory = 'supplier' | 'contractor' | 'service' | 'logistics' | 'other';
export type PRPriority = 'low' | 'medium' | 'high' | 'critical';
export type PRStatus = 'draft' | 'pending_approval' | 'approved' | 'rejected' | 'converted';
export type POStatus = 'draft' | 'sent' | 'acknowledged' | 'partial_received' | 'received' | 'invoiced' | 'paid' | 'cancelled';
export type VendorInvoiceStatus = 'pending_verification' | 'approved' | 'disputed' | 'paid';
export type MatchResult = 'match' | 'quantity_mismatch' | 'price_mismatch' | 'both_mismatch';
export type VendorPaymentMethod = 'bank_transfer' | 'check' | 'cash' | 'credit_note';

export interface Vendor {
  id: number;
  code: string;
  name: string;
  nameFa: string | null;
  taxId: string | null;
  economicCode: string | null;
  phone: string | null;
  email: string | null;
  contactPerson: string | null;
  creditLimit: string;
  paymentTerms: number;
  totalPurchased: string;
  totalPaid: string;
  balanceDue: string;
  rating: number;
  onTimeDeliveryRate: number;
  qualityScore: number;
  isActive: boolean;
  isApproved: boolean;
  category: VendorCategory;
}

export interface PRLine {
  id: number;
  itemId: number | null;
  description: string;
  quantity: string;
  estimatedUnitPrice: string;
  uom: string | null;
  status: string;
}

export interface PurchaseRequest {
  id: number;
  requestNumber: string;
  requesterId: number;
  department: string;
  priority: PRPriority;
  requiredDate: string | null;
  justification: string | null;
  status: PRStatus;
  totalEstimated: string;
  approverId: number | null;
  approvedAt: string | null;
  approvalNotes: string | null;
  rejectionReason: string | null;
  lines: PRLine[];
  createdAt: string;
}

export interface POLine {
  id: number;
  itemId: number;
  description: string;
  quantity: string;
  unitPrice: string;
  discountPercent: string;
  taxPercent: string;
  lineTotal: string;
  quantityReceived: string;
  quantityInvoiced: string;
  status: string;
}

export interface PurchaseOrder {
  id: number;
  poNumber: string;
  vendorId: number;
  requestId: number | null;
  orderDate: string;
  expectedDelivery: string | null;
  actualDelivery: string | null;
  subtotal: string;
  discountAmount: string;
  taxAmount: string;
  shippingCost: string;
  totalAmount: string;
  status: POStatus;
  lines: POLine[];
  createdAt: string;
}

export interface ReceiptLine {
  poLineId: number;
  itemId: number;
  quantityReceived: string;
  unitPrice: string;
  condition: string;
  rejectionReason?: string;
}

export interface GoodsReceipt {
  id: number;
  receiptNumber: string;
  poId: number;
  receiptDate: string;
  receivedById: number;
  journalEntryId: number | null;
  lines: ReceiptLine[];
}

export interface VendorInvoice {
  id: number;
  invoiceNumber: string;
  poId: number | null;
  vendorId: number;
  invoiceDate: string;
  dueDate: string;
  amount: string;
  taxAmount: string;
  totalAmount: string;
  amountPaid: string;
  amountDue: string;
  status: VendorInvoiceStatus;
  matchResult: MatchResult | null;
  matchNotes: string | null;
  verifiedById: number | null;
  journalEntryId: number | null;
}

export interface ThreeWayMatchResult {
  poId: number;
  receiptId: number;
  invoiceId: number;
  result: MatchResult;
  poTotal: string;
  receiptTotal: string;
  invoiceTotal: string;
  qtyVariance: string;
  priceVariancePct: string;
  notes: string;
  autoApproved: boolean;
}

export interface VendorPayment {
  id: number;
  paymentNumber: string;
  vendorId: number;
  vendorInvoiceId: number | null;
  paymentDate: string;
  amount: string;
  method: VendorPaymentMethod;
  referenceNumber: string | null;
  journalEntryId: number | null;
  status: string;
}

export interface CreatePRLine {
  itemId?: number;
  description: string;
  quantity: string;
  estimatedUnitPrice?: string;
  uom?: string;
  specifications?: string;
}

export interface CreatePR {
  department: string;
  priority?: PRPriority;
  requiredDate?: string;
  justification?: string;
  lines: CreatePRLine[];
}

export interface CreatePOLine {
  itemId: number;
  description: string;
  quantity: string;
  unitPrice: string;
  discountPercent?: string;
  taxPercent?: string;
}

export interface CreatePO {
  vendorId: number;
  requestId?: number;
  orderDate: string;
  expectedDelivery?: string;
  deliveryLocationId?: number;
  lines: CreatePOLine[];
}

export interface CreateReceipt {
  poId: number;
  receiptDate: string;
  deliveryNoteNumber?: string;
  notes?: string;
  lines: ReceiptLine[];
}

// ─────────────────────────────────────────────────────────────────────────────
// Sales Types
// ─────────────────────────────────────────────────────────────────────────────

export type CustomerCategory = 'A' | 'B' | 'C';
export type QuoteStatus = 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired' | 'converted';
export type InvoiceStatus = 'draft' | 'issued' | 'partial_paid' | 'paid' | 'overdue' | 'cancelled';
export type PaymentMethod = 'cash' | 'check' | 'bank_transfer' | 'card' | 'credit_note';
export type PaymentStatus = 'pending' | 'cleared' | 'bounced';

export interface Customer {
  id: number;
  code: string;
  name: string;
  nameFa: string | null;
  taxId: string | null;
  economicCode: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  city: string | null;
  creditLimit: string;
  paymentTerms: number;
  defaultDiscountPercent: string;
  totalInvoiced: string;
  totalPaid: string;
  balanceDue: string;
  isActive: boolean;
  isVip: boolean;
  category: CustomerCategory;
}

export interface QuoteLine {
  id: number;
  itemId: number;
  description: string;
  quantity: string;
  unitPrice: string;
  discountPercent: string;
  taxPercent: string;
  lineTotal: string;
}

export interface SalesQuote {
  id: number;
  quoteNumber: string;
  customerId: number;
  quoteDate: string;
  expiryDate: string;
  status: QuoteStatus;
  subtotal: string;
  discountAmount: string;
  taxAmount: string;
  total: string;
  notes: string | null;
  convertedToInvoiceId: number | null;
  lines: QuoteLine[];
}

export interface InvoiceLine {
  id: number;
  itemId: number;
  description: string;
  unitOfMeasure: string | null;
  quantity: string;
  unitPrice: string;
  discountAmount: string;
  taxAmount: string;
  lineTotal: string;
  unitCost: string;
  totalCost: string;
  grossMargin?: string;
}

export interface SalesInvoice {
  id: number;
  invoiceNumber: string;
  customerId: number;
  quoteId: number | null;
  draftDate: string;
  issueDate: string | null;
  dueDate: string | null;
  subtotal: string;
  discountAmount: string;
  taxAmount: string;
  totalAmount: string;
  amountPaid: string;
  amountDue: string;
  status: InvoiceStatus;
  revenueJournalEntryId: number | null;
  cogsJournalEntryId: number | null;
  taxInvoiceNumber: string | null;
  qrData: string | null;
  lines: InvoiceLine[];
}

export interface InvoiceListItem {
  id: number;
  invoiceNumber: string;
  customerId: number;
  customerName: string | null;
  issueDate: string | null;
  dueDate: string | null;
  totalAmount: string;
  amountDue: string;
  status: InvoiceStatus;
  ageDays: number | null;
}

export interface SalesPayment {
  id: number;
  paymentNumber: string;
  customerId: number;
  invoiceId: number | null;
  paymentDate: string;
  amount: string;
  method: PaymentMethod;
  referenceNumber: string | null;
  journalEntryId: number | null;
  status: PaymentStatus;
}

export interface CreateQuoteLine {
  itemId: number;
  description: string;
  quantity: string;
  unitPrice: string;
  discountPercent?: string;
  taxPercent?: string;
}

export interface CreateQuote {
  customerId: number;
  quoteDate: string;
  expiryDate: string;
  notes?: string;
  terms?: string;
  lines: CreateQuoteLine[];
}

export interface CreateInvoiceLine {
  itemId: number;
  description: string;
  unitOfMeasure?: string;
  quantity: string;
  unitPrice: string;
  discountAmount?: string;
  taxPercent?: string;
}

export interface CreateInvoice {
  customerId: number;
  draftDate: string;
  dueDate?: string;
  quoteId?: number;
  notes?: string;
  lines: CreateInvoiceLine[];
}

export interface CreatePayment {
  customerId: number;
  invoiceId?: number;
  paymentDate: string;
  amount: string;
  method: PaymentMethod;
  bankAccountId?: number;
  referenceNumber?: string;
  notes?: string;
}

export interface RevenueByPeriodRow {
  period: string;
  invoiceCount: number;
  subtotal: string;
  discount: string;
  tax: string;
  total: string;
  totalPaid: string;
  outstanding: string;
}

export interface TopCustomerRow {
  customerId: number;
  customerCode: string;
  customerName: string;
  invoiceCount: number;
  totalRevenue: string;
  totalPaid: string;
  balanceDue: string;
}

export interface ProductMarginRow {
  itemId: number;
  sku: string;
  itemName: string;
  quantitySold: string;
  revenue: string;
  cogs: string;
  grossProfit: string;
  marginPercent: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Common/Shared Types
// ─────────────────────────────────────────────────────────────────────────────

export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface SelectOption {
  value: string | number;
  label: string;
}