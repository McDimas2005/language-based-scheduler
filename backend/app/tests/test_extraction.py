from app.core.config import get_settings
from app.services.extraction_service import ExtractionService


def test_extract_tomorrow_at_10():
    service = ExtractionService(get_settings())
    result = service.extract("Schedule a meeting with my lecturer tomorrow at 10 AM")
    assert result.activity_title == "A meeting with my lecturer"
    assert result.time == "10:00"
    assert "time" not in result.missing_fields


def test_extract_in_two_days_duration():
    service = ExtractionService(get_settings())
    result = service.extract("Add gym session in 2 days at 7 AM for 90 minutes")
    assert result.activity_title == "Gym session"
    assert result.duration_minutes == 90
    assert result.time == "07:00"


def test_missing_time_is_flagged():
    service = ExtractionService(get_settings())
    result = service.extract("Book dentist appointment on Friday")
    assert "time" in result.missing_fields

