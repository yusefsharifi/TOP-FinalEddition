export type ContractStatus = "active" | "expired" | "terminated" | "renewed";

export interface Contract {
  id: string;
  title: string;
  type: string; // استخدامی، پروژه‌ای، خرید، فروش و ...
  party: { id: string; name: string; type: "employee" | "company" | "customer" };
  status: ContractStatus;
  startDate: string;
  endDate: string;
  fileUrl: string;
  access: "public" | "private" | "role";
  roles?: string[];
  version: number;
  history?: { version: number; fileUrl: string; updatedAt: string }[];
  createdBy: { id: string; name: string };
  createdAt: string;
  updatedAt: string;
  relatedProjectId?: string;
}