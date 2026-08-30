import React, { useState } from 'react';
import { Alert, Button, Card, Checkbox, Form, Input, Typography } from 'antd';
import { BankOutlined, EyeInvisibleOutlined, EyeOutlined, LockOutlined, UserOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../core/auth/AuthProvider';

const { Title, Link } = Typography;

const Login: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (values: { username: string; password: string }) => {
    if (!values.username || !values.password) {
      setError(t('login.invalidCredentials'));
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await login(values);
      if (rememberMe) {
        localStorage.setItem('rememberMe', 'true');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(t('login.loginFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <Card
        style={{
          width: '100%',
          maxWidth: 400,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 24 }}>
          <BankOutlined style={{ fontSize: 40, color: '#1677ff', marginRight: 12 }} />
          <Title level={2} style={{ margin: 0 }}>
            TopWorx ERP
          </Title>
        </div>

        <Title level={4} style={{ marginBottom: 24 }}>
          {t('login.title')}
        </Title>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: 24, width: '100%' }}
          />
        )}

        <Form
          name="login"
          onFinish={handleSubmit}
          layout="vertical"
          style={{ width: '100%' }}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: t('login.usernameRequired') }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder={t('login.username')}
              size="large"
              autoComplete="username"
              autoFocus
              disabled={isLoading}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: t('login.passwordRequired') }]}
          >
            <Input
              prefix={<LockOutlined />}
              type={showPassword ? 'text' : 'password'}
              placeholder={t('login.password')}
              size="large"
              autoComplete="current-password"
              disabled={isLoading}
              suffix={
                <Button
                  type="text"
                  size="small"
                  icon={showPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                />
              }
            />
          </Form.Item>

          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Checkbox
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={isLoading}
              >
                {t('login.rememberMe')}
              </Checkbox>
              <Link href="#" onClick={(e) => e.preventDefault()}>
                {t('login.forgotPassword')}
              </Link>
            </div>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              loading={isLoading}
              disabled={isLoading}
            >
              {t('login.signIn')}
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Link href="#" onClick={(e) => e.preventDefault()}>
            {t('login.needHelp')}
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default Login;
