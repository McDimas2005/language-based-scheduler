import type {
  AuthStartResponse,
  AuthStatus,
  CalendarCreateResponse,
  EditableDraft,
  EventDraft,
  HealthResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/health"),
  authStatus: () => request<AuthStatus>("/api/auth/google/status"),
  startGoogleAuth: () => request<AuthStartResponse>("/api/auth/google/start"),
  logoutGoogle: () =>
    request<AuthStatus>("/api/auth/google/logout", {
      method: "POST",
    }),
  analyzeText: (text: string) =>
    request<EventDraft>("/api/analyze-text", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),
  scheduleFromAudio: (file: File | Blob, filename = "recording.webm") => {
    const form = new FormData();
    form.append("file", file, filename);
    return request<EventDraft>("/api/schedule-from-audio", {
      method: "POST",
      body: form,
    });
  },
  createEvent: (draft: EditableDraft) =>
    request<CalendarCreateResponse>("/api/calendar/create-event", {
      method: "POST",
      body: JSON.stringify({
        title: draft.title,
        start_datetime: draft.start_datetime,
        end_datetime: draft.end_datetime,
        timezone: draft.timezone,
        description: draft.description,
        category: draft.category,
      }),
    }),
};

