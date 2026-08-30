import React from 'react';

const ProjectDashboard: React.FC = () => {
  return (
    <div className="project-dashboard">
      <h2>داشبورد پروژه‌ها</h2>
      <p>نمایش آمار و وضعیت پروژه‌ها</p>
      
      {/* آمار کلی */}
      <div className="stats-grid">
        <div className="stat-item">
          <h3>کل پروژه‌ها</h3>
          <p className="number">24</p>
          <span className="trend positive">+3 پروژه جدید</span>
        </div>
        <div className="stat-item">
          <h3>در حال اجرا</h3>
          <p className="number">12</p>
          <span className="trend neutral">بدون تغییر</span>
        </div>
        <div className="stat-item">
          <h3>تکمیل شده</h3>
          <p className="number">8</p>
          <span className="trend positive">+2 تکمیل شده</span>
        </div>
        <div className="stat-item">
          <h3>تأخیر</h3>
          <p className="number">4</p>
          <span className="trend negative">نیاز به توجه</span>
        </div>
      </div>
      
      {/* پروژه‌های فعال */}
      <div className="active-projects">
        <h3>پروژه‌های فعال</h3>
        <div className="project-grid">
          <div className="project-card">
            <div className="project-header">
              <h4>پروژه توسعه نرم‌افزار</h4>
              <span className="status active">فعال</span>
            </div>
            <p>توسعه سیستم مدیریت مشتریان</p>
            <div className="project-progress">
              <p>پیشرفت: 75%</p>
              <div className="progress-bar">
                <div className="progress" style={{width: '75%'}}></div>
              </div>
            </div>
            <div className="project-meta">
              <span>مدیر: علی احمدی</span>
              <span>تاریخ پایان: 15 فروردین 1403</span>
            </div>
          </div>
          
          <div className="project-card">
            <div className="project-header">
              <h4>پروژه بهینه‌سازی</h4>
              <span className="status planning">برنامه‌ریزی</span>
            </div>
            <p>بهینه‌سازی فرآیندهای تولید</p>
            <div className="project-progress">
              <p>پیشرفت: 25%</p>
              <div className="progress-bar">
                <div className="progress" style={{width: '25%'}}></div>
              </div>
            </div>
            <div className="project-meta">
              <span>مدیر: محمد رضایی</span>
              <span>تاریخ پایان: 30 خرداد 1403</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDashboard; 