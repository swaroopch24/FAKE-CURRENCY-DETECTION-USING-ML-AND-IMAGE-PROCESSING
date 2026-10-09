import re
import numpy as np
from PIL import Image
import structlog

logger = structlog.get_logger()

# Counterfeit / Novelty / Toy Bank indicator keywords (case-insensitive)
SUSPICIOUS_KEYWORD_PATTERNS = [
    # Children / Toy / Kid banks
    r"children'?s?\s*bank(\s*of\s*india)?",
    r"child'?s?\s*bank(\s*of\s*india)?",
    r"kid'?s?\s*bank(\s*of\s*india)?",
    r"bachon\s*ka\s*bank",
    r"bacho\s*ka\s*bank",
    r"bhartiya\s*bachon",
    r"bharat\s*bachon",
    r"churan\s*(label|note|bank)?",
    r"full\s*of\s*fun",
    r"manoranjan\s*(bank|note)?",
    r"purna\s*manoranjan",
    r"entertainment\s*(bank|note|money)?",
    r"toy\s*bank",
    r"toy\s*money",
    r"play\s*(money|note|currency)",
    r"reverse\s*bank\s*of\s*india",
    r"reserve\s*bank\s*of\s*bharat",
    r"cinema\s*(note|money)?",
    r"coupon\s*(note|money)?",
    r"prop\s*money",
    r"dummy\s*(currency|note|money)",
    r"not\s*for\s*circulation",
    r"specimen",
    r"000\s*000000",   # Dummy zero serial number (e.g. 000 000000 in toy notes)
    r"\b0000000\b",
    r"training\s*note",
    r"souvenir"
]

COMPILED_FAKE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_KEYWORD_PATTERNS]

# Denomination Word Mappings (English and Hindi)
DENOM_WORD_MAP = {
    # 2000
    r"\btwo\s*thousand(\s*rupees)?\b": 2000,
    r"\bदो\s*हज़ार(\s*रुपये)?\b": 2000,
    r"\b२०००\b": 2000,
    # 500
    r"\bfive\s*hundred(\s*rupees)?\b": 500,
    r"\b(पाँच|पांच)\s*सौ(\s*रुपये)?\b": 500,
    r"\b५००\b": 500,
    # 200
    r"\btwo\s*hundred(\s*rupees)?\b": 200,
    r"\bदो\s*सौ(\s*रुपये)?\b": 200,
    r"\b२००\b": 200,
    # 100
    r"\b(one\s*hundred|hundred)(\s*rupees)?\b": 100,
    r"\b(एक\s*सौ|सौ\s*रुपये)\b": 100,
    r"\b१००\b": 100,
    # 50
    r"\bfifty(\s*rupees)?\b": 50,
    r"\bपचास(\s*रुपये)?\b": 50,
    r"\b५०\b": 50,
    # 20
    r"\btwenty(\s*rupees)?\b": 20,
    r"\bबीस(\s*रुपये)?\b": 20,
    r"\b२०\b": 20,
    # 10
    r"\bten(\s*rupees)?\b": 10,
    r"\bदस(\s*रुपये)?\b": 10,
    r"\b१०\b": 10,
}

VALID_DENOMINATIONS = {10, 20, 50, 100, 200, 500, 2000}

class BanknoteTextAnalyzer:
    """
    Lightweight OCR analyzer for:
    1. Detecting overt fake / toy money markings (e.g. 'CHILDRENS BANK OF INDIA')
    2. Extracting the true printed denomination (e.g. 50, 100, 200, 500, 2000) from banknote text
    """
    _instance = None
    _ocr = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BanknoteTextAnalyzer, cls).__new__(cls)
        return cls._instance

    def _get_ocr(self):
        if self._ocr is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._ocr = RapidOCR()
            except Exception as e:
                logger.warning("RapidOCR could not be initialized. OCR text checks will be skipped.", error=str(e))
                self._ocr = False
        return self._ocr

    def analyze_banknote_text(self, image: Image.Image) -> dict:
        """
        Runs OCR on the banknote image to detect fake markings and extract printed denomination.
        Returns:
            {
                "is_fake": bool,
                "fake_matched_text": str or None,
                "detected_denomination": int or None,
                "all_text": str
            }
        """
        result = {
            "is_fake": False,
            "fake_matched_text": None,
            "detected_denomination": None,
            "all_text": ""
        }

        ocr = self._get_ocr()
        if not ocr:
            return result

        try:
            np_img = np.array(image.convert("RGB"))
            ocr_results, _ = ocr(np_img)
            if not ocr_results:
                return result

            detected_lines = []
            found_denoms = []

            for item in ocr_results:
                if len(item) >= 2:
                    line_text = str(item[1]).strip()
                    conf = float(item[2]) if len(item) > 2 else 0.8
                    detected_lines.append(line_text)

                    # 1. Check for Fake / Childrens Bank keywords on individual lines
                    if not result["is_fake"]:
                        for pattern in COMPILED_FAKE_PATTERNS:
                            if pattern.search(line_text):
                                result["is_fake"] = True
                                result["fake_matched_text"] = line_text
                                logger.info("Counterfeit novelty text detected by OCR.", matched_text=line_text)
                                break

                    # 2. Check for Currency Numeral Patterns in line (e.g. ₹200, Rs 50, 100)
                    num_matches = re.findall(r"(?:₹|rs\.?|inr)?\s*\b(2000|500|200|100|50|20|10)\b\s*(?:₹|rs\.?|inr|rupees?)?", line_text, re.IGNORECASE)
                    for m in num_matches:
                        val = int(m)
                        if val in VALID_DENOMINATIONS:
                            found_denoms.append((val, conf, "numeral"))

                    # Check for Word patterns in line
                    for word_pattern, val in DENOM_WORD_MAP.items():
                        if re.search(word_pattern, line_text, re.IGNORECASE):
                            found_denoms.append((val, conf + 0.2, "word"))

            full_text = " ".join(detected_lines)
            result["all_text"] = full_text

            # Full text fake pattern fallback
            if not result["is_fake"]:
                for pattern in COMPILED_FAKE_PATTERNS:
                    match = pattern.search(full_text)
                    if match:
                        result["is_fake"] = True
                        result["fake_matched_text"] = match.group(0)
                        logger.info("Counterfeit text pattern matched in full text.", matched_text=result["fake_matched_text"])
                        break

            # Select most confident / frequent detected denomination
            if found_denoms:
                scores = {}
                for denom, score, src in found_denoms:
                    weight = 2.0 if src == "word" else 1.0
                    scores[denom] = scores.get(denom, 0.0) + (score * weight)

                best_denom = max(scores.keys(), key=lambda d: scores[d])
                result["detected_denomination"] = best_denom
                logger.info("OCR extracted banknote denomination.", denomination=best_denom, score=scores[best_denom])

        except Exception as e:
            logger.error("Error during OCR banknote analysis.", error=str(e))

        return result

text_analyzer = BanknoteTextAnalyzer()
