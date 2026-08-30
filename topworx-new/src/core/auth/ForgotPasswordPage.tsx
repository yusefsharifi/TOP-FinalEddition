import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Alert, Button, Card, Input, Spin, Typography } from 'antd';
import { authService } from './authService';

type PageState = 'idle' | 'loading' | 'success' | 'error';

export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [pageState, setPageState] = useState<PageState>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    setPageState('loading');
    setErrorMsg('');
    try {
      await authService.forgotPassword({ email: email.trim() });
      setPageState('success');
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'خطا در ارسال ایمیل. لطفاً دوباره تلاش کنید.';
      setErrorMsg(msg);
      setPageState('error');
    }
  };

  if (pageState === 'success') {
    return (
      <Card style={{ maxWidth: 400, width: '100%', textAlign: 'center' }}>
        <Typography.Title level={3}>ایمیل ارسال شد ✅</Typography.Title>
        <Alert message={`لینک بازیابی رمز عبور به ${email} ارسال شد.`} type="success" showIcon style={{ marginBottom: 16 }} />
        <Button onClick={() => setPageState('idle')}>دوباره ارسال کنید</Button>
        <div style={{ marginTop: 16 }}><RouterLink to="/login">بازگشت به صفحه ورود</RouterLink></div>
      </Card>
    );
  }

  return (
    <Card style={{ maxWidth: 400, width: '100%' }}>
      <Typography.Title level={3}>فراموشی رمز عبور</Typography.Title>
      <Typography.Text type="secondary">ایمیل حساب خود را وارد کنید.</Typography.Text>
      {pageState === 'error' && <Alert message={errorMsg} type="error" showIcon style={{ margin: '16px 0' }} />}
      <form onSubmit={handleSubmit}>
        <Input placeholder="آدرس ایمیل" type="email" value={email} onChange={(e) => setEmail(e.target.value)} disabled={pageState === 'loading'} style={{ marginBottom: 16 }} />
        <Button type="primary" htmlType="submit" block loading={pageState === 'loading'} disabled={!email.trim()}>
          {pageState === 'loading' ? 'در حال ارسال...' : 'ارسال لینک بازیابی'}
        </Button>
      </form>
      <div style={{ marginTop: 16, textAlign: 'center' }}><RouterLink to="/login">بازگشت به صفحه ورود</RouterLink></div>
    </Card>
  );
};
