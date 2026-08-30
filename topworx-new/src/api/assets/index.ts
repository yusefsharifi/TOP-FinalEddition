export type AssetCategory = "fixed" | "equipment" | "vehicle" | "it" | "other";

export interface Asset {
  id: string;
  code: string;
  name: string;
  category: AssetCategory;
  location: string;
  manager: { id: string; name: string };
  value: number;
  purchaseDate: string;
  warrantyEnd?: string;
  insuranceEnd?: string;
  status: "active" | "inactive" | "maintenance" | "disposed";
  documents?: { id: string; name: string; url: string }[];
  history?: { date: string; user: string; action: string; description?: string }[];
  createdAt: string;
  updatedAt: string;
}