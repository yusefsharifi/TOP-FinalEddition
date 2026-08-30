import React from 'react';
import ProcurementDashboard from '../../components/procurement/ProcurementDashboard';
import PurchaseRequestForm from '../../components/procurement/PurchaseRequestForm';
import SupplierManager from '../../components/procurement/SupplierManager';

const Procurement: React.FC = () => {
  return (
    <div className="procurement-page">
      <h1>ماژول تأمین و خرید</h1>
      <p>در این بخش می‌توانید فرآیندهای تأمین و خرید را مدیریت کنید.</p>
      
      {/* داشبورد تأمین و خرید */}
      <ProcurementDashboard />
      
      {/* فرم درخواست خرید */}
      <PurchaseRequestForm />
      
      {/* مدیریت تأمین‌کنندگان */}
      <SupplierManager />
    </div>
  );
};

export default Procurement; 