import React, { useState, useEffect } from "react";
import {
  Card,
  List,
  Typography,
  Space,
  Spin,
  Tag,
  Button,
  Badge,
  Modal,
  Descriptions,
  Empty,
  Select,
  Switch,
  message,
  Row,
  Col,
} from "antd";
import {
  BulbOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  FilterOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import apiClient from "../../../services/api";

const { Title, Text, Paragraph } = Typography;

interface Insight {
  id: number;
  insight_type: string;
  severity: string;
  module: string;
  title: string;
  description: string;
  data: any;
  is_read: boolean;
  is_dismissed: boolean;
  created_at: string;
}

interface AIInsightsPanelProps {
  module?: string;
  showUnreadOnly?: boolean;
}

const AIInsightsPanel: React.FC<AIInsightsPanelProps> = ({
  module: filterModule,
  showUnreadOnly = false,
}) => {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [selectedInsight, setSelectedInsight] = useState<Insight | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [showUnreadOnly, setShowUnreadOnly] = useState(showUnreadOnly);
  const [selectedModule, setSelectedModule] = useState<string | undefined>(filterModule);
  const { t } = useTranslation();

  useEffect(() => {
    fetchInsights();
  }, [selectedModule, showUnreadOnly]);

  const fetchInsights = async () => {
    try {
      const params: any = {
        limit: 50,
        unread_only: showUnreadOnly,
      };
      if (selectedModule) {
        params.module = selectedModule;
      }

      const [insightsRes, countRes] = await Promise.all([
        apiClient.get("/ai/insights", { params }),
        apiClient.get("/ai/insights/unread-count"),
      ]);
      setInsights(insightsRes.data);
      setUnreadCount(countRes.data.unread_count);
    } catch (err) {
      console.error("Failed to fetch insights:", err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await apiClient.post(`/ai/insights/${id}/read`);
      setInsights((prev) =>
        prev.map((insight) =>
          insight.id === id ? { ...insight, is_read: true } : insight
        )
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      message.error("Failed to mark as read");
    }
  };

  const dismissInsight = async (id: number) => {
    try {
      await apiClient.post(`/ai/insights/${id}/dismiss`);
      setInsights((prev) => prev.filter((insight) => insight.id !== id));
      message.success("Insight dismissed");
    } catch (err) {
      message.error("Failed to dismiss insight");
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: "red",
      high: "orange",
      medium: "gold",
      low: "blue",
      info: "cyan",
    };
    return colors[severity] || "default";
  };

  const getModuleColor = (module: string) => {
    const colors: Record<string, string> = {
      inventory: "green",
      sales: "blue",
      finance: "gold",
      hr: "purple",
      crm: "cyan",
      procurement: "orange",
      cross_module: "magenta",
    };
    return colors[module] || "default";
  };

  const getInsightIcon = (severity: string) => {
    switch (severity) {
      case "critical":
      case "high":
        return <WarningOutlined style={{ color: "#ff4d4f" }} />;
      case "medium":
        return <BulbOutlined style={{ color: "#faad14" }} />;
      default:
        return <BulbOutlined style={{ color: "#1677ff" }} />;
    }
  };

  const modules = [
    { value: "inventory", label: t("ai.automation.modules.inventory") },
    { value: "sales", label: t("ai.automation.modules.sales") },
    { value: "finance", label: t("ai.automation.modules.finance") },
    { value: "hr", label: t("ai.automation.modules.hr") },
    { value: "crm", label: t("ai.automation.modules.crm") },
    { value: "procurement", label: t("ai.automation.modules.procurement") },
    { value: "cross_module", label: "Cross-Module" },
  ];

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: "center", padding: "40px 0" }}>
          <Spin />
        </div>
      </Card>
    );
  }

  return (
    <div style={{ padding: "24px" }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2}>
            <BulbOutlined style={{ marginRight: 8, color: "#faad14" }} />
            {t("ai.insights.title")}
            <Badge count={unreadCount} style={{ marginLeft: 8 }} />
          </Title>
        </Col>
        <Col>
          <Space>
            <Select
              placeholder={t("ai.chat.selectModule")}
              allowClear
              style={{ width: 150 }}
              value={selectedModule}
              onChange={setSelectedModule}
              options={modules}
            />
            <Space>
              <Text>{t("ai.insights.markAsRead")}</Text>
              <Switch
                checked={showUnreadOnly}
                onChange={setShowUnreadOnly}
              />
            </Space>
          </Space>
        </Col>
      </Row>

      {insights.length === 0 ? (
        <Card>
          <Empty description={t("ai.insights.noInsights")} />
        </Card>
      ) : (
        <List
          dataSource={insights}
          renderItem={(insight) => (
            <Card
              size="small"
              style={{
                marginBottom: 12,
                backgroundColor: insight.is_read ? "transparent" : "#f6ffed",
                borderLeft: `4px solid ${
                  insight.severity === "critical" || insight.severity === "high"
                    ? "#ff4d4f"
                    : "#1677ff"
                }`,
              }}
            >
              <List.Item
                actions={[
                  !insight.is_read && (
                    <Button
                      type="link"
                      icon={<EyeOutlined />}
                      onClick={() => markAsRead(insight.id)}
                    >
                      {t("ai.insights.markAsRead")}
                    </Button>
                  ),
                  <Button
                    type="link"
                    danger
                    icon={<CloseCircleOutlined />}
                    onClick={() => dismissInsight(insight.id)}
                  >
                    {t("ai.insights.dismiss")}
                  </Button>,
                ].filter(Boolean)}
              >
                <List.Item.Meta
                  avatar={getInsightIcon(insight.severity)}
                  title={
                    <Space>
                      <Text strong>{insight.title}</Text>
                      <Tag color={getSeverityColor(insight.severity)}>
                        {t(`ai.insights.severity.${insight.severity}`)}
                      </Tag>
                      <Tag color={getModuleColor(insight.module)}>
                        {insight.module}
                      </Tag>
                    </Space>
                  }
                  description={
                    <Paragraph
                      ellipsis={{ rows: 2, expandable: true, symbol: "more" }}
                      style={{ margin: 0 }}
                    >
                      {insight.description}
                    </Paragraph>
                  }
                />
              </List.Item>
            </Card>
          )}
        />
      )}

      {/* Detail Modal */}
      <Modal
        title={t("ai.insights.detail")}
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
      >
        {selectedInsight && (
          <Descriptions bordered column={1}>
            <Descriptions.Item label={t("ai.insights.title")}>
              {selectedInsight.title}
            </Descriptions.Item>
            <Descriptions.Item label={t("ai.insights.severity.severity")}>
              <Tag color={getSeverityColor(selectedInsight.severity)}>
                {t(`ai.insights.severity.${selectedInsight.severity}`)}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label={t("ai.automation.module")}>
              <Tag color={getModuleColor(selectedInsight.module)}>
                {selectedInsight.module}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label={t("ai.insights.detail")}>
              {selectedInsight.description}
            </Descriptions.Item>
            <Descriptions.Item label={t("ai.automation.createdAt")}>
              {new Date(selectedInsight.created_at).toLocaleString()}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export { AIInsightsPanel };
