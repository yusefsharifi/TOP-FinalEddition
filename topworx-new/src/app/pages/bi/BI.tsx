import React from 'react';
import InteractiveDashboard from '../../components/bi/InteractiveDashboard';
import DrillDownAnalytics from '../../components/bi/DrillDownAnalytics';

const BI: React.FC = () => {
  return (
    <div className="bi-page">
      <h1>ماژول هوش تجاری (BI)</h1>
      <p>در این بخش می‌توانید از ابزارهای تحلیلی پیشرفته برای تصمیم‌گیری استفاده کنید.</p>
      
      {/* داشبورد تعاملی */}
      <InteractiveDashboard />
      
      {/* تحلیل عمیق داده‌ها */}
      <DrillDownAnalytics />
    </div>
  );
};

export default BI; 