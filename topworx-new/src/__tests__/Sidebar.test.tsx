import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Sidebar } from '../app/components/Sidebar';

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('Sidebar', () => {
  it('renders menu items', () => {
    render(<Sidebar />, { wrapper: Wrapper });
    expect(screen.getByText(/داشبورد/)).toBeInTheDocument();
  });

  it('renders finance menu', () => {
    render(<Sidebar />, { wrapper: Wrapper });
    expect(screen.getByText(/مالی/)).toBeInTheDocument();
  });

  it('renders HR menu', () => {
    render(<Sidebar />, { wrapper: Wrapper });
    expect(screen.getByText(/منابع انسانی/)).toBeInTheDocument();
  });

  it('renders inventory menu', () => {
    render(<Sidebar />, { wrapper: Wrapper });
    expect(screen.getByText(/انبارداری/)).toBeInTheDocument();
  });

  it('renders AI menu', () => {
    render(<Sidebar />, { wrapper: Wrapper });
    expect(screen.getByText(/هوش مصنوعی/)).toBeInTheDocument();
  });

  it('renders settings menu', () => {
    render(<Sidebar />, { wrapper: Wrapper });
    expect(screen.getByText(/تنظیمات/)).toBeInTheDocument();
  });
});
