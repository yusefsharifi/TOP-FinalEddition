import React from "react";
import { Button, Input, InputNumber, List, List.Item, Modal, Typography } from 'antd';

export const AssetMaintenanceHistory: React.FC<{
  history: { id: string; date: string; type: string; description?: string }[];
  onAdd: (data: any) => void;
}> = ({ history, onAdd }) => {
  // فرم افزودن تعمیر/سرویس جدید (ساده)
  // ...
  return (
    <div>
      <Typography.Title level={4}>سوابق تعمیرات و سرویس‌ها</Typography.Title>
      <List>
        {history.map(h => (
          <ListItem key={h.id}>
            <ListItemText
              primary={`${h.type} - ${new Date(h.date).toLocaleDateString("fa-IR")}`}
              secondary={h.description}
            />
          </ListItem>
        ))}
      </List>
      <Button variant="outlined" size="small" style={{  mt: 1  }}>ثبت سرویس/تعمیر جدید</Button>
    </div>
  );
};