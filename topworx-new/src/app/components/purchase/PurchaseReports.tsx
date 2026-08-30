import React, { useState } from 'react';
import { Button, Card, Col, DatePicker, Input, InputNumber, Row, Select, Table, Tag, Typography } from 'antd';
import { usePurchaseOrders, usePurchaseRequests, usePurchaseInvoices } from '../../../api/procurement';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

export const PurchaseReports: React.FC = () => {
  const [reportType, setReportType] = useState('orders');
  const [startDate, setStartDate] = useState<dayjs.Dayjs | null>(null);
  const [endDate, setEndDate] = useState<dayjs.Dayjs | null>(null);
  const [status, setStatus] = useState('');

  const { data: orders = [] } = usePurchaseOrders();
  const { data: requests = [] } = usePurchaseRequests();
  const { data: invoices = [] } = usePurchaseInvoices();

  const generateReport = () => {
    let filteredData: any[] = [];

    switch (reportType) {
      case 'orders':
        filteredData = orders.filter((order: any) => {
          const orderDate = dayjs(order.orderDate);
          const matchesDate = (!startDate || orderDate.isAfter(startDate)) &&
                             (!endDate || orderDate.isBefore(endDate));
          const matchesStatus = !status || order.status === status;
          return matchesDate && matchesStatus;
        });
        break;
      case 'requests':
        filteredData = requests.filter((request: any) => {
          const requestDate = dayjs(request.requestDate);
          const matchesDate = (!startDate || requestDate.isAfter(startDate)) &&
                             (!endDate || requestDate.isBefore(endDate));
          const matchesStatus = !status || request.status === status;
          return matchesDate && matchesStatus;
        });
        break;
      case 'invoices':
        filteredData = invoices.filter((invoice: any) => {
          const dueDate = dayjs(invoice.dueDate);
          const matchesDate = (!startDate || dueDate.isAfter(startDate)) &&
                             (!endDate || dueDate.isBefore(endDate));
          const matchesStatus = !status || invoice.status === status;
          return matchesDate && matchesStatus;
        });
        break;
    }

    return filteredData;
  };

  const reportData = generateReport();

  const getStatusOptions = () => {
    switch (reportType) {
      case 'orders':
        return ['در انتظار تأیید', 'تأیید شده', 'ارسال شده', 'دریافت شده', 'لغو شده'];
      case 'requests':
        return ['در انتظار بررسی', 'تأیید شده', 'رد شده', 'در حال خرید', 'تکمیل شده'];
      case 'invoices':
        return ['در انتظار پرداخت', 'پرداخت شده', 'تأخیر'];
      default:
        return [];
    }
  };

  const orderColumns = [
    { title: 'شماره سفارش', dataIndex: 'orderNumber', key: 'orderNumber' },
    { title: 'تأمین‌کننده', dataIndex: 'supplierName', key: 'supplierName' },
    { title: 'تاریخ سفارش', dataIndex: 'orderDate', key: 'orderDate', render: (v: string) => new Date(v).toLocaleDateString() },
    { title: 'مبلغ نهایی', dataIndex: 'finalAmount', key: 'finalAmount', render: (v: number) => v?.toLocaleString() + ' تومان' },
    {
      title: 'وضعیت', dataIndex: 'status', key: 'status',
      render: (s: string) => (
        <Tag color={s === 'دریافت شده' ? 'green' : s === 'لغو شده' ? 'red' : 'blue'}>{s}</Tag>
      ),
    },
  ];

  const requestColumns = [
    { title: 'شماره درخواست', dataIndex: 'requestNumber', key: 'requestNumber' },
    { title: 'دپارتمان', dataIndex: 'department', key: 'department' },
    { title: 'تاریخ درخواست', dataIndex: 'requestDate', key: 'requestDate', render: (v: string) => new Date(v).toLocaleDateString() },
    {
      title: 'اولویت', dataIndex: 'priority', key: 'priority',
      render: (p: string) => (
        <Tag color={p === 'فوری' ? 'red' : p === 'زیاد' ? 'orange' : 'blue'}>{p}</Tag>
      ),
    },
    {
      title: 'وضعیت', dataIndex: 'status', key: 'status',
      render: (s: string) => (
        <Tag color={s === 'تکمیل شده' ? 'green' : s === 'رد شده' ? 'red' : 'blue'}>{s}</Tag>
      ),
    },
  ];

  const invoiceColumns = [
    { title: 'شماره فاکتور', dataIndex: 'invoiceNumber', key: 'invoiceNumber' },
    { title: 'تأمین‌کننده', dataIndex: 'supplierName', key: 'supplierName' },
    { title: 'تاریخ سررسید', dataIndex: 'dueDate', key: 'dueDate', render: (v: string) => new Date(v).toLocaleDateString() },
    { title: 'مبلغ کل', dataIndex: 'totalAmount', key: 'totalAmount', render: (v: number) => v?.toLocaleString() + ' تومان' },
    {
      title: 'وضعیت', dataIndex: 'status', key: 'status',
      render: (s: string) => (
        <Tag color={s === 'پرداخت شده' ? 'green' : s === 'تأخیر' ? 'red' : 'orange'}>{s}</Tag>
      ),
    },
  ];

  const columnsMap: Record<string, any[]> = {
    orders: orderColumns,
    requests: requestColumns,
    invoices: invoiceColumns,
  };

  return (
    <div style={{ padding: 24 }}>
      <Typography.Title level={2}>گزارشات تدارکات و خرید</Typography.Title>

      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12}>
            <Select
              style={{ width: '100%' }}
              value={reportType}
              onChange={setReportType}
            >
              <Select.Option value="orders">گزارش سفارشات</MenuItem>
              <Select.Option value="requests">گزارش درخواست‌ها</MenuItem>
              <Select.Option value="invoices">گزارش فاکتورها</MenuItem>
            </Select>
          </Col>
          <Col xs={24} sm={12}>
            <DatePicker.RangePicker
              style={{ width: '100%' }}
              value={startDate && endDate ? [startDate, endDate] : null}
              onChange={(dates) => {
                setStartDate(dates?.[0] || null);
                setEndDate(dates?.[1] || null);
              }}
            />
          </Col>
          <Col xs={24} sm={12}>
            <Select
              style={{ width: '100%' }}
              placeholder="وضعیت"
              value={status || undefined}
              onChange={(val) => setStatus(val || '')}
              allowClear
            >
              <Select.Option value="">همه</MenuItem>
              {getStatusOptions().map((option) => (
                <Select.Option key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12}>
            <Button type="primary" block>
              تولید گزارش
            </Button>
          </Col>
        </Row>
      </Card>

      <Card>
        <Typography.Title level={4}>
          نتایج گزارش ({reportData.length} مورد)
        </Typography.Title>
        <Table
          columns={columnsMap[reportType]}
          dataSource={reportData.map((item: any) => ({ ...item, key: item.id }))}
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: 'داده‌ای یافت نشد' }}
        />
      </Card>
    </div>
  );
};
