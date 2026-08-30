import React from "react";
import { Button, List, List.Item, Typography } from 'antd';

export const AssetTransferHistory: React.FC<{
  transfers: { id: string; date: string; from: string; to: string; description?: string }[];
  onAdd: (data: any) => void;
}> = ({ transfers, onAdd }) => (
  <div>
    <Typography.Title level={4}>سوابق نقل و انتقالات</Typography.Title>
    <List>
      {transfers.map(t => (
        <ListItem key={t.id}>
          <ListItemText
            primary={`از "${t.from}" به "${t.to}" - ${new Date(t.date).toLocaleDateString("fa-IR")}`}
            secondary={t.description}
          />
        </ListItem>
      ))}
    </List>
    <Button variant="outlined" size="small" style={{  mt: 1  }}>ثبت انتقال جدید</Button>
  </div>
);