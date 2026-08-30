import React, { useState, useEffect } from "react";
import { Button, Modal, Row, Col, Card, Typography, message, Select, Space, Tooltip, IconButton } from "antd";
import { PlusOutlined, DeleteOutlined, EditOutlined, HolderOutlined } from "@ant-design/icons";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { KPIWidget } from "./KPIWidget";
import { ChartWidget } from "./ChartWidget";
import { AISummaryWidget, AIInsightsWidget, AIQuickActionsWidget, AIRecommendationsWidget, AIPredictionsWidget, AICorrelationsWidget, AIActivityWidget } from "./AIDashboardWidgets";

const { Text } = Typography;

const defaultWidgets = [
  { id: "ai-summary", type: "ai-summary", props: {} },
  { id: "ai-insights", type: "ai-insights", props: {} },
  { id: "ai-recs", type: "ai-recs", props: {} },
  { id: "ai-preds", type: "ai-preds", props: {} },
  { id: "ai-corr", type: "ai-corr", props: {} },
  { id: "ai-actions", type: "ai-actions", props: {} },
  { id: "ai-activity", type: "ai-activity", props: {} },
  { id: "kpi1", type: "kpi", props: { title: "مجموع فروش", value: "$24,000", icon: "DollarOutlined", color: "#1677ff", description: "در ماه جاری", timeRange: "ماه جاری" } },
  { id: "kpi2", type: "kpi", props: { title: "تعداد مشتریان", value: 150, icon: "TeamOutlined", color: "#52c41a", description: "فعال", timeRange: "ماه جاری" } },
  { id: "chart1", type: "chart", props: { title: "روند فروش ماهانه", data: [{ name: "فروردین", value: 4000 }, { name: "اردیبهشت", value: 3000 }, { name: "خرداد", value: 5000 }, { name: "تیر", value: 7000 }, { name: "مرداد", value: 6000 }, { name: "شهریور", value: 8000 }], type: "line", dataKey: "value", categoryKey: "name", color: "#1677ff", timeRange: "۶ ماه اخیر" } },
  { id: "chart2", type: "chart", props: { title: "تقسیم‌بندی مشتریان", data: [{ name: "جدید", value: 40 }, { name: "فعال", value: 90 }, { name: "غیرفعال", value: 20 }], type: "pie", dataKey: "value", categoryKey: "name", timeRange: "ماه جاری" } },
];

const availableWidgets = [
  { id: "kpi3", type: "kpi", props: { title: "سفارشات باز", value: 25, icon: "ShoppingCartOutlined", color: "#faad14", description: "در انتظار ارسال", timeRange: "ماه جاری" } },
  { id: "kpi4", type: "kpi", props: { title: "درآمد", value: "$12,000", icon: "RiseOutlined", color: "#ff4d4f", description: "خالص", timeRange: "ماه جاری" } },
];

const WIDGETS_KEY = "dashboard_widgets";
const timeRanges = ["روز جاری", "هفته جاری", "ماه جاری", "۶ ماه اخیر", "سال جاری"];

export const WidgetManager: React.FC = () => {
  const [widgets, setWidgets] = useState(() => { const s = localStorage.getItem(WIDGETS_KEY); return s ? JSON.parse(s) : defaultWidgets; });
  const [addOpen, setAddOpen] = useState(false);
  const [editIdx, setEditIdx] = useState<number | null>(null);

  useEffect(() => { localStorage.setItem(WIDGETS_KEY, JSON.stringify(widgets)); }, [widgets]);

  const onDragEnd = (result: any) => {
    if (!result.destination) return;
    const r = Array.from(widgets);
    const [removed] = r.splice(result.source.index, 1);
    r.splice(result.destination.index, 0, removed);
    setWidgets(r);
    message.success("ترتیب ویجت‌ها ذخیره شد.");
  };

  const handleAddWidget = (w: any) => { setWidgets((p: any) => [...p, w]); setAddOpen(false); message.success("ویجت جدید اضافه شد."); };
  const handleRemoveWidget = (id: string) => { setWidgets((p: any) => p.filter((w: any) => w.id !== id)); message.success("ویجت حذف شد."); };
  const handleEditSave = (v: string) => { if (editIdx === null) return; setWidgets((p: any) => p.map((w: any, i: number) => i === editIdx ? { ...w, props: { ...w.props, timeRange: v } } : w)); setEditIdx(null); message.success("تنظیمات ویجت ذخیره شد."); };

  const renderWidget = (w: any) => {
    switch (w.type) {
      case "ai-summary": return <AISummaryWidget />;
      case "ai-insights": return <AIInsightsWidget />;
      case "ai-recs": return <AIRecommendationsWidget />;
      case "ai-preds": return <AIPredictionsWidget />;
      case "ai-corr": return <AICorrelationsWidget />;
      case "ai-actions": return <AIQuickActionsWidget />;
      case "ai-activity": return <AIActivityWidget />;
      case "kpi": return <KPIWidget {...w.props} />;
      case "chart": return <ChartWidget {...w.props} />;
      default: return null;
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>مدیریت ویجت‌های داشبورد</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddOpen(true)}>افزودن ویجت</Button>
      </div>
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="dashboard-widgets">
          {(provided) => (
            <Row gutter={[16, 16]} ref={provided.innerRef} {...provided.droppableProps}>
              {widgets.map((w: any, idx: number) => (
                <Draggable key={w.id} draggableId={w.id} index={idx}>
                  {(p, snap) => (
                    <Col xs={24} sm={12} md={8} lg={6} ref={p.innerRef} {...p.draggableProps} style={{ ...p.draggableProps.style }}>
                      <Card size="small" style={{ opacity: snap.isDragging ? 0.8 : 1 }}
                        extra={<Space size={4}><Tooltip title="ویرایش"><Button type="text" size="small" onClick={() => setEditIdx(idx)}><EditOutlined /></Button></Tooltip><Tooltip title="حذف"><Button type="text" size="small" danger onClick={() => handleRemoveWidget(w.id)}><DeleteOutlined /></Button></Tooltip></Space>}>
                        <div {...p.dragHandleProps} style={{ cursor: "grab", textAlign: "center", marginBottom: 4, color: "#999" }}><HolderOutlined /></div>
                        {renderWidget(w)}
                        <Text type="secondary" style={{ fontSize: 11, display: "block", marginTop: 4 }}>بازه زمانی: {w.props.timeRange}</Text>
                      </Card>
                    </Col>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </Row>
          )}
        </Droppable>
      </DragDropContext>
      <Modal title="افزودن ویجت جدید" open={addOpen} onCancel={() => setAddOpen(false)} footer={null}>
        <Row gutter={[16, 16]}>
          {availableWidgets.map((w) => (
            <Col span={24} key={w.id}>
              <Card size="small"><div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}><div><Text strong>{w.props.title}</Text><br /><Text type="secondary" style={{ fontSize: 12 }}>{w.type === "kpi" ? "KPI" : "نمودار"}</Text></div><Button onClick={() => handleAddWidget(w)}>افزودن</Button></div></Card>
            </Col>
          ))}
        </Row>
      </Modal>
      <Modal title="ویرایش بازه زمانی ویجت" open={editIdx !== null} onCancel={() => setEditIdx(null)} footer={null}>
        <Select style={{ width: "100%" }} placeholder="بازه زمانی" value={editIdx !== null ? widgets[editIdx]?.props?.timeRange : undefined} onChange={handleEditSave} options={timeRanges.map((r) => ({ label: r, value: r }))} />
      </Modal>
    </div>
  );
};
