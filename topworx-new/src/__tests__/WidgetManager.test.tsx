import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { WidgetManager } from '../app/components/dashboard/WidgetManager';

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('WidgetManager', () => {
  it('renders without crashing', () => {
    render(<WidgetManager />, { wrapper: Wrapper });
  });

  it('renders add widget button', () => {
    render(<WidgetManager />, { wrapper: Wrapper });
    expect(screen.getByText(/افزودن ویجت/)).toBeInTheDocument();
  });
});
