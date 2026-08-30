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
  Badge,
  Tooltip,
  Progress,
  Divider,
  Empty,
} from "antd";
import {
  RobotOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  FileTextOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  UserOutlined,
  WarningOutlined,
  ArrowRightOutlined,
  ClockCircleOutlined,
  LineChartOutlined,
  LinkOutlined,
  CheckCircleOutlined,
  RiseOutlined,
  FallOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import apiClient from "../../../services/api";

const { Text, Paragraph, Title } = Typography;

// ═══════════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════════

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

interface ModuleAnalytics {
  module: string;
  summary: Record<string, any>;
  insights: any[];
  generated_at: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════════

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

const MODULE_LABELS: Record<string, string> = {
  inventory: "انبار",
  finance: "مالی",
  hr: "منابع انسانی",
  sales: "فروش",
  crm: "مشتریان",
  procurement: "تدارکات",
  bi: "هوش تجاری",
  hse: "HSE",
  support: "پشتیبانی",
  documents: "اسناد",
  contracts: "قراردادها",
  settings: "تنظیمات",
  messages: "پیام‌ها",
  tasks: "وظایف",
  projects: "پروژه‌ها",
  quality: "کیفیت",
  budget: "بودجه",
  auth: "امنیت",
  orders: "سفارشات",
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

// ═══════════════════════════════════════════════════════════════════════════════
// Widget 1: AI Executive Summary — Cross-module stats at a glance
// ═══════════════════════════════════════════════════════════════════════════════

const AISummaryWidget: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState<CrossModuleDashboard | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await apiClient.get("/ai/modules/cross-module/dashboard");
      setDashboard(response.data);
    } catch (err) {
      console.error("Failed to fetch AI dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: "center", padding: "40px 0" }}>
          <Spin />
        </div>
      </Card>
    );
  }

  if (!dashboard) return null;

  return (
    <Card
      title={
        <Space>
          <RobotOutlined style={{ color: "#1677ff" }} />
          <span>خلاصه هوش مصنوعی</span>
        </Space>
      }
      extra={
        <Button
          type="link"
          icon={<ArrowRightOutlined />}
          onClick={() => navigate("/ai/analytics")}
        >
          مشاهده همه
        </Button>
      }
      style={{ height: "100%" }}
    >
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Statistic
            title="ماژول‌ها"
            value={dashboard.modules_analyzed}
            prefix={<RobotOutlined style={{ color: "#1677ff" }} />}
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="بینش‌ها"
            value={dashboard.summary.total_insights}
            prefix={<BulbOutlined style={{ color: "#faad14" }} />}
            suffix={
              dashboard.summary.critical > 0 ? (
                <Tooltip title={`${dashboard.summary.critical} بحرانی`}>
                  <Badge color="red" count={dashboard.summary.critical} style={{ marginLeft: 4 }} />
                </Tooltip>
              ) : null
            }
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="توصیه‌ها"
            value={dashboard.summary.total_recommendations}
            prefix={<ThunderboltOutlined style={{ color: "#722ed1" }} />}
          />
        </Col>
      </Row>

      <Divider style={{ margin: "12px 0" }} />

      <Row gutter={[8, 8]}>
        <Col span={8}>
          <div style={{ textAlign: "center" }}>
            <Badge color="red" />
            <Text style={{ marginLeft: 4, fontSize: 12 }}>بحرانی: {dashboard.summary.critical}</Text>
          </div>
        </Col>
        <Col span={8}>
          <div style={{ textAlign: "center" }}>
            <Badge color="orange" />
            <Text style={{ marginLeft: 4, fontSize: 12 }}>بالا: {dashboard.summary.high}</Text>
          </div>
        </Col>
        <Col span={8}>
          <div style={{ textAlign: "center" }}>
            <Badge color="gold" />
            <Text style={{ marginLeft: 4, fontSize: 12 }}>متوسط: {dashboard.summary.medium}</Text>
          </div>
        </Col>
      </Row>
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Widget 2: AI Insights — Top insights across all modules
// ═══════════════════════════════════════════════════════════════════════════════

const AIInsightsWidget: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      const response = await apiClient.get("/ai/modules/cross-module/dashboard");
      // Sort by severity and take top 8
      const severityOrder: Record<string, number> = {
        critical: 0, high: 1, medium: 2, low: 3, info: 4,
      };
      const sorted = [...(response.data.insights || [])].sort(
        (a, b) => (severityOrder[a.severity] ?? 5) - (severityOrder[b.severity] ?? 5)
      );
      setInsights(sorted.slice(0, 8));
    } catch (err) {
      console.error("Failed to fetch insights:", err);
    } finally {
      setLoading(false);
    }
  };

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
    <Card
      title={
        <Space>
          <BulbOutlined style={{ color: "#faad14" }} />
          <span>بینش‌های هوش مصنوعی</span>
          {insights.length > 0 && <Badge count={insights.length} />}
        </Space>
      }
      extra={
        <Button
          type="link"
          icon={<ArrowRightOutlined />}
          onClick={() => navigate("/ai/analytics")}
        >
          مشاهده همه
        </Button>
      }
      style={{ height: "100%" }}
    >
      {insights.length === 0 ? (
        <div style={{ textAlign: "center", padding: "20px 0" }}>
          <Text type="secondary">بینشی یافت نشد</Text>
        </div>
      ) : (
        <List
          size="small"
          dataSource={insights}
          renderItem={(insight: any) => (
            <List.Item
              style={{
                padding: "6px 0",
              }}
            >
              <List.Item.Meta
                avatar={
                  insight.severity === "critical" || insight.severity === "high" ? (
                    <WarningOutlined style={{ color: "#ff4d4f", fontSize: 16 }} />
                  ) : (
                    <BulbOutlined style={{ color: "#1677ff", fontSize: 16 }} />
                  )
                }
                title={
                  <Space size={4} wrap>
                    <Text ellipsis style={{ maxWidth: 180, fontSize: 13 }}>
                      {insight.title}
                    </Text>
                    <Tag color={getSeverityColor(insight.severity)} style={{ fontSize: 10, margin: 0 }}>
                      {insight.severity}
                    </Tag>
                    {insight.module && (
                      <Tag color={MODULE_COLORS[insight.module]} style={{ fontSize: 10, margin: 0 }}>
                        {MODULE_LABELS[insight.module] || insight.module}
                      </Tag>
                    )}
                  </Space>
                }
                description={
                  <Text type="secondary" ellipsis style={{ fontSize: 12 }}>
                    {insight.description}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      )}
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Widget 3: AI Recommendations — Top actions to take
// ═══════════════════════════════════════════════════════════════════════════════

const AIRecommendationsWidget: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const response = await apiClient.get("/ai/modules/cross-module/dashboard");
      const recs = response.data.recommendations || [];
      setRecommendations(recs.slice(0, 6));
    } catch (err) {
      console.error("Failed to fetch recommendations:", err);
    } finally {
      setLoading(false);
    }
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
      <Card>
        <div style={{ textAlign: "center", padding: "40px 0" }}>
          <Spin />
        </div>
      </Card>
    );
  }

  return (
    <Card
      title={
        <Space>
          <ThunderboltOutlined style={{ color: "#722ed1" }} />
          <span>توصیه‌های هوش مصنوعی</span>
          {recommendations.length > 0 && <Badge count={recommendations.length} />}
        </Space>
      }
      extra={
        <Button
          type="link"
          icon={<ArrowRightOutlined />}
          onClick={() => navigate("/ai/analytics")}
        >
          مشاهده همه
        </Button>
      }
      style={{ height: "100%" }}
    >
      {recommendations.length === 0 ? (
        <div style={{ textAlign: "center", padding: "20px 0" }}>
          <Text type="secondary">توصیه‌ای یافت نشد</Text>
        </div>
      ) : (
        <List
          size="small"
          dataSource={recommendations}
          renderItem={(rec: any) => (
            <List.Item style={{ padding: "6px 0" }}>
              <List.Item.Meta
                avatar={<ThunderboltOutlined style={{ color: "#722ed1", fontSize: 16 }} />}
                title={
                  <Space size={4} wrap>
                    <Text ellipsis style={{ maxWidth: 180, fontSize: 13 }}>
                      {rec.action}
                    </Text>
                    {rec.priority && (
                      <Tag color={getPriorityColor(rec.priority)} style={{ fontSize: 10, margin: 0 }}>
                        {rec.priority}
                      </Tag>
                    )}
                    {rec.module && (
                      <Tag color={MODULE_COLORS[rec.module]} style={{ fontSize: 10, margin: 0 }}>
                        {MODULE_LABELS[rec.module] || rec.module}
                      </Tag>
                    )}
                  </Space>
                }
                description={
                  <Text type="secondary" ellipsis style={{ fontSize: 12 }}>
                    {rec.reason || rec.description || ""}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      )}
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Widget 4: AI Predictions — Key predictions across modules
// ═══════════════════════════════════════════════════════════════════════════════

const AIPredictionsWidget: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [predictions, setPredictions] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      const response = await apiClient.get("/ai/modules/cross-module/dashboard");
      setPredictions((response.data.predictions || []).slice(0, 6));
    } catch (err) {
      console.error("Failed to fetch predictions:", err);
    } finally {
      setLoading(false);
    }
  };

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
    <Card
      title={
        <Space>
          <LineChartOutlined style={{ color: "#52c41a" }} />
          <span>پیش‌بینی‌های هوش مصنوعی</span>
          {predictions.length > 0 && <Badge count={predictions.length} />}
        </Space>
      }
      extra={
        <Button
          type="link"
          icon={<ArrowRightOutlined />}
          onClick={() => navigate("/ai/analytics")}
        >
          مشاهده همه
        </Button>
      }
      style={{ height: "100%" }}
    >
      {predictions.length === 0 ? (
        <div style={{ textAlign: "center", padding: "20px 0" }}>
          <Text type="secondary">پیش‌بینی‌ای یافت نشد</Text>
        </div>
      ) : (
        <List
          size="small"
          dataSource={predictions}
          renderItem={(pred: any) => (
            <List.Item style={{ padding: "6px 0" }}>
              <List.Item.Meta
                avatar={<LineChartOutlined style={{ color: "#52c41a", fontSize: 16 }} />}
                title={
                  <Space size={4} wrap>
                    <Text ellipsis style={{ maxWidth: 180, fontSize: 13 }}>
                      {pred.metric || pred.period || "پیش‌بینی"}
                    </Text>
                    {pred.module && (
                      <Tag color={MODULE_COLORS[pred.module]} style={{ fontSize: 10, margin: 0 }}>
                        {MODULE_LABELS[pred.module] || pred.module}
                      </Tag>
                    )}
                  </Space>
                }
                description={
                  <Space direction="vertical" size={0}>
                    {Object.entries(pred)
                      .filter(([key]) => !["module", "metric", "period"].includes(key))
                      .slice(0, 3)
                      .map(([key, value]) => (
                        <Text key={key} type="secondary" style={{ fontSize: 11 }}>
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
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Widget 5: Cross-Module Correlations
// ═══════════════════════════════════════════════════════════════════════════════

const AICorrelationsWidget: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [correlations, setCorrelations] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCorrelations();
  }, []);

  const fetchCorrelations = async () => {
    try {
      const response = await apiClient.get("/ai/modules/cross-module/correlations");
      setCorrelations((response.data.correlations || []).slice(0, 5));
    } catch (err) {
      console.error("Failed to fetch correlations:", err);
    } finally {
      setLoading(false);
    }
  };

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
    <Card
      title={
        <Space>
          <LinkOutlined style={{ color: "#1677ff" }} />
          <span>همبستگی‌های بین ماژولی</span>
          {correlations.length > 0 && <Badge count={correlations.length} />}
        </Space>
      }
      extra={
        <Button
          type="link"
          icon={<ArrowRightOutlined />}
          onClick={() => navigate("/ai/analytics")}
        >
          مشاهده همه
        </Button>
      }
      style={{ height: "100%" }}
    >
      {correlations.length === 0 ? (
        <div style={{ textAlign: "center", padding: "20px 0" }}>
          <Text type="secondary">همبستگی‌ای یافت نشد</Text>
        </div>
      ) : (
        <List
          size="small"
          dataSource={correlations}
          renderItem={(corr: any) => (
            <List.Item style={{ padding: "6px 0" }}>
              <List.Item.Meta
                avatar={
                  corr.type === "risk" ? (
                    <WarningOutlined style={{ color: "#ff4d4f", fontSize: 16 }} />
                  ) : (
                    <BulbOutlined style={{ color: "#1677ff", fontSize: 16 }} />
                  )
                }
                title={
                  <Space size={4} wrap>
                    <Text ellipsis style={{ maxWidth: 180, fontSize: 13 }}>
                      {corr.title}
                    </Text>
                    <Tag color={getSeverityColor(corr.severity)} style={{ fontSize: 10, margin: 0 }}>
                      {corr.severity}
                    </Tag>
                    {corr.modules?.map((mod: string) => (
                      <Tag key={mod} color={MODULE_COLORS[mod]} style={{ fontSize: 10, margin: 0 }}>
                        {MODULE_LABELS[mod] || mod}
                      </Tag>
                    ))}
                  </Space>
                }
                description={
                  <Text type="secondary" ellipsis style={{ fontSize: 12 }}>
                    {corr.description}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      )}
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Widget 6: AI Quick Actions — Navigation to AI pages
// ═══════════════════════════════════════════════════════════════════════════════

const AIQuickActionsWidget: React.FC = () => {
  const navigate = useNavigate();

  const actions = [
    {
      icon: <RobotOutlined />,
      title: "دستیار هوش مصنوعی",
      description: "سؤال بپرسید، تحلیل کنید",
      color: "#1677ff",
      path: "/ai/assistant",
    },
    {
      icon: <BulbOutlined />,
      title: "تحلیل‌ها",
      description: "بینش‌ها و پیش‌بینی‌ها",
      color: "#faad14",
      path: "/ai/analytics",
    },
    {
      icon: <FileTextOutlined />,
      title: "گزارشات AI",
      description: "تولید گزارش هوشمند",
      color: "#52c41a",
      path: "/ai/reports",
    },
    {
      icon: <ThunderboltOutlined />,
      title: "اتوماسیون",
      description: "گردش کار خودکار",
      color: "#722ed1",
      path: "/ai/automation",
    },
  ];

  return (
    <Card
      title={
        <Space>
          <ThunderboltOutlined style={{ color: "#faad14" }} />
          <span>دسترسی سریع AI</span>
        </Space>
      }
      style={{ height: "100%" }}
    >
      <Row gutter={[8, 8]}>
        {actions.map((action, index) => (
          <Col span={12} key={index}>
            <Card
              size="small"
              hoverable
              onClick={() => navigate(action.path)}
              style={{ textAlign: "center", cursor: "pointer" }}
            >
              <div style={{ color: action.color, fontSize: 22, marginBottom: 6 }}>
                {action.icon}
              </div>
              <Text strong style={{ fontSize: 13 }}>{action.title}</Text>
              <br />
              <Text type="secondary" style={{ fontSize: 11 }}>
                {action.description}
              </Text>
            </Card>
          </Col>
        ))}
      </Row>
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Widget 7: AI Activity — Recent AI activity
// ═══════════════════════════════════════════════════════════════════════════════

const AIActivityWidget: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [activities, setActivities] = useState<any[]>([]);
  const { t } = useTranslation();

  useEffect(() => {
    fetchActivities();
  }, []);

  const fetchActivities = async () => {
    try {
      const response = await apiClient.get("/ai/assistant/conversations", {
        params: { limit: 5 },
      });
      const acts = (response.data || []).map((conv: any) => ({
        type: "chat",
        title: conv.title,
        module: conv.module || "general",
        time: conv.updated_at,
      }));
      setActivities(acts);
    } catch (err) {
      console.error("Failed to fetch activities:", err);
    } finally {
      setLoading(false);
    }
  };

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
    <Card
      title={
        <Space>
          <ClockCircleOutlined style={{ color: "#1677ff" }} />
          <span>فعالیت‌های اخیر AI</span>
        </Space>
      }
      style={{ height: "100%" }}
    >
      {activities.length === 0 ? (
        <div style={{ textAlign: "center", padding: "20px 0" }}>
          <Text type="secondary">فعالیتی ثبت نشده</Text>
        </div>
      ) : (
        <List
          size="small"
          dataSource={activities}
          renderItem={(item: any) => (
            <List.Item style={{ padding: "6px 0" }}>
              <List.Item.Meta
                avatar={<RobotOutlined style={{ color: "#1677ff" }} />}
                title={
                  <Space>
                    <Text ellipsis style={{ maxWidth: 150, fontSize: 13 }}>
                      {item.title}
                    </Text>
                    <Tag color={MODULE_COLORS[item.module]} style={{ fontSize: 10 }}>
                      {MODULE_LABELS[item.module] || item.module}
                    </Tag>
                  </Space>
                }
                description={
                  <Text type="secondary" style={{ fontSize: 11 }}>
                    {new Date(item.time).toLocaleString("fa-IR")}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      )}
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Combined Dashboard Widget — All-in-one for main dashboard
// ═══════════════════════════════════════════════════════════════════════════════

const AIDashboardFull: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState<CrossModuleDashboard | null>(null);
  const [correlations, setCorrelations] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [dashRes, corrRes] = await Promise.allSettled([
        apiClient.get("/ai/modules/cross-module/dashboard"),
        apiClient.get("/ai/modules/cross-module/correlations"),
      ]);

      if (dashRes.status === "fulfilled") setDashboard(dashRes.value.data);
      if (corrRes.status === "fulfilled") setCorrelations(corrRes.value.data.correlations || []);
    } catch (err) {
      console.error("Failed to fetch AI dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      critical: "red", high: "orange", medium: "gold", low: "blue",
    };
    return colors[priority] || "default";
  };

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: "center", padding: "60px 0" }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>در حال بارگذاری تحلیل‌های هوش مصنوعی...</Text>
          </div>
        </div>
      </Card>
    );
  }

  if (!dashboard) return null;

  const topInsights = [...(dashboard.insights || [])]
    .sort((a: any, b: any) => {
      const order: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
      return (order[a.severity] ?? 5) - (order[b.severity] ?? 5);
    })
    .slice(0, 5);

  const topRecs = (dashboard.recommendations || []).slice(0, 5);
  const topPreds = (dashboard.predictions || []).slice(0, 5);

  return (
    <Card
      title={
        <Space>
          <RobotOutlined style={{ color: "#1677ff" }} />
          <span>داشبورد هوش مصنوعی</span>
        </Space>
      }
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchData} size="small">
            بروزرسانی
          </Button>
          <Button
            type="link"
            icon={<ArrowRightOutlined />}
            onClick={() => navigate("/ai/analytics")}
          >
            تحلیل کامل
          </Button>
        </Space>
      }
    >
      {/* Summary Stats */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Statistic
            title="ماژول‌ها"
            value={dashboard.modules_analyzed}
            prefix={<RobotOutlined style={{ color: "#1677ff" }} />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="بینش‌ها"
            value={dashboard.summary.total_insights}
            prefix={<BulbOutlined style={{ color: "#faad14" }} />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="پیش‌بینی‌ها"
            value={dashboard.summary.total_predictions}
            prefix={<LineChartOutlined style={{ color: "#52c41a" }} />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="توصیه‌ها"
            value={dashboard.summary.total_recommendations}
            prefix={<ThunderboltOutlined style={{ color: "#722ed1" }} />}
          />
        </Col>
      </Row>

      {/* Critical/High Alerts Banner */}
      {(dashboard.summary.critical > 0 || dashboard.summary.high > 0) && (
        <div style={{ marginBottom: 16 }}>
          {dashboard.summary.critical > 0 && (
            <Tag color="red" style={{ fontSize: 13, padding: "4px 12px" }}>
              <WarningOutlined /> {dashboard.summary.critical} هشدار بحرانی
            </Tag>
          )}
          {dashboard.summary.high > 0 && (
            <Tag color="orange" style={{ fontSize: 13, padding: "4px 12px" }}>
              <WarningOutlined /> {dashboard.summary.high} هشدار مهم
            </Tag>
          )}
        </div>
      )}

      <Row gutter={[16, 16]}>
        {/* Top Insights */}
        <Col span={8}>
          <Card
            size="small"
            title={
              <Space>
                <BulbOutlined style={{ color: "#faad14" }} />
                <span style={{ fontSize: 13 }}>بینش‌ها</span>
              </Space>
            }
            style={{ height: 280 }}
            bodyStyle={{ padding: "0 12px", overflow: "auto", maxHeight: 230 }}
          >
            {topInsights.length === 0 ? (
              <Empty description="ندارد" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              <List
                size="small"
                dataSource={topInsights}
                renderItem={(insight: any) => (
                  <List.Item style={{ padding: "4px 0" }}>
                    <List.Item.Meta
                      avatar={
                        insight.severity === "critical" || insight.severity === "high" ? (
                          <WarningOutlined style={{ color: "#ff4d4f", fontSize: 14 }} />
                        ) : (
                          <BulbOutlined style={{ color: "#1677ff", fontSize: 14 }} />
                        )
                      }
                      title={
                        <Space size={2}>
                          <Text ellipsis style={{ maxWidth: 120, fontSize: 12 }}>
                            {insight.title}
                          </Text>
                          <Tag color={getSeverityColor(insight.severity)} style={{ fontSize: 9, margin: 0 }}>
                            {insight.severity}
                          </Tag>
                        </Space>
                      }
                      description={
                        <Text type="secondary" ellipsis style={{ fontSize: 11 }}>
                          {insight.description}
                        </Text>
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        {/* Top Recommendations */}
        <Col span={8}>
          <Card
            size="small"
            title={
              <Space>
                <ThunderboltOutlined style={{ color: "#722ed1" }} />
                <span style={{ fontSize: 13 }}>توصیه‌ها</span>
              </Space>
            }
            style={{ height: 280 }}
            bodyStyle={{ padding: "0 12px", overflow: "auto", maxHeight: 230 }}
          >
            {topRecs.length === 0 ? (
              <Empty description="ندارد" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              <List
                size="small"
                dataSource={topRecs}
                renderItem={(rec: any) => (
                  <List.Item style={{ padding: "4px 0" }}>
                    <List.Item.Meta
                      avatar={<ThunderboltOutlined style={{ color: "#722ed1", fontSize: 14 }} />}
                      title={
                        <Space size={2}>
                          <Text ellipsis style={{ maxWidth: 120, fontSize: 12 }}>
                            {rec.action}
                          </Text>
                          {rec.priority && (
                            <Tag color={getPriorityColor(rec.priority)} style={{ fontSize: 9, margin: 0 }}>
                              {rec.priority}
                            </Tag>
                          )}
                        </Space>
                      }
                      description={
                        <Text type="secondary" ellipsis style={{ fontSize: 11 }}>
                          {rec.reason || rec.description || ""}
                        </Text>
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        {/* Top Predictions */}
        <Col span={8}>
          <Card
            size="small"
            title={
              <Space>
                <LineChartOutlined style={{ color: "#52c41a" }} />
                <span style={{ fontSize: 13 }}>پیش‌بینی‌ها</span>
              </Space>
            }
            style={{ height: 280 }}
            bodyStyle={{ padding: "0 12px", overflow: "auto", maxHeight: 230 }}
          >
            {topPreds.length === 0 ? (
              <Empty description="ندارد" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              <List
                size="small"
                dataSource={topPreds}
                renderItem={(pred: any) => (
                  <List.Item style={{ padding: "4px 0" }}>
                    <List.Item.Meta
                      avatar={<LineChartOutlined style={{ color: "#52c41a", fontSize: 14 }} />}
                      title={
                        <Space size={2}>
                          <Text ellipsis style={{ maxWidth: 120, fontSize: 12 }}>
                            {pred.metric || pred.period || "پیش‌بینی"}
                          </Text>
                          {pred.module && (
                            <Tag color={MODULE_COLORS[pred.module]} style={{ fontSize: 9, margin: 0 }}>
                              {pred.module}
                            </Tag>
                          )}
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size={0}>
                          {Object.entries(pred)
                            .filter(([key]) => !["module", "metric", "period"].includes(key))
                            .slice(0, 2)
                            .map(([key, value]) => (
                              <Text key={key} type="secondary" style={{ fontSize: 10 }}>
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
      </Row>

      {/* Cross-Module Correlations */}
      {correlations.length > 0 && (
        <Card
          size="small"
          title={
            <Space>
              <LinkOutlined style={{ color: "#1677ff" }} />
              <span style={{ fontSize: 13 }}>همبستگی‌های بین ماژولی</span>
              <Badge count={correlations.length} size="small" />
            </Space>
          }
          style={{ marginTop: 16 }}
        >
          <Row gutter={[12, 12]}>
            {correlations.slice(0, 3).map((corr: any, i: number) => (
              <Col span={8} key={i}>
                <Card size="small" style={{ height: "100%" }}>
                  <Space style={{ marginBottom: 4 }}>
                    {corr.type === "risk" ? (
                      <WarningOutlined style={{ color: "#ff4d4f" }} />
                    ) : (
                      <BulbOutlined style={{ color: "#1677ff" }} />
                    )}
                    <Tag color={getSeverityColor(corr.severity)} style={{ fontSize: 10 }}>
                      {corr.severity}
                    </Tag>
                  </Space>
                  <Text strong style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                    {corr.title}
                  </Text>
                  <Text type="secondary" style={{ fontSize: 11, display: "block" }}>
                    {corr.description}
                  </Text>
                  <Space style={{ marginTop: 4 }}>
                    {corr.modules?.map((mod: string) => (
                      <Tag key={mod} color={MODULE_COLORS[mod]} style={{ fontSize: 9 }}>
                        {mod}
                      </Tag>
                    ))}
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Exports
// ═══════════════════════════════════════════════════════════════════════════════

export {
  AISummaryWidget,
  AIInsightsWidget,
  AIRecommendationsWidget,
  AIPredictionsWidget,
  AICorrelationsWidget,
  AIQuickActionsWidget,
  AIActivityWidget,
  AIDashboardFull,
};
