import React from "react";
import { Button, Divider, Drawer, Typography } from 'antd';
import { CloseOutlined } from '@ant-design/icons';
import { Customer } from "./CustomerForm";

interface CustomerDetailsProps {
  open: boolean;
  onClose: () => void;
  customer: Customer | null;
}

export const CustomerDetails: React.FC<CustomerDetailsProps> = ({ open, onClose, customer }) => {
  if (!customer) return null;
  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <div style={{  width: 350, p: 3  }}>
        <div style={{  display: "flex", justifyContent: "space-between", alignItems: "center"  }}>
          <Typography.Title level={4}>جزئیات مشتری</Typography.Title>
          <Button type="text" onClick={onClose}><CloseOutlined /></Button>
        </div>
        <Divider style={{  my: 2  }} />
        <Typography variant="subtitle2">نام:</Typography>
        <Typography style={{  mb: 1  }}>{customer.name}</Typography>
        <Typography variant="subtitle2">ایمیل:</Typography>
        <Typography style={{  mb: 1  }}>{customer.email}</Typography>
        <Typography variant="subtitle2">تلفن:</Typography>
        <Typography style={{  mb: 1  }}>{customer.phone}</Typography>
        <Typography variant="subtitle2">شرکت:</Typography>
        <Typography style={{  mb: 1  }}>{customer.company}</Typography>
        <Typography variant="subtitle2">وضعیت:</Typography>
        <Typography style={{  mb: 1  }}>{customer.status === "Active" ? "فعال" : "غیرفعال"}</Typography>
      </div>
    </Drawer>
  );
}; 