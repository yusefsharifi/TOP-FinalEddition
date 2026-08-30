import React from "react";
import { Button, List, List.Item, Modal } from 'antd';
import { Contract } from "../../api/contracts/types";

export const ContractVersionHistory: React.FC<{
  contract: Contract | null;
  onClose: () => void;
}> = ({ contract, onClose }) => {
  if (!contract || !contract.history) return null;
  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>تاریخچه نسخه‌های {contract.title}</div>
      <div>
        <List>
          {contract.history.map((ver) => (
            <ListItem key={ver.version} secondaryAction={
              <Button href={ver.fileUrl} target="_blank" size="small">دانلود</Button>
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