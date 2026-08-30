import React from "react";
import { Calendar, dateFnsLocalizer, Event as RBCEvent } from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { faIR } from "date-fns/locale";
import { format, parse, startOfWeek, getDay } from "date-fns";
import { CalendarEvent } from "../../api/calendar/types";
import withDragAndDrop from "react-big-calendar-dnd";

const DnDCalendar = withDragAndDrop(Calendar);

export const CalendarView: React.FC<{
  events: CalendarEvent[];
  onSelectEvent: (event: CalendarEvent) => void;
  onSelectSlot: (slot: { start: Date; end: Date }) => void;
  onEventDrop: (event: CalendarEvent, start: Date, end: Date) => void;
}> = ({ events, onSelectEvent, onSelectSlot, onEventDrop }) => (
  <DnDCalendar
    // ... سایر props ...
    onEventDrop={({ event, start, end }) => onEventDrop(event.resource, start, end)}
    draggableAccessor={() => true}
    // ...
  />
);

const locales = { "fa-IR": faIR };
const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 6 }),
  getDay,
  locales,
});

export const CalendarView: React.FC<{
  events: CalendarEvent[];
  onSelectEvent: (event: CalendarEvent) => void;
  onSelectSlot: (slot: { start: Date; end: Date }) => void;
}> = ({ events, onSelectEvent, onSelectSlot }) => (
  <Calendar
    localizer={localizer}
    events={events.map(e => ({
      ...e,
      start: new Date(e.start),
      end: new Date(e.end),
      title: e.title,
      allDay: e.allDay,
      resource: e,
    }))}
    startAccessor="start"
    endAccessor="end"
    style={{ height: 600 }}
    selectable
    onSelectEvent={e => onSelectEvent(e.resource)}
    onSelectSlot={slot => onSelectSlot({ start: slot.start, end: slot.end })}
    popup
    views={["month", "week", "day"]}
    messages={{
      month: "ماه",
      week: "هفته",
      day: "روز",
      today: "امروز",
      previous: "قبلی",
      next: "بعدی",
    }}
  />
);