// src/App.tsx
// ============================================================================
// Main Application — TOPWorX ERP
// Consolidated from dual MUI/Ant Design architecture.
// Uses Ant Design for UI, React Query for data, i18next for translations.
// ============================================================================

import React, { Suspense, lazy } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ConfigProvider } from "antd";
import { I18nextProvider } from "react-i18next";

// Core providers
import i18n from "./i18n";
import { AuthProvider } from "./core/auth/AuthProvider";
import { AccessibilityProvider } from "./app/components/common/AccessibilityProvider";
import { ErrorBoundary } from "./app/components/common/ErrorBoundary";
import { LoadingSpinner } from "./app/components/common/LoadingSpinner";
import { PrivateRoute } from "./app/components/common/PrivateRoute";
import { PublicRoute } from "./app/components/common/PublicRoute";
import { MainLayout } from "./app/components/layout/MainLayout";

// ── Auth Pages (loaded immediately) ──────────────────────────────────────────
import { LoginPage } from "./app/pages/auth/LoginPage";
import { ForgotPasswordPage } from "./app/pages/auth/ForgotPasswordPage";
import { ResetPasswordPage } from "./app/pages/auth/ResetPasswordPage";

// ── React Query Client ──────────────────────────────────────────────────────
const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
    mutations: { retry: 0 },
  },
});

// ── Ant Design Theme ────────────────────────────────────────────────────────
const antdTheme = {
  token: {
    colorPrimary: "#1677ff",
    borderRadius: 6,
  },
};

// ── Lazy-loaded modules ─────────────────────────────────────────────────────

// Dashboard
const WidgetManager = lazy(() =>
  import("./app/components/dashboard/WidgetManager").then(m => ({ default: m.WidgetManager }))
);

// Finance
const FinanceDashboard = lazy(() =>
  import("./app/components/finance/FinanceDashboard").then(m => ({ default: m.FinanceDashboard }))
);

// Accounting
const AccountingDashboard = lazy(() =>
  import("./app/components/accounting/AccountingDashboard").then(m => ({ default: m.AccountingDashboard }))
);

// AI
const AIDashboard = lazy(() =>
  import("./app/components/ai/AIDashboard").then(m => ({ default: m.AIDashboard }))
);
const AIAnalyticsDashboard = lazy(() =>
  import("./app/components/ai/AIAnalyticsDashboard").then(m => ({ default: m.AIAnalyticsDashboard }))
);
const AIInsightsPanel = lazy(() =>
  import("./app/components/ai/AIInsightsPanel").then(m => ({ default: m.AIInsightsPanel }))
);
const AIChat = lazy(() =>
  import("./app/components/ai/AIChat").then(m => ({ default: m.AIChat }))
);
const AIReports = lazy(() =>
  import("./app/components/ai/AIReports").then(m => ({ default: m.AIReports }))
);
const AIAutomationDashboard = lazy(() =>
  import("./app/components/ai/AIAutomationDashboard").then(m => ({ default: m.AIAutomationDashboard }))
);

// Correspondence
const CorrespondenceDashboard = lazy(() =>
  import("./app/components/correspondence/CorrespondenceDashboard").then(m => ({ default: m.CorrespondenceDashboard }))
);

// CRM
const CRMCustomerDetails = lazy(() =>
  import("./app/components/crm/CustomerDetails").then(m => ({ default: m.CRMCustomerDetails }))
);
const CRMCustomerForm = lazy(() =>
  import("./app/components/crm/CustomerForm").then(m => ({ default: m.CRMCustomerForm }))
);
const SalesOrdersTable = lazy(() =>
  import("./app/components/crm/SalesOrdersTable").then(m => ({ default: m.SalesOrdersTable }))
);
const SalesInvoicesTable = lazy(() =>
  import("./app/components/crm/SalesInvoicesTable").then(m => ({ default: m.SalesInvoicesTable }))
);

// Inventory
const InventoryDashboard = lazy(() =>
  import("./app/components/inventory/InventoryDashboard").then(m => ({ default: m.InventoryDashboard }))
);
const ItemsList = lazy(() =>
  import("./app/components/inventory/ItemsList").then(m => ({ default: m.ItemsList }))
);
const ItemForm = lazy(() =>
  import("./app/components/inventory/ItemForm").then(m => ({ default: m.ItemForm }))
);
const WarehouseList = lazy(() =>
  import("./app/components/inventory/WarehouseList").then(m => ({ default: m.WarehouseList }))
);
const StockMovements = lazy(() =>
  import("./app/components/inventory/StockMovements").then(m => ({ default: m.StockMovements }))
);

