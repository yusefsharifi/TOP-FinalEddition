import React from "react";
import Timeline from "react-calendar-timeline";
import "react-calendar-timeline/lib/Timeline.css";
import { Project } from "../../api/projects/types";

export const ProjectTimeline: React.FC<{ projects: Project[] }> = ({ projects }) => {
  const groups = projects.map((p) => ({ id: p.id, title: p.title }));
  const items = projects.map((p) => ({
    id: p.id,
    group: p.id,
    title: p.title,
    start_time: new Date(p.startDate),
    end_time: new Date(p.endDate),
  }));

  return (
    <Timeline
      groups={groups}
      items={items}
      defaultTimeStart={new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)}
      defaultTimeEnd={new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)}
      canMove={false}
      canResize={false}
      stackItems
      itemHeightRatio={0.75}
    />
  );
};