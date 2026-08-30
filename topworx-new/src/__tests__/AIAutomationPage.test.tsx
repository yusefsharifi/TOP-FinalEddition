import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AIAutomationPage } from '../app/pages/ai/AIAutomationPage';

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('AIAutomationPage', () => {
  it('renders page title', () => {
    render(<AIAutomationPage />, { wrapper: Wrapper });
    expect(screen.getByText(/اتوماسیون هوشمند/)).toBeInTheDocument();
  });

  it('renders automation stats section', () => {
    render(<AIAutomationPage />, { wrapper: Wrapper });
    expect(screen.getByText(/وضعیت اتوماسیون/)).toBeInTheDocument();
  });
});
