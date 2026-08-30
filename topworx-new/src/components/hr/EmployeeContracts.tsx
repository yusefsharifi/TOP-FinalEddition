import React from "react";
import { Button, Input, InputNumber, List, List.Item, Modal, Typography } from 'antd';

export const EmployeeContracts: React.FC<{
  contracts: { id: string; type: string; start: string; end: string; fileUrl?: string }[];
  onAdd: (data: any) => void;
}> = ({ contracts, onAdd }) => {
  // فرم افزودن قرارداد جدید (ساده)
  // ...
  return (
    <div>
      <Typography.Title level={4}>قراردادها و سوابق شغلی</Typography.Title>
      <List>
        {contracts.map(c => (
          <ListItem key={c.id}>
            <ListItemText
              primary={`${c.type} (${c.start} تا ${c.end})`}
              secondary={c.fileUrl && <a href={c.fileUrl} target="_blank" rel="noopener noreferrer">دانلود فایل</a>}
            />
          </ListItem>
        ))}
      </List>
      {/* دکمه افزودن قرارداد جدید */}
      <Button variant="outlined" size="small" style={{  mt: 1  }}>افزودن قرارداد جدید</Button>
    </div>
  );
};