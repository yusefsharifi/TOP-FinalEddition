import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Avatar, Badge, Button, Menu, Tooltip, Typography } from 'antd';
import { BellOutlined as NotificationsIcon, LogoutOutlined as LogoutIcon, MenuOutlined as MenuIcon, QuestionCircleOutlined as HelpIcon, SearchOutlined as SearchIcon, SettingOutlined as SettingsIcon, UserOutlined as PersonIcon } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(3),
    width: 'auto',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('md')]: {
      width: '20ch',
    },
  },
}));

interface NavbarProps {
  open: boolean;
  toggleDrawer: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ open, toggleDrawer }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotifications = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationsClose = () => {
    setNotificationsAnchor(null);
  };

  const handleLogout = () => {
    // Add logout logic here
    navigate('/login');
  };

  return (
    <AppBar
      position="fixed"
      style={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: 'white',
        color: 'text.primary',
        boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
       }}
    >
      <Toolbar>
        <Button type="text"
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={toggleDrawer}
          style={{  mr: 2  }}
        >
          <MenuIcon />
        </Button>
        <Typography.Title level={4}>
          TopWorx ERP
        </Typography.Title>
        <Search>
          <SearchIconWrapper>
            <SearchIcon />
          </SearchIconWrapper>
          <StyledInputBase
            placeholder={t('search')}
            inputProps={{ 'aria-label': 'search' }}
          />
        </Search>
        <div>
        <div style={{  display: 'flex', alignItems: 'center'  }}>
          <Tooltip title={t('notifications')}>
            <Button type="text"
              size="large"
              color="inherit"
              onClick={handleNotifications}
            >
              <Badge badgeContent={4} color="error">
                <NotificationsIcon />
              </Badge>
            </Button>
          </Tooltip>
          <Tooltip title={t('settings')}>
            <Button type="text"
              size="large"
              color="inherit"
              onClick={() => navigate('/settings')}
            >
              <SettingsIcon />
            </Button>
          </Tooltip>
          <Tooltip title={t('profile')}>
            <Button type="text"
              size="large"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar style={{  width: 32, height: 32  }}>
                <PersonIcon />
              </Avatar>
            </Button>
          </Tooltip>
        </div>
      </Toolbar>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            mt: 1.5,
            minWidth: 180,
            borderRadius: 1,
          },
        }}
      >
        <MenuItem onClick={() => navigate('/profile')}>
          <PersonIcon style={{  mr: 1  }} />
          {t('profile')}
        </Select.Option>
        <MenuItem onClick={() => navigate('/settings')}>
          <SettingsIcon style={{  mr: 1  }} />
          {t('settings')}
        </Select.Option>
        <MenuItem onClick={() => navigate('/help')}>
          <HelpIcon style={{  mr: 1  }} />
          {t('help')}
        </Select.Option>
        <MenuItem onClick={handleLogout}>
          <LogoutIcon style={{  mr: 1  }} />
          {t('logout')}
        </Select.Option>
      </Menu>
      <Menu
        anchorEl={notificationsAnchor}
        open={Boolean(notificationsAnchor)}
        onClose={handleNotificationsClose}
        PaperProps={{
          sx: {
            mt: 1.5,
            minWidth: 300,
            borderRadius: 1,
          },
        }}
      >
        <MenuItem>
          <Typography.Text>
            {t('newNotification')}
          </Typography.Text>
        </Select.Option>
        <MenuItem>
          <Typography.Text>
            {t('systemUpdate')}
          </Typography.Text>
        </Select.Option>
        <MenuItem>
          <Typography.Text>
            {t('taskReminder')}
          </Typography.Text>
        </Select.Option>
      </Menu>
    </AppBar>
  );
};

export default Navbar; 