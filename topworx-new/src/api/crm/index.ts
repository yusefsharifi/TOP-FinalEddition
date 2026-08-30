import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Customer, Lead, Opportunity, Deal, Activity, Campaign, SalesPipeline, SalesForecast } from '../../types/crm';

// --- Customers ---
export const useCustomers = (filter?: any) =>
  useQuery<Customer[]>(['customers', filter], async () => {
    const { data } = await axios.get('/api/crm/customers', { params: filter });
    return data;
  });

export const useCreateCustomer = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Customer>) => axios.post('/api/crm/customers', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['customers'])
    }
  );
};

export const useUpdateCustomer = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Customer>) => axios.put(`/api/crm/customers/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['customers'])
    }
  );
};

export const useDeleteCustomer = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/crm/customers/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['customers'])
    }
  );
};

// --- Leads ---
export const useLeads = (filter?: any) =>
  useQuery<Lead[]>(['leads', filter], async () => {
    const { data } = await axios.get('/api/crm/leads', { params: filter });
    return data;
  });

export const useCreateLead = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Lead>) => axios.post('/api/crm/leads', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['leads'])
    }
  );
};

export const useUpdateLead = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Lead>) => axios.put(`/api/crm/leads/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['leads'])
    }
  );
};

export const useDeleteLead = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/crm/leads/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['leads'])
    }
  );
};

// --- Opportunities ---
export const useOpportunities = (filter?: any) =>
  useQuery<Opportunity[]>(['opportunities', filter], async () => {
    const { data } = await axios.get('/api/crm/opportunities', { params: filter });
    return data;
  });

export const useCreateOpportunity = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Opportunity>) => axios.post('/api/crm/opportunities', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['opportunities'])
    }
  );
};

export const useUpdateOpportunity = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Opportunity>) => axios.put(`/api/crm/opportunities/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['opportunities'])
    }
  );
};

export const useDeleteOpportunity = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/crm/opportunities/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['opportunities'])
    }
  );
};

// --- Deals ---
export const useDeals = (filter?: any) =>
  useQuery<Deal[]>(['deals', filter], async () => {
    const { data } = await axios.get('/api/crm/deals', { params: filter });
    return data;
  });

export const useCreateDeal = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Deal>) => axios.post('/api/crm/deals', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['deals'])
    }
  );
};

export const useUpdateDeal = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Deal>) => axios.put(`/api/crm/deals/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['deals'])
    }
  );
};

export const useDeleteDeal = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/crm/deals/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['deals'])
    }
  );
};

// --- Activities ---
export const useActivities = (filter?: any) =>
  useQuery<Activity[]>(['activities', filter], async () => {
    const { data } = await axios.get('/api/crm/activities', { params: filter });
    return data;
  });

export const useCreateActivity = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Activity>) => axios.post('/api/crm/activities', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['activities'])
    }
  );
};

export const useUpdateActivity = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Activity>) => axios.put(`/api/crm/activities/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['activities'])
    }
  );
};

export const useDeleteActivity = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/crm/activities/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['activities'])
    }
  );
};

// --- Campaigns ---
export const useCampaigns = (filter?: any) =>
  useQuery<Campaign[]>(['campaigns', filter], async () => {
    const { data } = await axios.get('/api/crm/campaigns', { params: filter });
    return data;
  });

export const useCreateCampaign = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Campaign>) => axios.post('/api/crm/campaigns', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['campaigns'])
    }
  );
};

export const useUpdateCampaign = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Campaign>) => axios.put(`/api/crm/campaigns/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['campaigns'])
    }
  );
};

export const useDeleteCampaign = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/crm/campaigns/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['campaigns'])
    }
  );
};

// --- Sales Pipelines ---
export const useSalesPipelines = (filter?: any) =>
  useQuery<SalesPipeline[]>(['salesPipelines', filter], async () => {
    const { data } = await axios.get('/api/crm/sales-pipelines', { params: filter });
    return data;
  });

export const useCreateSalesPipeline = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<SalesPipeline>) => axios.post('/api/crm/sales-pipelines', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['salesPipelines'])
    }
  );
};

export const useUpdateSalesPipeline = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<SalesPipeline>) => axios.put(`/api/crm/sales-pipelines/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['salesPipelines'])
    }
  );
};

export const useDeleteSalesPipeline = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/crm/sales-pipelines/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['salesPipelines'])
    }
  );
};

// --- Sales Forecasts ---
export const useSalesForecasts = (filter?: any) =>
  useQuery<SalesForecast[]>(['salesForecasts', filter], async () => {
    const { data } = await axios.get('/api/crm/sales-forecasts', { params: filter });
    return data;
  });

export const useCreateSalesForecast = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<SalesForecast>) => axios.post('/api/crm/sales-forecasts', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['salesForecasts'])
    }
  );
};

export const useUpdateSalesForecast = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<SalesForecast>) => axios.put(`/api/crm/sales-forecasts/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['salesForecasts'])
    }
  );
};

export const useDeleteSalesForecast = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/crm/sales-forecasts/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['salesForecasts'])
    }
  );
};

// --- CRM Dashboard ---
export const useCRMDashboard = () =>
  useQuery(['crmDashboard'], async () => {
    const { data } = await axios.get('/api/crm/dashboard');
    return data;
  }); 