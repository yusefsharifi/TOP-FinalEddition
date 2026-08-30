import React from 'react';

const HSEAlerts: React.FC = () => {
  return (
    <div className="hse-alerts">
      <h3>اعلان‌ها و هشدارها</h3>
      <div className="alerts-container">
        <div className="alert-item critical">
          <h4>هشدار بحرانی</h4>
          <p>رویداد ایمنی بحرانی در بخش تولید</p>
          <span className="alert-time">2 ساعت پیش</span>
        </div>
        <div className="alert-item warning">
          <h4>هشدار متوسط</h4>
          <p>نیاز به بازرسی ایمنی در انبار</p>
          <span className="alert-time">1 روز پیش</span>
        </div>
        <div className="alert-item info">
          <h4>اطلاعیه</h4>
          <p>جلسه آموزش ایمنی فردا</p>
          <span className="alert-time">3 روز پیش</span>
        </div>
      </div>
    </div>
  );
};

export default HSEAlerts; 