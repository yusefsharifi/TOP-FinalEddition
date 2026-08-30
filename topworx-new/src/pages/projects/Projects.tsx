import React, { useState } from "react";
import { Alert, Button, Card } from 'antd';
import { useProjects, useCreateProject, useUpdateProject, useDeleteProject } from "../../api/projects";
import { ProjectTable } from "../../components/projects/ProjectTable";
import { ProjectForm } from "../../components/projects/ProjectForm";
import { useNavigate } from "react-router-dom";
import { Col, Input, InputNumber, Row } from 'antd';
import React, { useState } from "react";

const [search, setSearch] = useState("");
const [status, setStatus] = useState("");
const [onlyMine, setOnlyMine] = useState(false);
const currentUserId = "1"; // از AuthContext بگیر

const filtered = data.filter(project =>
  (!search || project.title.includes(search)) &&
  (!status || project.status === status) &&
  (!onlyMine || project.members.some(m => m.id === currentUserId))
);

// در UI:
<Row gutter={[16, 16]}>
  <Col xs={Math.round(12 / 12 * 24)}>
    <Input fullWidth label="جستجو" value={search} onChange={e => setSearch(e.target.value)} />
  </Col>
  <Col xs={Math.round(6 / 12 * 24)}>
    <Input select fullWidth label="وضعیت" value={status} onChange={e => setStatus(e.target.value)}>
      <MenuItem value="">همه</Select.Option>
      <MenuItem value="active">در حال انجام</Select.Option>
      <MenuItem value="completed">تکمیل شده</Select.Option>
      <MenuItem value="paused">متوقف</Select.Option>
      <MenuItem value="cancelled">لغو شده</Select.Option>
    </Input>
  </Col>
  <Col xs={Math.round(6 / 12 * 24)}>
    <FormControlLabel
      control={<Checkbox checked={onlyMine} onChange={e => setOnlyMine(e.target.checked)} />}
      label="فقط پروژه‌های من"
    />
  </Col>
</Row>

// فرض: لیست کاربران را از API یا Context بگیر
const users = [
  { id: "1", name: "مدیر" },
  { id: "2", name: "کاربر نمونه" },
];

export const Projects: React.FC = () => {
  const { data = [], isLoading, refetch } = useProjects();
  const createProject = useCreateProject();
  const updateProject = useUpdateProject();
  const deleteProject = useDeleteProject();

  const [openForm, setOpenForm] = useState(false);
  const [selected, setSelected] = useState<any>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  const navigate = useNavigate();

  const handleEdit = (project: any) => {
    setSelected(project);
    setOpenForm(true);
  };

  const handleAdd = () => {
    setSelected(null);
    setOpenForm(true);
  };

  const handleSave = async (data: any) => {
    try {
      if (selected) {
        await updateProject.mutateAsync({ id: selected.id, ...data });
        setSnackbar({ open: true, message: "پروژه با موفقیت ویرایش شد.", severity: "success" });
      } else {
        await createProject.mutateAsync(data);
        setSnackbar({ open: true, message: "پروژه جدید با موفقیت افزوده شد.", severity: "success" });
      }
      setOpenForm(false);
      refetch();
    } catch (e: any) {
      setSnackbar({ open: true, message: e.message || "خطا در ذخیره‌سازی اطلاعات", severity: "error" });
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteProject.mutateAsync(id);
      setSnackbar({ open: true, message: "پروژه حذف شد.", severity: "success" });
      refetch();
    } catch (e: any) {
      setSnackbar({ open: true, message: e.message || "خطا در حذف پروژه", severity: "error" });
    }
  };

  const handleDetails = (id: string) => {
    navigate(`/projects/${id}`);
  };

  return (
    <Card style={{  p: 3  }}>
      <div>
        <Button variant="contained" onClick={handleAdd}>افزودن پروژه جدید</Button>
      </div>
      <ProjectTable data={data} onEdit={handleEdit} onDelete={handleDelete} onDetails={handleDetails} />
      <ProjectForm
        open={openForm}
        onClose={() => setOpenForm(false)}
        project={selected}
        onSave={handleSave}
        users={users}
      />
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