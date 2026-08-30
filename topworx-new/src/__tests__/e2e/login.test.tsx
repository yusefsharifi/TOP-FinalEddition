/**
 * Login E2E Test
 * TOP WorX ERP System
 * 
 * Tests the login flow including:
 * - Page rendering
 * - Form submission
 * - Error handling
 * - Navigation after login
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import Login from '../../pages/Login';

// Mock the useAuth hook
jest.mock('../../core/auth/AuthProvider', () => ({
  useAuth: () => ({
    login: jest.fn(),
    isAuthenticated: false,
    user: null,
  }),
}));

// Mock react-i18next
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

const renderLogin = () => {
  return render(
    <BrowserRouter>
      <ConfigProvider>
        <Login />
      </ConfigProvider>
    </BrowserRouter>
  );
};

describe('Login Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders login form correctly', () => {
    renderLogin();
    
    expect(screen.getByText('TopWorx ERP')).toBeInTheDocument();
    expect(screen.getByText('login.title')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('login.username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('login.password')).toBeInTheDocument();
  });

  it('displays error when submitting empty form', async () => {
    renderLogin();
    
    const submitButton = screen.getByRole('button', { name: /login\.signIn/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('login.invalidCredentials')).toBeInTheDocument();
    });
  });

  it('displays error when login fails', async () => {
    const mockLogin = jest.fn().mockRejectedValue(new Error('Invalid credentials'));
    jest.spyOn(require('../../core/auth/AuthProvider'), 'useAuth').mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      user: null,
    });
    
    renderLogin();
    
    const usernameInput = screen.getByPlaceholderText('login.username');
    const passwordInput = screen.getByPlaceholderText('login.password');
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    
    const submitButton = screen.getByRole('button', { name: /login\.signIn/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('login.loginFailed')).toBeInTheDocument();
    });
  });

  it('toggles password visibility', () => {
    renderLogin();
    
    const passwordInput = screen.getByPlaceholderText('login.password');
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    const toggleButton = screen.getByRole('button', { name: /toggle password/i });
    fireEvent.click(toggleButton);
    
    expect(passwordInput).toHaveAttribute('type', 'text');
  });

  it('handles remember me checkbox', () => {
    renderLogin();
    
    const rememberMeCheckbox = screen.getByRole('checkbox');
    expect(rememberMeCheckbox).not.toBeChecked();
    
    fireEvent.click(rememberMeCheckbox);
    expect(rememberMeCheckbox).toBeChecked();
  });

  it('displays loading state during submission', async () => {
    const mockLogin = jest.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    );
    jest.spyOn(require('../../core/auth/AuthProvider'), 'useAuth').mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      user: null,
    });
    
    renderLogin();
    
    const usernameInput = screen.getByPlaceholderText('login.username');
    const passwordInput = screen.getByPlaceholderText('login.password');
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    const submitButton = screen.getByRole('button', { name: /login\.signIn/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });
});
