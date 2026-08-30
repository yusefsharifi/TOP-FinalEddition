import React from 'react';

const LetterComposer: React.FC = () => {
  return (
    <div className="letter-composer">
      <h3>نویسنده نامه</h3>
      <form>
        <div className="form-group">
          <label>نوع نامه:</label>
          <select required>
            <option value="">انتخاب کنید</option>
            <option value="official">نامه رسمی</option>
            <option value="internal">نامه داخلی</option>
            <option value="contract">نامه قراردادی</option>
            <option value="complaint">نامه شکایت</option>
            <option value="request">نامه درخواست</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>قالب نامه:</label>
          <select>
            <option value="">انتخاب قالب</option>
            <option value="template1">قالب رسمی شرکت</option>
            <option value="template2">قالب قراردادی</option>
            <option value="template3">قالب درخواست</option>
            <option value="template4">قالب شکایت</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>گیرنده:</label>
          <input type="text" placeholder="نام گیرنده یا سازمان" required />
        </div>
        
        <div className="form-group">
          <label>موضوع:</label>
          <input type="text" placeholder="موضوع نامه" required />
        </div>
        
        <div className="form-group">
          <label>متن نامه:</label>
          <textarea rows={10} placeholder="متن نامه را اینجا بنویسید..." required></textarea>
        </div>
        
        <div className="form-group">
          <label>اولویت:</label>
          <select required>
            <option value="">انتخاب کنید</option>
            <option value="normal">عادی</option>
            <option value="important">مهم</option>
            <option value="urgent">فوری</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>فایل‌های پیوست:</label>
          <input type="file" multiple />
        </div>
        
        <div className="form-group">
          <label>تاریخ ارسال:</label>
          <input type="date" required />
        </div>
        
        <div className="form-actions">
          <button type="button">پیش‌نمایش</button>
          <button type="button">ذخیره پیش‌نویس</button>
          <button type="submit">ارسال نامه</button>
        </div>
      </form>
    </div>
  );
};

export default LetterComposer; 