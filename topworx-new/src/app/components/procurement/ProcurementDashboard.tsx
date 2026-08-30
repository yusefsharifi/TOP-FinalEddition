import React from 'react';

const ProcurementDashboard: React.FC = () => {
  return (
    <div className="procurement-dashboard">
      <h2>داشبورد تأمین و خرید</h2>
      <p>نمایش آمار و وضعیت فرآیندهای تأمین و خرید</p>
      
      {/* آمار کلی */}
      <div className="stats-grid">
        <div className="stat-item">
          <h3>درخواست‌های خرید</h3>
          <p className="number">45</p>
          <span className="trend positive">+12% نسبت به ماه گذشته</span>
        </div>
        <div className="stat-item">
          <h3>سفارشات خرید</h3>
          <p className="number">32</p>
          <span className="trend positive">+8% نسبت به ماه گذشته</span>
        </div>
        <div className="stat-item">
          <h3>تأمین‌کنندگان</h3>
          <p className="number">28</p>
          <span className="trend neutral">بدون تغییر</span>
        </div>
        <div className="stat-item">
          <h3>مبلغ کل خرید</h3>
          <p className="number">2.5 میلیارد تومان</p>
          <span className="trend positive">+15% نسبت به ماه گذشته</span>
        </div>
      </div>
      
      {/* درخواست‌های در انتظار */}
      <div className="pending-requests">
        <h3>درخواست‌های در انتظار تأیید</h3>
        <div className="request-list">
          <div className="request-item">
            <h4>درخواست خرید تجهیزات</h4>
            <p>تأمین‌کننده: شرکت ABC</p>
            <span className="amount">مبلغ: 150 میلیون تومان</span>
            <span className="status pending">در انتظار تأیید</span>
          </div>
          <div className="request-item">
            <h4>درخواست خرید مواد اولیه</h4>
            <p>تأمین‌کننده: شرکت XYZ</p>
            <span className="amount">مبلغ: 75 میلیون تومان</span>
            <span className="status pending">در انتظار تأیید</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcurementDashboard; 