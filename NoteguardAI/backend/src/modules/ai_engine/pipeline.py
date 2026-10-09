import time
import threading
from fastapi import HTTPException
from src.modules.ai_engine.validation import ImageValidator
from src.modules.ai_engine.preprocessing import ImagePreprocessor
from src.modules.ai_engine.inference import AIInferenceService
from src.modules.ai_engine.decision import DecisionEngine
from src.modules.ai_engine.text_analyzer import text_analyzer
from src.modules.ai_engine.eligibility import EligibilityState, assess_currency_eligibility
from src.modules.ai_engine.ocr_safety import detect_counterfeit_marker
from src.modules.ai_engine.schemas import (
    Authenticity,
    CirculationStatus,
    DecisionState,
    VerificationAction,
    VerificationResult,
)
from src.config import settings
import structlog

logger = structlog.get_logger()

class AIInferencePipeline:
    """
    Orchestrates the end-to-end inference flow:
    Validation -> Text Analysis (OCR) -> Preprocessing -> Prediction -> Decision Engine.
    """
    def __init__(self, model_path: str = None):
        self.validator = ImageValidator()
        self.preprocessor = ImagePreprocessor()
        self.inference_service = AIInferenceService(model_path)
        self.decision_engine = DecisionEngine()
        self.text_analyzer = text_analyzer
        self.eligibility_check = assess_currency_eligibility
        self.semaphore = threading.Semaphore(settings.MAX_CONCURRENT_INFERENCES)

    def process_inference(self, image_bytes: bytes) -> dict:
        """
        Executes the prediction pipeline on image bytes.
        """
        logger.info("Starting inference pipeline transaction.")
        
        # 1. Validation & Safe Decode
        # (Size, Magic Bytes, Resolution checks)
        img = self.validator.validate_and_decode(image_bytes)
        logger.info("Image validation passed successfully.")

        grayscale_extrema = img.convert("L").getextrema()
        if grayscale_extrema[0] == grayscale_extrema[1]:
            logger.warning("Uniform blank image rejected before OCR and CNN inference.")
            return {
                "status": DecisionState.UNABLE_TO_DETERMINE,
                "result": None,
                "action": VerificationAction(
                    requires_retake=True,
                    requires_manual_review=True,
                    decision_reason=(
                        "The image has no visible contrast and cannot be verified. "
                        "Please upload a clear image of a banknote."
                    ),
                ),
            }

        # 2. OCR safety screening and Indian-currency eligibility run before CNN inference.
        try:
            text_analysis = self.text_analyzer.analyze_banknote_text(img)
        except Exception as exc:
            logger.warning("OCR analysis failed; continuing with eligibility screening.", error=str(exc))
            text_analysis = {"all_text": "", "detected_denomination": None}

        matched_marker = detect_counterfeit_marker(str(text_analysis.get("all_text") or ""))
        if not matched_marker and text_analysis.get("is_fake"):
            matched_marker = str(
                text_analysis.get("fake_matched_text") or "Existing OCR counterfeit marker"
            )
        if matched_marker:
            logger.warning("Explicit counterfeit marker detected by OCR safety rule.", marker=matched_marker)
            denomination = text_analysis.get("detected_denomination")
            if denomination not in {10, 20, 50, 100, 200, 500, 2000}:
                denomination = 0
            return {
                "status": DecisionState.COUNTERFEIT_WARNING,
                "result": VerificationResult(
                    denomination=denomination,
                    denomination_label=f"₹{denomination}" if denomination else "Unknown",
                    denomination_confidence=0.0,
                    authenticity=Authenticity.COUNTERFEIT,
                    authenticity_confidence=1.0,
                    circulation_status=(
                        CirculationStatus.WITHDRAWN_FROM_CIRCULATION
                        if denomination == 2000
                        else CirculationStatus.ACTIVE
                    ),
                    detection_method="OCR_SAFETY_RULE",
                ),
                "action": VerificationAction(
                    requires_retake=False,
                    requires_manual_review=True,
                    decision_reason=(
                        "An explicit counterfeit marker was detected through the OCR safety rule. "
                        "CNN inference was not run."
                    ),
                ),
            }

        eligibility = self.eligibility_check(text_analysis)
        if eligibility == EligibilityState.UNSUPPORTED_CURRENCY:
            return {
                "status": DecisionState.UNSUPPORTED_CURRENCY,
                "result": None,
                "action": VerificationAction(
                    requires_retake=True,
                    requires_manual_review=False,
                    decision_reason=(
                        "This system is designed to verify Indian currency notes only. "
                        "Please upload an Indian banknote."
                    ),
                ),
            }

        if text_analysis.get("detected_denomination"):
            logger.info("Denomination extracted by OCR.", denomination=text_analysis.get("detected_denomination"))

        # 3. Prepare target tensor shape [1, 224, 224, 3]
        tensor = self.preprocessor.normalize_for_cnn(img)

        # 4. Run prediction within concurrency bounds
        # Use timeout=0.1 to reject immediately if capacity is full instead of unbounded queuing
        acquired = self.semaphore.acquire(timeout=0.1)
        if not acquired:
            logger.warning("Inference capacity exhausted. Rejecting request.")
            raise HTTPException(status_code=503, detail="System is currently at maximum capacity. Please try again in a moment.")
            
        try:
            raw_result = self.inference_service.execute_prediction(tensor)
            raw_result["text_analysis"] = text_analysis
            logger.info("CNN inference prediction succeeded.", label=raw_result["class_label"], confidence=raw_result["confidence"])
        finally:
            self.semaphore.release()

        # 5. Route through Decision Engine
        final_decision = self.decision_engine.evaluate(raw_result)
        logger.info("Decision engine routing complete.", status=final_decision["status"])

        return final_decision
