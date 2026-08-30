// src/app/components/common/PrivateRoute.tsx
// ============================================================================
// PrivateRoute — Protects routes requiring authentication.
// Validates JWT existence and expiry before allowing access.
// ============================================================================

import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

/**
 * Decode a JWT payload without verifying the signature.
 */
function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
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
  if (!payload || typeof payload.exp !== "number") return true;
  const now = Math.floor(Date.now() / 1000);
  return payload.exp < now + bufferSeconds;
}

/**
 * Check if the user has valid authentication.
 * Returns true if either:
 * - Access token exists and is not expired, OR
 * - Refresh token exists and is not expired (AuthProvider will refresh)
 */
function isAuthenticated(): boolean {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

  // Valid access token → authenticated
  if (accessToken && !isTokenExpired(accessToken)) {
    return true;
  }

  // Expired access token but valid refresh token → AuthProvider will handle refresh
  if (refreshToken && !isTokenExpired(refreshToken)) {
    return true;
  }

  // No valid tokens → not authenticated
  return false;
}

export const PrivateRoute: React.FC = () => {
  const location = useLocation();

  if (!isAuthenticated()) {
    // Save current path for redirect after successful login
    return (
      <Navigate
        to="/login"
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // Render children (Outlet = nested routes)
  return <Outlet />;
};
