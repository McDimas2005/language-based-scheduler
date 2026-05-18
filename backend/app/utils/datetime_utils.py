from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

TIME_OF_DAY_DEFAULTS = {
    "morning": time(9, 0),
    "noon": time(12, 0),
    "afternoon": time(14, 0),
    "evening": time(18, 0),
    "tonight": time(20, 0),
    "night": time(20, 0),
}


def now_in_timezone(timezone: str) -> datetime:
    return datetime.now(ZoneInfo(timezone))


def next_weekday(today: date, weekday_name: str, force_next: bool = True) -> date:
    weekday = WEEKDAYS[weekday_name.lower()]
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0 or force_next:
        days_ahead += 7 if days_ahead <= 0 else 0
    return today + timedelta(days=days_ahead)


def combine_local(target_date: date, target_time: time, timezone: str) -> datetime:
    return datetime.combine(target_date, target_time, tzinfo=ZoneInfo(timezone))

