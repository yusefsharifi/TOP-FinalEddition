// Sales & CRM Module Types

export interface Customer {
  id: string;
  code: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  country: string;
  postal_code: string;
  customer_type: 'individual' | 'corporate' | 'government';
  industry: string;
  segment_id?: string;
  segment_name?: string;
  loyalty_tier_id?: string;
  loyalty_tier_name?: string;
  credit_limit: number;
  current_balance: number;
  status: 'active' | 'inactive' | 'suspended';
  assigned_to?: string;
  assigned_to_name?: string;
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  position: string;
  source: 'website' | 'social_media' | 'referral' | 'cold_call' | 'event' | 'other';
  status: 'new' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigned_to?: string;
  assigned_to_name?: string;
  estimated_value: number;
  probability: number;
  expected_close_date: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface Opportunity {
  id: string;
  title: string;
  customer_id: string;
  customer_name: string;
  lead_id?: string;
  lead_name?: string;
  stage: 'prospecting' | 'qualification' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
  probability: number;
  expected_revenue: number;
  actual_revenue: number;
  expected_close_date: string;
  actual_close_date?: string;
  assigned_to?: string;
  assigned_to_name?: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Quote {
  id: string;
  quote_number: string;
  customer_id: string;
  customer_name: string;
  opportunity_id?: string;
  opportunity_title?: string;
  status: 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired';
  valid_until: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  currency: string;
  notes: string;
  terms_conditions: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface QuoteItem {
  id: string;
  quote_id: string;
  product_id: string;
  product_name: string;
  product_code: string;
  description: string;
  quantity: number;
  unit_price: number;
  discount_percentage: number;
  tax_percentage: number;
  line_total: number;
}

export interface SalesOrder {
  id: string;
  order_number: string;
  customer_id: string;
  customer_name: string;
  quote_id?: string;
  quote_number?: string;
  opportunity_id?: string;
  opportunity_title?: string;
  status: 'draft' | 'confirmed' | 'in_production' | 'ready_for_delivery' | 'delivered' | 'cancelled';
  order_date: string;
  delivery_date: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  shipping_amount: number;
  total_amount: number;
  currency: string;
  payment_terms: string;
  shipping_address: string;
  billing_address: string;
  notes: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface SalesOrderItem {
  id: string;
  sales_order_id: string;
  product_id: string;
  product_name: string;
  product_code: string;
  description: string;
  quantity: number;
  unit_price: number;
  discount_percentage: number;
  tax_percentage: number;
  line_total: number;
  delivered_quantity: number;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  customer_id: string;
  customer_name: string;
  sales_order_id?: string;
  sales_order_number?: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  invoice_date: string;
  due_date: string;
  paid_date?: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  shipping_amount: number;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  currency: string;
  payment_terms: string;
  notes: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface InvoiceItem {
  id: string;
  invoice_id: string;
  product_id: string;
  product_name: string;
  product_code: string;
  description: string;
  quantity: number;
  unit_price: number;
  discount_percentage: number;
  tax_percentage: number;
  line_total: number;
}

export interface SalesActivity {
  id: string;
  type: 'call' | 'email' | 'meeting' | 'presentation' | 'follow_up' | 'other';
  subject: string;
  description: string;
  customer_id?: string;
  customer_name?: string;
  lead_id?: string;
  lead_name?: string;
  opportunity_id?: string;
  opportunity_title?: string;
  assigned_to: string;
  assigned_to_name: string;
  activity_date: string;
  duration: number; // in minutes
  outcome: string;
  next_action: string;
  next_action_date?: string;
  created_at: string;
  updated_at: string;
}

export interface SalesPipeline {
  id: string;
  name: string;
  description: string;
  stages: SalesPipelineStage[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SalesPipelineStage {
  id: string;
  pipeline_id: string;
  name: string;
  description: string;
  order: number;
  probability: number;
  color: string;
  is_active: boolean;
}

export interface SalesTarget {
  id: string;
  user_id: string;
  user_name: string;
  period: string; // 'monthly', 'quarterly', 'yearly'
  period_start: string;
  period_end: string;
  target_amount: number;
  achieved_amount: number;
  target_opportunities: number;
  achieved_opportunities: number;
  target_leads: number;
  achieved_leads: number;
  status: 'active' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface SalesReport {
  id: string;
  name: string;
  type: 'sales_summary' | 'pipeline_analysis' | 'customer_analysis' | 'product_performance' | 'sales_activity';
  parameters: Record<string, any>;
  schedule: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly' | 'manual';
  recipients: string[];
  last_generated?: string;
  created_at: string;
  updated_at: string;
}

// Form Types
export interface CustomerFormData {
  code: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  country: string;
  postal_code: string;
  customer_type: 'individual' | 'corporate' | 'government';
  industry: string;
  segment_id?: string;
  loyalty_tier_id?: string;
  credit_limit: number;
  assigned_to?: string;
}

export interface LeadFormData {
  name: string;
  email: string;
  phone: string;
  company: string;
  position: string;
  source: 'website' | 'social_media' | 'referral' | 'cold_call' | 'event' | 'other';
  status: 'new' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigned_to?: string;
  estimated_value: number;
  probability: number;
  expected_close_date: string;
  notes: string;
}

export interface OpportunityFormData {
  title: string;
  customer_id: string;
  lead_id?: string;
  stage: 'prospecting' | 'qualification' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
  probability: number;
  expected_revenue: number;
  expected_close_date: string;
  assigned_to?: string;
  description: string;
}

export interface QuoteFormData {
  customer_id: string;
  opportunity_id?: string;
  valid_until: string;
  currency: string;
  notes: string;
  terms_conditions: string;
  items: QuoteItemFormData[];
}

export interface QuoteItemFormData {
  product_id: string;
  description: string;
  quantity: number;
  unit_price: number;
  discount_percentage: number;
  tax_percentage: number;
}

// Filter Types
export interface SalesFilters {
  date_from?: string;
  date_to?: string;
  status?: string;
  assigned_to?: string;
  customer_id?: string;
  search?: string;
}

export interface CustomerFilters {
  customer_type?: string;
  status?: string;
  segment_id?: string;
  assigned_to?: string;
  search?: string;
}

export interface LeadFilters {
  status?: string;
  source?: string;
  priority?: string;
  assigned_to?: string;
  search?: string;
}

// Response Types
export interface SalesResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface SalesStats {
  total_revenue: number;
  total_opportunities: number;
  total_leads: number;
  total_customers: number;
  conversion_rate: number;
  average_deal_size: number;
  sales_cycle_days: number;
  win_rate: number;
} 