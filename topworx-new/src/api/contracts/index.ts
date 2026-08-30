import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { Contract } from "./types";

const API_URL = "/api/contracts";

export const useContracts = (filters?: any) => {
  return useQuery<Contract[]>({
    queryKey: ["contracts", filters],
    queryFn: async () => (await axios.get(API_URL, { params: filters })).data,
    refetchInterval: 10000,
  });
};

export const useCreateContract = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) => axios.post(API_URL, formData),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["contracts"] }),
  });
};

export const useUpdateContract = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, formData }: { id: string; formData: FormData }) => axios.put(`${API_URL}/${id}`, formData),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["contracts"] }),
  });
};

export const useDeleteContract = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => axios.delete(`${API_URL}/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["contracts"] }),
  });
};