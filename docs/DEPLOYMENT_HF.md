# Hugging Face Docker Space Deployment

This deployment uses a single Docker container for the React/Vite frontend and FastAPI backend. Google Calendar is optional for this first public demo.

## 1. Create a local Hugging Face CLI environment

```bash
cd /home/mcdimas/projects/language-based-scheduler
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -U huggingface_hub
```

## 2. Log in

```bash
hf auth login
```

## 3. Create the Docker Space

```bash
hf repos create TsukishimaAlan20/language-based-scheduler \
  --repo-type space \
  --space-sdk docker \
  --public \
  --exist-ok
```

## 4. Create the BERT model artifact repo

```bash
hf repos create TsukishimaAlan20/language-based-scheduler-bert-checkpoint \
  --repo-type model \
  --public \
  --exist-ok
```

## 5. Upload the legacy BERT checkpoint

```bash
hf upload TsukishimaAlan20/language-based-scheduler-bert-checkpoint \
  /home/mcdimas/projects/language-based-scheduler/LEGACY/last_trained_model_checkpoint.pth \
  last_trained_model_checkpoint.pth
```

Do not commit `LEGACY/last_trained_model_checkpoint.pth` to GitHub. It is ignored by `.gitignore` and `.dockerignore`.

## 6. Add the GitHub Actions secret

In GitHub, open:

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

Use:

```text
Name: HF_TOKEN
Value: Hugging Face write token
```

## 7. Push main to trigger Space sync

```bash
git push origin main
```

The workflow `.github/workflows/sync-to-huggingface.yml` syncs this repository to:

```text
TsukishimaAlan20/language-based-scheduler
```

## 8. Configure Hugging Face Space variables

In the Space settings, add:

```text
BERT_HF_REPO_ID=TsukishimaAlan20/language-based-scheduler-bert-checkpoint
BERT_HF_FILENAME=last_trained_model_checkpoint.pth
BERT_DOWNLOAD_FROM_HF=true
BERT_CHECKPOINT_PATH=/app/models/last_trained_model_checkpoint.pth
WHISPER_MODEL=base
SPACY_MODEL=en_core_web_sm
LOAD_MODELS_ON_STARTUP=true
APP_TIMEZONE=Asia/Jakarta
ENABLE_GOOGLE_CALENDAR=false
FRONTEND_URL=https://TsukishimaAlan20-language-based-scheduler.hf.space
```

No Google secrets are needed for this deployment phase.

## Local Docker verification

```bash
cd /home/mcdimas/projects/language-based-scheduler
docker build -t language-based-scheduler .
docker run --rm -p 7860:7860 \
  -e BERT_HF_REPO_ID=TsukishimaAlan20/language-based-scheduler-bert-checkpoint \
  -e BERT_HF_FILENAME=last_trained_model_checkpoint.pth \
  -e BERT_DOWNLOAD_FROM_HF=true \
  -e BERT_CHECKPOINT_PATH=/app/models/last_trained_model_checkpoint.pth \
  -e WHISPER_MODEL=base \
  -e SPACY_MODEL=en_core_web_sm \
  -e LOAD_MODELS_ON_STARTUP=true \
  -e ENABLE_GOOGLE_CALENDAR=false \
  language-based-scheduler
```

Open:

```text
http://localhost:7860
http://localhost:7860/health
```

Expected health:

- spaCy available: `true`
- BERT available: `true` after the checkpoint downloads and loads
- Whisper available: `true` after the model and ffmpeg are available
- Calendar configured: `false`
- Calendar optional: `true`

## Limitations

- Whisper base and BERT run on CPU, so cold starts and transcription can be slow.
- Free Spaces may sleep after inactivity and restart on the next request.
- Calendar event creation remains disabled until Google OAuth is configured with the deployed HTTPS callback.
