FROM node:22-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    XDG_CACHE_HOME=/app/.cache \
    PORT=7860 \
    ENVIRONMENT=hf-space \
    SPACY_MODEL=en_core_web_sm \
    SPACY_FALLBACK_MODEL=en_core_web_sm \
    WHISPER_MODEL=base \
    LOAD_MODELS_ON_STARTUP=true \
    ENABLE_GOOGLE_CALENDAR=false \
    BERT_CHECKPOINT_PATH=/app/models/last_trained_model_checkpoint.pth \
    BERT_HF_REPO_ID=DimasAI20/language-based-scheduler-bert-checkpoint \
    BERT_HF_FILENAME=last_trained_model_checkpoint.pth \
    BERT_DOWNLOAD_FROM_HF=true

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ffmpeg \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app/backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python -m spacy download en_core_web_sm \
    && python -c "import whisper; whisper.load_model('base')"

COPY backend/app ./app
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

RUN mkdir -p /app/models \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
