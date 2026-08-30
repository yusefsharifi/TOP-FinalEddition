import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card, Input, InputNumber, Typography } from 'antd';
import { useAuth } from '../../../core/auth/AuthProvider';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login({ username: formData.username, password: formData.password });
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div>
      <Card
        
        style={{ 
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          width: '100%',
         }}
      >
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
        <div>
          <Input
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username"
            name="username"
            autoComplete="username"
            autoFocus
            value={formData.username}
            onChange={(e) =>
              setFormData({ ...formData, username: e.target.value })
            }
          />
          <Input
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={formData.password}
            onChange={(e) =>
              setFormData({ ...formData, password: e.target.value })
            }
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            style={{  mt: 3, mb: 2  }}
          >
            Sign In
          </Button>
        </div>
      </Card>
    </div>
  );
}; 