import React, { useEffect, useState } from "react";
import { Card, List, Button, Typography, Spin } from "antd";
import { CalendarOutlined } from "@ant-design/icons";

const { Text } = Typography;
interface CalendarEvent { id: string; title: string; date: string; type: string; }

const fetchEvents = (): Promise<CalendarEvent[]> =>
  new Promise((resolve) => setTimeout(() => resolve([
    { id: "1", title: "جلسه تیم توسعه", date: "1403/05/10", type: "meeting" },
    { id: "2", title: "تولد همکار", date: "1403/05/10", type: "birthday" },
    { id: "3", title: "یادآوری پرداخت", date: "1403/05/10", type: "reminder" },
  ]), 1000));

export const CalendarWidget: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => { fetchEvents().then((d) => { setEvents(d); setLoading(false); }); }, []);

  return (
    <Card title={<span><CalendarOutlined style={{ marginRight: 8 }} />رویدادهای امروز</span>} style={{ minHeight: 180 }}>
      {loading ? <div style={{ textAlign: "center", padding: "40px 0" }}><Spin /></div> : (
        <List size="small" dataSource={showAll ? events : events.slice(0, 2)}
          renderItem={(e) => (
            <List.Item style={{ padding: "4px 0" }}>
              <List.Item.Meta title={<Text strong>{e.title}</Text>} description={`${e.type} - ${e.date}`} />
            </List.Item>
          )} />
      )}
      {events.length > 2 && <Button type="link" size="small" onClick={() => setShowAll((v) => !v)}>{showAll ? "نمایش کمتر" : "نمایش همه"}</Button>}
    </Card>
  );
};
