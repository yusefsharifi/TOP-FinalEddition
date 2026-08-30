import React, { useState } from 'react';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import { Alert, Button, Card, Input, Typography } from 'antd';
import { authService } from './authService';

export const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) { setError('رمز عبور مطابقت ندارد'); return; }
    setLoading(true);
    setError('');
    try {
      await authService.resetPassword({ token, new_password: password });
      setSuccess(true);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'خطا در بازیابی رمز عبور');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Card style={{ maxWidth: 400, width: '100%', textAlign: 'center' }}>
        <Typography.Title level={3}>رمز عبور بازیابی شد ✅</Typography.Title>
        <RouterLink to="/login">ورود با رمز جدید</RouterLink>
      </Card>
    );
  }

  return (
    <Card style={{ maxWidth: 400, width: '100%' }}>
      <Typography.Title level={3}>بازیابی رمز عبور</Typography.Title>
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />}
      <form onSubmit={handleSubmit}>
        <Input.Password placeholder="رمز عبور جدید" value={password} onChange={(e) => setPassword(e.target.value)} style={{ marginBottom: 16 }} />
        <Input.Password placeholder="تکرار رمز عبور" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} style={{ marginBottom: 16 }} />
        <Button type="primary" htmlType="submit" block loading={loading}>بازیابی رمز عبور</Button>
      </form>
    </Card>
  );
};
