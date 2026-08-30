import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { Payroll } from "./types";

const API_URL = "/api/payroll";

export const usePayrolls = (filters?: any) => {
  return useQuery<Payroll[]>({
    queryKey: ["payrolls", filters],
    queryFn: async () => (await axios.get(API_URL, { params: filters })).data,
    refetchInterval: 10000,
  });
};

export const useCreatePayroll = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Payroll>) => axios.post(API_URL, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payrolls"] }),
  });
};

export const useUpdatePayroll = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: any) => axios.put(`${API_URL}/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payrolls"] }),
  });
};

export const useDeletePayroll = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => axios.delete(`${API_URL}/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payrolls"] }),
  });
};