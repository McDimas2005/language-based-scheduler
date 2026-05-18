# Backend

FastAPI backend for Language Based Scheduler.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_trf
uvicorn app.main:app --reload
```

Whisper requires `ffmpeg` on the system path.

## Legacy Model

The BERT classifier loads `../LEGACY/last_trained_model_checkpoint.pth` and uses `bert-base-uncased` with labels:

```text
career, education, health, hobby, social
```

