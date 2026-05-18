from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.api.deps import get_services
from app.models.schemas import EventDraft, TextAnalyzeRequest, TranscriptionResponse


router = APIRouter(prefix="/api", tags=["schedule"])


@router.post("/analyze-text", response_model=EventDraft)
async def analyze_text(payload: TextAnalyzeRequest, services=Depends(get_services)) -> EventDraft:
    return services.pipeline.analyze_text(payload.text, payload.timezone)


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile, services=Depends(get_services)) -> TranscriptionResponse:
    try:
        return await services.whisper_service.transcribe_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/schedule-from-audio", response_model=EventDraft)
async def schedule_from_audio(file: UploadFile, services=Depends(get_services)) -> EventDraft:
    try:
        transcription = await services.whisper_service.transcribe_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    draft = services.pipeline.analyze_text(transcription.transcript, transcript=transcription.transcript)
    draft.warnings.extend(transcription.warnings)
    return draft
