import React from 'react';
import { Outlet } from 'react-router-dom';
import { ThemeToggle, LoadingSpinner } from '../components/common';

const MainLayout: React.FC = () => {
  return (
    <div className="main-layout">
      <header className="main-header">
        <div className="header-content">
          <h1 className="app-title">TOP WorX</h1>
          <div className="header-actions">
            <ThemeToggle />
            {/* Add other header actions here */}
          </div>
        </div>
      </header>
      
      <div className="main-content">
        <nav className="sidebar">
          {/* Navigation menu will be here */}
        </nav>
        
        <main className="content-area">
          <React.Suspense fallback={<LoadingSpinner text="در حال بارگذاری..." />}>
        <Outlet />
          </React.Suspense>
        </main>
      </div>
    </div>
);
};

export default MainLayout;