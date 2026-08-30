import React from 'react';
import { render, screen } from '@testing-library/react';
import { KPIWidget } from '../app/components/dashboard/KPIWidget';

describe('KPIWidget', () => {
  it('renders title and value', () => {
    render(<KPIWidget title="فروش" value={1250000} />);
    expect(screen.getByText('فروش')).toBeInTheDocument();
    expect(screen.getByText('1,250,000')).toBeInTheDocument();
  });

  it('renders with string value', () => {
    render(<KPIWidget title="وضعیت" value="فعال" />);
    expect(screen.getByText('فعال')).toBeInTheDocument();
  });

  it('shows description when provided', () => {
    render(<KPIWidget title="فروش" value={100} description="توضیحات تست" />);
    expect(screen.getByText('توضیحات تست')).toBeInTheDocument();
  });

  it('renders with loading state', () => {
    const { container } = render(<KPIWidget title="فروش" value={0} loading={true} />);
    expect(container).toBeTruthy();
  });

  it('renders with custom color', () => {
    render(<KPIWidget title="فروش" value={100} color="#52c41a" />);
    expect(screen.getByText('فروش')).toBeInTheDocument();
  });
});
