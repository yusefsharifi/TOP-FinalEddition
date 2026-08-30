import React, { useMemo } from "react";
import { Button, Card, Space, Tag, Tooltip, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";
import { Opportunity, OpportunityStage } from "../../../types/crm";

export interface OpportunitiesKanbanProps {
  opportunities: Opportunity[];
  onEdit: (op: Opportunity) => void;
  onDelete: (id: number) => void;
  onView: (op: Opportunity) => void;
  onStageChange: (id: number, newStage: OpportunityStage) => void;
}

const stages: OpportunityStage[] = ["سرنخ", "مذاکره", "پیشنهاد", "توافق", "برنده", "باخته"];

export const OpportunitiesKanban: React.FC<OpportunitiesKanbanProps> = ({ opportunities, onEdit, onDelete, onView, onStageChange }) => {
  const stageMap = useMemo(() => {
    const map: Record<OpportunityStage, Opportunity[]> = { سرنخ: [], مذاکره: [], پیشنهاد: [], توافق: [], برنده: [], باخته: [] };
    opportunities.forEach(op => map[op.stage].push(op));
    return map;
  }, [opportunities]);

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return;
    const fromStage = result.source.droppableId as OpportunityStage;
    const toStage = result.destination.droppableId as OpportunityStage;
    if (fromStage !== toStage) {
      const op = stageMap[fromStage][result.source.index];
      onStageChange(op.id!, toStage);
    }
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div>
        {stages.map(stage => (
          <Droppable droppableId={stage} key={stage}>
            {(provided, snapshot) => (
              <Card ref={provided.innerRef} {...provided.droppableProps} style={{  minWidth: 280, p: 2, bgcolor: snapshot.isDraggingOver ? "grey.100" : "white"  }}>
                <Typography.Title level={4}>{stage}</Typography.Title>
                <Stack spacing={2}>
                  {stageMap[stage].map((op, idx) => (
                    <Draggable draggableId={String(op.id)} index={idx} key={op.id}>
                      {(provided, snapshot) => (
                        <Card ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} style={{  p: 1, bgcolor: snapshot.isDragging ? "grey.200" : "white"  }}>
                          <Typography fontWeight={600}>{op.title}</Typography>
                          <Typography.Text>{op.customerName}</Typography.Text>
                          <Typography.Text>مبلغ: {op.amount.toLocaleString()} {op.currency}</Typography.Text>
                          <Tag label={op.status} size="small" style={{  mt: 1  }} color={op.status === "برنده" ? "success" : op.status === "باخته" ? "error" : "default"} />
                          <div>
                            <Tooltip title="مشاهده جزئیات"><Button type="text" onClick={() => onView(op)}><VisibilityIcon /></Button></Tooltip>
                            <Tooltip title="ویرایش"><Button type="text" onClick={() => onEdit(op)}><EditIcon /></Button></Tooltip>
                            <Tooltip title="حذف"><Button type="text" onClick={() => onDelete(op.id!)}><DeleteIcon color="error" /></Button></Tooltip>
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