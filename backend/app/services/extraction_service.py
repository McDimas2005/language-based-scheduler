from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta

from dateutil import parser

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.schemas import ExtractionResult
from app.utils.datetime_utils import (
    TIME_OF_DAY_DEFAULTS,
    WEEKDAYS,
    combine_local,
    next_weekday,
    now_in_timezone,
)
from app.utils.text_utils import clean_text, strip_command_prefix


logger = get_logger(__name__)


class ExtractionService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._nlp = None
        self._spacy_error: str | None = None
        self._spacy_model_name: str | None = None

    def is_spacy_available(self) -> bool:
        return self._load_spacy() is not None

    def spacy_warning(self) -> str | None:
        self._load_spacy()
        return self._spacy_error

    def extract(self, text: str, timezone: str | None = None) -> ExtractionResult:
        tz = timezone or self.settings.app_timezone
        cleaned = clean_text(text)
        warnings: list[str] = []
        if not cleaned:
            return ExtractionResult(
                cleaned_text="",
                missing_fields=["title", "date", "time"],
                warnings=["Please provide a schedule request."],
            )

        doc = self._load_spacy()
        date_candidates, time_candidates = self._extract_entities(cleaned, doc)
        date_expr = self._find_date_expression(cleaned, date_candidates)
        time_expr = self._find_time_expression(cleaned, time_candidates)
        duration_minutes = self._find_duration(cleaned) or self.settings.default_duration_minutes

        if self._spacy_error:
            warnings.append(self._spacy_error)

        parsed_date = self._parse_date(date_expr, tz)
        parsed_time, time_warning = self._parse_time(time_expr, cleaned)
        if time_warning:
            warnings.append(time_warning)

        missing_fields: list[str] = []
        if parsed_date is None:
            missing_fields.append("date")
            warnings.append("Date was not clear enough to schedule automatically.")
        if parsed_time is None:
            missing_fields.append("time")
            warnings.append("Time was not clear enough to schedule automatically.")

        title = self._extract_title(cleaned, date_expr, time_expr)
        if not title:
            missing_fields.append("title")
            warnings.append("Activity title was not clear enough.")

        start_datetime = None
        end_datetime = None
        if parsed_date and parsed_time:
            start = combine_local(parsed_date, parsed_time, tz)
            end = start + timedelta(minutes=duration_minutes)
            start_datetime = start.isoformat()
            end_datetime = end.isoformat()

        return ExtractionResult(
            cleaned_text=cleaned,
            activity_title=title,
            date=parsed_date.isoformat() if parsed_date else None,
            time=parsed_time.strftime("%H:%M") if parsed_time else None,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            duration_minutes=duration_minutes,
            notes=cleaned,
            missing_fields=sorted(set(missing_fields)),
            warnings=self._dedupe(warnings),
            needs_user_confirmation=True,
        )

    def _load_spacy(self):
        if self._nlp is not None or self._spacy_error:
            return self._nlp
        try:
            import spacy
        except Exception as exc:
            self._spacy_error = f"spaCy is unavailable; using rule-based extraction only ({exc})."
            logger.warning(self._spacy_error)
            return None

        for model_name in (self.settings.spacy_model, self.settings.spacy_fallback_model):
            try:
                self._nlp = spacy.load(model_name)
                self._spacy_model_name = model_name
                if model_name != self.settings.spacy_model:
                    self._spacy_error = (
                        f"Configured spaCy model {self.settings.spacy_model} is unavailable; "
                        f"using {model_name}."
                    )
                return self._nlp
            except Exception:
                continue

        self._spacy_error = (
            f"spaCy model {self.settings.spacy_model} is unavailable. "
            "Install it with: python -m spacy download en_core_web_trf."
        )
        logger.warning(self._spacy_error)
        return None

    @staticmethod
    def _extract_entities(text: str, doc) -> tuple[list[str], list[str]]:
        dates: list[str] = []
        times: list[str] = []
        if doc is None:
            return dates, times
        parsed_doc = doc(text)
        for ent in parsed_doc.ents:
            if ent.label_ == "DATE":
                dates.append(ent.text)
            elif ent.label_ == "TIME":
                times.append(ent.text)
        return dates, times

    def _find_date_expression(self, text: str, candidates: list[str]) -> str | None:
        lowered = text.lower()
        patterns = [
            r"\btonight\b",
            r"\btomorrow\b",
            r"\btoday\b",
            r"\bnext\s+week\b",
            r"\bin\s+\d+\s+(?:day|days|week|weeks)\b",
            r"\bnext\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            r"\b(?:on\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:,\s*\d{4})?\b",
            r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, lowered, flags=re.IGNORECASE)
            if match:
                return match.group(0).removeprefix("on ").strip()
        return candidates[0] if candidates else None

    def _find_time_expression(self, text: str, candidates: list[str]) -> str | None:
        patterns = [
            r"\b\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)\b",
            r"\bat\s+\d{1,2}(?::\d{2})?\b",
            r"\b(?:morning|afternoon|evening|tonight|night|noon)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(0).removeprefix("at ").strip()
        return candidates[0] if candidates else None

    @staticmethod
    def _find_duration(text: str) -> int | None:
        match = re.search(r"\b(?:for\s+)?(\d+(?:\.\d+)?)\s*(hour|hours|hr|hrs|minute|minutes|min|mins)\b", text, re.I)
        if not match:
            return None
        amount = float(match.group(1))
        unit = match.group(2).lower()
        return int(amount * 60) if unit.startswith(("hour", "hr")) else int(amount)

    def _parse_date(self, expression: str | None, timezone: str) -> date | None:
        today = now_in_timezone(timezone).date()
        if not expression:
            return None
        expr = expression.lower().strip()
        if expr in {"today", "tonight"}:
            return today
        if expr == "tomorrow":
            return today + timedelta(days=1)
        if expr == "next week":
            return today + timedelta(days=7)

        match = re.search(r"in\s+(\d+)\s+(day|days|week|weeks)", expr)
        if match:
            amount = int(match.group(1))
            return today + timedelta(days=amount * (7 if "week" in match.group(2) else 1))

        match = re.search(r"next\s+(" + "|".join(WEEKDAYS) + r")", expr)
        if match:
            return next_weekday(today, match.group(1), force_next=True)

        match = re.search(r"\b(" + "|".join(WEEKDAYS) + r")\b", expr)
        if match:
            return next_weekday(today, match.group(1), force_next=False)

        try:
            default = datetime.combine(today, time(12, 0))
            parsed = parser.parse(expression, default=default, fuzzy=True)
            return parsed.date()
        except Exception:
            return None

    def _parse_time(self, expression: str | None, text: str) -> tuple[time | None, str | None]:
        if not expression:
            return None, None
        expr = expression.lower().strip()
        if expr in TIME_OF_DAY_DEFAULTS:
            return TIME_OF_DAY_DEFAULTS[expr], f"Using {TIME_OF_DAY_DEFAULTS[expr].strftime('%H:%M')} for '{expr}'."
        numeric_match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?", expr)
        if numeric_match:
            hour = int(numeric_match.group(1))
            minute = int(numeric_match.group(2) or 0)
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                warning = "Time has no AM/PM marker; please confirm it in the preview."
                return time(hour, minute), warning
        try:
            parsed = parser.parse(expr, fuzzy=True)
            parsed_time = parsed.time().replace(second=0, microsecond=0)
            return parsed_time, None
        except Exception:
            return None, None

    def _extract_title(self, text: str, date_expr: str | None, time_expr: str | None) -> str | None:
        title = strip_command_prefix(text)
        remove_phrases = [date_expr, time_expr]
        duration = re.search(r"\b(?:for\s+)?\d+(?:\.\d+)?\s*(?:hour|hours|hr|hrs|minute|minutes|min|mins)\b", title, re.I)
        if duration:
            remove_phrases.append(duration.group(0))
        for phrase in remove_phrases:
            if phrase:
                title = re.sub(r"\b(?:on|at|in|next)?\s*" + re.escape(phrase) + r"\b", " ", title, flags=re.I)
        title = re.sub(r"\b(?:on|at|for|in|next)\s*$", "", title, flags=re.I)
        title = clean_text(title).strip(" ,.")
        return title[:1].upper() + title[1:] if title else None

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        return list(dict.fromkeys(item for item in items if item))
