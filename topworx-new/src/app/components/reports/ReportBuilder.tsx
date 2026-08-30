import React from 'react';

const ReportBuilder: React.FC = () => {
  return (
    <div className="report-builder">
      <h3>سازنده گزارش</h3>
      <form>
        <div className="form-group">
          <label>نوع گزارش:</label>
          <select required>
            <option value="">انتخاب کنید</option>
            <option value="financial">گزارش مالی</option>
            <option value="sales">گزارش فروش</option>
            <option value="inventory">گزارش انبار</option>
            <option value="hr">گزارش منابع انسانی</option>
            <option value="custom">گزارش سفارشی</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>بازه زمانی:</label>
          <select required>
            <option value="">انتخاب کنید</option>
            <option value="today">امروز</option>
            <option value="week">هفته جاری</option>
            <option value="month">ماه جاری</option>
            <option value="quarter">فصل جاری</option>
            <option value="year">سال جاری</option>
            <option value="custom">سفارشی</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>فیلدهای گزارش:</label>
          <div className="field-selector">
            <label><input type="checkbox" /> تاریخ</label>
            <label><input type="checkbox" /> مبلغ</label>
            <label><input type="checkbox" /> وضعیت</label>
            <label><input type="checkbox" /> توضیحات</label>
          </div>
        </div>
        
        <div className="form-group">
          <label>فرمت خروجی:</label>
          <select required>
            <option value="pdf">PDF</option>
            <option value="excel">Excel</option>
            <option value="csv">CSV</option>
            <option value="html">HTML</option>
          </select>
        </div>
        
        <button type="submit">ایجاد گزارش</button>
      </form>
    </div>
  );
};

export default ReportBuilder; 