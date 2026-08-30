import React from "react";
import { Card, Tag, Typography } from 'antd';
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { Project } from "../../api/projects/types";

const statusOrder: Project["status"][] = ["active", "completed", "paused", "cancelled"];
const statusLabels: Record<string, string> = {
  active: "در حال انجام",
  completed: "تکمیل شده",
  paused: "متوقف",
  cancelled: "لغو شده",
};

export const ProjectKanban: React.FC<{
  projects: Project[];
  onStatusChange: (projectId: string, newStatus: Project["status"]) => void;
  onDetails: (id: string) => void;
}> = ({ projects, onStatusChange, onDetails }) => {
  const columns = statusOrder.map((status) => ({
    status,
    projects: projects.filter((p) => p.status === status),
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
                {col.projects.map((project, i) => (
                  <Draggable draggableId={project.id} index={i} key={project.id}>
                    {(prov) => (
                      <Card
                        ref={prov.innerRef}
                        {...prov.draggableProps}
                        {...prov.dragHandleProps}
                        style={{  mb: 2, p: 1.5, bgcolor: "#fff", boxShadow: 1, cursor: "pointer"  }}
                        onClick={() => onDetails(project.id)}
                      >
                        <Typography fontWeight="bold">{project.title}</Typography>
                        <Typography fontSize={13} color="text.secondary" mb={1}>{project.description?.slice(0, 40)}</Typography>
                        <Tag label={statusLabels[project.status]} size="small" />
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