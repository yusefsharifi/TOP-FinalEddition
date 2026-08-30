import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { PurchaseLayout } from '../components/purchase/PurchaseLayout';
import { PurchaseDashboard } from '../pages/purchase/PurchaseDashboard';
import { PurchaseOrders } from '../pages/purchase/PurchaseOrders';
import { PurchaseRequests } from '../pages/purchase/PurchaseRequests';
import { PurchaseInvoices } from '../pages/purchase/PurchaseInvoices';
import { Suppliers } from '../pages/purchase/Suppliers';
import { PurchaseReports } from '../pages/purchase/PurchaseReports';
import { PurchaseSettings } from '../pages/purchase/PurchaseSettings';

export const PurchaseRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<PurchaseLayout />}>
        <Route index element={<PurchaseDashboard />} />
        <Route path="dashboard" element={<PurchaseDashboard />} />
        <Route path="orders" element={<PurchaseOrders />} />
        <Route path="requests" element={<PurchaseRequests />} />
        <Route path="invoices" element={<PurchaseInvoices />} />
        <Route path="suppliers" element={<Suppliers />} />
        <Route path="reports" element={<PurchaseReports />} />
        <Route path="settings" element={<PurchaseSettings />} />
      </Route>
    </Routes>
  );
}; 