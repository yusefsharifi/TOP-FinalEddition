import React from 'react';

const ScheduledReports: React.FC = () => {
  return (
    <div className="scheduled-reports">
      <h3>گزارشات زمان‌بندی شده</h3>
      <div className="scheduled-list">
        <div className="scheduled-item">
          <h4>گزارش ماهانه فروش</h4>
          <p>هر ماه در روز اول</p>
          <span className="status active">فعال</span>
          <button>ویرایش</button>
        </div>
        <div className="scheduled-item">
          <h4>گزارش هفتگی موجودی</h4>
          <p>هر هفته در روز شنبه</p>
          <span className="status active">فعال</span>
          <button>ویرایش</button>
        </div>
        <div className="scheduled-item">
          <h4>گزارش روزانه مالی</h4>
          <p>هر روز ساعت 9 صبح</p>
          <span className="status inactive">غیرفعال</span>
          <button>فعال‌سازی</button>
        </div>
      </div>
      
      <button className="add-scheduled">افزودن گزارش زمان‌بندی شده</button>
    </div>
  );
};

export default ScheduledReports; 