import React from 'react';
import AIDashboard from '../../components/ai/AIDashboard';
import DataMonitoring from '../../components/ai/DataMonitoring';
import PredictiveAnalytics from '../../components/ai/PredictiveAnalytics';

const AI: React.FC = () => {
  return (
    <div className="ai-page">
      <h1>ماژول هوش مصنوعی</h1>
      <p>در این بخش می‌توانید از قابلیت‌های هوش مصنوعی برای نظارت بر فرآیندها و ورود اطلاعات استفاده کنید.</p>
      
      {/* داشبورد هوش مصنوعی */}
      <AIDashboard />
      
      {/* نظارت بر داده‌ها */}
      <DataMonitoring />
      
      {/* تحلیل پیش‌بینی‌کننده */}
      <PredictiveAnalytics />
    </div>
  );
};

export default AI; 