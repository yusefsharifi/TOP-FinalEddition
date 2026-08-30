export type EmployeeStatus = "active" | "inactive" | "on_leave" | "retired";

export interface Employee {
  id: string;
  code: string;
  firstName: string;
  lastName: string;
  nationalId: string;
  position: string;
  department: string;
  status: EmployeeStatus;
  hireDate: string;
  contractType: string;
  phone: string;
  email: string;
  address: string;
  avatarUrl?: string;
  documents?: { id: string; name: string; url: string }[];
  roles: string[];
  createdAt: string;
  updatedAt: string;
}