// HR
const HRDashboard = lazy(() =>
  import("./app/components/hr/HRDashboard").then(m => ({ default: m.HRDashboard }))
);
const EmployeeList = lazy(() =>
  import("./app/components/hr/EmployeeList").then(m => ({ default: m.EmployeeList }))
);
const EmployeeForm = lazy(() =>
  import("./app/components/hr/EmployeeForm").then(m => ({ default: m.EmployeeForm }))
);
const EmployeeDetails = lazy(() =>
  import("./app/components/hr/EmployeeDetails").then(m => ({ default: m.EmployeeDetails }))
);
const LeaveManagement = lazy(() =>
  import("./app/components/hr/LeaveManagement").then(m => ({ default: m.LeaveManagement }))
);

// Payroll
const PayrollDashboard = lazy(() =>
  import("./app/components/payroll/PayrollDashboard").then(m => ({ default: m.PayrollDashboard }))
);
const PayrollList = lazy(() =>
  import("./app/components/payroll/PayrollList").then(m => ({ default: m.PayrollList }))
);
const PayslipDetails = lazy(() =>
  import("./app/components/payroll/PayslipDetails").then(m => ({ default: m.PayslipDetails }))
);

// Procurement
const ProcurementDashboard = lazy(() =>
  import("./app/components/procurement/ProcurementDashboard").then(m => ({ default: m.ProcurementDashboard }))
);
const PurchaseRequestList = lazy(() =>
  import("./app/components/procurement/PurchaseRequestList").then(m => ({ default: m.PurchaseRequestList }))
);
const PurchaseRequestForm = lazy(() =>
  import("./app/components/procurement/PurchaseRequestForm").then(m => ({ default: m.PurchaseRequestForm }))
);
const SupplierList = lazy(() =>
  import("./app/components/procurement/SupplierList").then(m => ({ default: m.SupplierList }))
);

// HSE
const HSEDashboard = lazy(() =>
  import("./app/components/hse/HSEDashboard").then(m => ({ default: m.HSEDashboard }))
);
const IncidentList = lazy(() =>
  import("./app/components/hse/IncidentList").then(m => ({ default: m.IncidentList }))
);
const IncidentForm = lazy(() =>
  import("./app/components/hse/IncidentForm").then(m => ({ default: m.IncidentForm }))
);
const SafetyChecklist = lazy(() =>
  import("./app/components/hse/SafetyChecklist").then(m => ({ default: m.SafetyChecklist }))
);

// Tasks
const TasksDashboard = lazy(() =>
  import("./app/components/tasks/TasksDashboard").then(m => ({ default: m.TasksDashboard }))
);
const TaskList = lazy(() =>
  import("./app/components/tasks/TaskManager").then(m => ({ default: m.TaskManager }))
);

// Reports
const ReportsDashboard = lazy(() =>
  import("./app/components/reports/ReportsDashboard").then(m => ({ default: m.ReportsDashboard }))
);

// BI
const BIDashboard = lazy(() =>
  import("./app/components/bi/BIDashboard").then(m => ({ default: m.BIDashboard }))
);

// Settings
const SettingsDashboard = lazy(() =>
  import("./app/components/settings/SettingsDashboard").then(m => ({ default: m.SettingsDashboard }))
);

// Budget
const BudgetDashboard = lazy(() =>
  import("./app/components/budget/BudgetDashboard").then(m => ({ default: m.BudgetDashboard }))
);

// Assets
const AssetsDashboard = lazy(() =>
  import("./app/components/assets/AssetsDashboard").then(m => ({ default: m.AssetsDashboard }))
);

// Messages
const MessagesPage = lazy(() =>
  import("./app/components/messages/MessagesPage").then(m => ({ default: m.MessagesPage }))
);

// 404
const NotFoundPage = lazy(() =>
  import("./app/pages/NotFoundPage").then(m => ({ default: m.NotFoundPage }))
);

