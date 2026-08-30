import React from 'react';
import { Col, List, List.Item, Modal, Row, Typography } from 'antd';
import { PurchaseRequest } from '../../../types/procurement';

interface PurchaseRequestDetailsProps {
  open: boolean;
  onClose: () => void;
  request: PurchaseRequest | null;
}

export const PurchaseRequestDetails: React.FC<PurchaseRequestDetailsProps> = ({ open, onClose, request }) => {
  if (!request) return null;
  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>جزئیات درخواست خرید</div>
      <div>
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">شماره درخواست:</Typography><Typography>{request.requestNumber}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">دپارتمان:</Typography><Typography>{request.department}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">تاریخ درخواست:</Typography><Typography>{new Date(request.requestDate).toLocaleDateString()}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">تاریخ مورد نیاز:</Typography><Typography>{new Date(request.requiredDate).toLocaleDateString()}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">اولویت:</Typography><Typography>{request.priority}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">وضعیت:</Typography><Typography>{request.status}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">توضیحات:</Typography><Typography>{request.description}</Typography></Col>
          <Col xs={Math.round(12 / 12 * 24)}><Typography variant="subtitle2">آیتم‌ها:</Typography>
            <List>
              {request.items.map((item, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={`${item.itemName} (${item.quantity} ${item.unit})`}
                    secondary={`قیمت واحد: ${item.estimatedPrice} | قیمت کل: ${item.totalPrice}`}
                  />
                </ListItem>
              ))}
            </List>
          </Col>
        </Row>
      </div>
    </Modal>
  );
}; 