import React from 'react';

const HSEReports: React.FC = () => {
  return (
    <div className="hse-reports">
      <h3>گزارش‌های HSE</h3>
      <div className="reports-grid">
        <div className="report-item">
          <h4>گزارش ماهانه رویدادها</h4>
          <p>خلاصه‌ای از تمام رویدادهای ماه جاری</p>
          <button>دانلود PDF</button>
        </div>
        <div className="report-item">
          <h4>گزارش KPI</h4>
          <p>شاخص‌های کلیدی عملکرد HSE</p>
          <button>دانلود Excel</button>
        </div>
        <div className="report-item">
          <h4>گزارش تحلیلی</h4>
          <p>تحلیل روند رویدادها و پیشنهادات</p>
          <button>مشاهده</button>
        </div>
        <div className="report-item">
          <h4>گزارش بازرسی</h4>
          <p>نتایج بازرسی‌های ایمنی</p>
          <button>دانلود</button>
        </div>
      </div>
    </div>
  );
};

export default HSEReports; 