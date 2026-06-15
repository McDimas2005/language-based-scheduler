from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402
from app.services.bert_classifier_service import BertActivityClassifier  # noqa: E402
from app.services.extraction_service import ExtractionService  # noqa: E402
from app.services.whisper_service import WhisperService  # noqa: E402


def ok(message: str) -> None:
    print(f"[OK] {message}")


def fail(message: str) -> None:
    print(f"[ERROR] {message}")


def main() -> int:
    settings = get_settings()
    failures = 0

    print(f"Python: {platform.python_version()} ({sys.executable})")
    print(f"Environment: {settings.environment}")
    print(f"BERT checkpoint path: {settings.bert_checkpoint_path}")

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        ok(f"ffmpeg available at {ffmpeg}")
    else:
        fail("ffmpeg is not available on PATH")
        failures += 1

    extraction = ExtractionService(settings)
    if extraction.is_spacy_available():
        ok(f"spaCy loaded: {extraction.spacy_model_name()}")
    else:
        fail(extraction.spacy_warning() or "spaCy could not load")
        failures += 1

    whisper = WhisperService(settings)
    if whisper.load_model():
        ok(f"Whisper loaded: {settings.whisper_model}")
    else:
        fail(whisper.status_warning() or "Whisper could not load")
        failures += 1

    classifier = BertActivityClassifier(settings)
    checkpoint_path = classifier._ensure_checkpoint()
    if checkpoint_path.exists():
        ok(f"BERT checkpoint available: {checkpoint_path}")
    else:
        fail(classifier.status_warning() or f"BERT checkpoint missing: {checkpoint_path}")
        failures += 1

    if classifier.load_model():
        ok("BERT model loaded")
        sample = "Schedule a meeting with my lecturer tomorrow at 10 AM"
        prediction = classifier.predict(sample)
        ok(
            "BERT sample prediction: "
            f"{prediction.label} ({prediction.confidence:.2%}) for {sample!r}"
        )
    else:
        fail(classifier.status_warning() or "BERT model could not load")
        failures += 1

    if failures:
        fail(f"{failures} model checks failed")
        return 1
    ok("All model checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