// ============================================================================
// App Component
// ============================================================================
const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>
        <ConfigProvider theme={antdTheme}>
          <AccessibilityProvider>
            <ErrorBoundary>
              <BrowserRouter>
                <AuthProvider>
                  <Suspense fallback={<LoadingSpinner fullScreen />}>
                    <Routes>
                      {/* ── Root redirect ─────────────────────────────────────── */}
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />

                      {/* ── Public Routes ─────────────────────────────────────── */}
                      <Route element={<PublicRoute />}>
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                        <Route path="/reset-password" element={<ResetPasswordPage />} />
                      </Route>

                      {/* ── Private Routes ────────────────────────────────────── */}
                      <Route element={<PrivateRoute />}>
                        <Route element={<MainLayout />}>
                          {/* Dashboard */}
                          <Route path="/dashboard" element={<WidgetManager />} />

                          {/* Finance & Accounting */}
                          <Route path="/finance" element={<FinanceDashboard />} />
                          <Route path="/accounting" element={<AccountingDashboard />} />

                          {/* AI */}
                          <Route path="/ai" element={<AIDashboard />} />
                          <Route path="/ai/analytics" element={<AIAnalyticsDashboard />} />
                          <Route path="/ai/insights" element={<AIInsightsPanel />} />
                          <Route path="/ai/chat" element={<AIChat />} />
                          <Route path="/ai/reports" element={<AIReports />} />
                          <Route path="/ai/automation" element={<AIAutomationDashboard />} />

                          {/* Correspondence */}
                          <Route path="/correspondence" element={<CorrespondenceDashboard />} />

                          {/* CRM */}
                          <Route path="/crm/customers" element={<CRMCustomerDetails />} />
                          <Route path="/crm/customers/new" element={<CRMCustomerForm />} />
                          <Route path="/crm/customers/:id/edit" element={<CRMCustomerForm />} />
                          <Route path="/crm/sales-orders" element={<SalesOrdersTable />} />
                          <Route path="/crm/sales-invoices" element={<SalesInvoicesTable />} />

                          {/* Inventory */}
                          <Route path="/inventory" element={<InventoryDashboard />} />
                          <Route path="/inventory/items" element={<ItemsList />} />
                          <Route path="/inventory/items/new" element={<ItemForm />} />
                          <Route path="/inventory/items/:id/edit" element={<ItemForm />} />
                          <Route path="/inventory/warehouses" element={<WarehouseList />} />
                          <Route path="/inventory/movements" element={<StockMovements />} />

                          {/* HR */}
                          <Route path="/hr" element={<HRDashboard />} />
                          <Route path="/hr/employees" element={<EmployeeList />} />
                          <Route path="/hr/employees/new" element={<EmployeeForm />} />
                          <Route path="/hr/employees/:id" element={<EmployeeDetails />} />
                          <Route path="/hr/employees/:id/edit" element={<EmployeeForm />} />
                          <Route path="/hr/leaves" element={<LeaveManagement />} />

                          {/* Payroll */}
                          <Route path="/payroll" element={<PayrollDashboard />} />
                          <Route path="/payroll/list" element={<PayrollList />} />
                          <Route path="/payroll/payslip/:id" element={<PayslipDetails />} />

                          {/* Procurement */}
                          <Route path="/procurement" element={<ProcurementDashboard />} />
                          <Route path="/procurement/requests" element={<PurchaseRequestList />} />
                          <Route path="/procurement/requests/new" element={<PurchaseRequestForm />} />
                          <Route path="/procurement/requests/:id/edit" element={<PurchaseRequestForm />} />
                          <Route path="/procurement/suppliers" element={<SupplierList />} />

                          {/* HSE */}
                          <Route path="/hse" element={<HSEDashboard />} />
                          <Route path="/hse/incidents" element={<IncidentList />} />
                          <Route path="/hse/incidents/new" element={<IncidentForm />} />
                          <Route path="/hse/incidents/:id/edit" element={<IncidentForm />} />
                          <Route path="/hse/safety-checklist" element={<SafetyChecklist />} />

                          {/* Tasks */}
                          <Route path="/tasks" element={<TasksDashboard />} />
                          <Route path="/tasks/list" element={<TaskList />} />

                          {/* Reports */}
                          <Route path="/reports" element={<ReportsDashboard />} />

                          {/* BI */}
                          <Route path="/bi" element={<BIDashboard />} />

                          {/* Settings */}
                          <Route path="/settings" element={<SettingsDashboard />} />

                          {/* Budget */}
                          <Route path="/budget" element={<BudgetDashboard />} />

                          {/* Assets */}
                          <Route path="/assets" element={<AssetsDashboard />} />

                          {/* Messages */}
                          <Route path="/messages" element={<MessagesPage />} />
                        </Route>
                      </Route>

                      {/* ── 404 ──────────────────────────────────────────────── */}
                      <Route path="*" element={<NotFoundPage />} />
                    </Routes>
                  </Suspense>
                </AuthProvider>
              </BrowserRouter>
            </ErrorBoundary>
          </AccessibilityProvider>
        </ConfigProvider>
      </I18nextProvider>
    </QueryClientProvider>
  );
};

export default App;
