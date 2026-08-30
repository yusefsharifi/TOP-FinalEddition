import React from 'react';

const SupplierManager: React.FC = () => {
  return (
    <div className="supplier-manager">
      <h3>مدیریت تأمین‌کنندگان</h3>
      
      {/* فیلترها */}
      <div className="supplier-filters">
        <select>
          <option value="">همه تأمین‌کنندگان</option>
          <option value="active">فعال</option>
          <option value="inactive">غیرفعال</option>
          <option value="verified">تأیید شده</option>
        </select>
        
        <select>
          <option value="">همه دسته‌بندی‌ها</option>
          <option value="equipment">تجهیزات</option>
          <option value="materials">مواد اولیه</option>
          <option value="services">خدمات</option>
        </select>
      </div>
      
      {/* لیست تأمین‌کنندگان */}
      <div className="supplier-list">
        <div className="supplier-item">
          <div className="supplier-header">
            <h4>شرکت ABC</h4>
            <span className="status active">فعال</span>
          </div>
          <p>تأمین‌کننده تجهیزات صنعتی</p>
          <div className="supplier-meta">
            <span>دسته‌بندی: تجهیزات</span>
            <span>شماره تماس: 021-12345678</span>
            <span>ایمیل: info@abc.com</span>
          </div>
          <div className="supplier-rating">
            <span>امتیاز: 4.5/5</span>
            <span>تعداد سفارشات: 25</span>
          </div>
          <div className="supplier-actions">
            <button>مشاهده جزئیات</button>
            <button>ویرایش</button>
          </div>
        </div>
        
        <div className="supplier-item">
          <div className="supplier-header">
            <h4>شرکت XYZ</h4>
            <span className="status active">فعال</span>
          </div>
          <p>تأمین‌کننده مواد اولیه</p>
          <div className="supplier-meta">
            <span>دسته‌بندی: مواد اولیه</span>
            <span>شماره تماس: 021-87654321</span>
            <span>ایمیل: contact@xyz.com</span>
          </div>
          <div className="supplier-rating">
            <span>امتیاز: 4.2/5</span>
            <span>تعداد سفارشات: 18</span>
          </div>
          <div className="supplier-actions">
            <button>مشاهده جزئیات</button>
            <button>ویرایش</button>
          </div>
        </div>
        
        <div className="supplier-item">
          <div className="supplier-header">
            <h4>شرکت DEF</h4>
            <span className="status inactive">غیرفعال</span>
          </div>
          <p>تأمین‌کننده خدمات</p>
          <div className="supplier-meta">
            <span>دسته‌بندی: خدمات</span>
            <span>شماره تماس: 021-11223344</span>
            <span>ایمیل: service@def.com</span>
          </div>
          <div className="supplier-rating">
            <span>امتیاز: 3.8/5</span>
            <span>تعداد سفارشات: 12</span>
          </div>
          <div className="supplier-actions">
            <button>مشاهده جزئیات</button>
            <button>فعال‌سازی</button>
          </div>
        </div>
      </div>
      
      <button className="add-supplier">افزودن تأمین‌کننده جدید</button>
    </div>
  );
};

export default SupplierManager; 