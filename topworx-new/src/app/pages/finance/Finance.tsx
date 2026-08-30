import React from 'react';
import { Col, Row, Typography } from 'antd';
import { FinanceDashboard } from '../../components/finance/FinanceDashboard';
import { GeneralLedger } from '../../components/finance/GeneralLedger';
import { AccountsReceivable } from '../../components/finance/AccountsReceivable';
import { AccountsPayable } from '../../components/finance/AccountsPayable';
import { CashManagement } from '../../components/finance/CashManagement';
import { Budgeting } from '../../components/finance/Budgeting';
import { AssetManagement } from '../../components/finance/AssetManagement';
import { FinancialReports } from '../../components/finance/FinancialReports';
import { ExpenseManagement } from '../../components/finance/ExpenseManagement';
import { TaxManagement } from '../../components/finance/TaxManagement';

export const Finance: React.FC = () => {
  return (
    <div style={{  p: 3  }}>
      <Typography.Title level={2}>
        مدیریت مالی و حسابداری
      </Typography.Title>
      
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <FinanceDashboard />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <GeneralLedger />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <AccountsReceivable />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <AccountsPayable />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <CashManagement />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <Budgeting />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <AssetManagement />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <ExpenseManagement />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <TaxManagement />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <FinancialReports />
        </Col>
      </Row>
    </div>
  );
}; 