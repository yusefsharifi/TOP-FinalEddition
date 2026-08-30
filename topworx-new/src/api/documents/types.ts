export interface Document {
  id: string;
  name: string;
  type: string; // pdf, image, word, excel, ...
  size: number;
  url: string;
  folder: string;
  tags: string[];
  createdBy: { id: string; name: string };
  createdAt: string;
  updatedAt: string;
  access: "public" | "private" | "role";
  roles?: string[];
  version: number;
  relatedProjectId?: string;
  relatedTaskId?: string;
  history?: { version: number; url: string; updatedAt: string }[];
}