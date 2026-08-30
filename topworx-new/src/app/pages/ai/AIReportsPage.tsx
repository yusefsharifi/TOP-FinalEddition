import React, { useState } from "react";
import {
  Card,
  Input,
  Button,
  Table,
  Typography,
  Space,
  Spin,
  Tabs,
  Select,
  message,
  Divider,
  Tag,
  Row,
  Col,
  Alert,
  Empty,
} from "antd";
import {
  SearchOutlined,
  FileTextOutlined,
  RobotOutlined,
  CodeOutlined,
  PlayCircleOutlined,
  BarChartOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import apiClient from "../../../services/api";

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface QueryResult {
  query: string;
  sql: string;
  columns: string[];
  data: any[];
  row_count: number;
  explanation?: string;
}

interface ReportSection {
  title: string;
  data: any;
}

interface GeneratedReport {
  report_title: string;
  generated_at: string;
  sections: ReportSection[];
  ai_model: string;
  tokens_used: number;
}

const REPORT_TYPES = [
  { value: "sales_summary", label: "📊 گزارش فروش" },
  { value: "inventory_status", label: "📦 وضعیت انبار" },
  { value: "financial_overview", label: "💰 مرور مالی" },
  { value: "hr_summary", label: "👥 گزارش منابع انسانی" },
  { value: "procurement_summary", label: "🛒 گزارش تدارکات" },
  { value: "executive_summary", label: "📈 گزارش مدیریتی" },
  { value: "hse_summary", label: "🛡️ گزارش HSE" },
  { value: "support_summary", label: "🎧 گزارش پشتیبانی" },
  { value: "quality_summary", label: "🔍 گزارش کیفیت" },
  { value: "project_summary", label: "🏗️ گزارش پروژه‌ها" },
];

const NL_QUERY_EXAMPLES = [
  "فروش ماه گذشته چقدر بود؟",
  "کالاهای کم‌موجودی کدامند؟",
  "تعداد کارمندان فعال چقدر است؟",
  "مشتریان جدید این ماه چند نفر هستند؟",
  "وضعیت جریان نقدی چگونه است؟",
  "见识 حوادث باز چقدر است؟",
  "نرخ حل مشکلات پشتیبانی چقدر است؟",
  "بیشترین محصول فروخته شده کدام است؟",
  " مقایسه فروش Q1 و Q2",
  "پیش‌بینی فروش سه ماه آینده",
];

const AIReportsPage: React.FC = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [reportType, setReportType] = useState<string>("sales_summary");
  const [reportDescription, setReportDescription] = useState("");
  const [generatedReport, setGeneratedReport] = useState<GeneratedReport | null>(null);
  const { t } = useTranslation();

  const executeQuery = async () => {
    if (!query.trim()) {
      message.warning("لطفاً سؤال خود را بنویسید");
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post("/ai/reports/query", {
        query: query,
      });
      setResult(response.data);
    } catch (err) {
      console.error("Failed to execute query:", err);
      message.error("خطا در اجرای سؤال");
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post("/ai/reports/generate", {
        report_type: reportType,
      });
      setGeneratedReport(response.data);
      message.success("گزارش با موفقیت تولید شد");
    } catch (err) {
      console.error("Failed to generate report:", err);
      message.error("خطا در تولید گزارش");
    } finally {
      setLoading(false);
    }
  };

  const generateAIReport = async () => {
    if (!reportDescription.trim()) {
      message.warning("لطفاً گزارش مورد نظر را توضیح دهید");
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post("/ai/reports/ai-generate", {
        description: reportDescription,
      });
      setGeneratedReport(response.data);
      message.success("گزارش هوش مصنوعی با موفقیت تولید شد");
    } catch (err) {
      console.error("Failed to generate AI report:", err);
      message.error("خطا در تولید گزارش هوش مصنوعی");
    } finally {
      setLoading(false);
    }
  };

  const columns = result?.columns?.map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
    render: (text: any) => (text === null ? "-" : String(text)),
  })) || [];

  const tableData = result?.data?.map((row, index) => ({
    key: index,
    ...row,
  })) || [];

  return (
    <div style={{ padding: "24px" }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2}>
            <FileTextOutlined style={{ marginRight: 8, color: "#1677ff" }} />
            گزارشات هوش مصنوعی
          </Title>
        </Col>
      </Row>

      <Tabs defaultActiveKey="nlQuery">
        {/* Tab 1: Natural Language to SQL */}
        <TabPane
          tab={
            <span>
              <SearchOutlined />
              {" "}جستجوی زبان طبیعی
            </span>
          }
          key="nlQuery"
        >
          <Card>
            <Space direction="vertical" style={{ width: "100%" }} size="large">
              <Alert
                message="با زبان فارسی سؤال بپرسید، هوش مصنوعی SQL تولید کرده و نتیجه را نمایش می‌دهد"
                type="info"
                showIcon
              />

              {/* Example Queries */}
              <div>
                <Text type="secondary" style={{ marginBottom: 8, display: "block" }}>
                  نمونه سؤالات:
                </Text>
                <Space wrap>
                  {NL_QUERY_EXAMPLES.map((example, i) => (
                    <Tag
                      key={i}
                      color="blue"
                      style={{ cursor: "pointer" }}
                      onClick={() => setQuery(example)}
                    >
                      {example}
                    </Tag>
                  ))}
                </Space>
              </div>

              <TextArea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="سؤال خود را بنویسید... مثلاً: فروش ماه گذشته چقدر بود؟"
                autoSize={{ minRows: 2, maxRows: 4 }}
                onPressEnter={(e) => {
                  if (!e.shiftKey) {
                    e.preventDefault();
                    executeQuery();
                  }
                }}
              />
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={executeQuery}
                loading={loading}
                size="large"
              >
                اجرا
              </Button>

              {result && (
                <>
                  {result.sql && (
                    <Card
                      title={
                        <Space>
                          <CodeOutlined />
                          <span>SQL تولید شده</span>
                        </Space>
                      }
                      size="small"
                    >
                      <pre
                        style={{
                          backgroundColor: "#2d2d2d",
                          color: "#e6e6e6",
                          padding: "12px",
                          borderRadius: "4px",
                          overflow: "auto",
                          maxHeight: "200px",
                          margin: 0,
                        }}
                      >
                        {result.sql}
                      </pre>
                    </Card>
                  )}

                  <Card
                    title={
                      <Space>
                        <FileTextOutlined />
                        <span>نتایج</span>
                        <Tag>{result.row_count} ردیف</Tag>
                      </Space>
                    }
                  >
                    <Table
                      columns={columns}
                      dataSource={tableData}
                      pagination={{ pageSize: 10 }}
                      scroll={{ x: "max-content" }}
                      size="small"
                    />
                  </Card>

                  {result.explanation && (
                    <Card size="small">
                      <Text type="secondary">{result.explanation}</Text>
                    </Card>
                  )}
                </>
              )}
            </Space>
          </Card>
        </TabPane>

        {/* Tab 2: Predefined Reports */}
        <TabPane
          tab={
            <span>
              <BarChartOutlined />
              {" "}گزارش‌های از پیش تعریف شده
            </span>
          }
          key="predefined"
        >
          <Card>
            <Space direction="vertical" style={{ width: "100%" }} size="large">
              <Alert
                message="گزارش‌های استاندارد برای هر ماژول با تحلیل هوش مصنوعی"
                type="info"
                showIcon
              />
              <Select
                value={reportType}
                onChange={setReportType}
                style={{ width: "100%" }}
                options={REPORT_TYPES}
                placeholder="نوع گزارش را انتخاب کنید"
              />
              <Button
                type="primary"
                icon={<FileTextOutlined />}
                onClick={generateReport}
                loading={loading}
                size="large"
              >
                تولید گزارش
              </Button>
            </Space>
          </Card>
        </TabPane>

        {/* Tab 3: AI Report Generator */}
        <TabPane
          tab={
            <span>
              <RobotOutlined />
              {" "}تولیدگر گزارش هوش مصنوعی
            </span>
          }
          key="aiGenerate"
        >
          <Card>
            <Space direction="vertical" style={{ width: "100%" }} size="large">
              <Alert
                message="گزارش سفارشی خود را توصیف کنید، هوش مصنوعی آن را تولید می‌کند"
                type="info"
                showIcon
              />
              <TextArea
                value={reportDescription}
                onChange={(e) => setReportDescription(e.target.value)}
                placeholder="گزارش مورد نظر را توصیف کنید... مثلاً: گزارش مقایسه‌ای فروش و هزینه‌های سه ماه اخیر با تحلیل روند"
                autoSize={{ minRows: 4, maxRows: 8 }}
              />
              <Button
                type="primary"
                icon={<RobotOutlined />}
                onClick={generateAIReport}
                loading={loading}
                size="large"
              >
                تولید گزارش هوش مصنوعی
              </Button>
            </Space>
          </Card>
        </TabPane>
      </Tabs>

      {/* Generated Report Display */}
      {generatedReport && (
        <Card
          title={
            <Space>
              <FileTextOutlined />
              <span>{generatedReport.report_title}</span>
            </Space>
          }
          style={{ marginTop: 24 }}
          extra={
            <Space>
              <Tag color="blue">{generatedReport.ai_model}</Tag>
              <Tag>{generatedReport.tokens_used} توکن</Tag>
              <Tag>{new Date(generatedReport.generated_at).toLocaleString("fa-IR")}</Tag>
            </Space>
          }
        >
          {generatedReport.sections?.length === 0 ? (
            <Empty description="بخشی برای نمایش وجود ندارد" />
          ) : (
            generatedReport.sections?.map((section, index) => (
              <Card
                key={index}
                title={section.title}
                size="small"
                style={{ marginBottom: 16 }}
              >
                {typeof section.data === "object" ? (
                  <pre
                    style={{
                      backgroundColor: "#f5f5f5",
                      padding: "12px",
                      borderRadius: "4px",
                      overflow: "auto",
                      maxHeight: "400px",
                      margin: 0,
                    }}
                  >
                    {JSON.stringify(section.data, null, 2)}
                  </pre>
                ) : (
                  <Text>{String(section.data)}</Text>
                )}
              </Card>
            ))
          )}
        </Card>
      )}
    </div>
  );
};

export default AIReportsPage;
