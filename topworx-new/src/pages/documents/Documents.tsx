import React, { useState } from "react";
import { Alert, Card } from 'antd';
import { useDocuments } from "../../api/documents";
import { DocumentTable } from "../../components/documents/DocumentTable";
import { DocumentUpload } from "../../components/documents/DocumentUpload";
import { DocumentPreview } from "../../components/documents/DocumentPreview";
import { DocumentFilters } from "../../components/documents/DocumentFilters";

const folders = ["عمومی", "مالی", "پروژه‌ها", "قراردادها", "HR"];

export const Documents: React.FC = () => {
  const [filters, setFilters] = useState({});
  const { data = [], isLoading, refetch } = useDocuments(filters);
  const [preview, setPreview] = useState<any>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const handleUploaded = () => {
    setSnackbar({ open: true, message: "سند با موفقیت بارگذاری شد.", severity: "success" });
    refetch();
  };

  const handleDelete = async (id: string) => {
    // ... حذف سند و نمایش اعلان ...
    setSnackbar({ open: true, message: "سند حذف شد.", severity: "success" });
    refetch();
  };

  return (
    <Card style={{  p: 3  }}>
      <DocumentUpload folders={folders} onUploaded={handleUploaded} />
      <DocumentFilters filters={filters} onChange={setFilters} folders={folders} />
      <DocumentTable data={data} onPreview={setPreview} onDelete={handleDelete} />
      <DocumentPreview doc={preview} onClose={() => setPreview(null)} />
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </div>
    </Card>
  );
};