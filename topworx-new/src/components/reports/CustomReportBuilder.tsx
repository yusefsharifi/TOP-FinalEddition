import React, { useState } from "react";
import { Button, Card, Col, Input, InputNumber, Row, Select } from 'antd';

const dataSources = [
  { value: "finance", label: "مالی" },
  { value: "hr", label: "منابع انسانی" },
  { value: "sales", label: "فروش" },
  { value: "project", label: "پروژه" },
];

const availableFields = {
  finance: ["مبلغ", "تاریخ", "نوع سند"],
  hr: ["نام", "سمت", "تاریخ استخدام"],
  sales: ["مشتری", "مبلغ", "تاریخ"],
  project: ["عنوان پروژه", "وضعیت", "پیشرفت"],
};

export const CustomReportBuilder: React.FC<{ onBuild: (config: any) => void }> = ({ onBuild }) => {
  const [source, setSource] = useState("");
  const [fields, setFields] = useState<string[]>([]);
  const [title, setTitle] = useState("");

  return (
    <Card style={{  p: 2, mb: 2  }}>
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Input label="عنوان گزارش" value={title} onChange={e => setTitle(e.target.value)} fullWidth />
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <FormControl fullWidth>
            <InputLabel>منبع داده</span>
            <Select value={source} onChange={e => { setSource(e.target.value); setFields([]); }} label="منبع داده">
              {dataSources.map(ds => <MenuItem key={ds.value} value={ds.value}>{ds.label}</Select.Option>)}
            </Select>
          </div>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <FormControl fullWidth>
            <InputLabel>فیلدها</span>
            <Select
              multiple
              value={fields}
              onChange={e => setFields(e.target.value as string[])}
              label="فیلدها"
              disabled={!source}
            >
              {(availableFields[source as keyof typeof availableFields] || []).map(f => (
                <MenuItem key={f} value={f}>{f}</Select.Option>
              ))}
            </Select>
          </div>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Button
            variant="contained"
            disabled={!title || !source || fields.length === 0}
            onClick={() => onBuild({ title, source, fields })}
          >
            ساخت گزارش
          </Button>
        </Col>
      </Row>
    </Card>
  );
};