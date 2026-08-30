import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  List,
  Tag,
  Button,
  Space,
  Spin,
  Alert,
  Badge,
  Tooltip,
  Progress,
  Divider,
  message,
} from "antd";
import {
  RobotOutlined,
  BulbOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  UserOutlined,
  TeamOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  RiseOutlined,
  FallOutlined,
  ReloadOutlined,
  PlusOutlined,
  ArrowRightOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import apiClient from "../../../services/api";

const { Title, Paragraph, Text } = Typography;

interface CrossModuleAnalysis {
  timestamp: string;
  modules: {
    inventory?: any;
    sales?: any;
    finance?: any;
    hr?: any;
    crm?: any;
    procurement?: any;
  };
  cross_module_insights: Array<{
    type: string;
    severity: string;
    title: string;
    description: string;
    modules?: string[];
  }>;
}

const AIAnalyticsDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState<CrossModuleAnalysis | null>(null);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    fetchAnalysis();
  }, []);

  const fetchAnalysis = async () => {
    try {
      const response = await apiClient.get("/ai/analytics/cross-module");
      setAnalysis(response.data);
    } catch (err) {
      console.error("Failed to fetch analysis:", err);
      message.error("Failed to load analytics data");
    } finally {
      setLoading(false);
    }
  };

  const generateInsights = async () => {
    setInsightsLoading(true);
    try {
      await apiClient.post("/ai/analytics/generate-insights");
      message.success("Insights generated successfully");
      fetchAnalysis();
    } catch (err) {
      message.error("Failed to generate insights");
    } finally {
      setInsightsLoading(false);
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

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "100px 0" }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>{t("ai.analytics.title")}...</Text>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "24px" }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2}>
            <RobotOutlined style={{ marginRight: 8, color: "#1677ff" }} />
            {t("ai.analytics.title")}
          </Title>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchAnalysis}
            >
              {t("ai.analytics.refresh")}
            </Button>
            <Button
              type="primary"
              icon={<BulbOutlined />}
              onClick={generateInsights}
              loading={insightsLoading}
            >
              {t("ai.analytics.generateInsights")}
            </Button>
          </Space>
        </Col>
      </Row>

      {analysis && (
        <>
          {/* Module Stats */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            {analysis.modules.inventory && (
              <Col span={4}>
                <Card size="small">
                  <Statistic
                    title={t("ai.analytics.inventoryAnalytics")}
                    value={analysis.modules.inventory.summary?.total_items || 0}
                    prefix={<ShoppingCartOutlined />}
                  />
                </Card>
              </Col>
            )}
            {analysis.modules.sales && (
              <Col span={4}>
                <Card size="small">
                  <Statistic
                    title={t("ai.analytics.salesAnalytics")}
                    value={analysis.modules.sales.summary?.total_orders || 0}
                    prefix={<DollarOutlined />}
                  />
                </Card>
              </Col>
            )}
            {analysis.modules.hr && (
              <Col span={4}>
                <Card size="small">
                  <Statistic
                    title={t("ai.analytics.hrAnalytics")}
                    value={analysis.modules.hr.summary?.total_employees || 0}
                    prefix={<UserOutlined />}
                  />
                </Card>
              </Col>
            )}
            {analysis.modules.crm && (
              <Col span={4}>
                <Card size="small">
                  <Statistic
                    title={t("ai.analytics.crmAnalytics")}
                    value={analysis.modules.crm.summary?.total_customers || 0}
                    prefix={<TeamOutlined />}
                  />
                </Card>
              </Col>
            )}
          </Row>

          {/* Cross-Module Insights */}
          <Card
            title={
              <Space>
                <BulbOutlined style={{ color: "#faad14" }} />
                <span>{t("ai.analytics.crossModuleInsights")}</span>
                <Badge count={analysis.cross_module_insights?.length || 0} />
              </Space>
            }
          >
            {analysis.cross_module_insights?.length === 0 ? (
              <div style={{ textAlign: "center", padding: "40px 0" }}>
                <Text type="secondary">{t("ai.insights.noInsights")}</Text>
              </div>
            ) : (
              <List
                dataSource={analysis.cross_module_insights}
                renderItem={(insight) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        insight.severity === "high" || insight.severity === "critical" ? (
                          <WarningOutlined style={{ color: "#ff4d4f", fontSize: 20 }} />
                        ) : (
                          <BulbOutlined style={{ color: "#1677ff", fontSize: 20 }} />
                        )
                      }
                      title={
                        <Space>
                          <Text>{insight.title}</Text>
                          <Tag color={getSeverityColor(insight.severity)}>
                            {t(`ai.insights.severity.${insight.severity}`)}
                          </Tag>
                          {insight.modules?.map((mod) => (
                            <Tag key={mod} color={getModuleColor(mod)}>
                              {mod}
                            </Tag>
                          ))}
                        </Space>
                      }
                      description={insight.description}
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </>
      )}
    </div>
  );
};

export { AIAnalyticsDashboard };
