// src/core/auth/authService.ts
import { axiosInstance } from '../api/axiosInstance';
import { AxiosError } from 'axios';

// ── Types ──────────────────────────────────────────────────────────────────

export interface LoginResponse {
  access_token: string;
  refresh_token: string;   // اضافه‌شده از نسخه جدید
  token_type: string;
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
  };
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

// ── Service ────────────────────────────────────────────────────────────────

export const authService = {
  async login(credentials: { username: string; password: string }): Promise<LoginResponse> {
    // Send as form-urlencoded (FastAPI OAuth2 form data)
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    const response = await axiosInstance.post<LoginResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  async getCurrentUser() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No token found');
    }
    const response = await axiosInstance.get('/users/me');
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await axiosInstance.post('/auth/logout');
    } catch {
      // Ignore logout API errors — clear tokens locally regardless
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  async refreshAccessToken(refreshToken: string): Promise<{ access_token: string; refresh_token: string }> {
    const response = await axiosInstance.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  // ── Password Recovery ────────────────────────────────────────────────────

  async forgotPassword(data: ForgotPasswordRequest): Promise<{ message: string }> {
    const response = await axiosInstance.post('/auth/password-recovery', data);
    return response.data;
  },

  async resetPassword(data: ResetPasswordRequest): Promise<{ message: string }> {
    const response = await axiosInstance.post('/auth/reset-password', data);
    return response.data;
  },
};
