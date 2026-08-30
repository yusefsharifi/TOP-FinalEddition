import React from 'react';
import { Outlet } from 'react-router-dom';

export const AuthLayout: React.FC = () => {
  return (
    <div style={{ maxWidth: 480, margin: '64px auto 0', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Outlet />
    </div>
  );
};
