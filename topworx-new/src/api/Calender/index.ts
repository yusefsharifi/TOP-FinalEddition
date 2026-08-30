import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { CalendarEvent } from "./types";

const API_URL = "/api/calendar/events";

export const useCalendarEvents = (filters?: any) => {
  return useQuery<CalendarEvent[]>({
    queryKey: ["calendar_events", filters],
    queryFn: async () => (await axios.get(API_URL, { params: filters })).data,
    refetchInterval: 10000,
  });
};

export const useCreateEvent = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<CalendarEvent>) => axios.post(API_URL, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["calendar_events"] }),
  });
};

export const useUpdateEvent = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: any) => axios.put(`${API_URL}/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["calendar_events"] }),
  });
};

export const useDeleteEvent = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => axios.delete(`${API_URL}/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["calendar_events"] }),
  });
};