import React, { useState } from 'react';

interface Task {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  progress: number;
  dependencies: string[];
  assignee: string;
}

const GanttChart: React.FC = () => {
  const [selectedTask, setSelectedTask] = useState<string | null>(null);

  const tasks: Task[] = [
    {
      id: '1',
      name: 'تحلیل نیازمندی‌ها',
      startDate: '2024-01-01',
      endDate: '2024-01-15',
      progress: 100,
      dependencies: [],
      assignee: 'علی احمدی'
    },
    {
      id: '2',
      name: 'طراحی سیستم',
      startDate: '2024-01-10',
      endDate: '2024-02-01',
      progress: 80,
      dependencies: ['1'],
      assignee: 'فاطمه کریمی'
    },
    {
      id: '3',
      name: 'توسعه فرانت‌اند',
      startDate: '2024-01-20',
      endDate: '2024-03-01',
      progress: 60,
      dependencies: ['2'],
      assignee: 'محمد رضایی'
    },
    {
      id: '4',
      name: 'توسعه بک‌اند',
      startDate: '2024-01-20',
      endDate: '2024-03-15',
      progress: 45,
      dependencies: ['2'],
      assignee: 'سارا محمدی'
    },
    {
      id: '5',
      name: 'تست و دیباگ',
      startDate: '2024-02-15',
      endDate: '2024-04-01',
      progress: 20,
      dependencies: ['3', '4'],
      assignee: 'حسن نوری'
    }
  ];

  const getTaskPosition = (task: Task) => {
    const start = new Date(task.startDate);
    const end = new Date(task.endDate);
    const projectStart = new Date('2024-01-01');
    
    const left = ((start.getTime() - projectStart.getTime()) / (1000 * 60 * 60 * 24)) * 20;
    const width = ((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) * 20;
    
    return { left: `${left}px`, width: `${width}px` };
  };

  return (
    <div className="gantt-chart">
      <h3>نمودار گانت</h3>
      
      <div className="gantt-container">
        <div className="gantt-header">
          <div className="task-header">وظیفه</div>
          <div className="timeline-header">
            <div className="timeline-months">
              <span>دی</span>
              <span>بهمن</span>
              <span>اسفند</span>
              <span>فروردین</span>
            </div>
          </div>
        </div>
        
        <div className="gantt-body">
          {tasks.map((task, index) => {
            const position = getTaskPosition(task);
            return (
              <div key={task.id} className="gantt-row">
                <div className="task-info">
                  <div className="task-name">{task.name}</div>
                  <div className="task-assignee">{task.assignee}</div>
                </div>
                
                <div className="timeline-area">
                  <div 
                    className={`task-bar ${selectedTask === task.id ? 'selected' : ''}`}
                    style={{
                      left: position.left,
                      width: position.width
                    }}
                    onClick={() => setSelectedTask(task.id)}
                  >
                    <div 
                      className="task-progress"
                      style={{ width: `${task.progress}%` }}
                    ></div>
                    <div className="task-label">{task.progress}%</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      {selectedTask && (
        <div className="task-details">
          <h4>جزئیات وظیفه</h4>
          <div className="detail-item">
            <strong>نام:</strong> {tasks.find(t => t.id === selectedTask)?.name}
          </div>
          <div className="detail-item">
            <strong>تکلیف:</strong> {tasks.find(t => t.id === selectedTask)?.assignee}
          </div>
          <div className="detail-item">
            <strong>پیشرفت:</strong> {tasks.find(t => t.id === selectedTask)?.progress}%
          </div>
          <div className="detail-item">
            <strong>تاریخ شروع:</strong> {tasks.find(t => t.id === selectedTask)?.startDate}
          </div>
          <div className="detail-item">
            <strong>تاریخ پایان:</strong> {tasks.find(t => t.id === selectedTask)?.endDate}
          </div>
        </div>
      )}
    </div>
  );
};

export default GanttChart; 