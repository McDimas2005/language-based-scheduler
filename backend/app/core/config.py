from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Language Based Scheduler"
    app_version: str = "1.0.0"
    app_timezone: str = "Asia/Jakarta"
    default_duration_minutes: int = 60
    frontend_url: str = "http://localhost:5173"
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    max_audio_size_mb: int = 25
    whisper_model: str = "base"
    whisper_language: str | None = "en"

    spacy_model: str = "en_core_web_trf"
    spacy_fallback_model: str = "en_core_web_sm"

    bert_base_model: str = "bert-base-uncased"
    bert_checkpoint_path: Path = ROOT_DIR / "LEGACY" / "last_trained_model_checkpoint.pth"
    bert_max_length: int = 128
    bert_labels: List[str] = Field(
        default_factory=lambda: ["career", "education", "health", "hobby", "social"]
    )

    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"
    google_calendar_scopes: str = "https://www.googleapis.com/auth/calendar.events"
    google_token_path: Path = ROOT_DIR / "backend" / ".tokens" / "google_token.json"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / "backend" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def max_audio_size_bytes(self) -> int:
        return self.max_audio_size_mb * 1024 * 1024

    @property
    def google_scopes(self) -> list[str]:
        return [scope.strip() for scope in self.google_calendar_scopes.split(",") if scope.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

