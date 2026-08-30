export type UserRole = "admin" | "manager" | "finance" | "hr" | "crm" | "inventory" | "guest";

export interface ModuleItem {
  label: string;
  path: string;
  icon: string;
  roles: UserRole[];
  children?: ModuleItem[];
}

export const modules: ModuleItem[] = [
  {
    label: "داشبورد",
    path: "/dashboard",
    icon: "Dashboard",
    roles: ["admin", "manager", "finance", "hr", "crm", "inventory"],
  },
  {
    label: "مدیریت مشتریان",
    icon: "People",
    path: "/crm",
    roles: ["admin", "crm", "manager"],
    children: [
      { label: "مشتریان", path: "/crm/customers", icon: "Person", roles: ["admin", "crm", "manager"] },
      { label: "فرصت‌ها", path: "/crm/opportunities", icon: "TrendingUp", roles: ["admin", "crm", "manager"] },
    ],
  },
  {
    label: "انبار و کالا",
    icon: "Inventory",
    path: "/inventory",
    roles: ["admin", "inventory", "manager"],
    children: [
      { label: "محصولات", path: "/inventory/products", icon: "Category", roles: ["admin", "inventory", "manager"] },
      // سایر زیرماژول‌های انبار
    ],
  },
  {
    label: "مالی و حسابداری",
    icon: "AccountBalance",
    path: "/finance",
    roles: ["admin", "finance", "manager"],
    children: [
      { label: "حساب‌ها", path: "/finance/accounts", icon: "AccountTree", roles: ["admin", "finance", "manager"] },
      // سایر زیرماژول‌های مالی
    ],
  },
  {
    label: "منابع انسانی",
    icon: "Group",
    path: "/hr",
    roles: ["admin", "hr", "manager"],
    children: [
      { label: "کارکنان", path: "/hr/employees", icon: "Person", roles: ["admin", "hr", "manager"] },
      // سایر زیرماژول‌های HR
    ],
  },
  {
    label: "HSE",
    icon: "Security",
    path: "/hse",
    roles: ["admin", "manager"],
  },
  {
    label: "گزارشات",
    icon: "Assessment",
    path: "/reports",
    roles: ["admin", "manager", "finance"],
  },
  {
    label: "وظایف",
    icon: "Assignment",
    path: "/tasks",
    roles: ["admin", "manager"],
  },
  {
    label: "تأمین و خرید",
    icon: "ShoppingCart",
    path: "/procurement",
    roles: ["admin", "manager"],
  },
  {
    label: "نامه‌نگاری",
    icon: "Mail",
    path: "/correspondence",
    roles: ["admin", "manager"],
  },
  {
    label: "هوش مصنوعی",
    icon: "Psychology",
    path: "/ai",
    roles: ["admin"],
  },
  {
    label: "مدیریت پروژه",
    icon: "Assignment",
    path: "/projects",
    roles: ["admin", "manager"],
  },
  {
    label: "هوش تجاری",
    icon: "Analytics",
    path: "/bi",
    roles: ["admin", "manager"],
  },
  {
    label: "امنیت و دسترسی‌ها",
    icon: "Security",
    path: "/security",
    roles: ["admin"],
  },
  {
    label: "تنظیمات",
    path: "/settings",
    icon: "Settings",
    roles: ["admin"],
  },
  // ... سایر ماژول‌ها و زیرسیستم‌ها
];