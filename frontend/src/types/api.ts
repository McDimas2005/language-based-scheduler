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
  version: string;
  environment: string;
  models: {
    spacy: {
      available: boolean;
      model?: string | null;
      error?: string | null;
    };
    bert: {
      available: boolean;
      checkpoint_path: string;
      labels: string[];
      error?: string | null;
    };
    whisper: {
      available: boolean;
      model: string;
      ffmpeg: boolean;
      error?: string | null;
    };
    warnings: string[];
  };
  calendar: {
    configured: boolean;
    connected: boolean;
    optional: boolean;
    message?: string | null;
  };
}

export interface AuthStatus {
  connected: boolean;
  configured: boolean;
  optional: boolean;
  message?: string | null;
  email?: string | null;
  name?: string | null;
  picture?: string | null;
  scopes: string[];
  warnings: string[];
}

export interface LogoutResponse {
  status: "success";
  connected: false;
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
