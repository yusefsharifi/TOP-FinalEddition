import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChartWidget } from '../app/components/dashboard/ChartWidget';

const mockData = [
  { name: 'فروردین', value: 100 },
  { name: 'اردیبهشت', value: 200 },
  { name: 'خرداد', value: 150 },
];

describe('ChartWidget', () => {
  it('renders title', () => {
    render(<ChartWidget title="نمودار فروش" data={mockData} type="bar" />);
    expect(screen.getByText('نمودار فروش')).toBeInTheDocument();
  });

  it('renders line chart', () => {
    const { container } = render(<ChartWidget title="test" data={mockData} type="line" />);
    expect(container).toBeTruthy();
  });

  it('renders bar chart', () => {
    const { container } = render(<ChartWidget title="test" data={mockData} type="bar" />);
    expect(container).toBeTruthy();
  });

  it('renders pie chart', () => {
    const { container } = render(<ChartWidget title="test" data={mockData} type="pie" />);
    expect(container).toBeTruthy();
  });

  it('renders with custom dataKey', () => {
    const data = [{ name: 'A', count: 50 }];
    render(<ChartWidget title="test" data={data} type="bar" dataKey="count" />);
    expect(screen.getByText('test')).toBeInTheDocument();
  });
});
