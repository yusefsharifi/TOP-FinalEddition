import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AIAnalyticsPage } from '../app/pages/ai/AIAnalyticsPage';

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('AIAnalyticsPage', () => {
  it('renders page title', () => {
    render(<AIAnalyticsPage />, { wrapper: Wrapper });
    expect(screen.getByText(/تحلیل‌های هوشمند/)).toBeInTheDocument();
  });

  it('renders tab navigation', () => {
    render(<AIAnalyticsPage />, { wrapper: Wrapper });
    expect(screen.getByText(/نمای کلی/)).toBeInTheDocument();
  });
});
