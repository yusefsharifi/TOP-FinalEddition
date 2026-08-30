import React from "react";
import { Input, InputNumber } from 'antd';

export const DocumentFilters: React.FC<{
  filters: any;
  onChange: (f: any) => void;
  folders: string[];
}> = ({ filters, onChange, folders }) => (
  <div>
    <Input label="جستجو" value={filters.search || ""} onChange={e => onChange({ ...filters, search: e.target.value })} />
    <Input select label="پوشه" value={filters.folder || ""} onChange={e => onChange({ ...filters, folder: e.target.value })} style={{  minWidth: 120  }}>
      <MenuItem value="">همه</Select.Option>
      {folders.map(f => <MenuItem key={f} value={f}>{f}</Select.Option>)}
    </Input>
    <Input label="برچسب" value={filters.tag || ""} onChange={e => onChange({ ...filters, tag: e.target.value })} />
  </div>
);