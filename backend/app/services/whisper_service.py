from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.schemas import TranscriptionResponse
from app.utils.audio_utils import validate_audio_filename


logger = get_logger(__name__)


class WhisperService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._model = None
        self._load_error: str | None = None

    def is_loaded(self) -> bool:
        return self._model is not None

    def status_warning(self) -> str | None:
        return self._load_error

    def load_model(self) -> bool:
        if self._model is not None:
            return True
        try:
            import whisper
        except Exception as exc:  # pragma: no cover
            self._load_error = f"Whisper is unavailable: {exc}"
            logger.warning(self._load_error)
            return False
        try:  # pragma: no cover
            self._model = whisper.load_model(self.settings.whisper_model)
            self._load_error = None
            logger.info("Loaded Whisper model %s", self.settings.whisper_model)
            return True
        except Exception as exc:
            self._load_error = f"Could not load Whisper model: {exc}"
            logger.exception(self._load_error)
            return False

    async def transcribe_upload(self, file: UploadFile) -> TranscriptionResponse:
        suffix = validate_audio_filename(file.filename or "")
        contents = await file.read()
        if not contents:
            raise ValueError("The uploaded audio file is empty.")
        if len(contents) > self.settings.max_audio_size_bytes:
            raise ValueError(f"Audio file is too large. Limit is {self.settings.max_audio_size_mb} MB.")
        if not self.load_model():
            raise RuntimeError(self._load_error or "Whisper model is unavailable.")

        temp_path: Path | None = None
        start = time.perf_counter()
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(contents)
                temp_path = Path(temp_file.name)

            result = self._model.transcribe(
                str(temp_path),
                language=self.settings.whisper_language,
            )
            transcript = (result.get("text") or "").strip()
            if not transcript:
                return TranscriptionResponse(
                    transcript="",
                    language=result.get("language"),
                    metadata={"duration_seconds": round(time.perf_counter() - start, 3)},
                    warnings=["No speech was detected in the uploaded audio."],
                )
            return TranscriptionResponse(
                transcript=transcript,
                language=result.get("language"),
                metadata={
                    "model": self.settings.whisper_model,
                    "filename": file.filename,
                    "processing_seconds": round(time.perf_counter() - start, 3),
                },
            )
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    @staticmethod
    def ffmpeg_available() -> bool:
        return shutil.which("ffmpeg") is not None

