import React, { useEffect, useState } from "react";
import { Card, List, Button, Typography, Spin } from "antd";
import { BellOutlined, CheckCircleOutlined } from "@ant-design/icons";

const { Text } = Typography;

interface Notification { id: string; title: string; message: string; date: string; read: boolean; }

const fetchNotifications = (): Promise<Notification[]> =>
  new Promise((resolve) => setTimeout(() => resolve([
    { id: "1", title: "سفارش جدید", message: "یک سفارش جدید ثبت شد.", date: "1403/05/10", read: false },
    { id: "2", title: "پرداخت موفق", message: "پرداخت مشتری تایید شد.", date: "1403/05/09", read: true },
    { id: "3", title: "تیکت پشتیبانی", message: "یک تیکت جدید دریافت شد.", date: "1403/05/08", read: false },
  ]), 1000));

export const NotificationWidget: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => { fetchNotifications().then((d) => { setNotifications(d); setLoading(false); }); }, []);

  return (
    <Card title={<span><BellOutlined style={{ marginRight: 8 }} />اعلان‌ها</span>} style={{ minHeight: 180 }}>
      {loading ? <div style={{ textAlign: "center", padding: "40px 0" }}><Spin /></div> : (
        <List size="small" dataSource={showAll ? notifications : notifications.slice(0, 2)}
          renderItem={(n) => (
            <List.Item style={{ backgroundColor: n.read ? "#f5f5f5" : "#e6f7ff", borderRadius: 8, marginBottom: 8, padding: "8px 12px" }}>
              <List.Item.Meta avatar={n.read ? <CheckCircleOutlined style={{ color: "#52c41a" }} /> : <BellOutlined style={{ color: "#1677ff" }} />}
                title={<Text strong={!n.read}>{n.title}</Text>} description={`${n.message} - ${n.date}`} />
            </List.Item>
          )} />
      )}
      {notifications.length > 2 && <Button type="link" size="small" onClick={() => setShowAll((v) => !v)}>{showAll ? "نمایش کمتر" : "نمایش همه"}</Button>}
    </Card>
  );
};
