import React from "react";
import { Badge, Button, List.Item } from 'antd';
import { BellOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';

export interface Notification {
  id: string;
  title: string;
  description: string;
  read: boolean;
  createdAt: string;
  type?: "info" | "warning" | "success" | "error";
}

export const NotificationItem: React.FC<{
  notification: Notification;
  onDelete: (id: string) => void;
  onRead: (id: string) => void;
}> = ({ notification, onDelete, onRead }) => (
  <ListItem
    button
    selected={!notification.read}
    onClick={() => !notification.read && onRead(notification.id)}
    style={{  bgcolor: !notification.read ? "#e3f2fd" : "inherit"  }}
    secondaryAction={
      <Button type="text" edge="end" onClick={() => onDelete(notification.id)}>
        <DeleteIcon />
      </Button>
    }
  >
    <ListItemIcon>
      <Badge color="error" variant="dot" invisible={notification.read}>
        <NotificationsIcon color={notification.type === "error" ? "error" : "primary"} />
      </Badge>
    </span>
    <ListItemText
      primary={notification.title}
      secondary={notification.description}
    />
  </ListItem>
);