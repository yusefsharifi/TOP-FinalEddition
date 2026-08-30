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
} from "antd";
import {
  SearchOutlined,
  FileTextOutlined,
  RobotOutlined,
  CodeOutlined,
  PlayCircleOutlined,
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

const AIReports: React.FC = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [reportType, setReportType] = useState<string>("sales_summary");
  const [reportDescription, setReportDescription] = useState("");
  const [generatedReport, setGeneratedReport] = useState<GeneratedReport | null>(null);
  const { t } = useTranslation();

  const reportTypes = [
    { value: "sales_summary", label: t("ai.reports.salesReport") },
    { value: "inventory_status", label: t("ai.reports.inventoryReport") },
    { value: "financial_overview", label: t("ai.reports.financeReport") },
    { value: "hr_summary", label: t("ai.reports.hrReport") },
    { value: "procurement_summary", label: t("ai.reports.procurementReport") },
    { value: "executive_summary", label: t("ai.reports.executiveReport") },
  ];

  const executeQuery = async () => {
    if (!query.trim()) {
      message.warning("Please enter a query");
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
      message.error("Failed to execute query");
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
      message.success("Report generated successfully");
    } catch (err) {
      console.error("Failed to generate report:", err);
      message.error("Failed to generate report");
    } finally {
      setLoading(false);
    }
  };

  const generateAIReport = async () => {
    if (!reportDescription.trim()) {
      message.warning("Please describe the report you want");
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post("/ai/reports/ai-generate", {
        description: reportDescription,
      });
      setGeneratedReport(response.data);
      message.success("AI report generated successfully");
    } catch (err) {
      console.error("Failed to generate AI report:", err);
      message.error("Failed to generate AI report");
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
      <Title level={2}>
        <FileTextOutlined style={{ marginRight: 8, color: "#1677ff" }} />
        {t("ai.reports.title")}
      </Title>

      <Tabs defaultActiveKey="nlQuery">
        <TabPane
          tab={
            <span>
              <SearchOutlined />
              {t("ai.reports.nlToSql")}
            </span>
          }
          key="nlQuery"
        >
          <Card>
            <Space direction="vertical" style={{ width: "100%" }} size="large">
              <TextArea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t("ai.reports.queryPlaceholder")}
                autoSize={{ minRows: 2, maxRows: 4 }}
              />
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={executeQuery}
                loading={loading}
              >
                {t("ai.reports.execute")}
              </Button>

              {result && (
                <>
                  <Card
                    title={
                      <Space>
                        <CodeOutlined />
                        <span>{t("ai.reports.generatedSql")}</span>
                      </Space>
                    }
                    size="small"
                  >
                    <pre
                      style={{
                        backgroundColor: "#f5f5f5",
                        padding: "12px",
                        borderRadius: "4px",
                        overflow: "auto",
                        maxHeight: "200px",
                      }}
                    >
                      {result.sql}
                    </pre>
                  </Card>

                  <Card
                    title={
                      <Space>
                        <FileTextOutlined />
                        <span>{t("ai.reports.results")}</span>
                        <Tag>{result.row_count} {t("ai.reports.rows")}</Tag>
                      </Space>
                    }
                  >
                    <Table
                      columns={columns}
                      dataSource={tableData}
                      pagination={{ pageSize: 10 }}
                      scroll={{ x: "max-content" }}
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

        <TabPane
          tab={
            <span>
              <FileTextOutlined />
              {t("ai.reports.predefinedReports")}
            </span>
          }
          key="predefined"
        >
          <Card>
            <Space direction="vertical" style={{ width: "100%" }} size="large">
              <Select
                value={reportType}
                onChange={setReportType}
                style={{ width: "100%" }}
                options={reportTypes}
              />
              <Button
                type="primary"
                icon={<FileTextOutlined />}
                onClick={generateReport}
                loading={loading}
              >
                {t("ai.reports.generateReport")}
              </Button>
            </Space>
          </Card>
        </TabPane>

        <TabPane
          tab={
            <span>
              <RobotOutlined />
              {t("ai.reports.aiReportGenerator")}
            </span>
          }
          key="aiGenerate"
        >
          <Card>
            <Space direction="vertical" style={{ width: "100%" }} size="large">
              <TextArea
                value={reportDescription}
                onChange={(e) => setReportDescription(e.target.value)}
                placeholder={t("ai.reports.descriptionPlaceholder")}
                autoSize={{ minRows: 3, maxRows: 6 }}
              />
              <Button
                type="primary"
                icon={<RobotOutlined />}
                onClick={generateAIReport}
                loading={loading}
              >
                {t("ai.reports.generate")}
              </Button>
            </Space>
          </Card>
        </TabPane>
      </Tabs>

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
              <Tag>{generatedReport.tokens_used} tokens</Tag>
            </Space>
          }
        >
          {generatedReport.sections?.map((section, index) => (
            <Card
              key={index}
              title={section.title}
              size="small"
              style={{ marginBottom: 16 }}
            >
              <pre
                style={{
                  backgroundColor: "#f5f5f5",
                  padding: "12px",
                  borderRadius: "4px",
                  overflow: "auto",
                }}
              >
                {JSON.stringify(section.data, null, 2)}
              </pre>
            </Card>
          ))}
        </Card>
      )}
    </div>
  );
};

export { AIReports };
