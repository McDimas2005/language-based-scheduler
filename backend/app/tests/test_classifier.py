from pathlib import Path

from app.core.config import Settings
from app.services.bert_classifier_service import BertActivityClassifier


def test_classifier_missing_checkpoint_degrades_gracefully(tmp_path: Path):
    settings = Settings(bert_checkpoint_path=tmp_path / "missing.pth")
    classifier = BertActivityClassifier(settings)
    result = classifier.predict("study NLP tonight")
    assert result.loaded is False
    assert result.label == "unavailable"
    assert result.confidence == 0.0

