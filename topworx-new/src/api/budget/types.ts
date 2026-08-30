export type BudgetType = "annual" | "monthly" | "project";

export interface Budget {
  id: string;
  title: string;
  type: BudgetType;
  year: number;
  month?: number;
  amount: number;
  allocatedTo: { id: string; name: string; type: "department" | "project" | "cost_center" };
  spent: number;
  income: number;
  status: "active" | "closed" | "over";
  createdBy: { id: string; name: string };
  createdAt: string;
  updatedAt: string;
  history?: { date: string; user: string; action: string; description?: string }[];
}