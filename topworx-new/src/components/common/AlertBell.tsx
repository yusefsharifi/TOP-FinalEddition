// src/components/common/AlertBell.tsx
// ============================================================================
// Alert Bell Notification
// ============================================================================

import React, { useState } from 'react';
import { Badge, Button, List, List.Item, Tooltip, Typography } from 'antd';
import { BellOutlined } from '@ant-design/icons';
import { CheckOutlined } from '@ant-design/icons';
import { useAlerts, useAcknowledgeAlert } from '../../hooks/useBI';
import { AlertSeverity } from '../../types';

const severityColors: Record<AlertSeverity, string> = {
  critical: '#f44336',
  warning: '#ff9800',
  info: '#2196f3',
};

export const AlertBell: React.FC = () => {
  const { data: alerts = [], isLoading } = useAlerts(true);
  const acknowledge = useAcknowledgeAlert();
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleAcknowledge = (eventId: number) => {
    acknowledge.mutate(eventId);
  };

  const open = Boolean(anchorEl);

  return (
    <>
      <Tooltip title="هشدارها">
        <Button type="text" onClick={handleClick} color="inherit">
          <Badge badgeContent={alerts.length} color="error">
            <NotificationsIcon />
          </Badge>
        </Button>
      </Tooltip>
      
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{ sx: { width: 400, maxHeight: 500 } }}
      >
        <List dense>
          {alerts.length === 0 && (
            <ListItem>
              <ListItemText
                primary={
                  <Typography align="center" color="text.secondary">
                    هشداری وجود ندارد
                  </Typography>
                }
              />
            </ListItem>
          )}
          
          {alerts.map((alert) => (
            <ListItem
              key={alert.id}
              secondaryAction={
                <ListIconButton
                  edge="end"
                  size="small"
                  onClick={() => handleAcknowledge(alert.id)}
                  disabled={acknowledge.isPending}
                >
                  <CheckIcon fontSize="small" />
                </ListIconButton>
              }
              sx={{
                borderRight: `3px solid ${severityColors[alert.severity]}`,
                mb: 0.5,
              }}
            >
              <ListItemText
                primary={
                  <Typography.Text>
                    {alert.message.split('\n')[0]}
                  </Typography.Text>
                }
                secondary={
                  <div>
                    {new Date(alert.triggeredAt).toLocaleString('fa-IR')}
                  </div>
                }
              />
            </ListItem>
          ))}
        </List>
      </Popover>
    </>
  );
};