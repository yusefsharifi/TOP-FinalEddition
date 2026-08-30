import React from 'react';
import { Card, Col, Progress, Row, Typography } from 'antd';
import { BankOutlined, CreditCardOutlined, DollarOutlined, FallOutlined, FileTextOutlined, RiseOutlined } from '@ant-design/icons';

const mockFinancialData = {
  totalRevenue: 1250000,
  totalExpenses: 850000,
  netProfit: 400000,
  cashBalance: 250000,
  accountsReceivable: 180000,
  accountsPayable: 95000,
  budgetUtilization: 75,
  profitMargin: 32,
};

export const FinanceDashboard: React.FC = () => {
  return (
    <div>
      <Typography.Title level={3}>
        داشبورد مالی
      </Typography.Title>
      
      <Row gutter={[16, 16]}>
        {/* شاخص‌های کلیدی */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography color="textSecondary" gutterBottom>
                    درآمد کل
                  </Typography>
                  <Typography.Title level={4}>
                    {mockFinancialData.totalRevenue.toLocaleString()} تومان
                  </Typography.Title>
                </div>
                <RiseOutlined color="success" />
              </div>
            </div>
          </Card>
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography color="textSecondary" gutterBottom>
                    هزینه‌ها
                  </Typography>
                  <Typography.Title level={4}>
                    {mockFinancialData.totalExpenses.toLocaleString()} تومان
                  </Typography.Title>
                </div>
                <FallOutlined color="error" />
              </div>
            </div>
          </Card>
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography color="textSecondary" gutterBottom>
                    سود خالص
                  </Typography>
                  <Typography.Title level={4}>
                    {mockFinancialData.netProfit.toLocaleString()} تومان
                  </Typography.Title>
                </div>
                <DollarOutlined color="success" />
              </div>
            </div>
          </Card>
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card>
            <div>
              <div>
                <div>
                  <Typography color="textSecondary" gutterBottom>
                    موجودی نقدی
                  </Typography>
                  <Typography.Title level={4}>
                    {mockFinancialData.cashBalance.toLocaleString()} تومان
                  </Typography.Title>
                </div>
                <BankOutlined color="primary" />
              </div>
            </div>
          </Card>
        </Col>
        
        {/* جزئیات بیشتر */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 3  }}>
            <Typography.Title level={4}>
              حساب‌های دریافتنی
            </Typography.Title>
            <Typography.Title level={2}>
              {mockFinancialData.accountsReceivable.toLocaleString()} تومان
            </Typography.Title>
            <Typography.Text>
              {Math.floor(mockFinancialData.accountsReceivable / mockFinancialData.totalRevenue * 100)}% از درآمد کل
            </Typography.Text>
          </Card>
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 3  }}>
            <Typography.Title level={4}>
              حساب‌های پرداختنی
            </Typography.Title>
            <Typography.Title level={2}>
              {mockFinancialData.accountsPayable.toLocaleString()} تومان
            </Typography.Title>
            <Typography.Text>
              {Math.floor(mockFinancialData.accountsPayable / mockFinancialData.totalExpenses * 100)}% از هزینه‌ها
            </Typography.Text>
          </Card>
        </Col>
        
        {/* پیشرفت بودجه */}
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 3  }}>
            <Typography.Title level={4}>
              استفاده از بودجه
            </Typography.Title>
            <div style={{  display: 'flex', alignItems: 'center', mb: 1  }}>
              <div style={{  width: '100%', mr: 1  }}>
                <Progress 
                  variant="determinate" 
                  value={mockFinancialData.budgetUtilization} 
                  style={{  height: 10, borderRadius: 5  }}
                />
              </div>
              <div style={{  minWidth: 35  }}>
                <Typography.Text>
                  {mockFinancialData.budgetUtilization}%
                </Typography.Text>
              </div>
            </div>
            <Typography.Text>
              {mockFinancialData.budgetUtilization}% از بودجه سالانه استفاده شده
            </Typography.Text>
          </Card>
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <Card style={{  p: 3  }}>
            <Typography.Title level={4}>
              حاشیه سود
            </Typography.Title>
            <Typography.Title level={2}>
              {mockFinancialData.profitMargin}%
            </Typography.Title>
            <Typography.Text>
              نسبت سود خالص به درآمد کل
            </Typography.Text>
          </Card>
        </Col>
      </Row>
    </div>
  );
}; 