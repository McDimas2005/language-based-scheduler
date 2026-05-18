# API Reference

Base URL: `http://localhost:8000`

## GET /health

Returns backend status, app version, timezone, and model availability.

```json
{
  "status": "ok",
  "app": "Language Based Scheduler",
  "version": "1.0.0",
  "timezone": "Asia/Jakarta",
  "models": {
    "whisper_available": false,
    "bert_available": false,
    "spacy_available": false,
    "warnings": []
  }
}
```

## POST /api/transcribe

Multipart form upload:

- `file`: `.wav`, `.mp3`, `.m4a`, `.ogg`, or `.webm`

Returns:

```json
{
  "transcript": "I want to go to the library tomorrow at 7 PM.",
  "language": "en",
  "metadata": { "model": "base" },
  "warnings": []
}
```

## POST /api/analyze-text

Request:

```json
{
  "text": "Schedule a meeting with my lecturer tomorrow at 10 AM",
  "timezone": "Asia/Jakarta"
}
```

Returns an editable event draft:

```json
{
  "source_text": "...",
  "title": "A meeting with my lecturer",
  "category": "education",
  "category_confidence": 0.87,
  "date": "2026-05-19",
  "time": "10:00",
  "timezone": "Asia/Jakarta",
  "duration_minutes": 60,
  "start_datetime": "2026-05-19T10:00:00+07:00",
  "end_datetime": "2026-05-19T11:00:00+07:00",
  "missing_fields": [],
  "warnings": [],
  "needs_user_confirmation": true
}
```

## POST /api/schedule-from-audio

Multipart form upload:

- `file`: audio file

Runs transcription and text analysis. Returns the same event draft schema as `/api/analyze-text`.

## GET /api/auth/google/status

Returns OAuth configuration and connection status.

## GET /api/auth/google/start

Returns:

```json
{
  "authorization_url": "https://accounts.google.com/...",
  "state": "..."
}
```

The frontend redirects the user to `authorization_url`.

## GET /api/auth/google/callback

Google OAuth redirect target. Stores the local dev token under `backend/.tokens/` and redirects back to the frontend.

## POST /api/auth/google/logout

Deletes the local dev OAuth token and returns updated auth status.

## POST /api/calendar/create-event

Request:

```json
{
  "title": "Meeting with advisor",
  "start_datetime": "2026-05-19T10:00:00+07:00",
  "end_datetime": "2026-05-19T11:00:00+07:00",
  "timezone": "Asia/Jakarta",
  "description": "Source: ...",
  "category": "education"
}
```

Returns:

```json
{
  "calendar_event_id": "abc123",
  "html_link": "https://calendar.google.com/...",
  "status": "created",
  "created_at": "2026-05-18T10:00:00"
}
```

