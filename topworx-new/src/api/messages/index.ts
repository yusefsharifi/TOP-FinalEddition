// topworx-new/src/api/messages/index.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Message, Conversation } from "./types";
import axios from "axios";

const API_URL = "/api/messages";

export const useConversations = () => {
  return useQuery<Conversation[]>({
    queryKey: ["conversations"],
    queryFn: async () => (await axios.get(`${API_URL}/conversations`)).data,
    refetchInterval: 10000,
  });
};

export const useMessages = (conversationId: string) => {
  return useQuery<Message[]>({
    queryKey: ["messages", conversationId],
    queryFn: async () => (await axios.get(`${API_URL}/conversations/${conversationId}/messages`)).data,
    enabled: !!conversationId,
    refetchInterval: 5000,
  });
};

export const useSendMessage = (conversationId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (content: string) =>
      axios.post(`${API_URL}/conversations/${conversationId}/messages`, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messages", conversationId] });
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
};