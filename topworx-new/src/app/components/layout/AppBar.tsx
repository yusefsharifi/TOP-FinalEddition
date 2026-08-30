import React from 'react';
import { Button, Typography } from 'antd';
import { MenuOutlined as MenuIcon, UserOutlined } from '@ant-design/icons';
import { useAuth } from '../../../core/auth/AuthProvider';

export const AppBar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <MuiAppBar position="fixed">
      <Toolbar>
        <Button type="text"
          color="inherit"
          aria-label="open drawer"
          edge="start"
          style={{  mr: 2  }}
        >
          <MenuIcon />
        </Button>
        <Typography.Title level={4}>
          TOP WorX
        </Typography.Title>
        <div style={{  display: 'flex', alignItems: 'center'  }}>
          <Typography variant="body1" style={{  mr: 2  }}>
            {user?.name}
          </Typography>
          <Button type="text" onClick={logout}
          >
            <AccountCircle />
          </Button>
        </div>
      </Toolbar>
    </MuiAppBar>
  );
}; 