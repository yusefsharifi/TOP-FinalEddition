import React, { useState } from 'react';

interface DrillDownLevel {
  id: string;
  name: string;
  level: 'region' | 'city' | 'store' | 'product' | 'category';
  data: any[];
  parentId?: string;
}

const DrillDownAnalytics: React.FC = () => {
  const [currentLevel, setCurrentLevel] = useState<string>('region');
  const [drillPath, setDrillPath] = useState<string[]>(['فروش کلی']);
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  const drillDownData: Record<string, DrillDownLevel> = {
    region: {
      id: 'region',
      name: 'منطقه',
      level: 'region',
      data: [
        { id: 'tehran', name: 'تهران', sales: 2500000, customers: 150, growth: 12 },
        { id: 'isfahan', name: 'اصفهان', sales: 1800000, customers: 95, growth: 8 },
        { id: 'mashhad', name: 'مشهد', sales: 1200000, customers: 75, growth: 15 },
        { id: 'shiraz', name: 'شیراز', sales: 900000, customers: 60, growth: 5 }
      ]
    },
    city: {
      id: 'city',
      name: 'شهر',
      level: 'city',
      data: [
        { id: 'tehran-central', name: 'تهران مرکزی', sales: 800000, customers: 45, growth: 10 },
        { id: 'tehran-north', name: 'تهران شمالی', sales: 600000, customers: 35, growth: 8 },
        { id: 'tehran-south', name: 'تهران جنوبی', sales: 400000, customers: 25, growth: 6 },
        { id: 'isfahan-central', name: 'اصفهان مرکزی', sales: 700000, customers: 40, growth: 12 },
        { id: 'mashhad-central', name: 'مشهد مرکزی', sales: 500000, customers: 30, growth: 18 }
      ]
    },
    store: {
      id: 'store',
      name: 'فروشگاه',
      level: 'store',
      data: [
        { id: 'store-1', name: 'فروشگاه مرکزی تهران', sales: 300000, customers: 20, growth: 15 },
        { id: 'store-2', name: 'فروشگاه شمال تهران', sales: 250000, customers: 18, growth: 12 },
        { id: 'store-3', name: 'فروشگاه اصفهان', sales: 200000, customers: 15, growth: 10 },
        { id: 'store-4', name: 'فروشگاه مشهد', sales: 180000, customers: 12, growth: 20 }
      ]
    },
    product: {
      id: 'product',
      name: 'محصول',
      level: 'product',
      data: [
        { id: 'prod-1', name: 'لپ‌تاپ', sales: 500000, units: 25, growth: 25 },
        { id: 'prod-2', name: 'موبایل', sales: 400000, units: 40, growth: 18 },
        { id: 'prod-3', name: 'تبلت', sales: 300000, units: 30, growth: 12 },
        { id: 'prod-4', name: 'لوازم جانبی', sales: 200000, units: 100, growth: 8 }
      ]
    }
  };

  const handleDrillDown = (itemId: string, itemName: string) => {
    setSelectedItem(itemId);
    setDrillPath([...drillPath, itemName]);
    
    // Determine next level
    const currentData = drillDownData[currentLevel];
    if (currentData) {
      const nextLevels: Record<string, string> = {
        'region': 'city',
        'city': 'store',
        'store': 'product',
        'product': 'category'
      };
      
      const nextLevel = nextLevels[currentLevel];
      if (nextLevel && drillDownData[nextLevel]) {
        setCurrentLevel(nextLevel);
      }
    }
  };

  const handleDrillUp = () => {
    if (drillPath.length > 1) {
      const newPath = drillPath.slice(0, -1);
      setDrillPath(newPath);
      
      const previousLevels: Record<string, string> = {
        'city': 'region',
        'store': 'city',
        'product': 'store',
        'category': 'product'
      };
      
      const previousLevel = previousLevels[currentLevel];
      if (previousLevel) {
        setCurrentLevel(previousLevel);
      }
    }
  };

  const currentData = drillDownData[currentLevel];

  return (
    <div className="drill-down-analytics">
      <h3>تحلیل عمیق داده‌ها (Drill-down)</h3>
      
      {/* مسیر Drill-down */}
      <div className="drill-path">
        <h4>مسیر تحلیل:</h4>
        <div className="path-breadcrumb">
          {drillPath.map((path, index) => (
            <React.Fragment key={index}>
              <span 
                className={`path-item ${index === drillPath.length - 1 ? 'active' : ''}`}
                onClick={() => {
                  if (index < drillPath.length - 1) {
                    setDrillPath(drillPath.slice(0, index + 1));
                  }
                }}
              >
                {path}
              </span>
              {index < drillPath.length - 1 && <span className="path-separator">→</span>}
            </React.Fragment>
          ))}
        </div>
        
        {drillPath.length > 1 && (
          <button onClick={handleDrillUp} className="button secondary">
            بازگشت به سطح بالاتر
          </button>
        )}
      </div>
      
      {/* داده‌های سطح فعلی */}
      {currentData && (
        <div className="drill-data">
          <h4>تحلیل {currentData.name}</h4>
          
          <div className="data-table">
            <table>
              <thead>
                <tr>
                  <th>نام</th>
                  <th>فروش (تومان)</th>
                  <th>مشتریان</th>
                  <th>رشد (%)</th>
                  <th>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {currentData.data.map(item => (
                  <tr 
                    key={item.id}
                    className={selectedItem === item.id ? 'selected' : ''}
                  >
                    <td>{item.name}</td>
                    <td>{item.sales.toLocaleString()}</td>
                    <td>{item.customers || item.units || '-'}</td>
                    <td>
                      <span className={`growth ${item.growth >= 0 ? 'positive' : 'negative'}`}>
                        {item.growth >= 0 ? '+' : ''}{item.growth}%
                      </span>
                    </td>
                    <td>
                      <button 
                        onClick={() => handleDrillDown(item.id, item.name)}
                        className="button"
                        disabled={currentLevel === 'product'}
                      >
                        تحلیل عمیق
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* خلاصه آماری */}
      {currentData && (
        <div className="drill-summary">
          <h4>خلاصه آماری</h4>
          <div className="summary-stats">
            <div className="stat-item">
              <strong>کل فروش:</strong>
              <span>{currentData.data.reduce((sum, item) => sum + item.sales, 0).toLocaleString()} تومان</span>
            </div>
            <div className="stat-item">
              <strong>میانگین رشد:</strong>
              <span>{Math.round(currentData.data.reduce((sum, item) => sum + item.growth, 0) / currentData.data.length)}%</span>
            </div>
            <div className="stat-item">
              <strong>تعداد آیتم‌ها:</strong>
              <span>{currentData.data.length}</span>
            </div>
          </div>
        </div>
      )}
      
      {/* نمودار خلاصه */}
      <div className="drill-chart">
        <h4>نمودار خلاصه</h4>
        <div className="chart-placeholder">
          <p>نمودار تعاملی برای نمایش روند و مقایسه</p>
          <div className="chart-legend">
            {currentData?.data.map(item => (
              <div key={item.id} className="legend-item">
                <span className="legend-color"></span>
                <span>{item.name}: {item.sales.toLocaleString()} تومان</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DrillDownAnalytics; 