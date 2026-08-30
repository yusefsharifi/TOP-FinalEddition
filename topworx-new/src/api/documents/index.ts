import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { Document } from "./types";

const API_URL = "/api/documents";

export const useDocuments = (filters?: any) => {
  return useQuery<Document[]>({
    queryKey: ["documents", filters],
    queryFn: async () => (await axios.get(API_URL, { params: filters })).data,
    refetchInterval: 10000,
  });
};

export const useUploadDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) => axios.post(API_URL, formData),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => axios.delete(`${API_URL}/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });
};