from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum

class DecisionState(str, Enum):
    ACCEPTED = "ACCEPTED"
    COUNTERFEIT_WARNING = "COUNTERFEIT_WARNING"
    UNSUPPORTED_CURRENCY = "UNSUPPORTED_CURRENCY"
    UNABLE_TO_DETERMINE = "UNABLE_TO_DETERMINE"
    INVALID_IMAGE = "INVALID_IMAGE"
    UNSUPPORTED_IMAGE = "UNSUPPORTED_IMAGE"
    PROCESSING_ERROR = "PROCESSING_ERROR"

class Authenticity(str, Enum):
    AUTHENTIC = "AUTHENTIC"
    COUNTERFEIT = "COUNTERFEIT"

class CirculationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    WITHDRAWN_FROM_CIRCULATION = "WITHDRAWN_FROM_CIRCULATION"

class VerificationResult(BaseModel):
    denomination: int
    denomination_label: str
    denomination_confidence: float
    authenticity: Authenticity
    authenticity_confidence: float
    circulation_status: CirculationStatus
    detection_method: str = "CNN_CLASSIFICATION"

class VerificationAction(BaseModel):
    requires_retake: bool
    requires_manual_review: bool
    decision_reason: str

class VerificationMeta(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    processing_time_ms: int
    model_version: str
    policy_threshold: float

class VerificationResponse(BaseModel):
    request_id: str
    timestamp: str
    status: DecisionState
    result: Optional[VerificationResult] = None
    action: VerificationAction
    meta: VerificationMeta

class VerificationHistoryItem(BaseModel):
    verification_id: str
    status: DecisionState
    timestamp: str
    authenticity: Optional[Authenticity] = None
    denomination: Optional[int] = None
    confidence: Optional[float] = None
    circulation_status: Optional[CirculationStatus] = None

class VerificationHistoryResponse(BaseModel):
    success: bool = True
    data: list[VerificationHistoryItem]
