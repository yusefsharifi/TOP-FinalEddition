import React, { useState } from 'react';
import { Card, Tabs, Typography } from 'antd';
import { SecurityDashboard } from '../../components/security/SecurityDashboard';
import { AccessManagement } from '../../components/security/AccessManagement';
import { UserManagement } from '../../components/security/UserManagement';
import { AuditTrail } from '../../components/security/AuditTrail';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`security-tabpanel-${index}`}
      aria-labelledby={`security-tab-${index}`}
      {...other}
    >
      {value === index && <div style={{  py: 3  }}>{children}</div>}
    </div>
  );
}

export const Security: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <div>
      <Typography.Title level={2}>
        مدیریت امنیت و دسترسی‌ها
      </Typography.Title>

      <Card style={{  width: '100%'  }}>
        <div style={{  borderBottom: 1, borderColor: 'divider'  }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="security tabs">
            <Tab label="داشبورد امنیت" />
            <Tab label="مدیریت دسترسی‌ها" />
            <Tab label="مدیریت کاربران" />
            <Tab label="سیستم پیگیری" />
          </Tabs>
        </div>

        <TabPanel value={tabValue} index={0}>
          <SecurityDashboard />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <AccessManagement />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <UserManagement />
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <AuditTrail />
        </TabPanel>
      </Card>
    </div>
  );
}; 