from __future__ import annotations

from app.core.config import Settings
from app.models.schemas import EventDraft
from app.services.bert_classifier_service import BertActivityClassifier
from app.services.extraction_service import ExtractionService


class SchedulerPipeline:
    def __init__(
        self,
        settings: Settings,
        extraction_service: ExtractionService,
        classifier: BertActivityClassifier,
    ):
        self.settings = settings
        self.extraction_service = extraction_service
        self.classifier = classifier

    def analyze_text(
        self,
        text: str,
        timezone: str | None = None,
        transcript: str | None = None,
    ) -> EventDraft:
        tz = timezone or self.settings.app_timezone
        extraction = self.extraction_service.extract(text, tz)
        title_for_classifier = extraction.activity_title or extraction.cleaned_text
        classification = self.classifier.predict(title_for_classifier)

        warnings = list(extraction.warnings)
        if classification.warning:
            warnings.append(classification.warning)

        description_parts = [f"Source: {extraction.cleaned_text}"]
        if classification.loaded:
            description_parts.append(
                f"Predicted category: {classification.label} ({classification.confidence:.0%})"
            )

        return EventDraft(
            source_text=text,
            transcript=transcript,
            title=extraction.activity_title,
            category=None if classification.label == "unavailable" else classification.label,
            category_confidence=classification.confidence,
            class_probabilities=classification.class_probabilities,
            date=extraction.date,
            time=extraction.time,
            timezone=tz,
            duration_minutes=extraction.duration_minutes,
            start_datetime=extraction.start_datetime,
            end_datetime=extraction.end_datetime,
            description="\n".join(description_parts),
            missing_fields=extraction.missing_fields,
            warnings=list(dict.fromkeys(warnings)),
            needs_user_confirmation=True,
            original_text=text,
            cleaned_text=extraction.cleaned_text,
            activity_title=extraction.activity_title,
            extracted_date=extraction.date,
            extracted_time=extraction.time,
            predicted_category=None if classification.label == "unavailable" else classification.label,
            confidence=classification.confidence,
        )

