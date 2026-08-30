export interface PayrollItem {
  id: string;
  type: "base" | "bonus" | "overtime" | "loan" | "insurance" | "tax" | "deduction" | "custom";
  title: string;
  amount: number;
}

export interface Payroll {
  id: string;
  employeeId: string;
  employeeName: string;
  month: number;
  year: number;
  items: PayrollItem[];
  total: number;
  net: number;
  status: "pending" | "paid" | "cancelled";
  createdAt: string;
  paidAt?: string;
  pdfUrl?: string;
  excelUrl?: string;
}