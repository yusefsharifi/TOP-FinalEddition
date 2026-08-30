import React from 'react';

const HSEDashboard: React.FC = () => {
  return (
    <div className="hse-dashboard">
      <h2>داشبورد HSE</h2>
      <p>نمایش وضعیت ایمنی، رویدادها و شاخص‌های کلیدی.</p>
      
      {/* نمودارها و ویجت‌های تحلیلی */}
      <div className="dashboard-grid">
        <div className="widget">
          <h3>وضعیت ایمنی</h3>
          <p>آخرین رویدادها و وضعیت‌ها</p>
        </div>
        <div className="widget">
          <h3>شاخص‌های کلیدی</h3>
          <p>KPI های HSE</p>
        </div>
        <div className="widget">
          <h3>گزارش‌های تحلیلی</h3>
          <p>نمودارها و آمار</p>
        </div>
      </div>
    </div>
  );
};

export default HSEDashboard; 