# Architecture

## Overview

Language Based Scheduler is split into a FastAPI backend and a React/TypeScript frontend. The backend owns AI inference, extraction, calendar OAuth, and event creation. The frontend owns recording/upload/text input, draft review, edits, and confirmation.

```text
React UI
  -> FastAPI routes
  -> Whisper / spaCy / BERT services
  -> Event draft response
  -> User edits and confirms
  -> Google Calendar API
```

## Backend

The backend is organized around services:

- `WhisperService`: validates audio files, writes temporary uploads, transcribes with `openai-whisper`, and removes temp files.
- `ExtractionService`: uses spaCy entities plus rule-based parsing to extract title, date, time, duration, and missing fields.
- `BertActivityClassifier`: lazily loads `bert-base-uncased` and the legacy checkpoint.
- `SchedulerPipeline`: orchestrates text analysis into an event draft.
- `CalendarService`: handles Google OAuth and Calendar event creation.

Models are lazy-loaded or status-reported so missing local dependencies produce clear warnings instead of stack traces.

## Frontend

The frontend exposes one scheduler workspace with three input tabs:

- Voice Record
- Upload Audio
- Type Text

After analysis, the UI renders an editable event draft. The create-event action is blocked until required fields are present and Google Calendar is connected.

## Request Flow

Text input:

```text
POST /api/analyze-text
  -> clean text
  -> extract schedule fields
  -> classify activity
  -> return event draft
```

Audio input:

```text
POST /api/schedule-from-audio
  -> validate upload
  -> Whisper transcript
  -> analyze transcript
  -> return event draft
```

Calendar creation:

```text
POST /api/calendar/create-event
  -> validate confirmed draft
  -> load OAuth credentials
  -> create primary calendar event
  -> return Google event id and link
```

## Calendar Integration

OAuth 2.0 is the production path. Local development stores OAuth token JSON under `backend/.tokens/`, which is ignored by git. Service-account credentials are not required for the app flow and should not be committed.

