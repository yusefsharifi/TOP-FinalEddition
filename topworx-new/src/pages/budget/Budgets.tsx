import { useEffect } from "react";
import { useNotificationSnackbar } from "../../core/notifications/NotificationSnackbarProvider";
const { showNotification } = useNotificationSnackbar();

useEffect(() => {
  data.forEach(budget => {
    if (budget.spent > budget.amount && budget.status === "active") {
      showNotification(`بودجه "${budget.title}" از سقف تعیین‌شده عبور کرده است!`, "error");
    }
  });
}, [data]);