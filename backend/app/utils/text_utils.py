import re


FILLER_PATTERNS = [
    r"^\s*(please\s+)?(schedule|add|book|create|set|remind me to)\s+",
    r"^\s*(i want to|i need to|i'm going to|i am going to)\s+",
]


def clean_text(text: str) -> str:
    compact = re.sub(r"\s+", " ", text or "").strip()
    return compact


def strip_command_prefix(text: str) -> str:
    title = clean_text(text)
    for pattern in FILLER_PATTERNS:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)
    return title.strip(" ,.")

