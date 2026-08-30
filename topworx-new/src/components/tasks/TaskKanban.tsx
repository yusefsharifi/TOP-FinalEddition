// topworx-new/src/components/tasks/TaskKanban.tsx
import React from "react";
import { Button, Card, Tag, Tooltip, Typography } from 'antd';
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { Task } from "../../api/tasks/types";
import { EditOutlined } from '@ant-design/icons';
import { statusLabels } from "./TaskTable";

const statusOrder: Task["status"][] = ["todo", "in_progress", "done", "cancelled"];

export const TaskKanban: React.FC<{
  tasks: Task[];
  onEdit: (task: Task) => void;
  onStatusChange: (taskId: string, newStatus: Task["status"]) => void;
}> = ({ tasks, onEdit, onStatusChange }) => {
  const columns = statusOrder.map((status) => ({
    status,
    tasks: tasks.filter((t) => t.status === status),
  }));

  const onDragEnd = (result: any) => {
    if (!result.destination) return;
    const { draggableId, destination, source } = result;
    const newStatus = statusOrder[destination.droppableId];
    if (newStatus && newStatus !== statusOrder[source.droppableId]) {
      onStatusChange(draggableId, newStatus);
    }
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div>
        {columns.map((col, idx) => (
          <Droppable droppableId={String(idx)} key={col.status}>
            {(provided) => (
              <Card
                ref={provided.innerRef}
                {...provided.droppableProps}
                style={{  minWidth: 270, p: 2, bgcolor: "#f5f5f5"  }}
              >
                <Typography.Title level={4}>{statusLabels[col.status]}</Typography.Title>
                {col.tasks.map((task, i) => (
                  <Draggable draggableId={task.id} index={i} key={task.id}>
                    {(prov) => (
                      <Card
                        ref={prov.innerRef}
                        {...prov.draggableProps}
                        {...prov.dragHandleProps}
                        style={{  mb: 2, p: 1.5, bgcolor: "#fff", boxShadow: 1  }}
                      >
                        <div>
                          <Typography fontWeight="bold">{task.title}</Typography>
                          <Tooltip title="ویرایش">
                            <Button type="text" size="small" onClick={() => onEdit(task)}>
                              <EditIcon fontSize="small" />
                            </Button>
                          </Tooltip>
                        </div>
                        <Typography fontSize={13} color="text.secondary" mb={1}>{task.assignee.name}</Typography>
                        <Tag label={task.priority === "high" ? "زیاد" : task.priority === "medium" ? "متوسط" : "کم"}
                              color={task.priority === "high" ? "error" : task.priority === "medium" ? "primary" : "default"}
                              size="small" />
                      </Card>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </Card>
            )}
          </Droppable>
        ))}
      </div>
    </DragDropContext>
  );
};