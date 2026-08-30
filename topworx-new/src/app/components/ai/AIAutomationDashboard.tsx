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

const AIAutomationDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [stats, setStats] = useState<WorkflowStats | null>(null);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [form] = Form.useForm();
  const { t } = useTranslation();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [workflowsRes, statsRes] = await Promise.all([
        apiClient.get("/ai/automation/workflows"),
        apiClient.get("/ai/automation/stats"),
      ]);
      setWorkflows(workflowsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error("Failed to fetch data:", err);
      message.error("Failed to load automation data");
    } finally {
      setLoading(false);
    }
  };

  const createWorkflow = async (values: any) => {
    try {
      await apiClient.post("/ai/automation/workflows", values);
      message.success(t("ai.automation.workflowCreated"));
      setCreateModalVisible(false);
      form.resetFields();
      fetchData();
    } catch (err) {
      message.error("Failed to create workflow");
    }
  };

  const triggerWorkflow = async (workflowId: number) => {
    try {
      await apiClient.post(`/ai/automation/workflows/${workflowId}/trigger`);
      message.success(t("ai.automation.workflowTriggered"));
      fetchData();
    } catch (err) {
      message.error(t("ai.automation.workflowTriggerFailed"));
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
    };
    return colors[module] || "default";
  };

  const columns = [
    {
      title: t("ai.automation.name"),
      dataIndex: "name",
      key: "name",
      render: (text: string, record: Workflow) => (
        <Space>
          <Text strong>{text}</Text>
          {!record.is_active && <Tag color="default">{t("ai.automation.inactive")}</Tag>}
        </Space>
      ),
    },
    {
      title: t("ai.automation.trigger"),
      key: "trigger",
      render: (_: any, record: Workflow) => (
        <Space>
          <Tag color={getModuleColor(record.trigger_module)}>
            {t(`ai.automation.modules.${record.trigger_module}`)}
          </Tag>
          <Tag>{record.trigger_event}</Tag>
        </Space>
      ),
    },
    {
      title: t("ai.automation.action"),
      dataIndex: "action_type",
      key: "action_type",
      render: (text: string) => <Tag>{text}</Tag>,
    },
    {
      title: t("ai.automation.executions"),
      key: "executions",
      render: (_: any, record: Workflow) => (
        <Space>
          <Text>{record.total_executions}</Text>
          <Tooltip title={`${record.success_count} success / ${record.fail_count} fail`}>
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
        </Space>
      ),
    },
    {
      title: t("ai.automation.status"),
      dataIndex: "is_active",
      key: "status",
      render: (isActive: boolean) => (
        <Tag color={isActive ? "green" : "default"}>
          {isActive ? t("ai.automation.active") : t("ai.automation.inactive")}
        </Tag>
      ),
    },
    {
      title: t("ai.automation.actions"),
      key: "actions",
      render: (_: any, record: Workflow) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => triggerWorkflow(record.id)}
          >
            {t("ai.automation.triggerNow")}
          </Button>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedWorkflow(record);
              setDetailModalVisible(true);
            }}
          >
            {t("ai.automation.viewDetails")}
          </Button>
        </Space>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "100px 0" }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: "24px" }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2}>
            <ThunderboltOutlined style={{ marginRight: 8, color: "#faad14" }} />
            {t("ai.automation.title")}
          </Title>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={fetchData}>
              {t("ai.automation.refresh")}
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              {t("ai.automation.createWorkflow")}
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
                title={t("ai.automation.totalWorkflows")}
                value={stats.total_workflows}
                prefix={<ThunderboltOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title={t("ai.automation.activeWorkflows")}
                value={stats.active_workflows}
                prefix={<CheckCircleOutlined style={{ color: "#52c41a" }} />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title={t("ai.automation.totalExecutions")}
                value={stats.total_executions}
                prefix={<PlayCircleOutlined style={{ color: "#1677ff" }} />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title={t("ai.automation.successRate")}
                value={stats.success_rate}
                suffix="%"
                prefix={<CheckCircleOutlined style={{ color: "#52c41a" }} />}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Workflows by Module */}
      {stats?.by_module && (
        <Card title={t("ai.automation.workflowsByModule")} style={{ marginBottom: 24 }}>
          <Row gutter={[16, 16]}>
            {Object.entries(stats.by_module).map(([module, count]) => (
              <Col span={4} key={module}>
                <Card size="small" style={{ textAlign: "center" }}>
                  <Statistic
                    title={t(`ai.automation.modules.${module}`)}
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
      <Card title={t("ai.automation.workflows")}>
        <Table
          columns={columns}
          dataSource={workflows}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Create Workflow Modal */}
      <Modal
        title={t("ai.automation.createNewWorkflow")}
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={createWorkflow} layout="vertical">
          <Form.Item
            name="name"
            label={t("ai.automation.workflowName")}
            rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="description" label={t("ai.automation.workflowDescription")}>
            <Input.TextArea />
          </Form.Item>
          <Form.Item
            name="trigger_module"
            label={t("ai.automation.module")}
            rules={[{ required: true }]}
          >
            <Select>
              {Object.keys(t("ai.automation.modules", { returnObjects: true })).map((mod) => (
                <Option key={mod} value={mod}>
                  {t(`ai.automation.modules.${mod}`)}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="trigger_event"
            label={t("ai.automation.eventType")}
            rules={[{ required: true }]}
          >
            <Select>
              {Object.keys(t("ai.automation.events", { returnObjects: true })).map((event) => (
                <Option key={event} value={event}>
                  {t(`ai.automation.events.${event}`)}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="action_type"
            label={t("ai.automation.actionType")}
            rules={[{ required: true }]}
          >
            <Select>
              {Object.keys(t("ai.automation.actions", { returnObjects: true })).map((action) => (
                <Option key={action} value={action}>
                  {t(`ai.automation.actions.${action}`)}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              {t("ai.automation.create")}
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Workflow Detail Modal */}
      <Modal
        title={t("ai.automation.workflowDetails")}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
      >
        {selectedWorkflow && (
          <div>
            <Paragraph>
              <Text strong>{t("ai.automation.name")}:</Text> {selectedWorkflow.name}
            </Paragraph>
            <Paragraph>
              <Text strong>{t("ai.automation.workflowDescription")}:</Text>{" "}
              {selectedWorkflow.description || "-"}
            </Paragraph>
            <Paragraph>
              <Text strong>{t("ai.automation.module")}:</Text>{" "}
              <Tag color={getModuleColor(selectedWorkflow.trigger_module)}>
                {t(`ai.automation.modules.${selectedWorkflow.trigger_module}`)}
              </Tag>
            </Paragraph>
            <Paragraph>
              <Text strong>{t("ai.automation.eventType")}:</Text>{" "}
              <Tag>{selectedWorkflow.trigger_event}</Tag>
            </Paragraph>
            <Paragraph>
              <Text strong>{t("ai.automation.actionType")}:</Text>{" "}
              <Tag>{selectedWorkflow.action_type}</Tag>
            </Paragraph>
            <Divider />
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title={t("ai.automation.executions")}
                  value={selectedWorkflow.total_executions}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title={t("ai.automation.successCount")}
                  value={selectedWorkflow.success_count}
                  valueStyle={{ color: "#52c41a" }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title={t("ai.automation.failCount")}
                  value={selectedWorkflow.fail_count}
                  valueStyle={{ color: "#ff4d4f" }}
                />
              </Col>
            </Row>
            <Paragraph style={{ marginTop: 16 }}>
              <Text strong>{t("ai.automation.createdAt")}:</Text>{" "}
              {new Date(selectedWorkflow.created_at).toLocaleString()}
            </Paragraph>
          </div>
        )}
      </Modal>
    </div>
  );
};

export { AIAutomationDashboard };
