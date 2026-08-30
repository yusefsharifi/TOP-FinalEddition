// src/components/common/JalaliPeriodSelector.tsx
// ============================================================================
// Jalali Period Selector
// ============================================================================

import React from 'react';
import { Select, Space } from 'antd';
import { JALALI_MONTHS } from '../../utils/formatters';

interface PeriodValue {
  year: number;
  month: number;
}

interface JalaliPeriodSelectorProps {
  value: PeriodValue;
  onChange: (v: PeriodValue) => void;
  minYear?: number;
  maxYear?: number;
}

export const JalaliPeriodSelector: React.FC<JalaliPeriodSelectorProps> = ({
  value,
  onChange,
  minYear = 1400,
  maxYear = 1410,
}) => {
  const years = Array.from({ length: maxYear - minYear + 1 }, (_, i) => minYear + i);

  return (
    <Stack direction="row" spacing={2}>
      <FormControl size="small" style={{  minWidth: 100  }}>
        <InputLabel>سال</span>
        <Select
          value={value.year}
          label="سال"
          onChange={(e) => onChange({ ...value, year: Number(e.target.value) })}
        >
          {years.map((y) => (
            <MenuItem key={y} value={y}>
              {y}
            </Select.Option>
          ))}
        </Select>
      </div>
      
      <FormControl size="small" style={{  minWidth: 130  }}>
        <InputLabel>ماه</span>
        <Select
          value={value.month}
          label="ماه"
          onChange={(e) => onChange({ ...value, month: Number(e.target.value) })}
        >
          {JALALI_MONTHS.map((name, i) => (
            <MenuItem key={i + 1} value={i + 1}>
              {name}
            </Select.Option>
          ))}
        </Select>
      </div>
    </Stack>
  );
};