import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Table,
  Button,
  Space,
  Spin,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  message,
  Badge,
  Progress,
  Tooltip,
  Divider,
  Switch,
  Empty,
  Alert,
} from "antd";
import {
  ThunderboltOutlined,
  PlusOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  EyeOutlined,
  RobotOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  DeleteOutlined,
  EditOutlined,
  StopOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import apiClient from "../../../services/api";

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

interface Workflow {
  id: number;
  name: string;
  description: string;
  trigger_module: string;
  trigger_event: string;
  action_type: string;
  is_active: boolean;
  total_executions: number;
  success_count: number;
  fail_count: number;
  created_at: string;
}

interface WorkflowStats {
  total_workflows: number;
  active_workflows: number;
  total_executions: number;
  success_rate: number;
  by_module: Record<string, number>;
}

const MODULE_OPTIONS = [
  { value: "inventory", label: "📦 انبارداری" },
  { value: "finance", label: "💰 مالی" },
  { value: "hr", label: "👥 منابع انسانی" },
  { value: "sales", label: "📈 فروش" },
  { value: "crm", label: "🤝 CRM" },
  { value: "procurement", label: "🛒 تدارکات" },
  { value: "bi", label: "📊 هوش تجاری" },
  { value: "hse", label: "🛡️ HSE" },
  { value: "support", label: "🎧 پشتیبانی" },
  { value: "documents", label: "📄 اسناد" },
  { value: "contracts", label: "📋 قراردادها" },
  { value: "messages", label: "💬 پیام‌ها" },
  { value: "tasks", label: "✅ وظایف" },
  { value: "projects", label: "🏗️ پروژه‌ها" },
  { value: "quality", label: "🔍 کیفیت" },
  { value: "budget", label: "💵 بودجه" },
];

const EVENT_TYPES = [
  { value: "low_stock", label: "موجودی کم" },
  { value: "invoice_due", label: "سررسید فاکتور" },
  { value: "lead_high_score", label: "امتیاز بالای لید" },
  { value: "expense_anomaly", label: "ناهنجاری هزینه" },
  { value: "employee_anniversary", label: "سالگرد استخدام" },
  { value: "project_delay", label: "تأخیر پروژه" },
  { value: "quality_issue", label: "مشکل کیفیت" },
  { value: "customer_churn_risk", label: "ریسک از دست دادن مشتری" },
  { value: "new_ticket", label: "تیکت جدید" },
  { value: "sla_breach", label: "نقض SLA" },
  { value: "contract_expiring", label: "انقضای قرارداد" },
  { value: "payment_received", label: "دریافت پرداخت" },
  { value: "attendance_anomaly", label: "ناهنجاری حضور" },
  { value: "safety_incident", label: "حادثه ایمنی" },
];

const ACTION_TYPES = [
  { value: "send_email", label: "ارسال ایمیل" },
  { value: "send_notification", label: "ارسال اعلان" },
  { value: "create_po", label: "ایجاد سفارش خرید" },
  { value: "create_task", label: "ایجاد وظیفه" },
  { value: "assign_rep", label: "تخصیص نماینده فروش" },
  { value: "escalate", label: "اعمال فشار" },
  { value: "quarantine_stock", label: "قرنطینه موجودی" },
  { value: "trigger_retention", label: "فعال‌سازی حفظ مشتری" },
  { value: "generate_report", label: "تولید گزارش" },
  { value: "update_status", label: "بروزرسانی وضعیت" },
  { value: "create_reminder", label: "ایجاد یادآوری" },
  { value: "block_user", label: "مسدود کردن کاربر" },
];

const PRESET_WORKFLOWS = [
  {
    name: "هشدار موجودی کم",
    description: "وقتی موجودی کالا به نقطه سفارش مجدد رسید، اعلان ارسال کن",
    trigger_module: "inventory",
    trigger_event: "low_stock",
    action_type: "send_notification",
  },
  {
    name: "یادآوری فاکتور سررسید",
    description: "وقتی فاکتور به سررسید رسید، یادآوری ارسال کن",
    trigger_module: "finance",
    trigger_event: "invoice_due",
    action_type: "create_reminder",
  },
  {
    name: "تخصیص خودکار لید",
    description: "وقتی امتیاز لید از آستانه بالاتر رفت، به نماینده فروش تخصیص بده",
    trigger_module: "crm",
    trigger_event: "lead_high_score",
    action_type: "assign_rep",
  },
  {
    name: "اعلام ناهنجاری هزینه",
    description: "وقتی هزینه غیرعادی شناسایی شد، به مدیر اطلاع بده",
    trigger_module: "finance",
    trigger_event: "expense_anomaly",
    action_type: "escalate",
  },
  {
    name: "قرنطینه مشکل کیفیت",
    description: "وقتی مشکل کیفیت گزارش شد، موجودی را قرنطینه کن",
    trigger_module: "quality",
    trigger_event: "quality_issue",
    action_type: "quarantine_stock",
  },
  {
    name: "حفظ مشتری در معرض ریسک",
    description: "وقتی ریسک از دست دادن مشتری بالا رفت، کمپین حفظ را فعال کن",
    trigger_module: "crm",
    trigger_event: "customer_churn_risk",
    action_type: "trigger_retention",
  },
];

const AIAutomationPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [stats, setStats] = useState<WorkflowStats | null>(null);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [presetModalVisible, setPresetModalVisible] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [form] = Form.useForm();
  const { t } = useTranslation();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [workflowsRes, statsRes] = await Promise.allSettled([
        apiClient.get("/ai/automation/workflows"),
        apiClient.get("/ai/automation/stats"),
      ]);

      if (workflowsRes.status === "fulfilled") setWorkflows(workflowsRes.value.data);
      if (statsRes.status === "fulfilled") setStats(statsRes.value.data);
    } catch (err) {
      console.error("Failed to fetch data:", err);
      message.error("خطا در بارگذاری داده‌ها");
    } finally {
      setLoading(false);
    }
  };

  const createWorkflow = async (values: any) => {
    try {
      await apiClient.post("/ai/automation/workflows", values);
      message.success("گردش کار با موفقیت ایجاد شد");
      setCreateModalVisible(false);
      form.resetFields();
      fetchData();
    } catch (err) {
      message.error("خطا در ایجاد گردش کار");
    }
  };

  const triggerWorkflow = async (workflowId: number) => {
    try {
      await apiClient.post(`/ai/automation/workflows/${workflowId}/trigger`);
      message.success("گردش کار فعال شد");
      fetchData();
    } catch (err) {
      message.error("خطا در فعال‌سازی گردش کار");
    }
  };

  const deleteWorkflow = async (workflowId: number) => {
    try {
      await apiClient.delete(`/ai/automation/workflows/${workflowId}`);
      message.success("گردش کار حذف شد");
      fetchData();
    } catch (err) {
      message.error("خطا در حذف گردش کار");
    }
  };

  const toggleWorkflow = async (workflowId: number, isActive: boolean) => {
    try {
      await apiClient.patch(`/ai/automation/workflows/${workflowId}`, {
        is_active: isActive,
      });
      message.success(isActive ? "گردش کار فعال شد" : "گردش کار غیرفعال شد");
      fetchData();
    } catch (err) {
      message.error("خطا در تغییر وضعیت");
    }
  };

  const getModuleColor = (module: string) => {
    const colors: Record<string, string> = {
      inventory: "green",
      sales: "blue",
      finance: "gold",
      hr: "purple",
      crm: "cyan",
      procurement: "orange",
      hse: "red",
      tasks: "default",
      support: "geekblue",
      quality: "lime",
    };
    return colors[module] || "default";
  };

  const columns = [
    {
      title: "نام",
      dataIndex: "name",
      key: "name",
      render: (text: string, record: Workflow) => (
        <Space>
          <Text strong>{text}</Text>
          {!record.is_active && <Tag color="default">غیرفعال</Tag>}
        </Space>
      ),
    },
    {
      title: "ماژول محرک",
      key: "trigger",
      render: (_: any, record: Workflow) => (
        <Space>
          <Tag color={getModuleColor(record.trigger_module)}>
            {record.trigger_module}
          </Tag>
          <Tag>{record.trigger_event}</Tag>
        </Space>
      ),
    },
    {
      title: "عملیات",
      dataIndex: "action_type",
      key: "action_type",
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: "اجراها",
      key: "executions",
      render: (_: any, record: Workflow) => (
        <Space>
          <Text>{record.total_executions}</Text>
          {record.total_executions > 0 && (
            <Tooltip title={`${record.success_count} موفق / ${record.fail_count} ناموفق`}>
              <Progress
                percent={
                  record.total_executions > 0
                    ? Math.round((record.success_count / record.total_executions) * 100)
                    : 0
                }
                size="small"
                style={{ width: 60 }}
              />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: "وضعیت",
      dataIndex: "is_active",
      key: "status",
      render: (isActive: boolean, record: Workflow) => (
        <Switch
          checked={isActive}
          onChange={(checked) => toggleWorkflow(record.id, checked)}
          checkedChildren="فعال"
          unCheckedChildren="غیرفعال"
        />
      ),
    },
    {
      title: "عملیات",
      key: "actions",
      render: (_: any, record: Workflow) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => triggerWorkflow(record.id)}
          >
            اجرا
          </Button>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedWorkflow(record);
              setDetailModalVisible(true);
            }}
          >
            جزئیات
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => deleteWorkflow(record.id)}
          />
        </Space>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "100px 0" }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>در حال بارگذاری...</Text>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "24px" }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2}>
            <ThunderboltOutlined style={{ marginRight: 8, color: "#faad14" }} />
            اتوماسیون هوش مصنوعی
          </Title>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={fetchData}>
              بروزرسانی
            </Button>
            <Button
              icon={<SettingOutlined />}
              onClick={() => setPresetModalVisible(true)}
            >
              الگوهای آماده
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              گردش کار جدید
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Stats Cards */}
      {stats && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="گردش کارها"
                value={stats.total_workflows}
                prefix={<ThunderboltOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="فعال"
                value={stats.active_workflows}
                prefix={<CheckCircleOutlined style={{ color: "#52c41a" }} />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="اجراها"
                value={stats.total_executions}
                prefix={<PlayCircleOutlined style={{ color: "#1677ff" }} />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="نرخ موفقیت"
                value={stats.success_rate}
                suffix="%"
                prefix={<CheckCircleOutlined style={{ color: "#52c41a" }} />}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Workflows by Module */}
      {stats?.by_module && Object.keys(stats.by_module).length > 0 && (
        <Card title="گردش کارها بر اساس ماژول" style={{ marginBottom: 24 }}>
          <Row gutter={[16, 16]}>
            {Object.entries(stats.by_module).map(([module, count]) => (
              <Col span={4} key={module}>
                <Card size="small" style={{ textAlign: "center" }}>
                  <Statistic
                    title={module}
                    value={count}
                    valueStyle={{ color: getModuleColor(module) === "gold" ? "#faad14" : "#1677ff" }}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* Workflows Table */}
      <Card title="گردش کارها">
        <Table
          columns={columns}
          dataSource={workflows}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: <Empty description="گردش کاری وجود ندارد" /> }}
        />
      </Card>

      {/* Create Workflow Modal */}
      <Modal
        title="ایجاد گردش کار جدید"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} onFinish={createWorkflow} layout="vertical">
          <Form.Item
            name="name"
            label="نام گردش کار"
            rules={[{ required: true, message: "نام را وارد کنید" }]}
          >
            <Input placeholder="مثال: هشدار موجودی کم" />
          </Form.Item>
          <Form.Item name="description" label="توضیحات">
            <Input.TextArea placeholder="توضیح عملکرد این گردش کار" />
          </Form.Item>
          <Form.Item
            name="trigger_module"
            label="ماژول محرک"
            rules={[{ required: true, message: "ماژول را انتخاب کنید" }]}
          >
            <Select placeholder="ماژول را انتخاب کنید">
              {MODULE_OPTIONS.map((opt) => (
                <Option key={opt.value} value={opt.value}>
                  {opt.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="trigger_event"
            label="رویداد محرک"
            rules={[{ required: true, message: "رویداد را انتخاب کنید" }]}
          >
            <Select placeholder="رویداد را انتخاب کنید">
              {EVENT_TYPES.map((opt) => (
                <Option key={opt.value} value={opt.value}>
                  {opt.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="action_type"
            label="نوع عملیات"
            rules={[{ required: true, message: "عملیات را انتخاب کنید" }]}
          >
            <Select placeholder="عملیات را انتخاب کنید">
              {ACTION_TYPES.map((opt) => (
                <Option key={opt.value} value={opt.value}>
                  {opt.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              ایجاد گردش کار
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Workflow Detail Modal */}
      <Modal
        title="جزئیات گردش کار"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={600}
      >
        {selectedWorkflow && (
          <div>
            <Paragraph>
              <Text strong>نام:</Text> {selectedWorkflow.name}
            </Paragraph>
            <Paragraph>
              <Text strong>توضیحات:</Text>{" "}
              {selectedWorkflow.description || "-"}
            </Paragraph>
            <Paragraph>
              <Text strong>ماژول محرک:</Text>{" "}
              <Tag color={getModuleColor(selectedWorkflow.trigger_module)}>
                {selectedWorkflow.trigger_module}
              </Tag>
            </Paragraph>
            <Paragraph>
              <Text strong>رویداد محرک:</Text>{" "}
              <Tag>{selectedWorkflow.trigger_event}</Tag>
            </Paragraph>
            <Paragraph>
              <Text strong>نوع عملیات:</Text>{" "}
              <Tag color="blue">{selectedWorkflow.action_type}</Tag>
            </Paragraph>
            <Divider />
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="اجراها"
                  value={selectedWorkflow.total_executions}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="موفق"
                  value={selectedWorkflow.success_count}
                  valueStyle={{ color: "#52c41a" }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="ناموفق"
                  value={selectedWorkflow.fail_count}
                  valueStyle={{ color: "#ff4d4f" }}
                />
              </Col>
            </Row>
            <Paragraph style={{ marginTop: 16 }}>
              <Text strong>تاریخ ایجاد:</Text>{" "}
              {new Date(selectedWorkflow.created_at).toLocaleString("fa-IR")}
            </Paragraph>
          </div>
        )}
      </Modal>

      {/* Preset Workflows Modal */}
      <Modal
        title="الگوهای آماده گردش کار"
        open={presetModalVisible}
        onCancel={() => setPresetModalVisible(false)}
        footer={null}
        width={700}
      >
        <Alert
          message="یکی از الگوهای آماده را انتخاب کنید تا گردش کار جدیدی با تنظیمات پیش‌فرض ایجاد شود"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        <List
          dataSource={PRESET_WORKFLOWS}
          renderItem={(preset) => (
            <List.Item
              actions={[
                <Button
                  type="primary"
                  size="small"
                  onClick={() => {
                    form.setFieldsValue(preset);
                    setPresetModalVisible(false);
                    setCreateModalVisible(true);
                  }}
                >
                  استفاده
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={preset.name}
                description={
                  <Space direction="vertical" size={4}>
                    <Text type="secondary">{preset.description}</Text>
                    <Space>
                      <Tag color={getModuleColor(preset.trigger_module)}>
                        {preset.trigger_module}
                      </Tag>
                      <Tag>{preset.trigger_event}</Tag>
                      <Tag color="blue">{preset.action_type}</Tag>
                    </Space>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Modal>
    </div>
  );
};

export default AIAutomationPage;
