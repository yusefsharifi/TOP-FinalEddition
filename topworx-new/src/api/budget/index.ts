import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { Budget } from "./types";

const API_URL = "/api/budget";

export const useBudgets = (filters?: any) => {
  return useQuery<Budget[]>({
    queryKey: ["budgets", filters],
    queryFn: async () => (await axios.get(API_URL, { params: filters })).data,
    refetchInterval: 10000,
  });
};

export const useCreateBudget = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Budget>) => axios.post(API_URL, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["budgets"] }),
  });
};

export const useUpdateBudget = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: any) => axios.put(`${API_URL}/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["budgets"] }),
  });
};

export const useDeleteBudget = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => axios.delete(`${API_URL}/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["budgets"] }),
  });
};