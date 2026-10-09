import re
import unicodedata


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).upper()
    normalized = normalized.replace("CHILDERN", "CHILDREN")
    return re.sub(r"[^A-Z0-9]", "", normalized)


def detect_counterfeit_marker(text: str) -> str | None:
    """Match explicit Children's Bank novelty-note markers despite OCR spacing/punctuation."""
    normalized = _normalize(text)
    markers = (
        "CHILDRENSBANKOFINDIA",
        "CHILDRENBANKOFINDIA",
        "BHARATIYABALAKBANK",
    )
    for marker in markers:
        if marker in normalized:
            return marker
    return None
