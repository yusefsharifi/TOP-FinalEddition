import React, { useState } from 'react';
import { Button, Card, Col, Divider, Input, InputNumber, List, List.Item, Modal, Row, Switch, Typography } from 'antd';
import { BankOutlined as BusinessIcon, BellOutlined as NotificationsIcon, CloudUploadOutlined as BackupIcon, DatabaseOutlined as StorageIcon, GlobalOutlined as LanguageIcon, SafetyOutlined as SecurityIcon, SaveOutlined as SaveIcon } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

interface SettingSection {
  title: string;
  icon: React.ReactNode;
  items: {
    title: string;
    description: string;
    type: 'switch' | 'text' | 'button';
    value?: boolean | string;
    action?: () => void;
  }[];
}

const Settings: React.FC = () => {
  const { t } = useTranslation();
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedSection, setSelectedSection] = useState<string>('');
  const [settings, setSettings] = useState({
    notifications: true,
    language: 'fa',
    companyName: 'شرکت نمونه',
    backupEnabled: true,
    storageLimit: '1000',
  });

  const sections: SettingSection[] = [
    {
      title: t('settings.company'),
      icon: <BusinessIcon />,
      items: [
        {
          title: t('settings.companyName'),
          description: t('settings.companyNameDesc'),
          type: 'text',
          value: settings.companyName,
          action: () => {
            setSelectedSection('company');
            setOpenDialog(true);
          },
        },
        {
          title: t('settings.companyAddress'),
          description: t('settings.companyAddressDesc'),
          type: 'text',
          value: '',
          action: () => {
            setSelectedSection('address');
            setOpenDialog(true);
          },
        },
      ],
    },
    {
      title: t('settings.language'),
      icon: <LanguageIcon />,
      items: [
        {
          title: t('settings.language'),
          description: t('settings.languageDesc'),
          type: 'text',
          value: settings.language,
          action: () => {
            setSelectedSection('language');
            setOpenDialog(true);
          },
        },
      ],
    },
    {
      title: t('settings.notifications'),
      icon: <NotificationsIcon />,
      items: [
        {
          title: t('settings.emailNotifications'),
          description: t('settings.emailNotificationsDesc'),
          type: 'switch',
          value: settings.notifications,
          action: () => {
            setSettings({ ...settings, notifications: !settings.notifications });
          },
        },
        {
          title: t('settings.smsNotifications'),
          description: t('settings.smsNotificationsDesc'),
          type: 'switch',
          value: false,
          action: () => {},
        },
      ],
    },
    {
      title: t('settings.security'),
      icon: <SecurityIcon />,
      items: [
        {
          title: t('settings.twoFactorAuth'),
          description: t('settings.twoFactorAuthDesc'),
          type: 'switch',
          value: false,
          action: () => {},
        },
        {
          title: t('settings.passwordExpiry'),
          description: t('settings.passwordExpiryDesc'),
          type: 'switch',
          value: true,
          action: () => {},
        },
      ],
    },
    {
      title: t('settings.backup'),
      icon: <BackupIcon />,
      items: [
        {
          title: t('settings.autoBackup'),
          description: t('settings.autoBackupDesc'),
          type: 'switch',
          value: settings.backupEnabled,
          action: () => {
            setSettings({ ...settings, backupEnabled: !settings.backupEnabled });
          },
        },
        {
          title: t('settings.backupSchedule'),
          description: t('settings.backupScheduleDesc'),
          type: 'button',
          action: () => {
            setSelectedSection('backup');
            setOpenDialog(true);
          },
        },
      ],
    },
    {
      title: t('settings.storage'),
      icon: <StorageIcon />,
      items: [
        {
          title: t('settings.storageLimit'),
          description: t('settings.storageLimitDesc'),
          type: 'text',
          value: settings.storageLimit,
          action: () => {
            setSelectedSection('storage');
            setOpenDialog(true);
          },
        },
      ],
    },
  ];

  const handleDialogClose = () => {
    setOpenDialog(false);
    setSelectedSection('');
  };

  const renderSettingItem = (item: SettingSection['items'][0]) => {
    switch (item.type) {
      case 'switch':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={item.value as boolean}
                onChange={item.action}
              />
            }
            label={item.title}
          />
        );
      case 'text':
        return (
          <Input
            fullWidth
            label={item.title}
            value={item.value}
            onClick={item.action}
            InputProps={{
              readOnly: true,
            }}
          />
        );
      case 'button':
        return (
          <Button
            variant="outlined"
            startIcon={<SaveIcon />}
            onClick={item.action}
          >
            {item.title}
          </Button>
        );
      default:
        return null;
    }
  };

  return (
    <div>
      <Typography.Title level={2}>
        {t('settings.title')}
      </Typography.Title>

      <Row gutter={[16, 16]}>
        {sections.map((section) => (
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card>
              <div style={{  p: 2, display: 'flex', alignItems: 'center'  }}>
                <div style={{  mr: 2, color: 'primary.main'  }}>
                  {section.icon}
                </div>
                <Typography.Title level={4}>
                  {section.title}
                </Typography.Title>
              </div>
              <Divider />
              <List>
                {section.items.map((item, index) => (
                  <React.Fragment key={item.title}>
                    <ListItem>
                      <ListItemText
                        primary={item.title}
                        secondary={item.description}
                      />
                      {renderSettingItem(item)}
                    </ListItem>
                    {index < section.items.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </Card>
          </Col>
        ))}
      </Row>

      <Modal open={false} onCancel={() => {}} footer={null}>
        <div>
          {t(`settings.${selectedSection}Title`)}
        </div>
        <div>
          <div style={{  mt: 2  }}>
            <Typography color="text.secondary">
              {t(`settings.${selectedSection}Form`)}
            </Typography>
          </div>
        </div>
        <div>
          <Button onClick={handleDialogClose}>{t('common.cancel')}</Button>
          <Button variant="contained" onClick={handleDialogClose}>
            {t('common.save')}
          </Button>
        </div>
      </Modal>
    </div>
  );
};

export default Settings; 