import React from 'react';

const CorrespondenceDashboard: React.FC = () => {
  return (
    <div className="correspondence-dashboard">
      <h2>داشبورد نامه‌نگاری و اتوماسیون</h2>
      <p>نمایش آمار مکاتبات، فرآیندها و اتوماسیون‌ها</p>
      
      {/* آمار کلی */}
      <div className="stats-grid">
        <div className="stat-item">
          <h3>کل نامه‌ها</h3>
          <p className="number">1,234</p>
          <span className="trend positive">+8% نسبت به ماه گذشته</span>
        </div>
        <div className="stat-item">
          <h3>در انتظار تأیید</h3>
          <p className="number">45</p>
          <span className="trend neutral">بدون تغییر</span>
        </div>
        <div className="stat-item">
          <h3>فرآیندهای فعال</h3>
          <p className="number">12</p>
          <span className="trend positive">+2 فرآیند جدید</span>
        </div>
        <div className="stat-item">
          <h3>اتوماسیون‌های فعال</h3>
          <p className="number">8</p>
          <span className="trend positive">+1 اتوماسیون جدید</span>
        </div>
      </div>
      
      {/* نامه‌های مهم */}
      <div className="important-letters">
        <h3>نامه‌های مهم و فوری</h3>
        <div className="letter-list">
          <div className="letter-item urgent">
            <h4>نامه فوری به اداره مالیات</h4>
            <p>موضوع: ارسال گزارش مالی</p>
            <span className="deadline">مهلت: 2 روز</span>
            <span className="status pending">در انتظار تأیید</span>
          </div>
          <div className="letter-item important">
            <h4>نامه به تأمین‌کنندگان</h4>
            <p>موضوع: بروزرسانی شرایط قرارداد</p>
            <span className="deadline">مهلت: 1 هفته</span>
            <span className="status in-progress">در حال بررسی</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CorrespondenceDashboard; 