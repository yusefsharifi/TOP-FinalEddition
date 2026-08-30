import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AIReportsPage } from '../app/pages/ai/AIReportsPage';

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('AIReportsPage', () => {
  it('renders page title', () => {
    render(<AIReportsPage />, { wrapper: Wrapper });
    expect(screen.getByText(/گزارشات هوشمند/)).toBeInTheDocument();
  });

  it('renders query input', () => {
    render(<AIReportsPage />, { wrapper: Wrapper });
    expect(screen.getByPlaceholderText(/سوال خود را بپرسید/)).toBeInTheDocument();
  });
});
