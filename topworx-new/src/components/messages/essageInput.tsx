import React, { useState } from "react";
import { Button, Card, Input, InputNumber } from 'antd';
import { SendOutlined } from '@ant-design/icons';

export const MessageInput: React.FC<{ onSend: (msg: string) => void; disabled?: boolean }> = ({
  onSend,
  disabled,
}) => {
  const [value, setValue] = useState("");

  const handleSend = () => {
    if (value.trim()) {
      onSend(value);
      setValue("");
    }
  };

  return (
    <Card style={{  p: 1, display: "flex", alignItems: "center"  }}>
      <Input
        fullWidth
        size="small"
        placeholder="پیام خود را بنویسید..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
        disabled={disabled}
      />
      <Button type="text" onClick={handleSend} disabled={disabled || !value.trim()}>
        <SendIcon />
      </Button>
    </Card>
  );
};