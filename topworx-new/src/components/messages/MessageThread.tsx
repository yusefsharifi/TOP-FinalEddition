import React, { useRef, useEffect } from "react";
import { Avatar, Card, Typography } from 'antd';
import { Message } from "../../api/messages/types";

export const MessageThread: React.FC<{ messages: Message[]; userId: string }> = ({ messages, userId }) => {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div style={{  flex: 1, overflowY: "auto", p: 2, bgcolor: "#f9f9f9"  }}>
      {messages.map((msg) => (
        <div>
          <Avatar style={{  ml: 1, mr: 1  }}>{msg.senderName[0]}</Avatar>
          <Card
            style={{ 
              p: 1.5,
              bgcolor: msg.senderId === userId ? "#1976d2" : "#fff",
              color: msg.senderId === userId ? "#fff" : "#222",
              maxWidth: 350,
              minWidth: 60,
              boxShadow: 1,
             }}
          >
            <Typography fontSize={14}>{msg.content}</Typography>
            <Typography fontSize={11} color="text.secondary" align="left">
              {new Date(msg.createdAt).toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" })}
            </Typography>
          </Card>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
};