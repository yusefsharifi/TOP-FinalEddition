import React from 'react';
import { Card, Divider, List, List.Item, Typography } from 'antd';
import { BellOutlined as NotificationsIcon, BgColorsOutlined as PaletteIcon, GlobalOutlined as LanguageIcon, SafetyOutlined as SecurityIcon, UserOutlined as PersonIcon } from '@ant-design/icons';

const settingsItems = [
  {
    id: 1,
    name: 'Profile Settings',
    description: 'Update your personal information',
    icon: <PersonIcon />,
  },
  {
    id: 2,
    name: 'Security',
    description: 'Manage your security preferences',
    icon: <SecurityIcon />,
  },
  {
    id: 3,
    name: 'Notifications',
    description: 'Configure notification settings',
    icon: <NotificationsIcon />,
  },
  {
    id: 4,
    name: 'Language',
    description: 'Change language preferences',
    icon: <LanguageIcon />,
  },
  {
    id: 5,
    name: 'Theme',
    description: 'Customize application appearance',
    icon: <PaletteIcon />,
  },
];

export const Settings: React.FC = () => {
  return (
    <div>
      <Typography.Title level={2}>
        Settings
      </Typography.Title>
      <Card>
        <List>
          {settingsItems.map((item, index) => (
            <React.Fragment key={item.id}>
              <ListItem button>
                <ListItemIcon>{item.icon}</span>
                <ListItemText
                  primary={item.name}
                  secondary={item.description}
                />
              </ListItem>
              {index < settingsItems.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </Card>
    </div>
  );
}; 