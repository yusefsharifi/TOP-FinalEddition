// src/app/components/auth/PrivateRoute.tsx
import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(decodeURIComponent(atob(base64).split("").map(c => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2)).join("")));
  } catch { return null; }
}

function isTokenExpired(token: string): boolean {
  const payload = decodeJwtPayload(token);
  if (!payload || typeof payload.exp !== "number") return true;
  return payload.exp < Math.floor(Date.now() / 1000) + 30;
}

function isAuthenticated(): boolean {
  const at = localStorage.getItem("access_token");
  const rt = localStorage.getItem("refresh_token");
  if (at && !isTokenExpired(at)) return true;
  if (rt && !isTokenExpired(rt)) return true;
  return false;
}

const PrivateRoute: React.FC = () => {
  const location = useLocation();
  if (!isAuthenticated()) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <Outlet />;
};

export default PrivateRoute;
