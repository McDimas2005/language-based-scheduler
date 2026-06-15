import os

from fastapi import APIRouter, Depends

from app.api.deps import get_services
from app.models.schemas import BertHealth, CalendarHealth, HealthResponse, ModelStatus, SpacyHealth, WhisperHealth


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(services=Depends(get_services)) -> HealthResponse:
    settings = services.settings
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
    if not services.whisper_service.ffmpeg_available():
        warnings.append("ffmpeg is not installed; Whisper audio transcription will fail until it is available.")
    auth_status = services.calendar_service.auth_status()
    environment = settings.environment
    if environment == "local" and os.environ.get("SPACE_ID"):
        environment = "hf-space"
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=environment,
        models=ModelStatus(
            spacy=SpacyHealth(
                available=services.extraction_service.is_spacy_available(),
                model=services.extraction_service.spacy_model_name(),
                error=None if services.extraction_service.is_spacy_available() else spacy_warning,
            ),
            bert=BertHealth(
                available=services.classifier.is_loaded(),
                checkpoint_path=str(settings.bert_checkpoint_path),
                labels=settings.bert_labels,
                error=classifier_warning,
            ),
            whisper=WhisperHealth(
                available=services.whisper_service.is_loaded(),
                model=settings.whisper_model,
                ffmpeg=services.whisper_service.ffmpeg_available(),
                error=whisper_warning,
            ),
            warnings=list(dict.fromkeys(warnings)),
        ),
        calendar=CalendarHealth(
            configured=auth_status.configured,
            connected=auth_status.connected,
            optional=True,
            message=auth_status.message,
        ),
    )
