import React from 'react';

const ReportsDashboard: React.FC = () => {
  return (
    <div className="reports-dashboard">
      <h2>داشبورد گزارشات</h2>
      <p>نمایش انواع گزارشات و آمار کلی سیستم</p>
      
      {/* انواع گزارشات */}
      <div className="reports-grid">
        <div className="report-category">
          <h3>گزارشات مالی</h3>
          <p>گزارشات حسابداری، بودجه و مالی</p>
        </div>
        <div className="report-category">
          <h3>گزارشات فروش</h3>
          <p>گزارشات فروش، مشتریان و فرصت‌ها</p>
        </div>
        <div className="report-category">
          <h3>گزارشات انبار</h3>
          <p>گزارشات موجودی و کالاها</p>
        </div>
        <div className="report-category">
          <h3>گزارشات منابع انسانی</h3>
          <p>گزارشات کارکنان و عملکرد</p>
        </div>
      </div>
    </div>
  );
};

export default ReportsDashboard; 