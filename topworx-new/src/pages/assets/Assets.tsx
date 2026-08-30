import { useEffect } from "react";
import { useNotificationSnackbar } from "../../core/notifications/NotificationSnackbarProvider";
const { showNotification } = useNotificationSnackbar();

useEffect(() => {
  data.forEach(asset => {
    const now = Date.now();
    if (asset.warrantyEnd && new Date(asset.warrantyEnd).getTime() - now < 30 * 24 * 60 * 60 * 1000 && new Date(asset.warrantyEnd).getTime() > now) {
      showNotification(`گارانتی دارایی "${asset.name}" تا کمتر از ۳۰ روز دیگر به پایان می‌رسد!`, "warning");
    }
    if (asset.insuranceEnd && new Date(asset.insuranceEnd).getTime() - now < 30 * 24 * 60 * 60 * 1000 && new Date(asset.insuranceEnd).getTime() > now) {
      showNotification(`بیمه دارایی "${asset.name}" تا کمتر از ۳۰ روز دیگر به پایان می‌رسد!`, "info");
    }
  });
}, [data]);