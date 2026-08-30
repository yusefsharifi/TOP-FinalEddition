import React from 'react';

const ProjectManager: React.FC = () => {
  return (
    <div className="project-manager">
      <h3>مدیریت پروژه‌ها</h3>
      
      {/* پروژه‌های فعال */}
      <div className="projects-grid">
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
            <span>تاریخ شروع: 1 آذر 1402</span>
            <span>تاریخ پایان: 1 فروردین 1403</span>
          </div>
          <div className="project-actions">
            <button>مشاهده جزئیات</button>
            <button>ویرایش</button>
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
            <span>تاریخ شروع: 15 دی 1402</span>
            <span>تاریخ پایان: 15 خرداد 1403</span>
          </div>
          <div className="project-actions">
            <button>مشاهده جزئیات</button>
            <button>ویرایش</button>
          </div>
        </div>
        
        <div className="project-card">
          <div className="project-header">
            <h4>پروژه آموزش</h4>
            <span className="status completed">تکمیل شده</span>
          </div>
          <p>آموزش کارکنان در زمینه ایمنی</p>
          <div className="project-progress">
            <p>پیشرفت: 100%</p>
            <div className="progress-bar">
              <div className="progress" style={{width: '100%'}}></div>
            </div>
          </div>
          <div className="project-meta">
            <span>مدیر: فاطمه کریمی</span>
            <span>تاریخ شروع: 1 مهر 1402</span>
            <span>تاریخ پایان: 30 آذر 1402</span>
          </div>
          <div className="project-actions">
            <button>مشاهده جزئیات</button>
            <button>گزارش نهایی</button>
          </div>
        </div>
      </div>
      
      <button className="add-project">افزودن پروژه جدید</button>
    </div>
  );
};

export default ProjectManager; 