import React, { useState, useEffect, useRef } from "react";
import {
  Card,
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
} from "antd";
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  ClearOutlined,
  PlusOutlined,
  MessageOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import apiClient from "../../../services/api";

const { Text, Paragraph } = Typography;
const { TextArea } = Input;

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface Conversation {
  id: number;
  title: string;
  module: string;
  created_at: string;
  updated_at: string;
}

interface AIChatProps {
  module?: string;
}

const AIChat: React.FC<AIChatProps> = ({ module: initialModule }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [selectedModule, setSelectedModule] = useState<string>(initialModule || "all");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { t } = useTranslation();

  const modules = [
    { value: "all", label: t("ai.chat.allModules") },
    { value: "inventory", label: t("ai.automation.modules.inventory") },
    { value: "sales", label: t("ai.automation.modules.sales") },
    { value: "finance", label: t("ai.automation.modules.finance") },
    { value: "hr", label: t("ai.automation.modules.hr") },
    { value: "crm", label: t("ai.automation.modules.crm") },
    { value: "procurement", label: t("ai.automation.modules.procurement") },
    { value: "hse", label: t("ai.automation.modules.hse") },
    { value: "tasks", label: t("ai.automation.modules.tasks") },
  ];

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
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
      const response = await apiClient.post("/ai/assistant/chat", {
        message: inputValue,
        module: selectedModule !== "all" ? selectedModule : undefined,
        conversation_id: currentConversationId,
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.reply,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (!currentConversationId && response.data.conversation_id) {
        setCurrentConversationId(response.data.conversation_id);
        fetchConversations();
      }
    } catch (err) {
      console.error("Failed to send message:", err);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
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
    <div style={{ display: "flex", height: "calc(100vh - 200px)" }}>
      {/* Conversations Sidebar */}
      <Card
        title={
          <Space>
            <MessageOutlined />
            <span>{t("ai.chat.conversations")}</span>
          </Space>
        }
        style={{ width: 280, marginRight: 16 }}
        bodyStyle={{ padding: 0, maxHeight: "calc(100% - 57px)", overflow: "auto" }}
        extra={
          <Button
            type="text"
            icon={<PlusOutlined />}
            onClick={clearChat}
            title={t("ai.chat.newConversation")}
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
                      {new Date(conv.updated_at).toLocaleDateString()}
                    </Text>
                  </Space>
                }
              />
            </List.Item>
          )}
          locale={{ emptyText: <Empty description={t("ai.chat.noMessages")} /> }}
        />
      </Card>

      {/* Chat Area */}
      <Card
        title={
          <Space>
            <RobotOutlined style={{ color: "#1677ff" }} />
            <span>{t("ai.chat.title")}</span>
            <Select
              value={selectedModule}
              onChange={setSelectedModule}
              style={{ width: 150 }}
              size="small"
              options={modules}
            />
          </Space>
        }
        style={{ flex: 1 }}
        bodyStyle={{ padding: 0, display: "flex", flexDirection: "column" }}
        extra={
          <Button
            type="text"
            icon={<ClearOutlined />}
            onClick={clearChat}
            title={t("ai.chat.clear")}
          />
        }
      >
        {/* Messages */}
        <div
          style={{
            flex: 1,
            overflow: "auto",
            padding: "16px",
            maxHeight: "calc(100vh - 350px)",
          }}
        >
          {messages.length === 0 ? (
            <div style={{ textAlign: "center", padding: "60px 0" }}>
              <RobotOutlined style={{ fontSize: 48, color: "#1677ff", marginBottom: 16 }} />
              <Paragraph type="secondary">{t("ai.chat.noMessages")}</Paragraph>
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
                    maxWidth: "70%",
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
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </Text>
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
              placeholder={t("ai.chat.placeholder")}
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
              {t("ai.chat.send")}
            </Button>
          </Space.Compact>
        </div>
      </Card>
    </div>
  );
};

export { AIChat };
