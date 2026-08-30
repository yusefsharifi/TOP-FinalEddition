import React, { useState } from 'react';

interface ChartData {
  id: string;
  type: 'line' | 'bar' | 'pie' | 'heatmap';
  title: string;
  data: any[];
  config: any;
}

const InteractiveDashboard: React.FC = () => {
  const [selectedChart, setSelectedChart] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('month');

  const charts: ChartData[] = [
    {
      id: '1',
      type: 'line',
      title: 'روند فروش ماهانه',
      data: [
        { month: 'دی', sales: 1200000, target: 1000000 },
        { month: 'بهمن', sales: 1500000, target: 1200000 },
        { month: 'اسفند', sales: 1800000, target: 1400000 },
        { month: 'فروردین', sales: 2000000, target: 1600000 }
      ],
      config: { xAxis: 'month', yAxis: 'sales', target: 'target' }
    },
    {
      id: '2',
      type: 'bar',
      title: 'فروش بر اساس محصول',
      data: [
        { product: 'محصول A', sales: 500000, units: 100 },
        { product: 'محصول B', sales: 800000, units: 150 },
        { product: 'محصول C', sales: 300000, units: 50 },
        { product: 'محصول D', sales: 600000, units: 120 }
      ],
      config: { xAxis: 'product', yAxis: 'sales' }
    },
    {
      id: '3',
      type: 'pie',
      title: 'توزیع مشتریان بر اساس منطقه',
      data: [
        { region: 'تهران', customers: 45, revenue: 1200000 },
        { region: 'اصفهان', customers: 25, revenue: 800000 },
        { region: 'مشهد', customers: 20, revenue: 600000 },
        { region: 'سایر', customers: 10, revenue: 300000 }
      ],
      config: { value: 'customers', label: 'region' }
    },
    {
      id: '4',
      type: 'heatmap',
      title: 'فعالیت‌های روزانه',
      data: [
        { day: 'شنبه', hour: '9', activity: 85 },
        { day: 'شنبه', hour: '10', activity: 92 },
        { day: 'شنبه', hour: '11', activity: 78 },
        { day: 'یکشنبه', hour: '9', activity: 88 },
        { day: 'یکشنبه', hour: '10', activity: 95 },
        { day: 'یکشنبه', hour: '11', activity: 82 }
      ],
      config: { xAxis: 'hour', yAxis: 'day', value: 'activity' }
    }
  ];

  const renderChart = (chart: ChartData) => {
    switch (chart.type) {
      case 'line':
        return (
          <div className="chart-container line-chart">
            <h4>{chart.title}</h4>
            <div className="chart-placeholder">
              <p>نمودار خطی تعاملی</p>
              <div className="chart-data">
                {chart.data.map((item, index) => (
                  <div key={index} className="data-point">
                    <span>{item.month}: {item.sales.toLocaleString()} تومان</span>
                    <div className="target-line">هدف: {item.target.toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      
      case 'bar':
        return (
          <div className="chart-container bar-chart">
            <h4>{chart.title}</h4>
            <div className="chart-placeholder">
              <p>نمودار ستونی تعاملی</p>
              <div className="chart-data">
                {chart.data.map((item, index) => (
                  <div key={index} className="data-point">
                    <span>{item.product}: {item.sales.toLocaleString()} تومان</span>
                    <div className="units">تعداد: {item.units}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      
      case 'pie':
        return (
          <div className="chart-container pie-chart">
            <h4>{chart.title}</h4>
            <div className="chart-placeholder">
              <p>نمودار دایره‌ای تعاملی</p>
              <div className="chart-data">
                {chart.data.map((item, index) => (
                  <div key={index} className="data-point">
                    <span>{item.region}: {item.customers}%</span>
                    <div className="revenue">درآمد: {item.revenue.toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      
      case 'heatmap':
        return (
          <div className="chart-container heatmap-chart">
            <h4>{chart.title}</h4>
            <div className="chart-placeholder">
              <p>نمودار حرارتی تعاملی</p>
              <div className="heatmap-grid">
                {chart.data.map((item, index) => (
                  <div 
                    key={index} 
                    className="heatmap-cell"
                    style={{ 
                      backgroundColor: `rgba(25, 118, 210, ${item.activity / 100})`,
                      color: item.activity > 50 ? 'white' : 'black'
                    }}
                  >
                    {item.activity}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      
      default:
        return <div>نوع نمودار پشتیبانی نمی‌شود</div>;
    }
  };

  return (
    <div className="interactive-dashboard">
      <h2>داشبورد تعاملی BI</h2>
      
      {/* کنترل‌های داشبورد */}
      <div className="dashboard-controls">
        <div className="control-group">
          <label>بازه زمانی:</label>
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="select"
          >
            <option value="week">هفته</option>
            <option value="month">ماه</option>
            <option value="quarter">فصل</option>
            <option value="year">سال</option>
          </select>
        </div>
        
        <div className="control-group">
          <button className="button">بروزرسانی داده‌ها</button>
          <button className="button secondary">صادر کردن گزارش</button>
        </div>
      </div>
      
      {/* نمودارها */}
      <div className="charts-grid">
        {charts.map(chart => (
          <div 
            key={chart.id} 
            className={`chart-card ${selectedChart === chart.id ? 'selected' : ''}`}
            onClick={() => setSelectedChart(chart.id)}
          >
            {renderChart(chart)}
          </div>
        ))}
      </div>
      
      {/* جزئیات نمودار انتخاب شده */}
      {selectedChart && (
        <div className="chart-details">
          <h3>جزئیات نمودار</h3>
          {(() => {
            const chart = charts.find(c => c.id === selectedChart);
            if (!chart) return null;
            
            return (
              <div className="details-content">
                <div className="detail-item">
                  <strong>عنوان:</strong> {chart.title}
                </div>
                <div className="detail-item">
                  <strong>نوع:</strong> {chart.type === 'line' ? 'خطی' : chart.type === 'bar' ? 'ستونی' : chart.type === 'pie' ? 'دایره‌ای' : 'حرارتی'}
                </div>
                <div className="detail-item">
                  <strong>تعداد نقاط داده:</strong> {chart.data.length}
                </div>
                <div className="detail-actions">
                  <button className="button">ویرایش نمودار</button>
                  <button className="button secondary">صادر کردن</button>
                  <button className="button secondary">اشتراک‌گذاری</button>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};

export default InteractiveDashboard; 