import React from 'react';
import CorrespondenceDashboard from '../../components/correspondence/CorrespondenceDashboard';
import LetterComposer from '../../components/correspondence/LetterComposer';
import WorkflowAutomation from '../../components/correspondence/WorkflowAutomation';

const Correspondence: React.FC = () => {
  return (
    <div className="correspondence-page">
      <h1>ماژول نامه‌نگاری و اتوماسیون</h1>
      <p>در این بخش می‌توانید نامه‌ها، مکاتبات و فرآیندهای اتوماسیون را مدیریت کنید.</p>
      
      {/* داشبورد نامه‌نگاری */}
      <CorrespondenceDashboard />
      
      {/* نویسنده نامه */}
      <LetterComposer />
      
      {/* اتوماسیون فرآیندها */}
      <WorkflowAutomation />
    </div>
  );
};

export default Correspondence; 