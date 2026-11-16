"""Language detection."""
from langdetect import detect


def detect_language(text: str) -> str:
    try:
        code = detect(text)
    except Exception:
        return "en"
    if code.startswith("ar"):
        return "ar"
    if code.startswith("fr"):
        return "fr"
    return "en"
