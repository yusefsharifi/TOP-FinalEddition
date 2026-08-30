import React from 'react';

const HSEIncidentForm: React.FC = () => {
  return (
    <div className="hse-incident-form">
      <h3>ثبت رویداد جدید</h3>
      <form>
        <div className="form-group">
          <label>نوع رویداد:</label>
          <select required>
            <option value="">انتخاب کنید</option>
            <option value="incident">حادثه</option>
            <option value="near-miss">نزدیک به حادثه</option>
            <option value="inspection">بازرسی</option>
            <option value="training">آموزش</option>
          </select>
        </div>
        <div className="form-group">
          <label>عنوان:</label>
          <input type="text" required />
        </div>
        <div className="form-group">
          <label>توضیحات:</label>
          <textarea rows={4} required></textarea>
        </div>
        <div className="form-group">
          <label>محل:</label>
          <input type="text" required />
        </div>
        <div className="form-group">
          <label>تاریخ و زمان:</label>
          <input type="datetime-local" required />
        </div>
        <div className="form-group">
          <label>اولویت:</label>
          <select required>
            <option value="">انتخاب کنید</option>
            <option value="low">کم</option>
            <option value="medium">متوسط</option>
            <option value="high">زیاد</option>
            <option value="critical">بحرانی</option>
          </select>
        </div>
        <button type="submit">ثبت رویداد</button>
      </form>
    </div>
  );
};

export default HSEIncidentForm; 