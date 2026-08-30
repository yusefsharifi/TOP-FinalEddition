import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Report, Dashboard, KPI, DataExport, AnalyticsEvent, AnalyticsMetric } from '../../types/reports';

// --- Reports ---
export const useReports = (filter?: any) =>
  useQuery<Report[]>(['reports', filter], async () => {
    const { data } = await axios.get('/api/reports', { params: filter });
    return data;
  });

export const useCreateReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Report>) => axios.post('/api/reports', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['reports'])
    }
  );
};

export const useUpdateReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Report>) => axios.put(`/api/reports/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['reports'])
    }
  );
};

export const useDeleteReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/reports/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['reports'])
    }
  );
};

export const useExecuteReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: { reportId: number; parameters?: Record<string, any> }) => 
      axios.post(`/api/reports/${payload.reportId}/execute`, payload.parameters),
    {
      onSuccess: () => queryClient.invalidateQueries(['reports'])
    }
  );
};

// --- Dashboards ---
export const useDashboards = (filter?: any) =>
  useQuery<Dashboard[]>(['dashboards', filter], async () => {
    const { data } = await axios.get('/api/reports/dashboards', { params: filter });
    return data;
  });

export const useCreateDashboard = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Dashboard>) => axios.post('/api/reports/dashboards', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['dashboards'])
    }
  );
};

export const useUpdateDashboard = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Dashboard>) => axios.put(`/api/reports/dashboards/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['dashboards'])
    }
  );
};

export const useDeleteDashboard = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/reports/dashboards/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['dashboards'])
    }
  );
};

// --- KPIs ---
export const useKPIs = (filter?: any) =>
  useQuery<KPI[]>(['kpis', filter], async () => {
    const { data } = await axios.get('/api/reports/kpis', { params: filter });
    return data;
  });

export const useCreateKPI = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<KPI>) => axios.post('/api/reports/kpis', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['kpis'])
    }
  );
};

export const useUpdateKPI = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<KPI>) => axios.put(`/api/reports/kpis/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['kpis'])
    }
  );
};

export const useDeleteKPI = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/reports/kpis/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['kpis'])
    }
  );
};

// --- Data Exports ---
export const useDataExports = (filter?: any) =>
  useQuery<DataExport[]>(['dataExports', filter], async () => {
    const { data } = await axios.get('/api/reports/data-exports', { params: filter });
    return data;
  });

export const useCreateDataExport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DataExport>) => axios.post('/api/reports/data-exports', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['dataExports'])
    }
  );
};

export const useUpdateDataExport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DataExport>) => axios.put(`/api/reports/data-exports/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['dataExports'])
    }
  );
};

export const useDeleteDataExport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/reports/data-exports/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['dataExports'])
    }
  );
};

export const useExecuteDataExport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: { exportId: number; parameters?: Record<string, any> }) => 
      axios.post(`/api/reports/data-exports/${payload.exportId}/execute`, payload.parameters),
    {
      onSuccess: () => queryClient.invalidateQueries(['dataExports'])
    }
  );
};

// --- Analytics Events ---
export const useAnalyticsEvents = (filter?: any) =>
  useQuery<AnalyticsEvent[]>(['analyticsEvents', filter], async () => {
    const { data } = await axios.get('/api/reports/analytics/events', { params: filter });
    return data;
  });

export const useCreateAnalyticsEvent = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<AnalyticsEvent>) => axios.post('/api/reports/analytics/events', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['analyticsEvents'])
    }
  );
};

// --- Analytics Metrics ---
export const useAnalyticsMetrics = (filter?: any) =>
  useQuery<AnalyticsMetric[]>(['analyticsMetrics', filter], async () => {
    const { data } = await axios.get('/api/reports/analytics/metrics', { params: filter });
    return data;
  });

export const useCreateAnalyticsMetric = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<AnalyticsMetric>) => axios.post('/api/reports/analytics/metrics', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['analyticsMetrics'])
    }
  );
};

export const useUpdateAnalyticsMetric = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<AnalyticsMetric>) => axios.put(`/api/reports/analytics/metrics/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['analyticsMetrics'])
    }
  );
};

export const useDeleteAnalyticsMetric = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/reports/analytics/metrics/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['analyticsMetrics'])
    }
  );
};

// --- Reports Dashboard ---
export const useReportsDashboard = () =>
  useQuery(['reportsDashboard'], async () => {
    const { data } = await axios.get('/api/reports/dashboard');
    return data;
  });