// src/components/common/KPICard.tsx
// ============================================================================
// KPI Card Component
// ============================================================================

import React from 'react';
import { Card, Tag, Typography } from 'antd';
import { RiseOutlined } from '@ant-design/icons';
import { FallOutlined } from '@ant-design/icons';
import { KPIData } from '../../types';
import { formatIRR } from '../../utils/formatters';

const healthColors: Record<KPIData['health'], string> = {
  good: '#4caf50',
  warning: '#ff9800',
  critical: '#f44336',
  neutral: '#9e9e9e',
};

const healthLabels: Record<KPIData['health'], string> = {
  good: 'مطلوب',
  warning: 'هشدار',
  critical: 'بحرانی',
  neutral: 'عادی',
};

interface KPICardProps {
  kpi: KPIData;
  formatFn?: (v: number) => string;
}

export const KPICard: React.FC<KPICardProps> = ({
  kpi,
  formatFn = (v) => formatIRR(v),
}) => {
  const borderColor = healthColors[kpi.health];
  const isUp = (kpi.changePct ?? 0) >= 0;

  return (
    <Card sx={{ borderTop: `4px solid ${borderColor}`, height: '100%' }}>
      <div>
        <Typography variant="caption" color="text.secondary" gutterBottom>
          {kpi.label}
        </Typography>
        <Typography.Title level={3}>
          {formatFn(kpi.value)} {kpi.unit === 'IRR' ? 'ریال' : kpi.unit}
        </Typography.Title>
        
        {kpi.changePct !== null && (
          <div>
            {isUp ? (
              <TrendingUpIcon color="success" fontSize="small" />
            ) : (
              <TrendingDownIcon color="error" fontSize="small" />
            )}
            <Typography.Text>
              {Math.abs(kpi.changePct).toFixed(1)}٪ نسبت به ماه قبل
            </Typography.Text>
          </div>
        )}
        
        <Tag
          label={healthLabels[kpi.health]}
          size="small"
          sx={{
            mt: 1,
            bgcolor: `${borderColor}22`,
            color: borderColor,
            fontWeight: 'medium',
          }}
        />
      </div>
    </Card>
  );
};