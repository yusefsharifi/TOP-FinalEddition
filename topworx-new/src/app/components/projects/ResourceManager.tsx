import React, { useState } from 'react';

interface Resource {
  id: string;
  name: string;
  type: 'human' | 'equipment' | 'material';
  availability: number; // percentage
  skills: string[];
  currentProjects: string[];
  hourlyRate?: number;
}

const ResourceManager: React.FC = () => {
  const [selectedResource, setSelectedResource] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');

  const resources: Resource[] = [
    {
      id: '1',
      name: 'علی احمدی',
      type: 'human',
      availability: 80,
      skills: ['React', 'TypeScript', 'Node.js'],
      currentProjects: ['پروژه A', 'پروژه B'],
      hourlyRate: 150000
    },
    {
      id: '2',
      name: 'فاطمه کریمی',
      type: 'human',
      availability: 60,
      skills: ['UI/UX', 'Figma', 'Adobe XD'],
      currentProjects: ['پروژه A'],
      hourlyRate: 120000
    },
    {
      id: '3',
      name: 'سرور توسعه',
      type: 'equipment',
      availability: 100,
      skills: ['Linux', 'Docker', 'AWS'],
      currentProjects: ['پروژه A', 'پروژه B', 'پروژه C']
    },
    {
      id: '4',
      name: 'لپ‌تاپ توسعه',
      type: 'equipment',
      availability: 90,
      skills: ['Windows', 'VS Code', 'Git'],
      currentProjects: ['پروژه A']
    },
    {
      id: '5',
      name: 'کتابخانه‌های نرم‌افزاری',
      type: 'material',
      availability: 100,
      skills: ['React', 'Material-UI', 'Axios'],
      currentProjects: ['پروژه A', 'پروژه B']
    }
  ];

  const filteredResources = filterType === 'all' 
    ? resources 
    : resources.filter(r => r.type === filterType);

  const getResourceTypeIcon = (type: string) => {
    switch (type) {
      case 'human': return '👤';
      case 'equipment': return '💻';
      case 'material': return '📦';
      default: return '❓';
    }
  };

  const getAvailabilityColor = (availability: number) => {
    if (availability >= 80) return 'success';
    if (availability >= 60) return 'warning';
    return 'error';
  };

  return (
    <div className="resource-manager">
      <h3>مدیریت منابع</h3>
      
      {/* فیلترها */}
      <div className="resource-filters">
        <select 
          value={filterType} 
          onChange={(e) => setFilterType(e.target.value)}
          className="select"
        >
          <option value="all">همه منابع</option>
          <option value="human">انسانی</option>
          <option value="equipment">تجهیزات</option>
          <option value="material">مواد</option>
        </select>
      </div>
      
      {/* لیست منابع */}
      <div className="resource-list">
        {filteredResources.map(resource => (
          <div 
            key={resource.id} 
            className={`resource-item ${selectedResource === resource.id ? 'selected' : ''}`}
            onClick={() => setSelectedResource(resource.id)}
          >
            <div className="resource-header">
              <span className="resource-icon">{getResourceTypeIcon(resource.type)}</span>
              <h4>{resource.name}</h4>
              <span className={`availability ${getAvailabilityColor(resource.availability)}`}>
                {resource.availability}% در دسترس
              </span>
            </div>
            
            <div className="resource-details">
              <div className="resource-type">
                <strong>نوع:</strong> {resource.type === 'human' ? 'انسانی' : resource.type === 'equipment' ? 'تجهیزات' : 'مواد'}
              </div>
              
              {resource.skills.length > 0 && (
                <div className="resource-skills">
                  <strong>مهارت‌ها:</strong>
                  <div className="skills-tags">
                    {resource.skills.map(skill => (
                      <span key={skill} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                </div>
              )}
              
              {resource.currentProjects.length > 0 && (
                <div className="resource-projects">
                  <strong>پروژه‌های فعلی:</strong>
                  <div className="project-tags">
                    {resource.currentProjects.map(project => (
                      <span key={project} className="project-tag">{project}</span>
                    ))}
                  </div>
                </div>
              )}
              
              {resource.hourlyRate && (
                <div className="resource-rate">
                  <strong>نرخ ساعتی:</strong> {resource.hourlyRate.toLocaleString()} تومان
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* جزئیات منبع انتخاب شده */}
      {selectedResource && (
        <div className="resource-details-panel">
          <h4>جزئیات منبع</h4>
          {(() => {
            const resource = resources.find(r => r.id === selectedResource);
            if (!resource) return null;
            
            return (
              <div className="detail-panel">
                <div className="detail-row">
                  <strong>نام:</strong> {resource.name}
                </div>
                <div className="detail-row">
                  <strong>نوع:</strong> {resource.type === 'human' ? 'انسانی' : resource.type === 'equipment' ? 'تجهیزات' : 'مواد'}
                </div>
                <div className="detail-row">
                  <strong>در دسترس بودن:</strong> {resource.availability}%
                </div>
                {resource.skills.length > 0 && (
                  <div className="detail-row">
                    <strong>مهارت‌ها:</strong>
                    <div className="skills-list">
                      {resource.skills.map(skill => (
                        <span key={skill} className="skill-item">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}
                {resource.currentProjects.length > 0 && (
                  <div className="detail-row">
                    <strong>پروژه‌های فعلی:</strong>
                    <div className="projects-list">
                      {resource.currentProjects.map(project => (
                        <span key={project} className="project-item">{project}</span>
                      ))}
                    </div>
                  </div>
                )}
                {resource.hourlyRate && (
                  <div className="detail-row">
                    <strong>نرخ ساعتی:</strong> {resource.hourlyRate.toLocaleString()} تومان
                  </div>
                )}
                
                <div className="detail-actions">
                  <button className="button">ویرایش</button>
                  <button className="button secondary">تخصیص به پروژه</button>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};

export default ResourceManager; 