// src/core/auth/AuthProvider.tsx
// ============================================================================
// AuthProvider — JWT authentication context with token refresh support
// ============================================================================

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, LoginResponse } from './authService';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (credentials: { username: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ── Token helpers ────────────────────────────────────────────────────────────

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

/**
 * Decode a JWT payload without verifying the signature.
 * Returns null if the token is malformed.
 */
function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

/**
 * Check if a JWT is expired (or about to expire within 30 seconds).
 */
function isTokenExpired(token: string, bufferSeconds = 30): boolean {
  const payload = decodeJwtPayload(token);
  if (!payload || typeof payload.exp !== 'number') return true;
  const now = Math.floor(Date.now() / 1000);
  return payload.exp < now + bufferSeconds;
}

// ── Provider ────────────────────────────────────────────────────────────────

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // ── Initialize auth from stored tokens ──────────────────────────────────
  useEffect(() => {
    const initAuth = async () => {
      try {
        const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

        if (accessToken && !isTokenExpired(accessToken)) {
          // Access token is valid — try to get user profile
          const userData = await authService.getCurrentUser();
          setUser(userData);
        } else if (refreshToken && !isTokenExpired(refreshToken)) {
          // Access token expired but refresh token is valid — refresh
          try {
            const { access_token, refresh_token } = await authService.refreshAccessToken(refreshToken);
            localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
            localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
            const userData = await authService.getCurrentUser();
            setUser(userData);
          } catch {
            // Refresh failed — clear everything
            clearTokens();
          }
        } else {
          // Both tokens invalid — clear
          clearTokens();
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        clearTokens();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // ── Login ───────────────────────────────────────────────────────────────
  const login = useCallback(async (credentials: { username: string; password: string }) => {
    setLoading(true);
    try {
      const response = await authService.login(credentials);

      // Store both tokens
      localStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);

      setUser(response.user);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // ── Logout ──────────────────────────────────────────────────────────────
  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      clearTokens();
      setUser(null);
      setLoading(false);
      navigate('/login');
    }
  }, [navigate]);

  // ── Clear tokens helper ─────────────────────────────────────────────────
  const clearTokens = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
  };

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Loading...</div>;
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};