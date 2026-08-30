import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { SystemSetting, UserPreference, EmailTemplate, NotificationSetting, Integration, BackupConfig, SecuritySetting, AuditLog, SystemInfo, MaintenanceMode, License } from '../../types/settings';

// --- System Settings ---
export const useSystemSettings = (filter?: any) =>
  useQuery<SystemSetting[]>(['systemSettings', filter], async () => {
    const { data } = await axios.get('/api/settings/system', { params: filter });
    return data;
  });

export const useUpdateSystemSetting = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<SystemSetting>) => axios.put(`/api/settings/system/${payload.key}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['systemSettings'])
    }
  );
};

export const useUpdateSystemSettings = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: SystemSetting[]) => axios.put('/api/settings/system/batch', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['systemSettings'])
    }
  );
};

// --- User Preferences ---
export const useUserPreferences = (userId: number, filter?: any) =>
  useQuery<UserPreference[]>(['userPreferences', userId, filter], async () => {
    const { data } = await axios.get(`/api/settings/users/${userId}/preferences`, { params: filter });
    return data;
  });

export const useUpdateUserPreference = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: { userId: number; key: string; value: any }) => 
      axios.put(`/api/settings/users/${payload.userId}/preferences/${payload.key}`, { value: payload.value }),
    {
      onSuccess: () => queryClient.invalidateQueries(['userPreferences'])
    }
  );
};

// --- Email Templates ---
export const useEmailTemplates = (filter?: any) =>
  useQuery<EmailTemplate[]>(['emailTemplates', filter], async () => {
    const { data } = await axios.get('/api/settings/email-templates', { params: filter });
    return data;
  });

export const useCreateEmailTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<EmailTemplate>) => axios.post('/api/settings/email-templates', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['emailTemplates'])
    }
  );
};

export const useUpdateEmailTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<EmailTemplate>) => axios.put(`/api/settings/email-templates/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['emailTemplates'])
    }
  );
};

export const useDeleteEmailTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/settings/email-templates/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['emailTemplates'])
    }
  );
};

// --- Notification Settings ---
export const useNotificationSettings = (filter?: any) =>
  useQuery<NotificationSetting[]>(['notificationSettings', filter], async () => {
    const { data } = await axios.get('/api/settings/notifications', { params: filter });
    return data;
  });

export const useCreateNotificationSetting = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<NotificationSetting>) => axios.post('/api/settings/notifications', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['notificationSettings'])
    }
  );
};

export const useUpdateNotificationSetting = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<NotificationSetting>) => axios.put(`/api/settings/notifications/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['notificationSettings'])
    }
  );
};

export const useDeleteNotificationSetting = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/settings/notifications/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['notificationSettings'])
    }
  );
};

// --- Integrations ---
export const useIntegrations = (filter?: any) =>
  useQuery<Integration[]>(['integrations', filter], async () => {
    const { data } = await axios.get('/api/settings/integrations', { params: filter });
    return data;
  });

export const useCreateIntegration = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Integration>) => axios.post('/api/settings/integrations', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['integrations'])
    }
  );
};

export const useUpdateIntegration = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Integration>) => axios.put(`/api/settings/integrations/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['integrations'])
    }
  );
};

export const useDeleteIntegration = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/settings/integrations/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['integrations'])
    }
  );
};

export const useTestIntegration = () => {
  return useMutation(
    (id: number) => axios.post(`/api/settings/integrations/${id}/test`)
  );
};

// --- Backup Configs ---
export const useBackupConfigs = (filter?: any) =>
  useQuery<BackupConfig[]>(['backupConfigs', filter], async () => {
    const { data } = await axios.get('/api/settings/backups', { params: filter });
    return data;
  });

export const useCreateBackupConfig = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<BackupConfig>) => axios.post('/api/settings/backups', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['backupConfigs'])
    }
  );
};

export const useUpdateBackupConfig = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<BackupConfig>) => axios.put(`/api/settings/backups/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['backupConfigs'])
    }
  );
};

export const useDeleteBackupConfig = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/settings/backups/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['backupConfigs'])
    }
  );
};

export const useRunBackup = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.post(`/api/settings/backups/${id}/run`),
    {
      onSuccess: () => queryClient.invalidateQueries(['backupConfigs'])
    }
  );
};

// --- Security Settings ---
export const useSecuritySettings = (filter?: any) =>
  useQuery<SecuritySetting[]>(['securitySettings', filter], async () => {
    const { data } = await axios.get('/api/settings/security', { params: filter });
    return data;
  });

export const useUpdateSecuritySetting = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<SecuritySetting>) => axios.put(`/api/settings/security/${payload.key}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['securitySettings'])
    }
  );
};

// --- Audit Logs ---
export const useAuditLogs = (filter?: any) =>
  useQuery<AuditLog[]>(['auditLogs', filter], async () => {
    const { data } = await axios.get('/api/settings/audit-logs', { params: filter });
    return data;
  });

// --- System Info ---
export const useSystemInfo = () =>
  useQuery<SystemInfo>(['systemInfo'], async () => {
    const { data } = await axios.get('/api/settings/system-info');
    return data;
  });

// --- Maintenance Mode ---
export const useMaintenanceMode = () =>
  useQuery<MaintenanceMode>(['maintenanceMode'], async () => {
    const { data } = await axios.get('/api/settings/maintenance-mode');
    return data;
  });

export const useUpdateMaintenanceMode = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<MaintenanceMode>) => axios.put('/api/settings/maintenance-mode', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['maintenanceMode'])
    }
  );
};

// --- License ---
export const useLicense = () =>
  useQuery<License>(['license'], async () => {
    const { data } = await axios.get('/api/settings/license');
    return data;
  });

export const useUpdateLicense = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<License>) => axios.put('/api/settings/license', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['license'])
    }
  );
}; 