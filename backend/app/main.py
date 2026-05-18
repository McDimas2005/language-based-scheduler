from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes_calendar import router as calendar_router
from app.api.routes_health import router as health_router
from app.api.routes_schedule import router as schedule_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, get_logger
from app.services.bert_classifier_service import BertActivityClassifier
from app.services.calendar_service import CalendarService
from app.services.extraction_service import ExtractionService
from app.services.scheduler_pipeline import SchedulerPipeline
from app.services.whisper_service import WhisperService


configure_logging()
logger = get_logger(__name__)


@dataclass
class ServiceContainer:
    settings: Settings
    whisper_service: WhisperService
    classifier: BertActivityClassifier
    extraction_service: ExtractionService
    calendar_service: CalendarService
    pipeline: SchedulerPipeline


def build_services(settings: Settings) -> ServiceContainer:
    classifier = BertActivityClassifier(settings)
    extraction_service = ExtractionService(settings)
    whisper_service = WhisperService(settings)
    calendar_service = CalendarService(settings)
    pipeline = SchedulerPipeline(settings, extraction_service, classifier)
    return ServiceContainer(
        settings=settings,
        whisper_service=whisper_service,
        classifier=classifier,
        extraction_service=extraction_service,
        calendar_service=calendar_service,
        pipeline=pipeline,
    )


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered natural-language scheduler using Whisper, spaCy, BERT, and Google Calendar.",
    )
    app.state.services = build_services(settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error for %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Something went wrong. Please try again.", "code": "internal_error"},
        )

    app.include_router(health_router)
    app.include_router(schedule_router)
    app.include_router(calendar_router)
    return app


app = create_app()

