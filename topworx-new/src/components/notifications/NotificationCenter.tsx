import React, { useState } from "react";
import { Badge, Button, Divider, List, Spin, Tabs, Typography } from 'antd';
import { BellOutlined } from '@ant-design/icons';
import { NotificationItem, Notification } from "./NotificationItem";
import { useNotifications } from "../../api/notifications";
import { Input, InputNumber } from 'antd';

<div>
  <Input
    fullWidth
    size="small"
    placeholder="جستجو در اعلان‌ها..."
    onChange={e => setSearch(e.target.value)}
    style={{  mb: 1  }}
  />
</div>

const filtered = notifications.filter(n =>
  (tab === "all" || n.type === tab) &&
  (n.title.includes(search) || n.description.includes(search))
);

const categories = [
  { label: "همه", value: "all" },
  { label: "پیام", value: "info" },
  { label: "هشدار", value: "warning" },
  { label: "موفقیت", value: "success" },
  { label: "خطا", value: "error" },
];

export const NotificationCenter: React.FC = () => {
  const { notifications, isLoading, markAsRead, remove, markAllAsRead } = useNotifications();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [tab, setTab] = useState("all");

  const unreadCount = notifications.filter((n) => !n.read).length;

  const filtered = tab === "all"
    ? notifications
    : notifications.filter((n) => n.type === tab);

  return (
    <>
      <Button type="text" onClick={(e) => setAnchorEl(e.currentTarget)}>
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </Button>
      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={() => setAnchorEl(null)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        transformOrigin={{ vertical: "top", horizontal: "center" }}
        PaperProps={{ sx: { width: 370, maxHeight: 450 } }}
      >
        <div>
          <Typography.Title level={4}>اعلان‌ها</Typography.Title>
          <Button size="small" onClick={markAllAsRead}>خواندن همه</Button>
        </div>
        <Divider />
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          variant="scrollable"
          scrollButtons="auto"
          style={{  px: 2, minHeight: 36  }}
        >
          {categories.map((cat) => (
            <Tab key={cat.value} label={cat.label} value={cat.value} style={{  minHeight: 36  }} />
          ))}
        </Tabs>
        <Divider />
        <List style={{  maxHeight: 320, overflow: "auto"  }}>
          {isLoading ? (
            <div><Spin /></div>
          ) : filtered.length === 0 ? (
            <Typography align="center" color="text.secondary" p={2}>
              هیچ اعلانی وجود ندارد.
            </Typography>
          ) : (
            filtered.map((n) => (
              <NotificationItem
                key={n.id}
                notification={n}
                onDelete={remove}
                onRead={markAsRead}
              />
            ))
          )}
        </List>
      </Popover>
    </>
  );
};