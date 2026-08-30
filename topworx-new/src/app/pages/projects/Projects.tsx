import React from 'react';
import ProjectDashboard from '../../components/projects/ProjectDashboard';
import GanttChart from '../../components/projects/GanttChart';
import ResourceManager from '../../components/projects/ResourceManager';

const Projects: React.FC = () => {
  return (
    <div className="projects-page">
      <h1>ماژول مدیریت پروژه</h1>
      <p>در این بخش می‌توانید پروژه‌ها، تیم‌ها و منابع را مدیریت کنید.</p>
      
      {/* داشبورد پروژه‌ها */}
      <ProjectDashboard />
      
      {/* نمودار گانت */}
      <GanttChart />
      
      {/* مدیریت منابع */}
      <ResourceManager />
    </div>
  );
};

export default Projects; 