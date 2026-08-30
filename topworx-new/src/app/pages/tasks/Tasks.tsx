import React from 'react';
import TasksDashboard from '../../components/tasks/TasksDashboard';
import TaskManager from '../../components/tasks/TaskManager';
import ProjectManager from '../../components/tasks/ProjectManager';

const Tasks: React.FC = () => {
  return (
    <div className="tasks-page">
      <h1>ماژول وظایف</h1>
      <p>در این بخش می‌توانید وظایف و پروژه‌ها را مدیریت کنید.</p>
      
      {/* داشبورد وظایف */}
      <TasksDashboard />
      
      {/* مدیریت وظایف */}
      <TaskManager />
      
      {/* مدیریت پروژه‌ها */}
      <ProjectManager />
    </div>
  );
};

export default Tasks; 