import React from 'react';
import { Col, Row, Typography } from 'antd';
import { InventoryDashboard } from '../../components/inventory/InventoryDashboard';
import { ProductManagement } from '../../components/inventory/ProductManagement';
import { WarehouseManagement } from '../../components/inventory/WarehouseManagement';
import { StockControl } from '../../components/inventory/StockControl';
import { SupplyChainManagement } from '../../components/inventory/SupplyChainManagement';
import { SupplierManagement } from '../../components/inventory/SupplierManagement';
import { DemandForecasting } from '../../components/inventory/DemandForecasting';
import { InventoryOptimization } from '../../components/inventory/InventoryOptimization';

export const Inventory: React.FC = () => {
  return (
    <div style={{  p: 3  }}>
      <Typography.Title level={2}>
        مدیریت انبار و موجودی
      </Typography.Title>
      
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <InventoryDashboard />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <ProductManagement />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <WarehouseManagement />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <StockControl />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <SupplyChainManagement />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <SupplierManagement />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <DemandForecasting />
        </Col>
        
        <Col xs={Math.round(12 / 12 * 24)}>
          <InventoryOptimization />
        </Col>
      </Row>
    </div>
  );
}; 