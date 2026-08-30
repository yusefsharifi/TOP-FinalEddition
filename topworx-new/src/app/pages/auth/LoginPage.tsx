// src/app/pages/auth/LoginPage.tsx
// ============================================================================
// LoginPage — صفحه ورود به سیستم
// استفاده از apiClient برای ارتباط با POST /api/v1/auth/login
// ============================================================================

import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Form, Input, Button, Card, Typography, Alert, Spin } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { apiClient } from "../../../services/api";

const { Title, Text } = Typography;

interface LoginFormValues {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const LoginPage: React.FC = () => {
  const navigate           = useNavigate();
  const location           = useLocation();
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);

  // مسیر قبلی که کاربر می‌خواست برود (از PrivateRoute)
  const from = (location.state as any)?.from || "/dashboard";

  const handleLogin = async (values: LoginFormValues) => {
    setLoading(true);
    setError(null);

    try {
      // FastAPI انتظار form-data دارد برای /auth/login
      const formData = new URLSearchParams();
      formData.append("username", values.username);
      formData.append("password", values.password);

      const response = await apiClient.post<LoginResponse>(
        "/auth/login",
        formData,
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
      );

      // ذخیره توکن‌ها
      localStorage.setItem("access_token",  response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);

      // هدایت به مسیر مورد نظر
      navigate(from, { replace: true });
    } catch (err: any) {
      const message =
        err.response?.data?.detail || "خطا در ورود. لطفاً دوباره تلاش کنید.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      }}
    >
      <Card style={{ width: 400, borderRadius: 12, boxShadow: "0 8px 32px rgba(0,0,0,0.2)" }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <Title level={2} style={{ margin: 0 }}>TOP WorX</Title>
          <Text type="secondary">سیستم یکپارچه مدیریت سازمانی</Text>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: 24 }}
            closable
            onClose={() => setError(null)}
          />
        )}

        <Spin spinning={loading}>
          <Form
            name="login"
            onFinish={handleLogin}
            layout="vertical"
            requiredMark={false}
          >
            <Form.Item
              name="username"
              label="نام کاربری / ایمیل"
              rules={[{ required: true, message: "لطفاً نام کاربری را وارد کنید" }]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="نام کاربری یا ایمیل"
                size="large"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="رمز عبور"
              rules={[{ required: true, message: "لطفاً رمز عبور را وارد کنید" }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="رمز عبور"
                size="large"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 8 }}>
              <Button
                type="primary"
                htmlType="submit"
                block
                size="large"
                loading={loading}
              >
                ورود به سیستم
              </Button>
            </Form.Item>

            <div style={{ textAlign: "center" }}>
              <Button
                type="link"
                onClick={() => navigate("/forgot-password")}
              >
                رمز عبور را فراموش کردم
              </Button>
            </div>
          </Form>
        </Spin>
      </Card>
    </div>
  );
};
