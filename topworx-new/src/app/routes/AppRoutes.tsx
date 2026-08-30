import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../../core/auth/AuthProvider';

// Layouts
import { MainLayout } from '../layouts/MainLayout';
import { AuthLayout } from '../layouts/AuthLayout';

// Pages
import { Login } from '../pages/auth/Login';
import { Dashboard } from '../pages/dashboard/Dashboard';
import { Customers } from '../pages/crm/Customers';
import { Opportunities } from '../pages/crm/Opportunities';
import { Products } from '../pages/inventory/Products';
import { Inventory } from '../pages/inventory/Inventory';
import { Accounts } from '../pages/finance/Accounts';
import { Finance } from '../pages/finance/Finance';
import { Employees } from '../pages/hr/Employees';
import { Settings } from '../pages/settings/Settings';
import { HSE } from '../pages/hse/HSE';
import { Reports } from '../pages/reports/Reports';
import { Tasks } from '../pages/tasks/Tasks';
import { Procurement } from '../pages/procurement/Procurement';
import { Correspondence } from '../pages/correspondence/Correspondence';
import { AI } from '../pages/ai/AI';
import AIAssistantPage from '../pages/ai/AIAssistantPage';
import AIAnalyticsPage from '../pages/ai/AIAnalyticsPage';
import AIReportsPage from '../pages/ai/AIReportsPage';
import AIAutomationPage from '../pages/ai/AIAutomationPage';
import { Projects } from '../pages/projects/Projects';
import { BI } from '../pages/bi/BI';
import { Security } from '../pages/security/Security';
import { Accounting } from '../pages/accounting/Accounting';
import { Assets } from '../pages/assets/Assets';
import { Budget } from '../pages/budget/Budget';
import { SalesOrders } from '../pages/crm/SalesOrders';
import { SalesInvoices } from '../pages/crm/SalesInvoices';
import { HR } from '../pages/hr/HR';
import { LeaveRequests } from '../pages/hr/LeaveRequests';
import { InventoryItems } from '../pages/inventory/InventoryItems';
import { InventoryMovements } from '../pages/inventory/InventoryMovements';
import { InventoryWarehouses } from '../pages/inventory/InventoryWarehouses';
import { Messages } from '../pages/messages/Messages';
import { Payroll } from '../pages/procurement/Payroll';
import { PurchaseRequests } from '../pages/procurement/PurchaseRequests';
import { Suppliers } from '../pages/procurement/Suppliers';

// Private Route Component
const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>; // TODO: Replace with proper loading component
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

export const AppRoutes: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
      </Route>

      {/* Private Routes */}
      <Route
        element={
          <PrivateRoute>
            <MainLayout />
          </PrivateRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/crm/customers" element={<Customers />} />
        <Route path="/crm/opportunities" element={<Opportunities />} />
        <Route path="/inventory/products" element={<Products />} />
        <Route path="/inventory" element={<Inventory />} />
        <Route path="/finance/accounts" element={<Accounts />} />
        <Route path="/finance" element={<Finance />} />
        <Route path="/hr/employees" element={<Employees />} />
        <Route path="/hse" element={<HSE />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/procurement" element={<Procurement />} />
        <Route path="/correspondence" element={<Correspondence />} />
        <Route path="/accounting" element={<Accounting />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/budget" element={<Budget />} />
        <Route path="/crm/sales-orders" element={<SalesOrders />} />
        <Route path="/crm/sales-invoices" element={<SalesInvoices />} />
        <Route path="/hr" element={<HR />} />
        <Route path="/hr/leaves" element={<LeaveRequests />} />
        <Route path="/inventory/items" element={<InventoryItems />} />
        <Route path="/inventory/movements" element={<InventoryMovements />} />
        <Route path="/inventory/warehouses" element={<InventoryWarehouses />} />
        <Route path="/messages" element={<Messages />} />
        <Route path="/payroll" element={<Payroll />} />
        <Route path="/procurement/requests" element={<PurchaseRequests />} />
        <Route path="/procurement/suppliers" element={<Suppliers />} />
        <Route path="/ai" element={<AI />} />
        <Route path="/ai/assistant" element={<AIAssistantPage />} />
        <Route path="/ai/analytics" element={<AIAnalyticsPage />} />
        <Route path="/ai/reports" element={<AIReportsPage />} />
        <Route path="/ai/automation" element={<AIAutomationPage />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/bi" element={<BI />} />
        <Route path="/security" element={<Security />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      {/* Catch all route */}
      <Route
        path="*"
        element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />}
      />
    </Routes>
  );
}; 