import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AIAssistantPage } from '../app/pages/ai/AIAssistantPage';

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('AIAssistantPage', () => {
  it('renders page title', () => {
    render(<AIAssistantPage />, { wrapper: Wrapper });
    expect(screen.getByText(/دستیار هوشمند/)).toBeInTheDocument();
  });

  it('renders chat input area', () => {
    render(<AIAssistantPage />, { wrapper: Wrapper });
    expect(screen.getByPlaceholderText(/پیام خود را بنویسید/)).toBeInTheDocument();
  });

  it('renders module selector', () => {
    render(<AIAssistantPage />, { wrapper: Wrapper });
    expect(screen.getByText(/ماژول/)).toBeInTheDocument();
  });
});
