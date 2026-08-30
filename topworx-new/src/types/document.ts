export type DocumentType = 'pdf' | 'doc' | 'docx' | 'xls' | 'xlsx' | 'ppt' | 'pptx' | 'txt' | 'image' | 'video' | 'audio' | 'other';
export type DocumentStatus = 'draft' | 'review' | 'approved' | 'archived' | 'deleted';
export type DocumentCategory = 'contract' | 'invoice' | 'report' | 'proposal' | 'manual' | 'policy' | 'form' | 'template' | 'other';
export type AccessLevel = 'public' | 'private' | 'restricted' | 'confidential';

export interface Document {
  id?: number;
  title: string;
  filename: string;
  originalFilename: string;
  type: DocumentType;
  category: DocumentCategory;
  status: DocumentStatus;
  accessLevel: AccessLevel;
  size: number;
  url: string;
  thumbnailUrl?: string;
  description?: string;
  tags: string[];
  version: string;
  authorId: number;
  authorName: string;
  department?: string;
  projectId?: number;
  projectName?: string;
  customerId?: number;
  customerName?: string;
  uploadedAt: string;
  lastModifiedAt: string;
  lastAccessedAt?: string;
  downloadCount: number;
  viewCount: number;
  isFavorite: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface DocumentFolder {
  id?: number;
  name: string;
  description?: string;
  parentId?: number;
  path: string;
  isPublic: boolean;
  accessLevel: AccessLevel;
  createdBy: number;
  createdByName: string;
  documentCount: number;
  subfolderCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface DocumentVersion {
  id?: number;
  documentId: number;
  version: string;
  filename: string;
  size: number;
  url: string;
  changes: string;
  uploadedBy: number;
  uploadedByName: string;
  uploadedAt: string;
}

export interface DocumentComment {
  id?: number;
  documentId: number;
  content: string;
  authorId: number;
  authorName: string;
  parentId?: number;
  replies: DocumentComment[];
  createdAt: string;
  updatedAt: string;
}

export interface DocumentShare {
  id?: number;
  documentId: number;
  documentTitle: string;
  sharedWithId: number;
  sharedWithName: string;
  sharedWithEmail: string;
  permission: 'view' | 'edit' | 'admin';
  expiresAt?: string;
  sharedBy: number;
  sharedByName: string;
  sharedAt: string;
}

export interface DocumentTemplate {
  id?: number;
  name: string;
  description?: string;
  category: DocumentCategory;
  type: DocumentType;
  url: string;
  isActive: boolean;
  usageCount: number;
  createdBy: number;
  createdByName: string;
  createdAt: string;
  updatedAt: string;
}

export interface DocumentWorkflow {
  id?: number;
  name: string;
  description?: string;
  steps: WorkflowStep[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface WorkflowStep {
  id?: number;
  name: string;
  order: number;
  assignedRole: string;
  assignedUserId?: number;
  assignedUserName?: string;
  action: 'approve' | 'review' | 'sign' | 'notify';
  isRequired: boolean;
  estimatedDays: number;
}

export interface DocumentAudit {
  id?: number;
  documentId: number;
  documentTitle: string;
  action: 'view' | 'download' | 'edit' | 'delete' | 'share' | 'comment';
  userId: number;
  userName: string;
  userIp?: string;
  userAgent?: string;
  details?: string;
  timestamp: string;
}

export interface DocumentSearch {
  query: string;
  filters: {
    category?: DocumentCategory[];
    type?: DocumentType[];
    status?: DocumentStatus[];
    authorId?: number[];
    dateRange?: {
      start: string;
      end: string;
    };
    tags?: string[];
  };
  sortBy: 'relevance' | 'date' | 'name' | 'size' | 'downloads' | 'views';
  sortOrder: 'asc' | 'desc';
  page: number;
  limit: number;
} 