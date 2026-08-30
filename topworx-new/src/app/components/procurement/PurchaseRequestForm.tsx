import React from 'react';

const PurchaseRequestForm: React.FC = () => {
  return (
    <div className="purchase-request-form">
      <h3>فرم درخواست خرید</h3>
      <form>
        <div className="form-group">
          <label>عنوان درخواست:</label>
          <input type="text" required />
        </div>
        
        <div className="form-group">
          <label>دسته‌بندی:</label>
          <select required>
            <option value="">انتخاب کنید</option>
            <option value="equipment">تجهیزات</option>
            <option value="materials">مواد اولیه</option>
            <option value="services">خدمات</option>
            <option value="office">لوازم اداری</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>تأمین‌کننده پیشنهادی:</label>
          <input type="text" />
        </div>
        
        <div className="form-group">
          <label>مبلغ تقریبی:</label>
          <input type="number" required />
        </div>
        
        <div className="form-group">
          <label>تاریخ مورد نیاز:</label>
          <input type="date" required />
        </div>
        
        <div className="form-group">
          <label>اولویت:</label>
          <select required>
            <option value="">انتخاب کنید</option>
            <option value="low">کم</option>
            <option value="medium">متوسط</option>
            <option value="high">زیاد</option>
            <option value="urgent">فوری</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>توضیحات:</label>
          <textarea rows={4} required></textarea>
        </div>
        
        <div className="form-group">
          <label>فایل‌های پیوست:</label>
          <input type="file" multiple />
        </div>
        
        <button type="submit">ارسال درخواست</button>
      </form>
    </div>
  );
};

export default PurchaseRequestForm; 