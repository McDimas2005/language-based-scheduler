from fastapi import APIRouter, Depends

from app.api.deps import get_services
from app.core.config import get_settings
from app.models.schemas import HealthResponse, ModelStatus
from app.services.whisper_service import WhisperService


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(services=Depends(get_services)) -> HealthResponse:
    settings = get_settings()
    warnings: list[str] = []
    classifier_warning = services.classifier.status_warning()
    spacy_warning = services.extraction_service.spacy_warning()
    whisper_warning = services.whisper_service.status_warning()
    if classifier_warning:
        warnings.append(classifier_warning)
    if spacy_warning:
        warnings.append(spacy_warning)
    if whisper_warning:
        warnings.append(whisper_warning)
    if not WhisperService.ffmpeg_available():
        warnings.append("ffmpeg is not installed; Whisper audio transcription will fail until it is available.")
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        timezone=settings.app_timezone,
        models=ModelStatus(
            whisper_available=services.whisper_service.is_loaded(),
            bert_available=services.classifier.is_loaded(),
            spacy_available=services.extraction_service.is_spacy_available(),
            warnings=list(dict.fromkeys(warnings)),
        ),
    )
