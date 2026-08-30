import React, { useEffect, useState } from "react";
import { Card, List, Checkbox, Typography, Spin } from "antd";
import { CheckSquareOutlined } from "@ant-design/icons";

const { Text } = Typography;
interface Task { id: string; title: string; done: boolean; }

const fetchTasks = (): Promise<Task[]> =>
  new Promise((resolve) => setTimeout(() => resolve([
    { id: "1", title: "تماس با مشتری جدید", done: false },
    { id: "2", title: "بررسی فاکتورهای پرداخت نشده", done: true },
    { id: "3", title: "پاسخ به تیکت پشتیبانی", done: false },
  ]), 1000));

export const TaskWidget: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchTasks().then((d) => { setTasks(d); setLoading(false); }); }, []);

  return (
    <Card title={<span><CheckSquareOutlined style={{ marginRight: 8 }} />وظایف من</span>} style={{ minHeight: 180 }}>
      {loading ? <div style={{ textAlign: "center", padding: "40px 0" }}><Spin /></div> : (
        <List size="small" dataSource={tasks}
          renderItem={(t) => (
            <List.Item style={{ padding: "4px 0" }}>
              <Checkbox checked={t.done} onChange={() => setTasks((prev) => prev.map((x) => x.id === t.id ? { ...x, done: !x.done } : x))} />
              <Text style={{ marginLeft: 8, textDecoration: t.done ? "line-through" : "none", color: t.done ? "#999" : undefined }}>{t.title}</Text>
            </List.Item>
          )} />
      )}
    </Card>
  );
};
