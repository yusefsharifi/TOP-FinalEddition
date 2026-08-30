import React, { useState, useEffect, useRef } from "react";
import {
  Card,
  Row,
  Col,
  Input,
  Button,
  List,
  Typography,
  Space,
  Spin,
  Tag,
  Select,
  Divider,
  Empty,
  Tabs,
  Alert,
  message,
  Tooltip,
  Badge,
} from "antd";
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  ClearOutlined,
  PlusOutlined,
  MessageOutlined,
  QuestionCircleOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import apiClient from "../../../services/api";

const { Text, Paragraph, Title } = Typography;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  sql?: string;
  data?: any[];
  tokens_used?: number;
  model?: string;
}

interface Conversation {
  id: number;
  title: string;
  module: string;
  created_at: string;
  updated_at: string;
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
  { value: "settings", label: "⚙️ تنظیمات" },
  { value: "messages", label: "💬 پیام‌ها" },
  { value: "tasks", label: "✅ وظایف" },
  { value: "projects", label: "🏗️ پروژه‌ها" },
  { value: "quality", label: "🔍 کیفیت" },
  { value: "budget", label: "💵 بودجه" },
  { value: "auth", label: "🔒 امنیت" },
  { value: "orders", label: "📦 سفارشات" },
];

const QUICK_QUERIES = [
  { module: "sales", query: "فروش ماه گذشته چقدر بود؟" },
  { module: "inventory", query: "کالاهای کم‌موجودی کدامند؟" },
  { module: "finance", query: "وضعیت جریان نقدی چگونه است؟" },
  { module: "hr", query: "تعداد کارمندان فعال چقدر است؟" },
  { module: "crm", query: "مشتریان جدید این ماه چند نفر هستند؟" },
  { module: "procurement", query: "سفارشات خرید در انتظار کدامند؟" },
  { module: "hse", query: " حوادث باز چقدر است؟" },
  { module: "support", query: "نرخ حل مشکلات پشتیبانی چقدر است؟" },
];

const AIAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [selectedModule, setSelectedModule] = useState<string>("inventory");
  const [modules, setModules] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { t } = useTranslation();

  useEffect(() => {
    fetchModules();
    fetchConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchModules = async () => {
    try {
      const response = await apiClient.get("/ai/modules/list");
      setModules(response.data.modules || []);
    } catch (err) {
      console.error("Failed to fetch modules:", err);
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await apiClient.get("/ai/assistant/conversations");
      setConversations(response.data);
    } catch (err) {
      console.error("Failed to fetch conversations:", err);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || loading) return;

    const userMessage: Message = {
      role: "user",
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);

    try {
      // Use module-specific natural query endpoint
      const response = await apiClient.post(
        `/ai/modules/${selectedModule}/natural-query`,
        { query: inputValue }
      );

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.answer,
        timestamp: new Date().toISOString(),
        sql: response.data.sql,
        data: response.data.data,
        tokens_used: response.data.tokens_used,
        model: response.data.model,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Failed to send message:", err);
      const errorMessage: Message = {
        role: "assistant",
        content: "متأسفانه در پردازش سؤال شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const sendQuickQuery = (query: string, module: string) => {
    setSelectedModule(module);
    setInputValue(query);
  };

  const clearChat = () => {
    setMessages([]);
    setCurrentConversationId(null);
  };

  const loadConversation = async (conversationId: number) => {
    try {
      const response = await apiClient.get(`/ai/assistant/conversations/${conversationId}`);
      const conversation = response.data;
      setMessages(
        conversation.messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.created_at,
        }))
      );
      setCurrentConversationId(conversationId);
    } catch (err) {
      console.error("Failed to load conversation:", err);
    }
  };

  return (
    <div style={{ padding: "24px" }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2}>
            <RobotOutlined style={{ marginRight: 8, color: "#1677ff" }} />
            دستیار هوش مصنوعی
          </Title>
        </Col>
      </Row>

      {/* Quick Query Chips */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Text type="secondary">سوالات سریع:</Text>
          {QUICK_QUERIES.map((q, i) => (
            <Tag
              key={i}
              color="blue"
              style={{ cursor: "pointer" }}
              onClick={() => sendQuickQuery(q.query, q.module)}
            >
              {q.query}
            </Tag>
          ))}
        </Space>
      </Card>

      <div style={{ display: "flex", height: "calc(100vh - 350px)" }}>
        {/* Conversations Sidebar */}
        <Card
          title={
            <Space>
              <MessageOutlined />
              <span>گفتگوها</span>
            </Space>
          }
          style={{ width: 280, marginRight: 16, flexShrink: 0 }}
          bodyStyle={{ padding: 0, maxHeight: "calc(100% - 57px)", overflow: "auto" }}
          extra={
            <Button
              type="text"
              icon={<PlusOutlined />}
              onClick={clearChat}
              title="گفتگوی جدید"
            />
          }
        >
          <List
            dataSource={conversations}
            renderItem={(conv) => (
              <List.Item
                style={{
                  padding: "12px 16px",
                  cursor: "pointer",
                  backgroundColor: currentConversationId === conv.id ? "#e6f7ff" : "transparent",
                }}
                onClick={() => loadConversation(conv.id)}
              >
                <List.Item.Meta
                  avatar={<MessageOutlined style={{ color: "#1677ff" }} />}
                  title={
                    <Text ellipsis style={{ maxWidth: 180 }}>
                      {conv.title}
                    </Text>
                  }
                  description={
                    <Space size={4}>
                      <Tag color="blue" style={{ fontSize: 10 }}>
                        {conv.module || "general"}
                      </Tag>
                      <Text type="secondary" style={{ fontSize: 10 }}>
                        {new Date(conv.updated_at).toLocaleDateString("fa-IR")}
                      </Text>
                    </Space>
                  }
                />
              </List.Item>
            )}
            locale={{ emptyText: <Empty description="گفتگویی وجود ندارد" /> }}
          />
        </Card>

        {/* Chat Area */}
        <Card
          title={
            <Space>
              <RobotOutlined style={{ color: "#1677ff" }} />
              <span>چت با هوش مصنوعی</span>
              <Select
                value={selectedModule}
                onChange={setSelectedModule}
                style={{ width: 180 }}
                size="small"
                placeholder="ماژول را انتخاب کنید"
              >
                {MODULE_OPTIONS.map((opt) => (
                  <Select.Option key={opt.value} value={opt.value}>
                    {opt.label}
                  </MenuItem>
                ))}
              </Select>
            </Space>
          }
          style={{ flex: 1 }}
          bodyStyle={{ padding: 0, display: "flex", flexDirection: "column" }}
          extra={
            <Button
              type="text"
              icon={<ClearOutlined />}
              onClick={clearChat}
              title="پاک کردن چت"
            />
          }
        >
          {/* Messages */}
          <div
            style={{
              flex: 1,
              overflow: "auto",
              padding: "16px",
              maxHeight: "calc(100vh - 450px)",
            }}
          >
            {messages.length === 0 ? (
              <div style={{ textAlign: "center", padding: "60px 0" }}>
                <RobotOutlined style={{ fontSize: 48, color: "#1677ff", marginBottom: 16 }} />
                <Paragraph type="secondary">
                  سؤال خود را درباره هر ماژول بپرسید. هوش مصنوعی داده‌های واقعی سیستم را تحلیل می‌کند.
                </Paragraph>
                <Space direction="vertical" style={{ marginTop: 16 }}>
                  <Text type="secondary">مثال‌ها:</Text>
                  <Tag color="blue" style={{ cursor: "pointer" }} onClick={() => sendQuickQuery("فروش ماه گذشته چقدر بود؟", "sales")}>
                    فروش ماه گذشته چقدر بود؟
                  </Tag>
                  <Tag color="green" style={{ cursor: "pointer" }} onClick={() => sendQuickQuery("کالاهای کم‌موجودی کدامند؟", "inventory")}>
                    کالاهای کم‌موجودی کدامند؟
                  </Tag>
                  <Tag color="orange" style={{ cursor: "pointer" }} onClick={() => sendQuickQuery(" وضعیت جریان نقدی چگونه است؟", "finance")}>
                    وضعیت جریان نقدی چگونه است؟
                  </Tag>
                </Space>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  style={{
                    marginBottom: 16,
                    display: "flex",
                    justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                  }}
                >
                  <div
                    style={{
                      maxWidth: "75%",
                      padding: "12px 16px",
                      borderRadius: 8,
                      backgroundColor: msg.role === "user" ? "#1677ff" : "#f5f5f5",
                      color: msg.role === "user" ? "white" : "black",
                    }}
                  >
                    <Space style={{ marginBottom: 4 }}>
                      {msg.role === "user" ? (
                        <UserOutlined style={{ color: "white" }} />
                      ) : (
                        <RobotOutlined style={{ color: "#1677ff" }} />
                      )}
                      <Text
                        style={{
                          color: msg.role === "user" ? "white" : "black",
                          fontSize: 12,
                        }}
                      >
                        {new Date(msg.timestamp).toLocaleTimeString("fa-IR")}
                      </Text>
                      {msg.model && (
                        <Tag color="blue" style={{ fontSize: 10 }}>
                          {msg.model}
                        </Tag>
                      )}
                    </Space>
                    <Paragraph
                      style={{
                        margin: 0,
                        color: msg.role === "user" ? "white" : "black",
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {msg.content}
                    </Paragraph>
                    {msg.sql && (
                      <Card
                        size="small"
                        style={{
                          marginTop: 8,
                          backgroundColor: "#2d2d2d",
                          color: "#e6e6e6",
                        }}
                      >
                        <pre style={{ margin: 0, fontSize: 12, color: "#e6e6e6" }}>
                          {msg.sql}
                        </pre>
                      </Card>
                    )}
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div style={{ padding: "16px", borderTop: "1px solid #f0f0f0" }}>
            <Space.Compact style={{ width: "100%" }}>
              <TextArea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="سؤال خود را بنویسید..."
                autoSize={{ minRows: 1, maxRows: 4 }}
                onPressEnter={(e) => {
                  if (!e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                disabled={loading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={sendMessage}
                loading={loading}
              >
                ارسال
              </Button>
            </Space.Compact>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default AIAssistantPage;
