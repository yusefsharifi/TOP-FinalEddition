export type ProjectStatus = "active" | "completed" | "paused" | "cancelled";

export interface ProjectMember {
  id: string;
  name: string;
  role: "manager" | "member" | "observer";
}

export interface Project {
  id: string;
  title: string;
  description: string;
  status: ProjectStatus;
  startDate: string;
  endDate: string;
  members: ProjectMember[];
  progress: number; // درصد پیشرفت
  tasks: string[]; // آرایه‌ای از TaskId
  createdBy: { id: string; name: string };
  createdAt: string;
  updatedAt: string;
}