import React, { useState } from 'react';
import { Alert, Button, Modal, Select, Typography, message, Timeline, Tag } from 'antd';
import { ReloadOutlined, PrinterOutlined, CheckCircleOutlined, CloseOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { PurchaseOrder, PurchaseOrderStatus } from '../../../types/procurement';
import { useOrderStatusHistory } from '../../../api/procurement';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

interface PurchaseOrderStatusHistoryProps {
  open: boolean;
  onClose: () => void;
  order: PurchaseOrder | null;
}

const statusColors: Record<string, string> = {
  'دریافت شده': 'green',
  'لغو شده': 'red',
  'ارسال شده': 'blue',
};

const statusIcons: Record<string, React.ReactNode> = {
  'دریافت شده': <CheckCircleOutlined style={{ color: '#52c41a' }} />,
  'لغو شده': <CloseOutlined style={{ color: '#ff4d4f' }} />,
  'default': <ClockCircleOutlined style={{ color: '#1677ff' }} />,
};

export const PurchaseOrderStatusHistory: React.FC<PurchaseOrderStatusHistoryProps> = ({ open, onClose, order }) => {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const { data: statusHistory = [], error, refetch } = useOrderStatusHistory(order?.id!);

  React.useEffect(() => {
    if (error) message.error('خطا در دریافت تاریخچه وضعیت');
  }, [error]);

  const filteredHistory = statusFilter
    ? statusHistory.filter((s: any) => s.status === statusFilter)
    : statusHistory;

  const handlePrint = () => {
    const doc = new jsPDF();
    autoTable(doc, {
      head: [['وضعیت', 'توسط', 'تاریخ', 'یادداشت']],
      body: filteredHistory.map((s: any) => [
        s.status,
        s.changedByName,
        new Date(s.changedAt).toLocaleString(),
        s.notes || '',
      ]),
    });
    doc.save('order_status_history.pdf');
  };

  if (!order) return null;

  return (
    <Modal
      open={open}
      onCancel={onClose}
      footer={null}
      width={700}
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>تاریخچه وضعیت سفارش</span>
          <div>
            <Button type="text" icon={<ReloadOutlined />} onClick={() => refetch()} />
            <Button type="text" icon={<PrinterOutlined />} onClick={handlePrint} />
          </div>
        </div>
      }
    >
      <div style={{ marginBottom: 16 }}>
        <Typography.Text style={{ display: 'block', textAlign: 'center', marginBottom: 8 }}>
          تعداد تغییر وضعیت: {statusHistory.length}
        </Typography.Text>
        {statusHistory.length > 0 && (
          <Typography.Text type="primary" style={{ display: 'block', textAlign: 'center', marginBottom: 16 }}>
            آخرین وضعیت: {statusHistory[statusHistory.length - 1]?.status}
          </Typography.Text>
        )}
        <Select
          style={{ width: '100%' }}
          placeholder="فیلتر وضعیت"
          value={statusFilter || undefined}
          onChange={(val) => setStatusFilter(val || '')}
          allowClear
        >
          <Select.Option value="">همه وضعیت‌ها</MenuItem>
          {[...new Set(statusHistory.map((s: any) => s.status))].map((status: string) => (
            <Select.Option key={status} value={status}>{status}</MenuItem>
          ))}
        </Select>
      </div>

      {filteredHistory.length === 0 ? (
        <Typography.Text style={{ display: 'block', textAlign: 'center' }}>
          هیچ سابقه‌ای یافت نشد.
        </Typography.Text>
      ) : (
        <Timeline
          items={filteredHistory.map((status: any) => ({
            color: statusColors[status.status] || 'gray',
            dot: statusIcons[status.status] || statusIcons['default'],
            children: (
              <div>
                <Typography.Text strong>{status.status}</Typography.Text>
                <br />
                <Typography.Text>توسط {status.changedByName}</Typography.Text>
                <br />
                <Typography.Text type="secondary">
                  {new Date(status.changedAt).toLocaleString()}
                </Typography.Text>
                {status.notes && (
                  <>
                    <br />
                    <Typography.Text type="info">{status.notes}</Typography.Text>
                  </>
                )}
              </div>
            ),
          }))}
        />
      )}
    </Modal>
  );
};
