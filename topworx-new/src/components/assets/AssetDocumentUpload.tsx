import React from "react";
import { Button, List, List.Item, Typography } from 'antd';

export const AssetDocumentUpload: React.FC<{
  documents: { id: string; name: string; url: string }[];
  onUpload: (file: File) => void;
}> = ({ documents, onUpload }) => (
  <div>
    <Typography.Title level={4}>مدارک دارایی</Typography.Title>
    <List>
      {documents.map(d => (
        <ListItem key={d.id}>
          <ListItemText
            primary={d.name}
            secondary={<a href={d.url} target="_blank" rel="noopener noreferrer">مشاهده/دانلود</a>}
          />
        </ListItem>
      ))}
    </List>
    <Button variant="outlined" size="small" style={{  mt: 1  }} component="label">
      بارگذاری مدرک جدید
      <input type="file" hidden onChange={e => e.target.files && onUpload(e.target.files[0])} />
    </Button>
  </div>
);