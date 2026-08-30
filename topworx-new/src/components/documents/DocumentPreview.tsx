import React from "react";
import { Modal } from 'antd';
import { Document } from "../../api/documents/types";

export const DocumentPreview: React.FC<{ doc: Document | null; onClose: () => void }> = ({ doc, onClose }) => {
  if (!doc) return null;
  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{doc.name}</div>
      <div>
        {doc.type === "pdf" ? (
          <iframe src={doc.url} width="100%" height="600px" title={doc.name} />
        ) : doc.type.startsWith("image") ? (
          <div><img src={doc.url} alt={doc.name} style={{ maxWidth: "100%", maxHeight: 500 }} /></div>
        ) : (
          <a href={doc.url} target="_blank" rel="noopener noreferrer">دانلود فایل</a>
        )}
      </div>
    </Modal>
  );
};