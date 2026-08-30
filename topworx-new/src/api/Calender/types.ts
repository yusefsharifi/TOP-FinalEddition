export type EventType = "meeting" | "reminder" | "holiday" | "birthday" | "task" | "custom";

export interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  type: EventType;
  start: string; // ISO date
  end: string;   // ISO date
  allDay?: boolean;
  participants: { id: string; name: string }[];
  color?: string;
  relatedTaskId?: string;
  relatedProjectId?: string;
  createdBy: { id: string; name: string };
}