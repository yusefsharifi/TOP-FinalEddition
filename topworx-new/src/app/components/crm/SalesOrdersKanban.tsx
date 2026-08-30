import React, { useMemo } from "react";
import { Button, Card, Space, Tag, Tooltip, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";
import { SalesOrder, SalesOrderStatus } from "../../../types/crm";

export interface SalesOrdersKanbanProps {
  orders: SalesOrder[];
  onEdit: (order: SalesOrder) => void;
  onDelete: (id: number) => void;
  onView: (order: SalesOrder) => void;
  onStatusChange: (id: number, newStatus: SalesOrderStatus) => void;
}

const statuses: SalesOrderStatus[] = ["در انتظار", "ارسال شده", "پرداخت شده", "لغو شده", "آرشیو"];

export const SalesOrdersKanban: React.FC<SalesOrdersKanbanProps> = ({ orders, onEdit, onDelete, onView, onStatusChange }) => {
  const statusMap = useMemo(() => {
    const map: Record<SalesOrderStatus, SalesOrder[]> = { "در انتظار": [], "ارسال شده": [], "پرداخت شده": [], "لغو شده": [], "آرشیو": [] };
    orders.forEach(order => map[order.status].push(order));
    return map;
  }, [orders]);

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return;
    const fromStatus = result.source.droppableId as SalesOrderStatus;
    const toStatus = result.destination.droppableId as SalesOrderStatus;
    if (fromStatus !== toStatus) {
      const order = statusMap[fromStatus][result.source.index];
      onStatusChange(order.id!, toStatus);
    }
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div>
        {statuses.map(status => (
          <Droppable droppableId={status} key={status}>
            {(provided, snapshot) => (
              <Card ref={provided.innerRef} {...provided.droppableProps} style={{  minWidth: 280, p: 2, bgcolor: snapshot.isDraggingOver ? "grey.100" : "white"  }}>
                <Typography.Title level={4}>{status}</Typography.Title>
                <Stack spacing={2}>
                  {statusMap[status].map((order, idx) => (
                    <Draggable draggableId={String(order.id)} index={idx} key={order.id}>
                      {(provided, snapshot) => (
                        <Card ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} style={{  p: 1, bgcolor: snapshot.isDragging ? "grey.200" : "white"  }}>
                          <Typography fontWeight={600}>{order.orderNumber}</Typography>
                          <Typography.Text>{order.customerName}</Typography.Text>
                          <Typography.Text>مبلغ: {order.totalAmount.toLocaleString()} {order.currency}</Typography.Text>
                          <Tag label={order.paymentStatus} size="small" style={{  mt: 1  }} color={order.paymentStatus === "پرداخت شده" ? "success" : order.paymentStatus === "نیمه پرداخت" ? "warning" : "default"} />
                          <div>
                            <Tooltip title="مشاهده جزئیات"><Button type="text" onClick={() => onView(order)}><VisibilityIcon /></Button></Tooltip>
                            <Tooltip title="ویرایش"><Button type="text" onClick={() => onEdit(order)}><EditIcon /></Button></Tooltip>
                            <Tooltip title="حذف"><Button type="text" onClick={() => onDelete(order.id!)}><DeleteIcon color="error" /></Button></Tooltip>
                          </div>
                        </Card>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </Stack>
              </Card>
            )}
          </Droppable>
        ))}
      </div>
    </DragDropContext>
  );
}; 