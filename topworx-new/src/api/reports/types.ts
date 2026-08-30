export interface KPI {
  id: string;
  title: string;
  value: number | string;
  icon: string;
  color?: string;
}

export interface ChartData {
  id: string;
  title: string;
  type: "line" | "bar" | "pie";
  data: any[];
}

export interface Report {
  id: string;
  title: string;
  columns: string[];
  rows: any[][];
  filters: Record<string, any>;
  createdAt: string;
  type: "finance" | "hr" | "sales" | "project" | "custom";
}