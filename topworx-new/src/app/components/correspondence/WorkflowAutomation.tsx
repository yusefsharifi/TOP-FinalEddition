import React from 'react';

const WorkflowAutomation: React.FC = () => {
  return (
    <div className="workflow-automation">
      <h3>اتوماسیون فرآیندها</h3>
      
      {/* فرآیندهای فعال */}
      <div className="active-workflows">
        <h4>فرآیندهای فعال</h4>
        <div className="workflow-list">
          <div className="workflow-item">
            <div className="workflow-header">
              <h5>فرآیند تأیید نامه‌ها</h5>
              <span className="status active">فعال</span>
            </div>
            <p>تأیید خودکار نامه‌های با مبلغ کمتر از 10 میلیون تومان</p>
            <div className="workflow-steps">
              <span>مرحله 1: بررسی مبلغ</span>
              <span>مرحله 2: تأیید خودکار</span>
              <span>مرحله 3: ارسال اعلان</span>
            </div>
            <div className="workflow-actions">
              <button>ویرایش</button>
              <button>غیرفعال‌سازی</button>
            </div>
          </div>
          
          <div className="workflow-item">
            <div className="workflow-header">
              <h5>فرآیند یادآوری</h5>
              <span className="status active">فعال</span>
            </div>
            <p>یادآوری خودکار برای نامه‌های در انتظار تأیید</p>
            <div className="workflow-steps">
              <span>مرحله 1: بررسی مهلت</span>
              <span>مرحله 2: ارسال یادآوری</span>
              <span>مرحله 3: ارتقا اولویت</span>
            </div>
            <div className="workflow-actions">
              <button>ویرایش</button>
              <button>غیرفعال‌سازی</button>
            </div>
          </div>
          
          <div className="workflow-item">
            <div className="workflow-header">
              <h5>فرآیند آرشیو</h5>
              <span className="status active">فعال</span>
            </div>
            <p>آرشیو خودکار نامه‌های قدیمی</p>
            <div className="workflow-steps">
              <span>مرحله 1: بررسی تاریخ</span>
              <span>مرحله 2: انتقال به آرشیو</span>
              <span>مرحله 3: فشرده‌سازی</span>
            </div>
            <div className="workflow-actions">
              <button>ویرایش</button>
              <button>غیرفعال‌سازی</button>
            </div>
          </div>
        </div>
      </div>
      
      {/* ایجاد فرآیند جدید */}
      <div className="create-workflow">
        <h4>ایجاد فرآیند جدید</h4>
        <form>
          <div className="form-group">
            <label>نام فرآیند:</label>
            <input type="text" placeholder="نام فرآیند" required />
          </div>
          
          <div className="form-group">
            <label>نوع فرآیند:</label>
            <select required>
              <option value="">انتخاب کنید</option>
              <option value="approval">تأیید</option>
              <option value="notification">اعلان</option>
              <option value="reminder">یادآوری</option>
              <option value="archive">آرشیو</option>
              <option value="custom">سفارشی</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>شرایط اجرا:</label>
            <textarea rows={3} placeholder="شرایط اجرای فرآیند"></textarea>
          </div>
          
          <div className="form-group">
            <label>عملیات:</label>
            <textarea rows={3} placeholder="عملیات‌های مورد نظر"></textarea>
          </div>
          
          <button type="submit">ایجاد فرآیند</button>
        </form>
      </div>
    </div>
  );
};

export default WorkflowAutomation; 