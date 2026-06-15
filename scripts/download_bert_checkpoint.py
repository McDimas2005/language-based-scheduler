from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402
from app.services.bert_classifier_service import BertActivityClassifier  # noqa: E402


def main() -> int:
    settings = get_settings()
    classifier = BertActivityClassifier(settings)
    checkpoint_path = classifier._ensure_checkpoint()
    if checkpoint_path.exists():
        print(f"[OK] BERT checkpoint ready at {checkpoint_path}")
        return 0
    print(f"[ERROR] BERT checkpoint is not available at {checkpoint_path}")
    if classifier.status_warning():
        print(f"[ERROR] {classifier.status_warning()}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
