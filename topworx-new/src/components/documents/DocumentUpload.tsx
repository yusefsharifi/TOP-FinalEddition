import React, { useState } from "react";
import { Button, Input, InputNumber, Select, Tag } from 'antd';
import { useUploadDocument } from "../../api/documents";
import { Checkbox, Select } from 'antd';
import { useNotificationSnackbar } from "../../core/notifications/NotificationSnackbarProvider";

const { showNotification } = useNotificationSnackbar();

const handleUpload = async () => {
  // ... آپلود سند ...
  showNotification("سند جدید با موفقیت بارگذاری شد", "success");
};

const handleDelete = async (id: string) => {
  // ... حذف سند ...
  showNotification("سند حذف شد", "info");
};
const [access, setAccess] = useState<"public" | "private" | "role">("private");
const [roles, setRoles] = useState<string[]>([]);

<FormControl>
  <InputLabel>دسترسی</span>
  <Select value={access} onChange={e => setAccess(e.target.value)} label="دسترسی">
    <MenuItem value="public">عمومی</Select.Option>
    <MenuItem value="private">خصوصی</Select.Option>
    <MenuItem value="role">نقش‌محور</Select.Option>
  </Select>
</div>
{access === "role" && (
  <FormControl>
    <InputLabel>نقش‌ها</span>
    <Select
      multiple
      value={roles}
      onChange={e => setRoles(e.target.value as string[])}
      renderValue={selected => (selected as string[]).join(", ")}
    >
      <MenuItem value="admin"><Checkbox checked={roles.includes("admin")} /> <ListItemText primary="مدیر" /></Select.Option>
      <MenuItem value="finance"><Checkbox checked={roles.includes("finance")} /> <ListItemText primary="مالی" /></Select.Option>
      <MenuItem value="hr"><Checkbox checked={roles.includes("hr")} /> <ListItemText primary="منابع انسانی" /></Select.Option>
      {/* ... */}
    </Select>
  </div>
)}

export const DocumentUpload: React.FC<{ folders: string[]; onUploaded: () => void }> = ({ folders, onUploaded }) => {
  const [file, setFile] = useState<File | null>(null);
  const [folder, setFolder] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState("");
  const upload = useUploadDocument();

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("folder", folder);
    formData.append("tags", JSON.stringify(tags));
    await upload.mutateAsync(formData);
    setFile(null); setFolder(""); setTags([]); setTagInput("");
    onUploaded();
  };

  return (
    <div>
      <Button component="label" variant="contained">
        انتخاب فایل
        <input type="file" hidden onChange={e => setFile(e.target.files?.[0] || null)} />
      </Button>
      <FormControl>
        <InputLabel>پوشه</span>
        <Select value={folder} onChange={e => setFolder(e.target.value)} label="پوشه" style={{  minWidth: 120  }}>
          {folders.map(f => <MenuItem key={f} value={f}>{f}</Select.Option>)}
        </Select>
      </div>
      <Input
        label="برچسب"
        value={tagInput}
        onChange={e => setTagInput(e.target.value)}
        onKeyDown={e => {
          if (e.key === "Enter" && tagInput) {
            setTags([...tags, tagInput]); setTagInput("");
          }
        }}
        style={{  width: 120  }}
      />
      {tags.map(tag => <Tag key={tag} label={tag} onDelete={() => setTags(tags.filter(t => t !== tag))} />)}
      <Button variant="contained" color="success" onClick={handleUpload} disabled={!file || !folder}>بارگذاری</Button>
    </div>
  );
};