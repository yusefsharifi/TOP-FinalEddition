// topworx-new/src/api/notifications/index.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

export interface Notification {
  id: string;
  title: string;
  description: string;
  read: boolean;
  createdAt: string;
  type?: "info" | "warning" | "success" | "error";
}

const API_URL = "/api/notifications"; // مسیر API واقعی

export const useNotifications = () => {
  const queryClient = useQueryClient();

  // دریافت اعلان‌ها
  const { data: notifications = [], isLoading } = useQuery<Notification[]>({
    queryKey: ["notifications"],
    queryFn: async () => (await axios.get(API_URL)).data,
    refetchInterval: 10000, // هر ۱۰ ثانیه یکبار بروزرسانی (برای شبه real-time)
  });

  // خواندن یک اعلان
  const markAsReadMutation = useMutation({
    mutationFn: (id: string) => axios.post(`${API_URL}/${id}/read`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  // خواندن همه اعلان‌ها
  const markAllAsReadMutation = useMutation({
    mutationFn: () => axios.post(`${API_URL}/read-all`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  // حذف اعلان
  const removeMutation = useMutation({
    mutationFn: (id: string) => axios.delete(`${API_URL}/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  return {
    notifications,
    isLoading,
    markAsRead: (id: string) => markAsReadMutation.mutate(id),
    markAllAsRead: () => markAllAsReadMutation.mutate(),
    remove: (id: string) => removeMutation.mutate(id),
  };
};