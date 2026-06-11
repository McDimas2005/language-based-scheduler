# Language Based Scheduler

An AI-powered language-based scheduler that turns natural-language requests into editable Google Calendar events. This is a production-style upgrade of the original college NLP AOL notebook project, preserving the legacy Whisper, spaCy, and fine-tuned BERT pipeline.

## Demo Screenshots

Screenshots can be added after running the app locally:

- Landing and scheduler workspace
- Event draft preview
- Google Calendar success state

## Key Features

- Browser voice recording with playback before analysis
- Audio upload for `.wav`, `.mp3`, `.m4a`, `.ogg`, and `.webm`
- Manual natural-language text input
- Whisper transcription using the legacy `base` model family
- spaCy and rule-assisted extraction for activity, date, time, and duration
- Fine-tuned BERT activity classification from `LEGACY/last_trained_model_checkpoint.pth`
- Editable event draft before any calendar write
- Google Calendar OAuth 2.0 event creation
- Clear loading, warning, missing-field, auth, success, and error states

## AI/NLP Pipeline

```text
Voice / Audio / Text
        |
        v
Whisper transcription
        |
        v
Text cleanup + spaCy DATE/TIME/entity extraction
        |
        v
Rule-based date/time/duration fallback parsing
        |
        v
Fine-tuned BERT activity classification
        |
        v
Editable event draft
        |
        v
Google Calendar event after user confirmation
```

## Tech Stack

- Backend: Python, FastAPI, Pydantic, PyTorch, transformers, openai-whisper, spaCy, python-dateutil, Google Calendar API
- Frontend: React, TypeScript, Vite, Tailwind CSS, Framer Motion, lucide-react
- Testing: pytest, FastAPI TestClient, TypeScript build

## Folder Structure

```text
backend/     FastAPI API, AI services, calendar integration, tests
frontend/    React + TypeScript scheduler UI
LEGACY/      Original notebooks, PDF, checkpoint, and audio samples
docs/        Architecture, model card, API reference, legacy notes
```

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_trf
uvicorn app.main:app --reload
```

Whisper requires `ffmpeg` on the system path. On Debian/Ubuntu:

```bash
sudo apt-get install ffmpeg
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173` and expects the backend at `http://localhost:8001` by default. Override the backend URL with `VITE_API_URL` if needed.

## Google Calendar Setup

This local/demo setup does not require Google Cloud billing. You only need a free Google Cloud project with the Calendar API enabled and an OAuth consent screen in Testing mode.

1. Create a Google Cloud project.
2. Enable **Google Calendar API**.
3. Configure the OAuth consent screen:
   - User type: **External**
   - Publishing status: **Testing**
   - Add your Google account under **Test users**
4. Add these OAuth scopes:
   - `https://www.googleapis.com/auth/calendar.events`
   - `openid`
   - `email`
   - `profile`
5. Create an OAuth 2.0 Client ID:
   - Application type: **Web application**
   - Authorized JavaScript origin: `http://localhost:5173`
   - Authorized redirect URI: `http://localhost:8001/api/auth/google/callback`
6. Copy `backend/.env.example` to `backend/.env`.
7. Fill `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `GOOGLE_CALENDAR_SCOPES`, and `FRONTEND_URL`.
8. Restart backend and frontend.
9. Test sign in, switch account, logout, draft confirmation, and event creation.

Do not commit `.env`, OAuth client secrets, local token files, credentials JSON, private keys, or service account files. The redirect URI in Google Cloud must exactly match `GOOGLE_REDIRECT_URI`; if the backend runs on `8001`, do not configure Google Cloud with `8000` unless the backend is actually running on `8000`.

## Environment Variables

See [backend/.env.example](backend/.env.example).

Important defaults:

- `APP_TIMEZONE=Asia/Jakarta`
- `WHISPER_MODEL=base`
- `BERT_CHECKPOINT_PATH=../LEGACY/last_trained_model_checkpoint.pth`
- `FRONTEND_URL=http://localhost:5173`
- `GOOGLE_REDIRECT_URI=http://localhost:8001/api/auth/google/callback`
- `GOOGLE_CALENDAR_SCOPES=https://www.googleapis.com/auth/calendar.events,openid,email,profile`

## Legacy Audio Testing

After installing backend dependencies and `ffmpeg`, test audio scheduling with:

```bash
curl -F "file=@../LEGACY/ContentBased_audio_SRPreTrained_TEST.wav" \
  http://localhost:8001/api/schedule-from-audio
```

The repository also includes `LEGACY/ContentBased_audio_SRPreTrained_TEST.mp3`.

## API Summary

- `GET /health`
- `POST /api/transcribe`
- `POST /api/analyze-text`
- `POST /api/schedule-from-audio`
- `GET /api/auth/google/start`
- `GET /api/auth/google/callback`
- `GET /api/auth/google/status`
- `POST /api/auth/google/logout`
- `POST /api/calendar/create-event`

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for request and response details.

## Model Notes

The legacy BERT notebook trained `bert-base-uncased` for five activity labels. The recovered inference label order is:

```text
career, education, health, hobby, social
```

The notebook reported weighted F1 of about `0.7606`. See [docs/MODEL_CARD.md](docs/MODEL_CARD.md).

## Known Limitations

- Whisper requires local model download and `ffmpeg`.
- `en_core_web_trf` is large and must be installed separately.
- The BERT checkpoint is large and local; model inference is unavailable until PyTorch/transformers dependencies are installed.
- Google Calendar writes require user OAuth setup.
- Date/time extraction is conservative and intentionally asks users to confirm uncertain drafts.

## Future Improvements

- Add faster-whisper as an optional ASR backend.
- Add persistent event history with SQLite/PostgreSQL.
- Add timezone selection and recurring event support.
- Add a dedicated Google disconnect route that revokes OAuth permission in addition to clearing the local token.
- Add Playwright E2E tests.
- Package production deployment with HTTPS OAuth callback support.

## Credits

Upgraded from the original college NLP AOL project by:

- Bintang Haidar Rabbani Pradipayasa
- Michael Dimas Chrispradipta
- Mousa Khalil Mousa Ayesh
