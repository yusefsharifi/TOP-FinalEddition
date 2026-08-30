import React from 'react';
import { Button, Col, Modal, Row, Typography } from 'antd';
import { PurchaseInvoice } from '../../../types/procurement';

interface PurchaseInvoiceDetailsProps {
  open: boolean;
  onClose: () => void;
  invoice: PurchaseInvoice | null;
}

export const PurchaseInvoiceDetails: React.FC<PurchaseInvoiceDetailsProps> = ({ open, onClose, invoice }) => {
  if (!invoice) return null;
  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>جزئیات فاکتور خرید</div>
      <div>
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">شماره فاکتور:</Typography><Typography>{invoice.invoiceNumber}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">تأمین‌کننده:</Typography><Typography>{invoice.supplierName}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">تاریخ سررسید:</Typography><Typography>{new Date(invoice.dueDate).toLocaleDateString()}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">مبلغ کل:</Typography><Typography>{invoice.totalAmount.toLocaleString()}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">وضعیت پرداخت:</Typography><Typography>{invoice.status}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">روش پرداخت:</Typography><Typography>{invoice.paymentMethod}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">یادداشت:</Typography><Typography>{invoice.notes}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}>
            {invoice.attachment && (
              <Button variant="outlined" href={invoice.attachment} target="_blank">دانلود/مشاهده فایل فاکتور</Button>
            )}
          </Col>
        </Row>
      </div>
    </Modal>
  );
}; 