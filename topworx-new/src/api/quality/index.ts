import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { QualityInspection, QualityControlPoint, QualityAudit, CustomerComplaint, CorrectiveAction, QualityDocument, QualityMetric, QualityReport, QualityTraining } from '../../types/quality';

// --- Quality Inspections ---
export const useQualityInspections = (filter?: any) =>
  useQuery<QualityInspection[]>(['qualityInspections', filter], async () => {
    const { data } = await axios.get('/api/quality/inspections', { params: filter });
    return data;
  });

export const useCreateQualityInspection = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityInspection>) => axios.post('/api/quality/inspections', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityInspections'])
    }
  );
};

export const useUpdateQualityInspection = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityInspection>) => axios.put(`/api/quality/inspections/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityInspections'])
    }
  );
};

export const useDeleteQualityInspection = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/quality/inspections/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityInspections'])
    }
  );
};

// --- Quality Control Points ---
export const useQualityControlPoints = (filter?: any) =>
  useQuery<QualityControlPoint[]>(['qualityControlPoints', filter], async () => {
    const { data } = await axios.get('/api/quality/control-points', { params: filter });
    return data;
  });

export const useCreateQualityControlPoint = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityControlPoint>) => axios.post('/api/quality/control-points', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityControlPoints'])
    }
  );
};

export const useUpdateQualityControlPoint = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityControlPoint>) => axios.put(`/api/quality/control-points/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityControlPoints'])
    }
  );
};

export const useDeleteQualityControlPoint = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/quality/control-points/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityControlPoints'])
    }
  );
};

// --- Quality Audits ---
export const useQualityAudits = (filter?: any) =>
  useQuery<QualityAudit[]>(['qualityAudits', filter], async () => {
    const { data } = await axios.get('/api/quality/audits', { params: filter });
    return data;
  });

export const useCreateQualityAudit = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityAudit>) => axios.post('/api/quality/audits', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityAudits'])
    }
  );
};

export const useUpdateQualityAudit = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityAudit>) => axios.put(`/api/quality/audits/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityAudits'])
    }
  );
};

export const useDeleteQualityAudit = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/quality/audits/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityAudits'])
    }
  );
};

// --- Customer Complaints ---
export const useCustomerComplaints = (filter?: any) =>
  useQuery<CustomerComplaint[]>(['customerComplaints', filter], async () => {
    const { data } = await axios.get('/api/quality/complaints', { params: filter });
    return data;
  });

export const useCreateCustomerComplaint = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<CustomerComplaint>) => axios.post('/api/quality/complaints', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['customerComplaints'])
    }
  );
};

export const useUpdateCustomerComplaint = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<CustomerComplaint>) => axios.put(`/api/quality/complaints/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['customerComplaints'])
    }
  );
};

export const useDeleteCustomerComplaint = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/quality/complaints/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['customerComplaints'])
    }
  );
};

// --- Corrective Actions ---
export const useCorrectiveActions = (filter?: any) =>
  useQuery<CorrectiveAction[]>(['correctiveActions', filter], async () => {
    const { data } = await axios.get('/api/quality/corrective-actions', { params: filter });
    return data;
  });

export const useCreateCorrectiveAction = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<CorrectiveAction>) => axios.post('/api/quality/corrective-actions', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['correctiveActions'])
    }
  );
};

export const useUpdateCorrectiveAction = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<CorrectiveAction>) => axios.put(`/api/quality/corrective-actions/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['correctiveActions'])
    }
  );
};

export const useDeleteCorrectiveAction = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/quality/corrective-actions/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['correctiveActions'])
    }
  );
};

// --- Quality Documents ---
export const useQualityDocuments = (filter?: any) =>
  useQuery<QualityDocument[]>(['qualityDocuments', filter], async () => {
    const { data } = await axios.get('/api/quality/documents', { params: filter });
    return data;
  });

export const useCreateQualityDocument = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityDocument>) => axios.post('/api/quality/documents', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityDocuments'])
    }
  );
};

export const useUpdateQualityDocument = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityDocument>) => axios.put(`/api/quality/documents/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityDocuments'])
    }
  );
};

export const useDeleteQualityDocument = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/quality/documents/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityDocuments'])
    }
  );
};

// --- Quality Metrics ---
export const useQualityMetrics = (filter?: any) =>
  useQuery<QualityMetric[]>(['qualityMetrics', filter], async () => {
    const { data } = await axios.get('/api/quality/metrics', { params: filter });
    return data;
  });

export const useCreateQualityMetric = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityMetric>) => axios.post('/api/quality/metrics', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityMetrics'])
    }
  );
};

export const useUpdateQualityMetric = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityMetric>) => axios.put(`/api/quality/metrics/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityMetrics'])
    }
  );
};

export const useDeleteQualityMetric = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/quality/metrics/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityMetrics'])
    }
  );
};

// --- Quality Reports ---
export const useQualityReports = (filter?: any) =>
  useQuery<QualityReport[]>(['qualityReports', filter], async () => {
    const { data } = await axios.get('/api/quality/reports', { params: filter });
    return data;
  });

export const useCreateQualityReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityReport>) => axios.post('/api/quality/reports', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityReports'])
    }
  );
};

export const useUpdateQualityReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityReport>) => axios.put(`/api/quality/reports/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityReports'])
    }
  );
};

export const useDeleteQualityReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/quality/reports/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityReports'])
    }
  );
};

// --- Quality Training ---
export const useQualityTraining = (filter?: any) =>
  useQuery<QualityTraining[]>(['qualityTraining', filter], async () => {
    const { data } = await axios.get('/api/quality/training', { params: filter });
    return data;
  });

export const useCreateQualityTraining = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityTraining>) => axios.post('/api/quality/training', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityTraining'])
    }
  );
};

export const useUpdateQualityTraining = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<QualityTraining>) => axios.put(`/api/quality/training/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityTraining'])
    }
  );
};

export const useDeleteQualityTraining = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/quality/training/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['qualityTraining'])
    }
  );
};

// --- Quality Dashboard ---
export const useQualityDashboard = () =>
  useQuery(['qualityDashboard'], async () => {
    const { data } = await axios.get('/api/quality/dashboard');
    return data;
  }); 