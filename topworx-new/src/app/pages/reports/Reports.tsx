import React from 'react';
import ReportsDashboard from '../../components/reports/ReportsDashboard';
import ReportBuilder from '../../components/reports/ReportBuilder';
import ScheduledReports from '../../components/reports/ScheduledReports';
import ReportAnalytics from '../../components/reports/ReportAnalytics';

const Reports: React.FC = () => {
  return (
    <div className="reports-page">
      <h1>ماژول گزارشات</h1>
      <p>در این بخش می‌توانید گزارشات مختلف از تمام بخش‌های سیستم را مشاهده و تولید کنید.</p>
      
      {/* داشبورد گزارشات */}
      <ReportsDashboard />
      
      {/* سازنده گزارش */}
      <ReportBuilder />
      
      {/* گزارشات زمان‌بندی شده */}
      <ScheduledReports />
      
      {/* تحلیل گزارشات */}
      <ReportAnalytics />
    </div>
  );
};

export default Reports; 