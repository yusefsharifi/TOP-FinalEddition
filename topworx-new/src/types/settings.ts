export type SettingType = 'string' | 'number' | 'boolean' | 'json' | 'array' | 'file';
export type SettingCategory = 'general' | 'security' | 'email' | 'notification' | 'integration' | 'appearance' | 'backup' | 'custom';

export interface SystemSetting {
  id?: number;
  key: string;
  value: any;
  type: SettingType;
  category: SettingCategory;
  label: string;
  description?: string;
  isRequired: boolean;
  isPublic: boolean;
  validation?: string;
  options?: string[];
  defaultValue?: any;
  group?: string;
  order: number;
  createdAt: string;
  updatedAt: string;
}

export interface UserPreference {
  id?: number;
  userId: number;
  key: string;
  value: any;
  type: SettingType;
  category: SettingCategory;
  label: string;
  description?: string;
  isPublic: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface EmailTemplate {
  id?: number;
  name: string;
  subject: string;
  body: string;
  variables: string[];
  category: string;
  isActive: boolean;
  isDefault: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface NotificationSetting {
  id?: number;
  name: string;
  description?: string;
  type: 'email' | 'sms' | 'push' | 'in_app';
  events: string[];
  recipients: string[];
  template?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Integration {
  id?: number;
  name: string;
  type: string;
  provider: string;
  description?: string;
  config: Record<string, any>;
  isActive: boolean;
  isConnected: boolean;
  lastSyncAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface BackupConfig {
  id?: number;
  name: string;
  type: 'full' | 'incremental' | 'differential';
  schedule: string;
  retention: number;
  storage: {
    type: 'local' | 's3' | 'ftp' | 'sftp';
    config: Record<string, any>;
  };
  isActive: boolean;
  lastBackupAt?: string;
  nextBackupAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SecuritySetting {
  id?: number;
  key: string;
  value: any;
  type: SettingType;
  category: 'authentication' | 'authorization' | 'encryption' | 'audit' | 'compliance';
  label: string;
  description?: string;
  isRequired: boolean;
  isSensitive: boolean;
  validation?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuditLog {
  id?: number;
  userId?: number;
  userName?: string;
  action: string;
  resource: string;
  resourceId?: string;
  details: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
  timestamp: string;
}

export interface SystemInfo {
  version: string;
  build: string;
  environment: string;
  database: {
    type: string;
    version: string;
    size: number;
  };
  server: {
    os: string;
    nodeVersion: string;
    memory: {
      total: number;
      used: number;
      free: number;
    };
    cpu: {
      cores: number;
      usage: number;
    };
    disk: {
      total: number;
      used: number;
      free: number;
    };
  };
  uptime: number;
  lastRestart: string;
}

export interface MaintenanceMode {
  isEnabled: boolean;
  message?: string;
  allowedIPs: string[];
  startTime?: string;
  endTime?: string;
  reason?: string;
  createdBy?: string;
  createdAt: string;
}

export interface License {
  id?: number;
  key: string;
  type: string;
  features: string[];
  maxUsers: number;
  currentUsers: number;
  expiresAt: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
} 