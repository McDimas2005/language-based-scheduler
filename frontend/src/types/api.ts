export interface EventDraft {
  source_text: string;
  transcript?: string | null;
  title?: string | null;
  category?: string | null;
  category_confidence: number;
  class_probabilities: Record<string, number>;
  date?: string | null;
  time?: string | null;
  timezone: string;
  duration_minutes: number;
  start_datetime?: string | null;
  end_datetime?: string | null;
  description?: string | null;
  missing_fields: string[];
  warnings: string[];
  needs_user_confirmation: boolean;
  original_text?: string | null;
  cleaned_text?: string | null;
  activity_title?: string | null;
  extracted_date?: string | null;
  extracted_time?: string | null;
  predicted_category?: string | null;
  confidence: number;
}

export interface HealthResponse {
  status: "ok";
  app: string;
  version: string;
  timezone: string;
  models: {
    whisper_available: boolean;
    bert_available: boolean;
    spacy_available: boolean;
    warnings: string[];
  };
}

export interface AuthStatus {
  connected: boolean;
  configured: boolean;
  email?: string | null;
  scopes: string[];
  warnings: string[];
}

export interface AuthStartResponse {
  authorization_url: string;
  state: string;
}

export interface CalendarCreateResponse {
  calendar_event_id: string;
  html_link?: string | null;
  status: "created";
  created_at: string;
}

export interface EditableDraft {
  title: string;
  date: string;
  time: string;
  duration_minutes: number;
  timezone: string;
  category: string;
  description: string;
  start_datetime: string;
  end_datetime: string;
}

