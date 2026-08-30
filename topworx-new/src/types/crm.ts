export type CustomerStatus = 'active' | 'inactive' | 'prospect' | 'lead';
export type CustomerType = 'individual' | 'company' | 'government';
export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'unqualified' | 'converted';
export type LeadSource = 'website' | 'referral' | 'social_media' | 'cold_call' | 'event' | 'other';
export type OpportunityStage = 'prospecting' | 'qualification' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
export type DealStatus = 'open' | 'won' | 'lost' | 'cancelled';
export type ActivityType = 'call' | 'email' | 'meeting' | 'task' | 'note';

export interface Customer {
  id?: number;
  name: string;
  email: string;
  phone: string;
  company?: string;
  status: CustomerStatus;
  type: CustomerType;
  address?: string;
  city?: string;
  country?: string;
  postalCode?: string;
  website?: string;
  industry?: string;
  employeeCount?: number;
  annualRevenue?: number;
  source: LeadSource;
  assignedTo?: string;
  tags: string[];
  notes?: string;
  lastContactDate?: string;
  nextFollowUpDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Lead {
  id?: number;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  company?: string;
  jobTitle?: string;
  status: LeadStatus;
  source: LeadSource;
  assignedTo?: string;
  score: number;
  address?: string;
  city?: string;
  country?: string;
  industry?: string;
  notes?: string;
  lastContactDate?: string;
  nextFollowUpDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Opportunity {
  id?: number;
  name: string;
  customerId: number;
  customerName: string;
  stage: OpportunityStage;
  value: number;
  currency: string;
  probability: number;
  expectedCloseDate: string;
  assignedTo?: string;
  source: LeadSource;
  description?: string;
  notes?: string;
  activities: Activity[];
  createdAt: string;
  updatedAt: string;
}

export interface Deal {
  id?: number;
  dealNumber: string;
  opportunityId: number;
  opportunityName: string;
  customerId: number;
  customerName: string;
  status: DealStatus;
  value: number;
  currency: string;
  closeDate: string;
  assignedTo?: string;
  products: DealProduct[];
  terms?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface DealProduct {
  id?: number;
  productId: number;
  productName: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  discount?: number;
}

export interface Activity {
  id?: number;
  type: ActivityType;
  subject: string;
  description?: string;
  customerId?: number;
  customerName?: string;
  leadId?: number;
  leadName?: string;
  opportunityId?: number;
  opportunityName?: string;
  assignedTo?: string;
  dueDate?: string;
  completedDate?: string;
  status: 'pending' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high';
  duration?: number;
  location?: string;
  attendees?: string[];
  attachments?: {
    id: string;
    name: string;
    url: string;
  }[];
  createdAt: string;
  updatedAt: string;
}

export interface Campaign {
  id?: number;
  name: string;
  type: 'email' | 'social_media' | 'direct_mail' | 'event' | 'other';
  status: 'draft' | 'active' | 'paused' | 'completed' | 'cancelled';
  startDate: string;
  endDate?: string;
  budget: number;
  currency: string;
  targetAudience: string;
  description?: string;
  goals: string[];
  metrics: {
    sent: number;
    opened: number;
    clicked: number;
    converted: number;
    revenue: number;
  };
  createdAt: string;
  updatedAt: string;
}

export interface SalesPipeline {
  id?: number;
  name: string;
  stages: PipelineStage[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface PipelineStage {
  id?: number;
  name: string;
  order: number;
  probability: number;
  color: string;
  isActive: boolean;
}

export interface SalesForecast {
  id?: number;
  period: string;
  totalForecast: number;
  currency: string;
  opportunities: {
    stage: string;
    count: number;
    value: number;
    probability: number;
  }[];
  createdAt: string;
  updatedAt: string;
} 