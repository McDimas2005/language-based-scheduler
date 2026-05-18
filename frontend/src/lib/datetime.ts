import type { EditableDraft, EventDraft } from "../types/api";

export function toEditableDraft(draft: EventDraft): EditableDraft {
  return {
    title: draft.title ?? "",
    date: draft.date ?? "",
    time: draft.time ?? "",
    duration_minutes: draft.duration_minutes || 60,
    timezone: draft.timezone || "Asia/Jakarta",
    category: draft.category ?? "",
    description: draft.description ?? "",
    start_datetime: draft.start_datetime ?? "",
    end_datetime: draft.end_datetime ?? "",
  };
}

export function recomputeDatetimes(draft: EditableDraft): EditableDraft {
  if (!draft.date || !draft.time) {
    return { ...draft, start_datetime: "", end_datetime: "" };
  }
  const start = new Date(`${draft.date}T${draft.time}:00`);
  if (Number.isNaN(start.getTime())) {
    return { ...draft, start_datetime: "", end_datetime: "" };
  }
  const end = new Date(start.getTime() + draft.duration_minutes * 60_000);
  const offset = "+07:00";
  return {
    ...draft,
    start_datetime: `${draft.date}T${draft.time}:00${offset}`,
    end_datetime: `${formatLocal(end)}${offset}`,
  };
}

function formatLocal(date: Date) {
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(
    date.getHours(),
  )}:${pad(date.getMinutes())}:00`;
}

