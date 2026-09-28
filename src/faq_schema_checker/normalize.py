import re
from html import unescape


def normalize_text(value: str) -> str:
    value = unescape(value or "")
    value = re.sub(r"\s+", " ", value)
    return value.strip().casefold()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value or "")).strip()
