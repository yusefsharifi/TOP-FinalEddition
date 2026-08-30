export type ProjectStatus = 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
export type ProjectPriority = 'low' | 'medium' | 'high' | 'critical';
export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'completed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';
export type TaskType = 'feature' | 'bug' | 'improvement' | 'documentation' | 'testing';

export interface Project {
  id?: number;
  name: string;
  code: string;
  description?: string;
  status: ProjectStatus;
  priority: ProjectPriority;
  startDate: string;
  endDate?: string;
  actualEndDate?: string;
  budget: number;
  currency: string;
  spentAmount: number;
  remainingAmount: number;
  progress: number;
  customerId?: number;
  customerName?: string;
  managerId: number;
  managerName: string;
  team: ProjectMember[];
  tasks: Task[];
  milestones: Milestone[];
  documents: ProjectDocument[];
  risks: ProjectRisk[];
  createdAt: string;
  updatedAt: string;
}

export interface ProjectMember {
  id?: number;
  employeeId: number;
  employeeName: string;
  role: string;
  hourlyRate: number;
  startDate: string;
  endDate?: string;
  allocation: number; // percentage
  isActive: boolean;
}

export interface Task {
  id?: number;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  type: TaskType;
  projectId: number;
  projectName: string;
  assignedToId?: number;
  assignedToName?: string;
  reporterId: number;
  reporterName: string;
  estimatedHours: number;
  actualHours: number;
  startDate?: string;
  dueDate?: string;
  completedDate?: string;
  parentTaskId?: number;
  subtasks: Task[];
  attachments: TaskAttachment[];
  comments: TaskComment[];
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface TaskAttachment {
  id?: number;
  name: string;
  url: string;
  size: number;
  type: string;
  uploadedBy: string;
  uploadedAt: string;
}

export interface TaskComment {
  id?: number;
  content: string;
  authorId: number;
  authorName: string;
  createdAt: string;
  updatedAt: string;
}

export interface Milestone {
  id?: number;
  name: string;
  description?: string;
  projectId: number;
  projectName: string;
  dueDate: string;
  completedDate?: string;
  isCompleted: boolean;
  tasks: Task[];
  createdAt: string;
  updatedAt: string;
}

export interface ProjectDocument {
  id?: number;
  name: string;
  type: string;
  url: string;
  size: number;
  uploadedBy: string;
  uploadedAt: string;
  version: string;
  description?: string;
}

export interface ProjectRisk {
  id?: number;
  title: string;
  description: string;
  probability: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
  status: 'open' | 'mitigated' | 'closed';
  mitigationPlan?: string;
  assignedToId?: number;
  assignedToName?: string;
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TimeEntry {
  id?: number;
  taskId: number;
  taskTitle: string;
  projectId: number;
  projectName: string;
  employeeId: number;
  employeeName: string;
  date: string;
  hours: number;
  description?: string;
  billable: boolean;
  hourlyRate: number;
  totalAmount: number;
  createdAt: string;
  updatedAt: string;
}

export interface ProjectReport {
  id?: number;
  name: string;
  type: 'progress' | 'financial' | 'resource' | 'risk' | 'custom';
  projectId: number;
  projectName: string;
  data: any;
  generatedAt: string;
  generatedBy: string;
}

export interface ProjectTemplate {
  id?: number;
  name: string;
  description?: string;
  phases: ProjectPhase[];
  defaultDuration: number;
  defaultBudget: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ProjectPhase {
  id?: number;
  name: string;
  description?: string;
  order: number;
  duration: number;
  tasks: ProjectTemplateTask[];
}

export interface ProjectTemplateTask {
  id?: number;
  title: string;
  description?: string;
  estimatedHours: number;
  priority: TaskPriority;
  type: TaskType;
  dependencies: number[];
} 