import React from 'react';

const HSEFilters: React.FC = () => {
  return (
    <div className="hse-filters">
      <h3>فیلترهای پیشرفته</h3>
      <div className="filter-grid">
        <div className="filter-item">
          <label>نوع رویداد:</label>
          <select>
            <option value="">همه</option>
            <option value="incident">حادثه</option>
            <option value="near-miss">نزدیک به حادثه</option>
            <option value="inspection">بازرسی</option>
            <option value="training">آموزش</option>
          </select>
        </div>
        <div className="filter-item">
          <label>وضعیت:</label>
          <select>
            <option value="">همه</option>
            <option value="open">باز</option>
            <option value="in-progress">در حال انجام</option>
            <option value="closed">بسته</option>
          </select>
        </div>
        <div className="filter-item">
          <label>تاریخ از:</label>
          <input type="date" />
        </div>
        <div className="filter-item">
          <label>تاریخ تا:</label>
          <input type="date" />
        </div>
      </div>
    </div>
  );
};

export default HSEFilters; 