import React from "react";
import { Button, List, List.Item, Modal } from 'antd';
import { Document } from "../../api/documents/types";

export const DocumentVersionHistory: React.FC<{
  doc: Document | null;
  onClose: () => void;
}> = ({ doc, onClose }) => {
  if (!doc || !doc.history) return null;
  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>تاریخچه نسخه‌های {doc.name}</div>
      <div>
        <List>
          {doc.history.map((ver) => (
            <ListItem key={ver.version} secondaryAction={
              <Button href={ver.url} target="_blank" size="small">دانلود</Button>
            }>
              <ListItemText
                primary={`نسخه ${ver.version}`}
                secondary={`تاریخ: ${new Date(ver.updatedAt).toLocaleString("fa-IR")}`}
              />
            </ListItem>
          ))}
        </List>
      </div>
    </Modal>
  );
};