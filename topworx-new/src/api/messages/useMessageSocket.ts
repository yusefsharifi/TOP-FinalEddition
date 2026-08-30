import { useEffect } from "react";
import { io, Socket } from "socket.io-client";
import { Message } from "./types";

let socket: Socket | null = null;

export const useMessageSocket = (
  conversationId: string,
  onNewMessage: (msg: Message) => void
) => {
  useEffect(() => {
    if (!conversationId) return;
    if (!socket) {
      socket = io("http://localhost:8000", { path: "/ws" }); // آدرس سرور خودت را جایگزین کن
    }
    socket.emit("join", conversationId);

    socket.on("new_message", onNewMessage);

    return () => {
      socket?.emit("leave", conversationId);
      socket?.off("new_message", onNewMessage);
    };
  }, [conversationId, onNewMessage]);
};