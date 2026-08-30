import React, { useState } from "react";
import { Button, Input, InputNumber, Typography } from 'antd';

export const PayrollFormulaBuilder: React.FC<{ onSave: (formula: string) => void; defaultValue?: string }> = ({ onSave, defaultValue }) => {
  const [formula, setFormula] = useState(defaultValue || "base + bonus - tax - insurance");

  return (
    <div>
      <Typography.Title level={5}>فرمول محاسبه حقوق (مثال: base + bonus - tax - insurance)</Typography.Title>
      <Input
        fullWidth
        value={formula}
        onChange={e => setFormula(e.target.value)}
        placeholder="فرمول را وارد کنید"
      />
      <Button variant="contained" style={{  mt: 1  }} onClick={() => onSave(formula)}>ذخیره فرمول</Button>
    </div>
  );
};