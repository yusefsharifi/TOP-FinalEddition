import React from 'react';

const TaskManager: React.FC = () => {
  return (
    <div className="task-manager">
      <h3>مدیریت وظایف</h3>
      
      {/* فیلترها */}
      <div className="task-filters">
        <select>
          <option value="">همه وظایف</option>
          <option value="todo">انجام نشده</option>
          <option value="in-progress">در حال انجام</option>
          <option value="completed">تکمیل شده</option>
          <option value="overdue">تأخیر</option>
        </select>
        
        <select>
          <option value="">همه اولویت‌ها</option>
          <option value="low">کم</option>
          <option value="medium">متوسط</option>
          <option value="high">زیاد</option>
          <option value="urgent">فوری</option>
        </select>
        
        <select>
          <option value="">همه اعضا</option>
          <option value="user1">کاربر 1</option>
          <option value="user2">کاربر 2</option>
          <option value="user3">کاربر 3</option>
        </select>
      </div>
      
      {/* لیست وظایف */}
      <div className="task-list">
        <div className="task-item">
          <div className="task-header">
            <h4>توسعه ویژگی جدید</h4>
            <span className="priority high">زیاد</span>
          </div>
          <p>توسعه ویژگی جدید برای ماژول فروش</p>
          <div className="task-meta">
            <span>تکلیف: علی احمدی</span>
            <span>تاریخ: 15 دی 1402</span>
            <span className="status in-progress">در حال انجام</span>
          </div>
        </div>
        
        <div className="task-item">
          <div className="task-header">
            <h4>بازرسی ایمنی</h4>
            <span className="priority urgent">فوری</span>
          </div>
          <p>بازرسی ایمنی در بخش تولید</p>
          <div className="task-meta">
            <span>تکلیف: محمد رضایی</span>
            <span>تاریخ: 10 دی 1402</span>
            <span className="status overdue">تأخیر</span>
          </div>
        </div>
        
        <div className="task-item">
          <div className="task-header">
            <h4>بروزرسانی مستندات</h4>
            <span className="priority medium">متوسط</span>
          </div>
          <p>بروزرسانی مستندات فنی پروژه</p>
          <div className="task-meta">
            <span>تکلیف: فاطمه کریمی</span>
            <span>تاریخ: 20 دی 1402</span>
            <span className="status todo">انجام نشده</span>
          </div>
        </div>
      </div>
      
      <button className="add-task">افزودن وظیفه جدید</button>
    </div>
  );
};

export default TaskManager; 