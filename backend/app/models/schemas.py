from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str
    code: str = "request_failed"
    warnings: list[str] = Field(default_factory=list)


class ModelStatus(BaseModel):
    whisper_available: bool
    bert_available: bool
    spacy_available: bool
    warnings: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app: str
    version: str
    timezone: str
    models: ModelStatus


class TextAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    timezone: str | None = None


class ClassificationResult(BaseModel):
    label: str
    confidence: float
    class_probabilities: dict[str, float] = Field(default_factory=dict)
    loaded: bool = True
    warning: str | None = None


class ExtractionResult(BaseModel):
    cleaned_text: str
    activity_title: str | None = None
    date: str | None = None
    time: str | None = None
    start_datetime: str | None = None
    end_datetime: str | None = None
    duration_minutes: int = 60
    notes: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    needs_user_confirmation: bool = True


class EventDraft(BaseModel):
    source_text: str
    transcript: str | None = None
    title: str | None = None
    category: str | None = None
    category_confidence: float = 0.0
    class_probabilities: dict[str, float] = Field(default_factory=dict)
    date: str | None = None
    time: str | None = None
    timezone: str = "Asia/Jakarta"
    duration_minutes: int = 60
    start_datetime: str | None = None
    end_datetime: str | None = None
    description: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    needs_user_confirmation: bool = True
    original_text: str | None = None
    cleaned_text: str | None = None
    activity_title: str | None = None
    extracted_date: str | None = None
    extracted_time: str | None = None
    predicted_category: str | None = None
    confidence: float = 0.0


class TranscriptionResponse(BaseModel):
    transcript: str
    language: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class CalendarCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    start_datetime: str
    end_datetime: str
    timezone: str = "Asia/Jakarta"
    description: str | None = None
    category: str | None = None
    notes: str | None = None


class CalendarCreateResponse(BaseModel):
    calendar_event_id: str
    html_link: str | None = None
    status: Literal["created"]
    created_at: datetime


class GoogleAuthStatus(BaseModel):
    connected: bool
    configured: bool
    email: str | None = None
    scopes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GoogleAuthStartResponse(BaseModel):
    authorization_url: str
    state: str

