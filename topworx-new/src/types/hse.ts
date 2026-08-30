export type IncidentType = 'injury' | 'illness' | 'near_miss' | 'property_damage' | 'environmental' | 'security';
export type IncidentSeverity = 'low' | 'medium' | 'high' | 'critical';
export type IncidentStatus = 'reported' | 'investigating' | 'resolved' | 'closed';
export type RiskLevel = 'low' | 'medium' | 'high' | 'extreme';
export type RiskStatus = 'identified' | 'assessed' | 'controlled' | 'monitored';
export type TrainingType = 'safety' | 'health' | 'environmental' | 'security' | 'emergency';
export type ComplianceStatus = 'compliant' | 'non_compliant' | 'pending' | 'exempt';

export interface Incident {
  id?: number;
  incidentNumber: string;
  type: IncidentType;
  severity: IncidentSeverity;
  status: IncidentStatus;
  title: string;
  description: string;
  location: string;
  department: string;
  incidentDate: string;
  reportedDate: string;
  reportedBy: string;
  reporterPhone: string;
  reporterEmail: string;
  involvedPersons: InvolvedPerson[];
  witnesses: Witness[];
  immediateActions: string;
  rootCause: string;
  correctiveActions: CorrectiveAction[];
  attachments: HSEAttachment[];
  investigation: IncidentInvestigation;
  createdAt: string;
  updatedAt: string;
}

export interface InvolvedPerson {
  id?: number;
  employeeId: number;
  employeeName: string;
  role: string;
  injuryType?: string;
  bodyPart?: string;
  severity: 'minor' | 'moderate' | 'severe' | 'fatal';
  treatmentRequired: boolean;
  hospitalVisit: boolean;
  lostTime: number;
  returnToWorkDate?: string;
}

export interface Witness {
  id?: number;
  name: string;
  phone: string;
  email: string;
  statement: string;
  interviewDate: string;
}

export interface IncidentInvestigation {
  id?: number;
  investigator: string;
  investigationDate: string;
  methodology: string;
  findings: string;
  conclusions: string;
  recommendations: string;
  costEstimate: number;
  lessonsLearned: string;
}

export interface RiskAssessment {
  id?: number;
  assessmentNumber: string;
  title: string;
  description: string;
  department: string;
  location: string;
  assessor: string;
  assessmentDate: string;
  reviewDate: string;
  risks: Risk[];
  overallRiskLevel: RiskLevel;
  status: RiskStatus;
  attachments: HSEAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface Risk {
  id?: number;
  hazard: string;
  description: string;
  probability: 'rare' | 'unlikely' | 'possible' | 'likely' | 'certain';
  consequence: 'negligible' | 'minor' | 'moderate' | 'major' | 'catastrophic';
  riskLevel: RiskLevel;
  existingControls: string;
  additionalControls: string;
  responsiblePerson: string;
  dueDate: string;
  status: RiskStatus;
  reviewDate: string;
}

export interface HSETraining {
  id?: number;
  title: string;
  description: string;
  type: TrainingType;
  trainer: string;
  duration: number;
  location: string;
  startDate: string;
  endDate: string;
  maxParticipants: number;
  currentParticipants: number;
  cost: number;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  participants: {
    employeeId: number;
    employeeName: string;
    status: 'registered' | 'attended' | 'completed' | 'failed';
    score?: number;
    certificate?: string;
    expiryDate?: string;
  }[];
  materials: HSEAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface SafetyInspection {
  id?: number;
  inspectionNumber: string;
  inspector: string;
  inspectionDate: string;
  location: string;
  department: string;
  type: 'routine' | 'special' | 'follow_up' | 'compliance';
  findings: InspectionFinding[];
  overallRating: 'excellent' | 'good' | 'fair' | 'poor' | 'unsatisfactory';
  recommendations: string;
  nextInspectionDate: string;
  attachments: HSEAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface InspectionFinding {
  id?: number;
  category: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  actionRequired: string;
  responsiblePerson: string;
  dueDate: string;
  status: 'open' | 'in_progress' | 'completed' | 'verified';
  completionDate?: string;
  verificationDate?: string;
  verifiedBy?: string;
}

export interface EmergencyPlan {
  id?: number;
  name: string;
  description: string;
  type: 'fire' | 'medical' | 'chemical' | 'natural_disaster' | 'security';
  location: string;
  responsiblePerson: string;
  emergencyContacts: EmergencyContact[];
  procedures: string;
  evacuationRoutes: string;
  assemblyPoints: string;
  equipment: string[];
  lastReviewDate: string;
  nextReviewDate: string;
  isActive: boolean;
  attachments: HSEAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface EmergencyContact {
  id?: number;
  name: string;
  role: string;
  phone: string;
  email: string;
  isPrimary: boolean;
}

export interface ComplianceRequirement {
  id?: number;
  title: string;
  description: string;
  regulation: string;
  standard: string;
  requirement: string;
  department: string;
  responsiblePerson: string;
  dueDate: string;
  status: ComplianceStatus;
  evidence: string;
  reviewDate: string;
  attachments: HSEAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface EnvironmentalAspect {
  id?: number;
  aspect: string;
  description: string;
  impact: 'positive' | 'negative' | 'neutral';
  significance: 'low' | 'medium' | 'high';
  controlMeasures: string;
  monitoringFrequency: string;
  responsiblePerson: string;
  lastAssessment: string;
  nextAssessment: string;
  isSignificant: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface WasteManagement {
  id?: number;
  wasteNumber: string;
  wasteType: string;
  description: string;
  quantity: number;
  unit: string;
  generationDate: string;
  location: string;
  department: string;
  disposalMethod: string;
  disposalDate?: string;
  disposalCompany?: string;
  cost: number;
  certificate?: string;
  status: 'generated' | 'stored' | 'disposed' | 'certified';
  attachments: HSEAttachment[];
  createdAt: string;
  updatedAt: string;
}

export interface HSEAttachment {
  id?: number;
  name: string;
  type: string;
  url: string;
  size: number;
  uploadedBy: string;
  uploadedAt: string;
}

export interface HSEMetric {
  id?: number;
  name: string;
  description?: string;
  category: 'safety' | 'health' | 'environmental' | 'compliance';
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

export interface HSEReport {
  id?: number;
  reportNumber: string;
  title: string;
  type: 'incident' | 'inspection' | 'training' | 'compliance' | 'environmental' | 'custom';
  period: string;
  data: any;
  generatedBy: string;
  generatedAt: string;
  recipients: string[];
  isPublic: boolean;
  attachments: HSEAttachment[];
  createdAt: string;
  updatedAt: string;
} 