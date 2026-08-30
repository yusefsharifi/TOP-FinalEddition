export interface Message {
  id: string;
  conversationId: string;
  senderId: string;
  senderName: string;
  content: string;
  createdAt: string;
  read: boolean;
  type?: "text" | "system";
}

export interface Conversation {
  id: string;
  title: string;
  participants: { id: string; name: string }[];
  lastMessage: Message;
  unreadCount: number;
}