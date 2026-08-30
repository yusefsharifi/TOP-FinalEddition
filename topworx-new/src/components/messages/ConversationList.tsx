import React from "react";
import { Avatar, Badge, List } from 'antd';
import { Conversation } from "../../api/messages/types";

export const ConversationList: React.FC<{
  conversations: Conversation[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}> = ({ conversations, selectedId, onSelect }) => (
  <List style={{  width: 300, borderLeft: "1px solid #eee", height: "100%", overflow: "auto"  }}>
    {conversations.map((conv) => (
      <ListItemButton
        key={conv.id}
        selected={conv.id === selectedId}
        onClick={() => onSelect(conv.id)}
        style={{  alignItems: "flex-start"  }}
      >
        <Badge
          color="error"
          badgeContent={conv.unreadCount}
          invisible={conv.unreadCount === 0}
          style={{  mr: 1, mt: 1  }}
        >
          <Avatar>{conv.title[0]}</Avatar>
        </Badge>
        <ListItemText
          primary={conv.title}
          secondary={
            <div>
              {conv.lastMessage?.senderName}: {conv.lastMessage?.content?.slice(0, 30)}
            </div>
          }
        />
      </div>
    ))}
  </List>
);