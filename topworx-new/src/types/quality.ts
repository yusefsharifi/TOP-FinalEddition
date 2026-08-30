export type QualityStatus = 'pending' | 'in_progress' | 'passed' | 'failed' | 'conditional' | 'cancelled';
export type InspectionType = 'incoming' | 'in_process' | 'final' | 'random' | 'special';
export type DefectType = 'critical' | 'major' | 'minor' | 'cosmetic';
export type AuditType = 'internal' | 'external' | 'supplier' | 'customer';
export type AuditStatus = 'planned' | 'in_progress' | 'completed' | 'cancelled';
export type ComplaintStatus = 'open' | 'investigating' | 'resolved' | 'closed';
export type CorrectiveActionStatus = 'pending' | 'in_progress' | 'completed' | 'verified' | 'closed';

export interface QualityInspection {
  id?: number;
  inspectionNumber: string;
  type: InspectionType;
  productId?: number;
  productName?: string;
  batchNumber?: string;
  lotNumber?: string;
  quantity: number;
  inspectedQuantity: number;
  passedQuantity: number;
  failedQuantity: number;
  status: QualityStatus;
  inspectorId: number;
  inspectorName: string;
  inspectionDate: string;
  nextInspectionDate?: string;
  specifications: InspectionSpecification[];
  defects: QualityDefect[];
  notes?: string;
  attachments: QualityAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface InspectionSpecification {
  id?: number;
  parameter: string;
  specification: string;
  unit: string;
  minValue?: number;
  maxValue?: number;
  targetValue?: number;
  actualValue?: number;
  isConforming: boolean;
  remarks?: string;
}

export interface QualityDefect {
  id?: number;
  defectCode: string;
  description: string;
  type: DefectType;
  quantity: number;
  location?: string;
  cause?: string;
  action?: string;
  responsiblePerson?: string;
  dueDate?: string;
  status: CorrectiveActionStatus;
  createdAt: string;
  updatedAt: string;
}

export interface QualityAttachment {
  id?: number;
  name: string;
  type: string;
  url: string;
  size: number;
  uploadedBy: string;
  uploadedAt: string;
}

export interface QualityControlPoint {
  id?: number;
  name: string;
  description?: string;
  processId: number;
  processName: string;
  location: string;
  frequency: string;
  parameters: string[];
  acceptanceCriteria: string;
  responsiblePerson: string;
  isCritical: boolean;
  isActive: boolean;
  lastInspectionDate?: string;
  nextInspectionDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface QualityAudit {
  id?: number;
  auditNumber: string;
  type: AuditType;
  scope: string;
  objective: string;
  status: AuditStatus;
  plannedDate: string;
  actualDate?: string;
  duration: number;
  auditorId: number;
  auditorName: string;
  auditeeId?: number;
  auditeeName?: string;
  findings: AuditFinding[];
  conclusions: string;
  recommendations: string;
  attachments: QualityAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface AuditFinding {
  id?: number;
  category: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  evidence: string;
  requirement?: string;
  correctiveAction?: string;
  responsiblePerson?: string;
  dueDate?: string;
  status: CorrectiveActionStatus;
  createdAt: string;
  updatedAt: string;
}

export interface CustomerComplaint {
  id?: number;
  complaintNumber: string;
  customerId: number;
  customerName: string;
  contactPerson: string;
  contactEmail: string;
  contactPhone: string;
  productId?: number;
  productName?: string;
  serviceId?: number;
  serviceName?: string;
  complaintDate: string;
  receivedDate: string;
  description: string;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: ComplaintStatus;
  assignedToId?: number;
  assignedToName?: string;
  investigation: ComplaintInvestigation;
  correctiveActions: CorrectiveAction[];
  attachments: QualityAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface ComplaintInvestigation {
  id?: number;
  rootCause: string;
  analysis: string;
  impact: string;
  investigator: string;
  investigationDate: string;
  findings: string;
  recommendations: string;
}

export interface CorrectiveAction {
  id?: number;
  actionNumber: string;
  description: string;
  type: 'corrective' | 'preventive' | 'improvement';
  rootCause: string;
  action: string;
  responsiblePerson: string;
  assignedToId: number;
  assignedToName: string;
  plannedDate: string;
  dueDate: string;
  completedDate?: string;
  status: CorrectiveActionStatus;
  effectiveness: string;
  verificationDate?: string;
  verifiedBy?: string;
  attachments: QualityAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface QualityDocument {
  id?: number;
  documentNumber: string;
  title: string;
  type: 'sop' | 'wi' | 'form' | 'policy' | 'procedure' | 'manual';
  category: string;
  version: string;
  status: 'draft' | 'review' | 'approved' | 'obsolete';
  content: string;
  authorId: number;
  authorName: string;
  reviewerId?: number;
  reviewerName?: string;
  approvalDate?: string;
  effectiveDate: string;
  expiryDate?: string;
  department: string;
  tags: string[];
  attachments: QualityAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface QualityMetric {
  id?: number;
  name: string;
  description?: string;
  category: string;
  unit: string;
  target: number;
  currentValue: number;
  previousValue: number;
  trend: 'up' | 'down' | 'stable';
  status: 'good' | 'warning' | 'critical';
  calculation: string;
  dataSource: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  lastUpdated: string;
  createdAt: string;
  updatedAt: string;
}

export interface QualityReport {
  id?: number;
  reportNumber: string;
  title: string;
  type: 'inspection' | 'audit' | 'complaint' | 'corrective_action' | 'metric' | 'custom';
  period: string;
  data: any;
  generatedBy: string;
  generatedAt: string;
  recipients: string[];
  isPublic: boolean;
  attachments: QualityAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface QualityTraining {
  id?: number;
  title: string;
  description?: string;
  category: string;
  duration: number;
  trainer: string;
  location: string;
  startDate: string;
  endDate: string;
  maxParticipants: number;
  currentParticipants: number;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  participants: {
    employeeId: number;
    employeeName: string;
    status: 'registered' | 'attended' | 'completed' | 'failed';
    score?: number;
    certificate?: string;
  }[];
  materials: QualityAttachment[];
  createdAt: string;
  updatedAt: string;
} 