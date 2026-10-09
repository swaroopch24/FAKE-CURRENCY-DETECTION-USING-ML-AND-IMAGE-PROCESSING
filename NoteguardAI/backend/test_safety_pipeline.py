import io
from unittest.mock import patch

import numpy as np
from PIL import Image

from src.modules.ai_engine.decision import DecisionEngine
from src.modules.ai_engine.eligibility import EligibilityState, assess_currency_eligibility
from src.modules.ai_engine.ocr_safety import detect_counterfeit_marker
from src.modules.ai_engine.pipeline import AIInferencePipeline
from src.modules.ai_engine.preprocessing import ImagePreprocessor


def make_test_image() -> bytes:
    image = Image.fromarray(np.random.default_rng(7).integers(0, 255, (200, 200, 3), dtype=np.uint8))
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=95)
    return output.getvalue()


def test_indian_currency_evidence_is_eligible():
    assert assess_currency_eligibility({"all_text": "RESERVE BANK OF INDIA"}) == EligibilityState.INDIAN_CURRENCY
    assert assess_currency_eligibility(
        {"all_text": "500 RUPEES", "detected_denomination": 500}
    ) == EligibilityState.INDIAN_CURRENCY


def test_foreign_currency_markers_are_rejected():
    cases = (
        "FEDERAL RESERVE UNITED STATES OF AMERICA DOLLAR",
        "EUROPEAN CENTRAL BANK EURO",
        "BANK OF ENGLAND POUNDS",
        "STATE BANK OF PAKISTAN",
        "BANGLADESH BANK",
        "NEPAL RASTRA BANK",
    )
    for text in cases:
        assert assess_currency_eligibility({"all_text": text}) == EligibilityState.UNSUPPORTED_CURRENCY


def test_ambiguous_ocr_text_is_allowed_to_reach_cnn():
    for text in ("", "BANK", "RESERVE", "EURO", "DOLLARS"):
        assert assess_currency_eligibility({"all_text": text}) == EligibilityState.ALLOW_CNN


def test_strong_foreign_currency_context_is_rejected():
    for text in ("US DOLLARS", "UNITED STATES DOLLAR", "BRITISH POUNDS"):
        assert assess_currency_eligibility({"all_text": text}) == EligibilityState.UNSUPPORTED_CURRENCY


def test_explicit_counterfeit_marker_variants():
    for text in (
        "CHILDREN'S BANK OF INDIA",
        "CHILDRENS BANK OF INDIA",
        "CHILDREN S BANK OF INDIA",
        "CHILDERN'S BANK OF INDIA",
        "BHARATIYA BALAK BANK",
    ):
        assert detect_counterfeit_marker(text) is not None
    assert detect_counterfeit_marker("A child is holding a note") is None


def test_counterfeit_marker_stops_before_cnn():
    pipeline = AIInferencePipeline()
    with patch.object(
        pipeline.text_analyzer,
        "analyze_banknote_text",
        return_value={"all_text": "CHILDREN'S BANK OF INDIA", "detected_denomination": None},
    ), patch.object(pipeline.inference_service, "execute_prediction") as predict:
        result = pipeline.process_inference(make_test_image())

    predict.assert_not_called()
    assert result["status"] == "COUNTERFEIT_WARNING"
    assert result["result"].authenticity.value == "COUNTERFEIT"
    assert result["result"].detection_method == "OCR_SAFETY_RULE"
    assert result["action"].requires_manual_review is True
    assert "CNN inference was not run" in result["action"].decision_reason


def test_existing_novelty_text_rule_stops_before_cnn():
    pipeline = AIInferencePipeline()
    with patch.object(
        pipeline.text_analyzer,
        "analyze_banknote_text",
        return_value={
            "all_text": "TOY MONEY",
            "is_fake": True,
            "fake_matched_text": "TOY MONEY",
        },
    ), patch.object(pipeline.inference_service, "execute_prediction") as predict:
        result = pipeline.process_inference(make_test_image())

    predict.assert_not_called()
    assert result["status"] == "COUNTERFEIT_WARNING"
    assert result["result"].detection_method == "OCR_SAFETY_RULE"


def test_foreign_currency_stops_before_cnn():
    pipeline = AIInferencePipeline()
    with patch.object(
        pipeline.text_analyzer,
        "analyze_banknote_text",
        return_value={"all_text": "EUROPEAN CENTRAL BANK EURO"},
    ), patch.object(pipeline.inference_service, "execute_prediction") as predict:
        result = pipeline.process_inference(make_test_image())

    predict.assert_not_called()
    assert result["status"] == "UNSUPPORTED_CURRENCY"
    assert "Indian banknote" in result["action"].decision_reason


def test_empty_or_failed_ocr_still_reaches_cnn():
    for ocr_result in ({}, RuntimeError("OCR unavailable")):
        pipeline = AIInferencePipeline()
        with patch.object(
            pipeline.text_analyzer,
            "analyze_banknote_text",
            side_effect=ocr_result if isinstance(ocr_result, Exception) else None,
            return_value=None if isinstance(ocr_result, Exception) else ocr_result,
        ), patch.object(
            pipeline.inference_service,
            "execute_prediction",
            return_value={
                "class_label": "real_500",
                "confidence": 0.95,
                "p_real": 0.95,
                "p_fake": 0.05,
            },
        ) as predict:
            result = pipeline.process_inference(make_test_image())

        predict.assert_called_once()
        assert result["status"] == "ACCEPTED"


def test_uniform_blank_image_is_uncertain_before_ocr_and_cnn():
    pipeline = AIInferencePipeline()

    for color in ("white", "black"):
        image = Image.new("RGB", (200, 200), color)
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=95)

        with patch.object(pipeline.text_analyzer, "analyze_banknote_text") as analyze, patch.object(
            pipeline.inference_service, "execute_prediction"
        ) as predict:
            result = pipeline.process_inference(output.getvalue())

        analyze.assert_not_called()
        predict.assert_not_called()
        assert result["status"] == "UNABLE_TO_DETERMINE"


def test_decision_requires_authenticity_and_denomination_thresholds():
    engine = DecisionEngine()
    low_denomination = engine.evaluate(
        {
            "class_label": "real_500",
            "confidence": 0.42,
            "p_real": 0.95,
            "p_fake": 0.05,
        }
    )
    high_confidence = engine.evaluate(
        {
            "class_label": "real_500",
            "confidence": 0.94,
            "p_real": 0.95,
            "p_fake": 0.05,
        }
    )
    threshold_boundary = engine.evaluate(
        {
            "class_label": "real_500",
            "confidence": 0.80,
            "p_real": 0.80,
            "p_fake": 0.20,
        }
    )

    assert low_denomination["status"] == "UNABLE_TO_DETERMINE"
    assert "Denomination confidence" in low_denomination["action"].decision_reason
    assert high_confidence["status"] == "ACCEPTED"
    assert threshold_boundary["status"] == "ACCEPTED"


def test_preprocessing_uses_bilinear_resize():
    image = Image.fromarray(np.array([[[0, 0, 0], [255, 255, 255]]] * 2, dtype=np.uint8))
    actual = ImagePreprocessor(target_size=8).normalize_for_cnn(image)
    expected = np.expand_dims(
        np.asarray(image.resize((8, 8), resample=Image.Resampling.BILINEAR), dtype=np.float32),
        axis=0,
    )

    np.testing.assert_array_equal(actual, expected)
