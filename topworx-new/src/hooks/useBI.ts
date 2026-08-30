// src/hooks/useBI.ts
// ============================================================================
// BI Dashboard Hooks
// ============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { biApi } from '../services/biApi';
import { AlertEvent, AlertRule, KPIData, CEODashboardData } from '../types';

const STALE_TIME = 60_000; // 1 minute

export function useCEODashboard(year: number, month: number) {
  return useQuery<CEODashboardData, Error>({
    queryKey: ['bi', 'dashboard', 'ceo', year, month],
    queryFn: async () => {
      const response = await biApi.getCEODashboard(year, month);
      return response.data;
    },
    staleTime: STALE_TIME,
    refetchInterval: STALE_TIME,
  });
}

export function useKPIs(year: number, month: number) {
  return useQuery<Record<string, KPIData>, Error>({
    queryKey: ['bi', 'kpis', year, month],
    queryFn: async () => {
      const response = await biApi.getAllKPIs(year, month);
      return response.data;
    },
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
}

export function useKPIHistory(kpiName: string, days = 90) {
  return useQuery({
    queryKey: ['bi', 'kpi-history', kpiName, days],
    queryFn: async () => {
      const response = await biApi.getKPIHistory(kpiName, days);
      return response.data;
    },
    enabled: !!kpiName,
  });
}

export function useAlerts(unacknowledgedOnly = false) {
  return useQuery<AlertEvent[], Error>({
    queryKey: ['bi', 'alerts', unacknowledgedOnly],
    queryFn: async () => {
      const response = await biApi.getAlerts(unacknowledgedOnly);
      return response.data;
    },
    refetchInterval: 30_000,
  });
}

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (eventId: number) => {
      const response = await biApi.acknowledgeAlert(eventId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bi', 'alerts'] });
    },
  });
}

export function useCreateAlertRule() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: Partial<AlertRule>) => {
      const response = await biApi.createAlertRule(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bi', 'alert-rules'] });
    },
  });
}