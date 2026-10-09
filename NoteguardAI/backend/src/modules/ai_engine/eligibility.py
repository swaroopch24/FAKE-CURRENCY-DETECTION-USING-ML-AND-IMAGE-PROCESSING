from enum import Enum
from typing import Any


class EligibilityState(str, Enum):
    INDIAN_CURRENCY = "INDIAN_CURRENCY"
    ALLOW_CNN = "ALLOW_CNN"
    UNSUPPORTED_CURRENCY = "UNSUPPORTED_CURRENCY"


FOREIGN_INSTITUTIONS = (
    "FEDERAL RESERVE",
    "UNITED STATES OF AMERICA",
    "BANK OF ENGLAND",
    "EUROPEAN CENTRAL BANK",
    "STATE BANK OF PAKISTAN",
    "BANGLADESH BANK",
    "NEPAL RASTRA BANK",
)

FOREIGN_CURRENCY_CONTEXTS = (
    "US DOLLAR",
    "US DOLLARS",
    "UNITED STATES DOLLAR",
    "UNITED STATES DOLLARS",
    "AMERICAN DOLLAR",
    "AMERICAN DOLLARS",
    "BRITISH POUND",
    "BRITISH POUNDS",
    "JAPANESE YEN",
    "CHINESE YUAN",
)

INDIAN_CURRENCY_MARKERS = (
    "RESERVE BANK OF INDIA",
    "RESERVE BANK",
    "BHARAT",
    "भारत",
)

RUPEE_MARKERS = {"RUPEE", "RUPEES", "INR", "रुपया", "रुपये"}
VALID_DENOMINATIONS = {10, 20, 50, 100, 200, 500, 2000}


def _compact(text: str) -> str:
    return "".join(character for character in text.upper() if character.isalnum())


def _has_phrase(text: str, phrase: str) -> bool:
    return _compact(phrase) in _compact(text)


def assess_currency_eligibility(text_analysis: dict[str, Any]) -> EligibilityState:
    """Block only strong foreign-currency evidence; otherwise let the CNN decide."""
    text = str(text_analysis.get("all_text") or "")
    compact_text = _compact(text)

    if any(_compact(marker) in compact_text for marker in FOREIGN_INSTITUTIONS):
        return EligibilityState.UNSUPPORTED_CURRENCY

    if any(_compact(context) in compact_text for context in FOREIGN_CURRENCY_CONTEXTS):
        return EligibilityState.UNSUPPORTED_CURRENCY

    if any(_has_phrase(text, marker) for marker in INDIAN_CURRENCY_MARKERS):
        return EligibilityState.INDIAN_CURRENCY

    detected_denomination = text_analysis.get("detected_denomination")
    has_valid_denomination = detected_denomination in VALID_DENOMINATIONS
    has_rupee_marker = (
        "₹" in text
        or any(_has_phrase(text, marker) for marker in RUPEE_MARKERS)
    )
    if has_valid_denomination and has_rupee_marker:
        return EligibilityState.INDIAN_CURRENCY

    # OCR is supporting evidence, not a required positive banknote classifier.
    # Single currency words can also be OCR errors, so they are not sufficient
    # to reject an image as foreign currency.
    return EligibilityState.ALLOW_CNN
