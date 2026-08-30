import React from 'react';

const TasksDashboard: React.FC = () => {
  return (
    <div className="tasks-dashboard">
      <h2>داشبورد وظایف</h2>
      <p>نمایش وضعیت وظایف، پروژه‌ها و پیشرفت‌ها</p>
      
      {/* آمار کلی */}
      <div className="stats-grid">
        <div className="stat-item">
          <h3>کل وظایف</h3>
          <p className="number">156</p>
        </div>
        <div className="stat-item">
          <h3>در حال انجام</h3>
          <p className="number">42</p>
        </div>
        <div className="stat-item">
          <h3>تکمیل شده</h3>
          <p className="number">98</p>
        </div>
        <div className="stat-item">
          <h3>تأخیر</h3>
          <p className="number">16</p>
        </div>
      </div>
      
      {/* پروژه‌های فعال */}
      <div className="active-projects">
        <h3>پروژه‌های فعال</h3>
        <div className="project-list">
          <div className="project-item">
            <h4>پروژه A</h4>
            <p>پیشرفت: 75%</p>
            <div className="progress-bar">
              <div className="progress" style={{width: '75%'}}></div>
            </div>
          </div>
          <div className="project-item">
            <h4>پروژه B</h4>
            <p>پیشرفت: 45%</p>
            <div className="progress-bar">
              <div className="progress" style={{width: '45%'}}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TasksDashboard; 