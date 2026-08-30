import React, { useState, useEffect, useCallback } from "react";
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
  Select,
  Tabs,
  Empty,
  message,
  Collapse,
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
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  LinkOutlined,
  ExperimentOutlined,
  ThunderboltOutlined,
  SafetyOutlined,
  InboxOutlined,
  AccountBookOutlined,
  ToolOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import apiClient from "../../../services/api";

const { Title, Paragraph, Text } = Typography;
const { TabPane } = Tabs;

interface ModuleInsight {
  module: string;
  insight_type: string;
  title: string;
  description: string;
  severity: string;
  data?: any;
  confidence?: number;
}

interface ModulePrediction {
  module: string;
  prediction_type: string;
  predictions: any[];
  confidence: number;
  model: string;
  generated_at: string;
}

interface ModuleRecommendation {
  module: string;
  recommendations: any[];
  priority: string;
  generated_at: string;
}

interface CrossModuleDashboard {
  timestamp: string;
  modules_analyzed: number;
  insights: any[];
  predictions: any[];
  recommendations: any[];
  summary: {
    total_insights: number;
    critical: number;
    high: number;
    medium: number;
    total_predictions: number;
    total_recommendations: number;
  };
}

interface CrossModuleCorrelation {
  timestamp: string;
  correlations: any[];
  modules_analyzed: string[];
}

const MODULE_COLORS: Record<string, string> = {
  inventory: "green",
  finance: "gold",
  hr: "purple",
  sales: "blue",
  crm: "cyan",
  procurement: "orange",
  bi: "magenta",
  hse: "red",
  support: "geekblue",
  documents: "default",
  contracts: "lime",
  settings: "default",
  messages: "blue",
  tasks: "green",
  projects: "purple",
  quality: "cyan",
  budget: "gold",
  auth: "red",
  orders: "blue",
};

const MODULE_ICONS: Record<string, React.ReactNode> = {
  inventory: <InboxOutlined />,
  finance: <DollarOutlined />,
  hr: <UserOutlined />,
  sales: <RiseOutlined />,
  crm: <TeamOutlined />,
  procurement: <ShoppingCartOutlined />,
  bi: <BarChartOutlined />,
  hse: <SafetyOutlined />,
  support: <ToolOutlined />,
  documents: <FileTextOutlined />,
  contracts: <FileTextOutlined />,
  settings: <ThunderboltOutlined />,
  messages: <BulbOutlined />,
  tasks: <CheckCircleOutlined />,
  projects: <ExperimentOutlined />,
  quality: <CheckCircleOutlined />,
  budget: <DollarOutlined />,
  auth: <WarningOutlined />,
  orders: <ShoppingCartOutlined />,
};

const AIAnalyticsPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [dashboard, setDashboard] = useState<CrossModuleDashboard | null>(null);
  const [correlations, setCorrelations] = useState<CrossModuleCorrelation | null>(null);
  const [selectedModule, setSelectedModule] = useState<string>("inventory");
  const [moduleInsights, setModuleInsights] = useState<ModuleInsight[]>([]);
  const [modulePredictions, setModulePredictions] = useState<ModulePrediction | null>(null);
  const [moduleRecommendations, setModuleRecommendations] = useState<ModuleRecommendation | null>(null);
  const [moduleAnalytics, setModuleAnalytics] = useState<any>(null);
  const [loadingModule, setLoadingModule] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    fetchDashboard();
    fetchCorrelations();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get("/ai/modules/cross-module/dashboard");
      setDashboard(response.data);
    } catch (err) {
      console.error("Failed to fetch dashboard:", err);
      message.error("خطا در بارگذاری داشبورد");
    } finally {
      setLoading(false);
    }
  };

  const fetchCorrelations = async () => {
    try {
      const response = await apiClient.get("/ai/modules/cross-module/correlations");
      setCorrelations(response.data);
    } catch (err) {
      console.error("Failed to fetch correlations:", err);
    }
  };

  const fetchModuleData = useCallback(async (module: string) => {
    setLoadingModule(true);
    try {
      const [insightsRes, predictionsRes, recommendationsRes, analyticsRes] = await Promise.allSettled([
        apiClient.get(`/ai/modules/${module}/insights`),
        apiClient.get(`/ai/modules/${module}/predictions`),
        apiClient.get(`/ai/modules/${module}/recommendations`),
        apiClient.get(`/ai/modules/${module}/analytics`),
      ]);

      if (insightsRes.status === "fulfilled") setModuleInsights(insightsRes.value.data);
      if (predictionsRes.status === "fulfilled") setModulePredictions(predictionsRes.value.data);
      if (recommendationsRes.status === "fulfilled") setModuleRecommendations(recommendationsRes.value.data);
      if (analyticsRes.status === "fulfilled") setModuleAnalytics(analyticsRes.value.data);
    } catch (err) {
      console.error("Failed to fetch module data:", err);
    } finally {
      setLoadingModule(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === "module") {
      fetchModuleData(selectedModule);
    }
  }, [selectedModule, activeTab, fetchModuleData]);

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

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      critical: "red",
      high: "orange",
      medium: "gold",
      low: "blue",
    };
    return colors[priority] || "default";
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "100px 0" }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>در حال بارگذاری تحلیل‌ها...</Text>
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
            تحلیل‌های هوش مصنوعی
          </Title>
        </Col>
        <Col>
          <Button icon={<ReloadOutlined />} onClick={fetchDashboard}>
            بروزرسانی
          </Button>
        </Col>
      </Row>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        {/* Tab 1: Cross-Module Overview */}
        <TabPane tab={<span><BarChartOutlined /> نمای کلی</span>} key="overview">
          {dashboard && (
            <>
              {/* Summary Stats */}
              <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="ماژول‌های تحلیل شده"
                      value={dashboard.modules_analyzed}
                      prefix={<RobotOutlined style={{ color: "#1677ff" }} />}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="بینش‌ها"
                      value={dashboard.summary.total_insights}
                      prefix={<BulbOutlined style={{ color: "#faad14" }} />}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="پیش‌بینی‌ها"
                      value={dashboard.summary.total_predictions}
                      prefix={<LineChartOutlined style={{ color: "#52c41a" }} />}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="توصیه‌ها"
                      value={dashboard.summary.total_recommendations}
                      prefix={<ThunderboltOutlined style={{ color: "#722ed1" }} />}
                    />
                  </Card>
                </Col>
              </Row>

              {/* Severity Breakdown */}
              <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                <Col span={8}>
                  <Card size="small">
                    <Space>
                      <Badge color="red" />
                      <Text>بحرانی: {dashboard.summary.critical}</Text>
                    </Space>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small">
                    <Space>
                      <Badge color="orange" />
                      <Text>بالا: {dashboard.summary.high}</Text>
                    </Space>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small">
                    <Space>
                      <Badge color="gold" />
                      <Text>متوسط: {dashboard.summary.medium}</Text>
                    </Space>
                  </Card>
                </Col>
              </Row>

              {/* Insights */}
              <Card
                title={
                  <Space>
                    <BulbOutlined style={{ color: "#faad14" }} />
                    <span>بینش‌ها</span>
                    <Badge count={dashboard.insights.length} />
                  </Space>
                }
                style={{ marginBottom: 16 }}
              >
                {dashboard.insights.length === 0 ? (
                  <Empty description="بینشی یافت نشد" />
                ) : (
                  <List
                    dataSource={dashboard.insights}
                    renderItem={(insight: any) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={
                            insight.severity === "critical" || insight.severity === "high" ? (
                              <WarningOutlined style={{ color: "#ff4d4f", fontSize: 20 }} />
                            ) : (
                              <BulbOutlined style={{ color: "#1677ff", fontSize: 20 }} />
                            )
                          }
                          title={
                            <Space>
                              <Text>{insight.title}</Text>
                              <Tag color={getSeverityColor(insight.severity)}>
                                {insight.severity}
                              </Tag>
                              {insight.module && (
                                <Tag color={MODULE_COLORS[insight.module]}>
                                  {insight.module}
                                </Tag>
                              )}
                            </Space>
                          }
                          description={insight.description}
                        />
                      </List.Item>
                    )}
                  />
                )}
              </Card>

              {/* Predictions */}
              <Card
                title={
                  <Space>
                    <LineChartOutlined style={{ color: "#52c41a" }} />
                    <span>پیش‌بینی‌ها</span>
                    <Badge count={dashboard.predictions.length} />
                  </Space>
                }
                style={{ marginBottom: 16 }}
              >
                {dashboard.predictions.length === 0 ? (
                  <Empty description="پیش‌بینی‌ای یافت نشد" />
                ) : (
                  <List
                    dataSource={dashboard.predictions}
                    renderItem={(pred: any) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={<LineChartOutlined style={{ color: "#52c41a", fontSize: 20 }} />}
                          title={
                            <Space>
                              <Text>{pred.metric || pred.period || "پیش‌بینی"}</Text>
                              {pred.module && (
                                <Tag color={MODULE_COLORS[pred.module]}>
                                  {pred.module}
                                </Tag>
                              )}
                            </Space>
                          }
                          description={
                            <Space direction="vertical" size={4}>
                              {Object.entries(pred)
                                .filter(([key]) => !["module", "metric", "period"].includes(key))
                                .map(([key, value]) => (
                                  <Text key={key} type="secondary">
                                    {key}: {typeof value === "object" ? JSON.stringify(value) : String(value)}
                                  </Text>
                                ))}
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                )}
              </Card>

              {/* Recommendations */}
              <Card
                title={
                  <Space>
                    <ThunderboltOutlined style={{ color: "#722ed1" }} />
                    <span>توصیه‌ها</span>
                    <Badge count={dashboard.recommendations.length} />
                  </Space>
                }
              >
                {dashboard.recommendations.length === 0 ? (
                  <Empty description="توصیه‌ای یافت نشد" />
                ) : (
                  <List
                    dataSource={dashboard.recommendations}
                    renderItem={(rec: any) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={<ThunderboltOutlined style={{ color: "#722ed1", fontSize: 20 }} />}
                          title={
                            <Space>
                              <Text>{rec.action || "توصیه"}</Text>
                              {rec.priority && (
                                <Tag color={getPriorityColor(rec.priority)}>
                                  {rec.priority}
                                </Tag>
                              )}
                              {rec.module && (
                                <Tag color={MODULE_COLORS[rec.module]}>
                                  {rec.module}
                                </Tag>
                              )}
                            </Space>
                          }
                          description={rec.reason || rec.description || ""}
                        />
                      </List.Item>
                    )}
                  />
                )}
              </Card>
            </>
          )}
        </TabPane>

        {/* Tab 2: Cross-Module Correlations */}
        <TabPane tab={<span><LinkOutlined /> همبستگی‌ها</span>} key="correlations">
          {correlations && (
            <>
              <Card
                title={
                  <Space>
                    <LinkOutlined style={{ color: "#1677ff" }} />
                    <span>همبستگی‌های بین ماژولی</span>
                    <Badge count={correlations.correlations.length} />
                  </Space>
                }
              >
                <Paragraph type="secondary" style={{ marginBottom: 16 }}>
                  ماژول‌های تحلیل شده: {correlations.modules_analyzed.join(", ")}
                </Paragraph>
                {correlations.correlations.length === 0 ? (
                  <Empty description="همبستگی‌ای یافت نشد" />
                ) : (
                  <List
                    dataSource={correlations.correlations}
                    renderItem={(corr: any) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={
                            corr.type === "risk" ? (
                              <WarningOutlined style={{ color: "#ff4d4f", fontSize: 20 }} />
                            ) : (
                              <BulbOutlined style={{ color: "#1677ff", fontSize: 20 }} />
                            )
                          }
                          title={
                            <Space>
                              <Text>{corr.title}</Text>
                              <Tag color={getSeverityColor(corr.severity)}>
                                {corr.severity}
                              </Tag>
                              {corr.modules?.map((mod: string) => (
                                <Tag key={mod} color={MODULE_COLORS[mod]}>
                                  {mod}
                                </Tag>
                              ))}
                            </Space>
                          }
                          description={
                            <Space direction="vertical" size={4}>
                              <Text>{corr.description}</Text>
                              {corr.recommendation && (
                                <Text type="secondary">
                                  <ThunderboltOutlined style={{ marginLeft: 4 }} />
                                  {corr.recommendation}
                                </Text>
                              )}
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                )}
              </Card>
            </>
          )}
        </TabPane>

        {/* Tab 3: Per-Module Deep Dive */}
        <TabPane tab={<span><ExperimentOutlined /> تحلیل ماژول</span>} key="module">
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Select
                value={selectedModule}
                onChange={setSelectedModule}
                style={{ width: "100%" }}
                placeholder="ماژول را انتخاب کنید"
              >
                {[
                  "inventory", "finance", "hr", "sales", "crm", "procurement",
                  "bi", "hse", "support", "documents", "contracts", "settings",
                  "messages", "tasks", "projects", "quality", "budget", "auth", "orders",
                ].map((mod) => (
                  <Select.Option key={mod} value={mod}>
                    {MODULE_ICONS[mod]} {mod}
                  </MenuItem>
                ))}
              </Select>
            </Col>
            <Col>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => fetchModuleData(selectedModule)}
                loading={loadingModule}
              >
                بارگذاری مجدد
              </Button>
            </Col>
          </Row>

          {loadingModule ? (
            <div style={{ textAlign: "center", padding: "60px 0" }}>
              <Spin size="large" />
            </div>
          ) : (
            <Row gutter={[16, 16]}>
              {/* Module Analytics Summary */}
              {moduleAnalytics && (
                <Col span={24}>
                  <Card
                    title={
                      <Space>
                        {MODULE_ICONS[selectedModule]}
                        <span>خلاصه تحلیل {selectedModule}</span>
                      </Space>
                    }
                  >
                    <Row gutter={[16, 16]}>
                      {moduleAnalytics.summary &&
                        Object.entries(moduleAnalytics.summary).map(([key, value]) => (
                          <Col span={4} key={key}>
                            <Card size="small">
                              <Statistic
                                title={key}
                                value={typeof value === "number" ? value : String(value)}
                              />
                            </Card>
                          </Col>
                        ))}
                    </Row>
                    {moduleAnalytics.insights?.length > 0 && (
                      <>
                        <Divider />
                        <List
                          dataSource={moduleAnalytics.insights}
                          renderItem={(insight: any) => (
                            <List.Item>
                              <List.Item.Meta
                                avatar={
                                  <BulbOutlined
                                    style={{
                                      color: insight.severity === "high" ? "#ff4d4f" : "#1677ff",
                                    }}
                                  />
                                }
                                title={
                                  <Space>
                                    <Text>{insight.title}</Text>
                                    <Tag color={getSeverityColor(insight.severity)}>
                                      {insight.severity}
                                    </Tag>
                                  </Space>
                                }
                                description={insight.description}
                              />
                            </List.Item>
                          )}
                        />
                      </>
                    )}
                  </Card>
                </Col>
              )}

              {/* Insights */}
              <Col span={12}>
                <Card
                  title={
                    <Space>
                      <BulbOutlined style={{ color: "#faad14" }} />
                      <span>بینش‌ها</span>
                    </Space>
                  }
                  style={{ height: "100%" }}
                >
                  {moduleInsights.length === 0 ? (
                    <Empty description="بینشی یافت نشد" />
                  ) : (
                    <List
                      dataSource={moduleInsights}
                      renderItem={(insight: any) => (
                        <List.Item>
                          <List.Item.Meta
                            avatar={
                              <BulbOutlined
                                style={{
                                  color: insight.severity === "high" ? "#ff4d4f" : "#1677ff",
                                }}
                              />
                            }
                            title={
                              <Space>
                                <Text>{insight.title}</Text>
                                <Tag color={getSeverityColor(insight.severity)}>
                                  {insight.severity}
                                </Tag>
                              </Space>
                            }
                            description={insight.description}
                          />
                        </List.Item>
                      )}
                    />
                  )}
                </Card>
              </Col>

              {/* Predictions */}
              <Col span={12}>
                <Card
                  title={
                    <Space>
                      <LineChartOutlined style={{ color: "#52c41a" }} />
                      <span>پیش‌بینی‌ها</span>
                    </Space>
                  }
                  style={{ height: "100%" }}
                >
                  {!modulePredictions || modulePredictions.predictions.length === 0 ? (
                    <Empty description="پیش‌بینی‌ای یافت نشد" />
                  ) : (
                    <List
                      dataSource={modulePredictions.predictions}
                      renderItem={(pred: any) => (
                        <List.Item>
                          <List.Item.Meta
                            avatar={<LineChartOutlined style={{ color: "#52c41a" }} />}
                            title={<Text>{pred.metric || pred.period || "پیش‌بینی"}</Text>}
                            description={
                              <Space direction="vertical" size={2}>
                                {Object.entries(pred)
                                  .filter(([key]) => !["metric", "period"].includes(key))
                                  .map(([key, value]) => (
                                    <Text key={key} type="secondary" style={{ fontSize: 12 }}>
                                      {key}: {String(value)}
                                    </Text>
                                  ))}
                              </Space>
                            }
                          />
                        </List.Item>
                      )}
                    />
                  )}
                </Card>
              </Col>

              {/* Recommendations */}
              <Col span={24}>
                <Card
                  title={
                    <Space>
                      <ThunderboltOutlined style={{ color: "#722ed1" }} />
                      <span>توصیه‌ها</span>
                    </Space>
                  }
                >
                  {!moduleRecommendations || moduleRecommendations.recommendations.length === 0 ? (
                    <Empty description="توصیه‌ای یافت نشد" />
                  ) : (
                    <List
                      dataSource={moduleRecommendations.recommendations}
                      renderItem={(rec: any) => (
                        <List.Item>
                          <List.Item.Meta
                            avatar={<ThunderboltOutlined style={{ color: "#722ed1" }} />}
                            title={
                              <Space>
                                <Text>{rec.action}</Text>
                                {rec.priority && (
                                  <Tag color={getPriorityColor(rec.priority)}>
                                    {rec.priority}
                                  </Tag>
                                )}
                              </Space>
                            }
                            description={rec.reason || rec.description || ""}
                          />
                        </List.Item>
                      )}
                    />
                  )}
                </Card>
              </Col>
            </Row>
          )}
        </TabPane>
      </Tabs>
    </div>
  );
};

export default AIAnalyticsPage;
