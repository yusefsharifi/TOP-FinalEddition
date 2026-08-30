import React from 'react';

import Navbar from './Navbar';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  open: boolean;
  toggleDrawer: () => void;
}

const Layout: React.FC<LayoutProps> = ({ children, open, toggleDrawer }) => {
  return (
    <div style={{  display: 'flex', minHeight: '100vh'  }}>
      <Navbar open={open} toggleDrawer={toggleDrawer} />
      <Sidebar open={open} onClose={toggleDrawer} />
      <div>
        <div style={{  mt: 8  }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout; 