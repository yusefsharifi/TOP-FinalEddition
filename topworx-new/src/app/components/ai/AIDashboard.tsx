import React, { useState, useEffect } from 'react';
import { Card, Col, Row, Statistic, Typography, Tag, Space, Spin, Alert } from 'antd';
import {
  RobotOutlined,
  ExperimentOutlined,
  AlertOutlined,
  BulbOutlined,
  CheckCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { getAIDashboard, getAllAIInsights } from '../../../api/ai';

const { Title, Text } = Typography;

interface DashboardData {
  usage: {
    total_requests: number;
    total_tokens: number;
    total_cost: number;
    avg_duration_ms: number;
  };
  unread_insights: number;
  active_workflows: number;
  recent_conversations: Array<{
    id: number;
    title: string;
    module: string;
    updated_at: string;
  }>;
  openai_configured: boolean;
  anthropic_configured: boolean;
  default_model: string;
}

interface ModuleInsights {
  inventory?: any;
  finance?: any;
  hr?: any;
  sales?: any;
  procurement?: any;
  quality?: any;
  hse?: any;
}

const AIDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [moduleInsights, setModuleInsights] = useState<ModuleInsights>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [dashboard, insights] = await Promise.all([
        getAIDashboard(),
        getAllAIInsights(['inventory', 'finance', 'hr', 'sales', 'procurement', 'quality', 'hse']),
      ]);
      setDashboardData(dashboard);
      setModuleInsights(insights.insights || {});
    } catch (err) {
      console.error('Failed to fetch AI dashboard:', err);
      setError('Failed to load AI dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>Loading AI Dashboard...</Text>
        </div>
      </div>
    );
  }

  if (error) {
    return <Alert message="Error" description={error} type="error" showIcon />;
  }

  const getModuleStatus = (moduleName: string) => {
    const insight = moduleInsights[moduleName as keyof ModuleInsights];
    if (!insight || insight.error) return { status: 'error', count: 0 };
    const keys = Object.keys(insight);
    return { status: 'active', count: keys.length };
  };

  const modules = [
    { key: 'inventory', name: 'Inventory', color: '#1890ff' },
    { key: 'finance', name: 'Finance', color: '#52c41a' },
    { key: 'hr', name: 'HR', color: '#722ed1' },
    { key: 'sales', name: 'Sales', color: '#fa8c16' },
    { key: 'procurement', name: 'Procurement', color: '#13c2c2' },
    { key: 'quality', name: 'Quality', color: '#eb2f96' },
    { key: 'hse', name: 'HSE', color: '#f5222d' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>
        <RobotOutlined /> AI Dashboard
      </Title>
      
      {/* Usage Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total AI Requests"
              value={dashboardData?.usage?.total_requests || 0}
              prefix={<ExperimentOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Tokens Used"
              value={dashboardData?.usage?.total_tokens || 0}
              suffix="tokens"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Cost"
              value={dashboardData?.usage?.total_cost || 0}
              prefix="$"
              precision={2}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Unread Insights"
              value={dashboardData?.unread_insights || 0}
              prefix={<BulbOutlined />}
              valueStyle={{ color: dashboardData?.unread_insights ? '#faad14' : '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Configuration Status */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12}>
          <Card title="AI Configuration">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>OpenAI: </Text>
                {dashboardData?.openai_configured ? (
                  <Tag color="success" icon={<CheckCircleOutlined />}>Configured</Tag>
                ) : (
                  <Tag color="warning" icon={<AlertOutlined />}>Not Configured</Tag>
                )}
              </div>
              <div>
                <Text strong>Anthropic: </Text>
                {dashboardData?.anthropic_configured ? (
                  <Tag color="success" icon={<CheckCircleOutlined />}>Configured</Tag>
                ) : (
                  <Tag color="warning" icon={<AlertOutlined />}>Not Configured</Tag>
                )}
              </div>
              <div>
                <Text strong>Default Model: </Text>
                <Tag>{dashboardData?.default_model || 'gpt-4o'}</Tag>
              </div>
              <div>
                <Text strong>Active Workflows: </Text>
                <Tag color="blue">{dashboardData?.active_workflows || 0}</Tag>
              </div>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card title="Recent Conversations">
            {dashboardData?.recent_conversations?.length ? (
              <div>
                {dashboardData.recent_conversations.map((conv) => (
                  <div key={conv.id} style={{ marginBottom: 8 }}>
                    <Text strong>{conv.title}</Text>
                    <br />
                    <Text type="secondary">
                      <Tag>{conv.module || 'general'}</Tag>
                      {new Date(conv.updated_at).toLocaleDateString()}
                    </Text>
                  </div>
                ))}
              </div>
            ) : (
              <Text type="secondary">No recent conversations</Text>
            )}
          </Card>
        </Col>
      </Row>

      {/* Module AI Status */}
      <Title level={4}>Module AI Status</Title>
      <Row gutter={[16, 16]}>
        {modules.map((module) => {
          const status = getModuleStatus(module.key);
          return (
            <Col xs={24} sm={12} md={8} lg={6} key={module.key}>
              <Card 
                size="small"
                title={
                  <Space>
                    <span style={{ color: module.color }}>●</span>
                    {module.name}
                  </Space>
                }
                extra={
                  status.status === 'active' ? (
                    <Tag color="success" icon={<CheckCircleOutlined />}>Active</Tag>
                  ) : (
                    <Tag color="error" icon={<AlertOutlined />}>Error</Tag>
                  )
                }
              >
                <Statistic
                  title="AI Features"
                  value={status.count}
                  suffix="active"
                />
              </Card>
            </Col>
          );
        })}
      </Row>
    </div>
  );
};

export default AIDashboard;
