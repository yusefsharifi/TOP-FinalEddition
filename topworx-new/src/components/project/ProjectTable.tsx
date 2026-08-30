import React from "react";
import { Button, Progress, Table, Tag, Tooltip } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { Project } from "../../api/projects/types";
import { Progress, Typography } from 'antd';

<div>
  <LinearProgress variant="determinate" value={project.progress} style={{  height: 10, borderRadius: 2  }} />
  <Typography fontSize={12} align="center">{project.progress}%</Typography>
</div>

const statusLabels: Record<string, string> = {
  active: "در حال انجام",
  completed: "تکمیل شده",
  paused: "متوقف",
  cancelled: "لغو شده",
};

export const ProjectTable: React.FC<{
  data: Project[];
  onEdit: (project: Project) => void;
  onDelete: (id: string) => void;
  onDetails: (id: string) => void;
}> = ({ data, onEdit, onDelete, onDetails }) => (
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>عنوان</TableCell>
        <TableCell>وضعیت</TableCell>
        <TableCell>تاریخ شروع</TableCell>
        <TableCell>تاریخ پایان</TableCell>
        <TableCell>پیشرفت</TableCell>
        <TableCell>عملیات</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((project) => (
        <TableRow key={project.id} hover onClick={() => onDetails(project.id)} style={{ cursor: "pointer" }}>
          <TableCell>{project.title}</TableCell>
          <TableCell>
            <Tag label={statusLabels[project.status]} color={
              project.status === "completed" ? "success" :
              project.status === "active" ? "primary" :
              project.status === "paused" ? "warning" : "error"
            } />
          </TableCell>
          <TableCell>{new Date(project.startDate).toLocaleDateString("fa-IR")}</TableCell>
          <TableCell>{new Date(project.endDate).toLocaleDateString("fa-IR")}</TableCell>
          <TableCell>
            <LinearProgress variant="determinate" value={project.progress} style={{  height: 8, borderRadius: 2  }} />
            <span style={{ fontSize: 12 }}>{project.progress}%</span>
          </TableCell>
          <TableCell>
            <Tooltip title="ویرایش">
              <Button type="text" onClick={e => { e.stopPropagation(); onEdit(project); }}><EditIcon /></Button>
            </Tooltip>
            <Tooltip title="حذف">
              <Button type="text" onClick={e => { e.stopPropagation(); onDelete(project.id); }}><DeleteIcon /></Button>
            </Tooltip>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);