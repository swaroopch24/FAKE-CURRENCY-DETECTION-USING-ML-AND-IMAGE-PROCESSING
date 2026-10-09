from typing import Dict, Any
from src.modules.ai_engine.training.config import training_config
from src.modules.ai_engine.schemas import (
    DecisionState,
    Authenticity,
    CirculationStatus,
    VerificationResult,
    VerificationAction
)

class DecisionEngine:
    """
    Independent Decision Engine middleware.
    Consumes raw model predictions and enforces business policies, thresholds, 
    and output schema mapping.
    """
    def __init__(self):
        self.threshold = training_config.CONFIDENCE_THRESHOLD

    def evaluate(self, raw_prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the raw CNN prediction against the confidence policy and business rules.
        """
        # Calculate Authenticity using Aggregate Scoring
        p_real = raw_prediction_result.get("p_real", 0.0)
        p_fake = raw_prediction_result.get("p_fake", 0.0)
        
        authenticity_confidence = max(p_real, p_fake)
        is_pred_real = p_real >= p_fake
        
        authenticity = Authenticity.AUTHENTIC if is_pred_real else Authenticity.COUNTERFEIT
        
        # Denomination relies on the highest individual class
        denomination_confidence = raw_prediction_result["confidence"]
        max_class_label = raw_prediction_result["class_label"]
        
        parts = max_class_label.split("_")
        cnn_denom_val = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        
        denom_val = cnn_denom_val
        
        # ACCEPTED requires both the binary authenticity and individual class thresholds.
        if authenticity_confidence < self.threshold or denomination_confidence < self.threshold:
            if denomination_confidence < self.threshold and authenticity_confidence < self.threshold:
                reason = (
                    f"Authenticity confidence ({authenticity_confidence:.3f}) and denomination "
                    f"confidence ({denomination_confidence:.3f}) are below the required "
                    f"threshold ({self.threshold:.2f})."
                )
            elif denomination_confidence < self.threshold:
                reason = (
                    f"Denomination confidence ({denomination_confidence:.3f}) is below the "
                    f"required threshold ({self.threshold:.2f})."
                )
            else:
                reason = (
                    f"Authenticity confidence ({authenticity_confidence:.3f}) is below the "
                    f"required threshold ({self.threshold:.2f})."
                )
            return {
                "status": DecisionState.UNABLE_TO_DETERMINE,
                "result": None,
                "action": VerificationAction(
                    requires_retake=True,
                    requires_manual_review=True,
                    decision_reason=reason
                )
            }
            
        # 3. Enforce ₹2000 Business Rule
        if denom_val == 2000:
            circulation = CirculationStatus.WITHDRAWN_FROM_CIRCULATION
            reason = "High confidence prediction. Note: Denomination is withdrawn."
        else:
            circulation = CirculationStatus.ACTIVE
            if authenticity == Authenticity.AUTHENTIC:
                reason = "High confidence authentic prediction."
            else:
                reason = "High confidence counterfeit prediction."
                
        # 4. Construct ACCEPTED State
        return {
            "status": DecisionState.ACCEPTED,
            "result": VerificationResult(
                denomination=denom_val,
                denomination_label=f"₹{denom_val}",
                denomination_confidence=denomination_confidence,
                authenticity=authenticity,
                authenticity_confidence=authenticity_confidence,
                circulation_status=circulation
            ),
            "action": VerificationAction(
                requires_retake=False,
                requires_manual_review=False,
                decision_reason=reason
            )
        }
