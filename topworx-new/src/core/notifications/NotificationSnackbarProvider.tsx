// src/core/notifications/NotificationSnackbarProvider.tsx
// ============================================================================
// Notification provider using Ant Design's message API (replaces MUI Snackbar)
// ============================================================================

import React, { createContext, useContext } from "react";
import { message } from "antd";

type NotificationSeverity = "info" | "success" | "warning" | "error";

interface NotificationSnackbarContextType {
  showNotification: (msg: string, severity?: NotificationSeverity) => void;
}

const NotificationSnackbarContext = createContext<NotificationSnackbarContextType>({
  showNotification: () => {},
});

export const useNotificationSnackbar = () => useContext(NotificationSnackbarContext);

const [messageApi, contextHolder] = message.useMessage();

const severityToMethod: Record<NotificationSeverity, typeof messageApi.success> = {
  info: messageApi.info,
  success: messageApi.success,
  warning: messageApi.warning,
  error: messageApi.error,
};

export const NotificationSnackbarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const showNotification = (msg: string, severity: NotificationSeverity = "info") => {
    severityToMethod[severity](msg);
  };

  return (
    <NotificationSnackbarContext.Provider value={{ showNotification }}>
      {contextHolder}
      {children}
    </NotificationSnackbarContext.Provider>
  );
};
