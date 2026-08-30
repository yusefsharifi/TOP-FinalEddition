import React from 'react';

const DataMonitoring: React.FC = () => {
  return (
    <div className="data-monitoring">
      <h3>نظارت بر داده‌ها</h3>
      
      {/* هشدارهای هوشمند */}
      <div className="smart-alerts">
        <h4>هشدارهای هوشمند</h4>
        <div className="alert-list">
          <div className="alert-item critical">
            <h5>تشخیص فعالیت مشکوک</h5>
            <p>تراکنش مالی غیرعادی در حساب 123456</p>
            <span className="confidence">اطمینان: 95%</span>
            <span className="time">2 ساعت پیش</span>
            <div className="alert-actions">
              <button>بررسی</button>
              <button>نادیده گرفتن</button>
            </div>
          </div>
          
          <div className="alert-item warning">
            <h5>خطای ورود داده</h5>
            <p>مقدار غیرمعمول در فیلد "مبلغ" - پیشنهاد: 1,500,000 تومان</p>
            <span className="confidence">اطمینان: 87%</span>
            <span className="time">1 ساعت پیش</span>
            <div className="alert-actions">
              <button>تأیید</button>
              <button>اصلاح</button>
            </div>
          </div>
          
          <div className="alert-item info">
            <h5>الگوی جدید شناسایی شد</h5>
            <p>افزایش 25% در فروش محصول A در هفته گذشته</p>
            <span className="confidence">اطمینان: 92%</span>
            <span className="time">30 دقیقه پیش</span>
            <div className="alert-actions">
              <button>تحلیل</button>
              <button>گزارش</button>
            </div>
          </div>
        </div>
      </div>
      
      {/* کیفیت داده‌ها */}
      <div className="data-quality">
        <h4>کیفیت داده‌ها</h4>
        <div className="quality-metrics">
          <div className="metric-item">
            <h5>دقت داده‌ها</h5>
            <p className="percentage">98.5%</p>
            <div className="progress-bar">
              <div className="progress" style={{width: '98.5%'}}></div>
            </div>
          </div>
          
          <div className="metric-item">
            <h5>کامل بودن داده‌ها</h5>
            <p className="percentage">94.2%</p>
            <div className="progress-bar">
              <div className="progress" style={{width: '94.2%'}}></div>
            </div>
          </div>
          
          <div className="metric-item">
            <h5>سازگاری داده‌ها</h5>
            <p className="percentage">96.8%</p>
            <div className="progress-bar">
              <div className="progress" style={{width: '96.8%'}}></div>
            </div>
          </div>
        </div>
      </div>
      
      {/* تنظیمات نظارت */}
      <div className="monitoring-settings">
        <h4>تنظیمات نظارت</h4>
        <form>
          <div className="form-group">
            <label>آستانه هشدار:</label>
            <select>
              <option value="high">بالا (حساس)</option>
              <option value="medium" selected>متوسط</option>
              <option value="low">پایین</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>نوع نظارت:</label>
            <div className="checkbox-group">
              <label><input type="checkbox" checked /> نظارت بر تراکنش‌های مالی</label>
              <label><input type="checkbox" checked /> نظارت بر ورود داده‌ها</label>
              <label><input type="checkbox" checked /> نظارت بر الگوهای رفتاری</label>
              <label><input type="checkbox" /> نظارت بر عملکرد سیستم</label>
            </div>
          </div>
          
          <button type="submit">ذخیره تنظیمات</button>
        </form>
      </div>
    </div>
  );
};

export default DataMonitoring; 