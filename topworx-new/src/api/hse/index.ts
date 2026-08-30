import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Incident, RiskAssessment, HSETraining, SafetyInspection, EmergencyPlan, ComplianceRequirement, EnvironmentalAspect, WasteManagement, HSEMetric, HSEReport } from '../../types/hse';

// --- Incidents ---
export const useIncidents = (filter?: any) =>
  useQuery<Incident[]>(['incidents', filter], async () => {
    const { data } = await axios.get('/api/hse/incidents', { params: filter });
    return data;
  });

export const useCreateIncident = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Incident>) => axios.post('/api/hse/incidents', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['incidents'])
    }
  );
};

export const useUpdateIncident = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Incident>) => axios.put(`/api/hse/incidents/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['incidents'])
    }
  );
};

export const useDeleteIncident = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/incidents/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['incidents'])
    }
  );
};

// --- Risk Assessments ---
export const useRiskAssessments = (filter?: any) =>
  useQuery<RiskAssessment[]>(['riskAssessments', filter], async () => {
    const { data } = await axios.get('/api/hse/risk-assessments', { params: filter });
    return data;
  });

export const useCreateRiskAssessment = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<RiskAssessment>) => axios.post('/api/hse/risk-assessments', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['riskAssessments'])
    }
  );
};

export const useUpdateRiskAssessment = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<RiskAssessment>) => axios.put(`/api/hse/risk-assessments/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['riskAssessments'])
    }
  );
};

export const useDeleteRiskAssessment = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/risk-assessments/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['riskAssessments'])
    }
  );
};

// --- HSE Training ---
export const useHSETraining = (filter?: any) =>
  useQuery<HSETraining[]>(['hseTraining', filter], async () => {
    const { data } = await axios.get('/api/hse/training', { params: filter });
    return data;
  });

export const useCreateHSETraining = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<HSETraining>) => axios.post('/api/hse/training', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['hseTraining'])
    }
  );
};

export const useUpdateHSETraining = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<HSETraining>) => axios.put(`/api/hse/training/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['hseTraining'])
    }
  );
};

export const useDeleteHSETraining = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/training/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['hseTraining'])
    }
  );
};

// --- Safety Inspections ---
export const useSafetyInspections = (filter?: any) =>
  useQuery<SafetyInspection[]>(['safetyInspections', filter], async () => {
    const { data } = await axios.get('/api/hse/safety-inspections', { params: filter });
    return data;
  });

export const useCreateSafetyInspection = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<SafetyInspection>) => axios.post('/api/hse/safety-inspections', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['safetyInspections'])
    }
  );
};

export const useUpdateSafetyInspection = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<SafetyInspection>) => axios.put(`/api/hse/safety-inspections/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['safetyInspections'])
    }
  );
};

export const useDeleteSafetyInspection = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/safety-inspections/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['safetyInspections'])
    }
  );
};

// --- Emergency Plans ---
export const useEmergencyPlans = (filter?: any) =>
  useQuery<EmergencyPlan[]>(['emergencyPlans', filter], async () => {
    const { data } = await axios.get('/api/hse/emergency-plans', { params: filter });
    return data;
  });

export const useCreateEmergencyPlan = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<EmergencyPlan>) => axios.post('/api/hse/emergency-plans', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['emergencyPlans'])
    }
  );
};

export const useUpdateEmergencyPlan = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<EmergencyPlan>) => axios.put(`/api/hse/emergency-plans/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['emergencyPlans'])
    }
  );
};

export const useDeleteEmergencyPlan = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/emergency-plans/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['emergencyPlans'])
    }
  );
};

// --- Compliance Requirements ---
export const useComplianceRequirements = (filter?: any) =>
  useQuery<ComplianceRequirement[]>(['complianceRequirements', filter], async () => {
    const { data } = await axios.get('/api/hse/compliance-requirements', { params: filter });
    return data;
  });

export const useCreateComplianceRequirement = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<ComplianceRequirement>) => axios.post('/api/hse/compliance-requirements', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['complianceRequirements'])
    }
  );
};

export const useUpdateComplianceRequirement = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<ComplianceRequirement>) => axios.put(`/api/hse/compliance-requirements/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['complianceRequirements'])
    }
  );
};

export const useDeleteComplianceRequirement = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/compliance-requirements/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['complianceRequirements'])
    }
  );
};

// --- Environmental Aspects ---
export const useEnvironmentalAspects = (filter?: any) =>
  useQuery<EnvironmentalAspect[]>(['environmentalAspects', filter], async () => {
    const { data } = await axios.get('/api/hse/environmental-aspects', { params: filter });
    return data;
  });

export const useCreateEnvironmentalAspect = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<EnvironmentalAspect>) => axios.post('/api/hse/environmental-aspects', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['environmentalAspects'])
    }
  );
};

export const useUpdateEnvironmentalAspect = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<EnvironmentalAspect>) => axios.put(`/api/hse/environmental-aspects/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['environmentalAspects'])
    }
  );
};

export const useDeleteEnvironmentalAspect = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/environmental-aspects/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['environmentalAspects'])
    }
  );
};

// --- Waste Management ---
export const useWasteManagement = (filter?: any) =>
  useQuery<WasteManagement[]>(['wasteManagement', filter], async () => {
    const { data } = await axios.get('/api/hse/waste-management', { params: filter });
    return data;
  });

export const useCreateWasteManagement = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<WasteManagement>) => axios.post('/api/hse/waste-management', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['wasteManagement'])
    }
  );
};

export const useUpdateWasteManagement = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<WasteManagement>) => axios.put(`/api/hse/waste-management/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['wasteManagement'])
    }
  );
};

export const useDeleteWasteManagement = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/waste-management/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['wasteManagement'])
    }
  );
};

// --- HSE Metrics ---
export const useHSEMetrics = (filter?: any) =>
  useQuery<HSEMetric[]>(['hseMetrics', filter], async () => {
    const { data } = await axios.get('/api/hse/metrics', { params: filter });
    return data;
  });

export const useCreateHSEMetric = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<HSEMetric>) => axios.post('/api/hse/metrics', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['hseMetrics'])
    }
  );
};

export const useUpdateHSEMetric = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<HSEMetric>) => axios.put(`/api/hse/metrics/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['hseMetrics'])
    }
  );
};

export const useDeleteHSEMetric = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/metrics/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['hseMetrics'])
    }
  );
};

// --- HSE Reports ---
export const useHSEReports = (filter?: any) =>
  useQuery<HSEReport[]>(['hseReports', filter], async () => {
    const { data } = await axios.get('/api/hse/reports', { params: filter });
    return data;
  });

export const useCreateHSEReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<HSEReport>) => axios.post('/api/hse/reports', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['hseReports'])
    }
  );
};

export const useUpdateHSEReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<HSEReport>) => axios.put(`/api/hse/reports/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['hseReports'])
    }
  );
};

export const useDeleteHSEReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/hse/reports/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['hseReports'])
    }
  );
};

// --- HSE Dashboard ---
export const useHSEDashboard = () =>
  useQuery(['hseDashboard'], async () => {
    const { data } = await axios.get('/api/hse/dashboard');
    return data;
  }); 