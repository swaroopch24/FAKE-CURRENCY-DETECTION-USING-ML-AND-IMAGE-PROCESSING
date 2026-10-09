from pydantic import BaseModel, HttpUrl
from datetime import datetime
from uuid import UUID
from typing import List, Optional, Dict

class VerificationVerdictSchema(BaseModel):
    authenticity_verdict: str  # e.g., 'AUTHENTIC', 'COUNTERFEIT'
    authenticity_confidence: float
    denomination: int
    denomination_confidence: float
    overall_status: str  # e.g., 'ACCEPTED', 'UNABLE_TO_DETERMINE', 'WITHDRAWN_FROM_CIRCULATION'
    verdict_reason: Optional[str] = None

class BasePredictionSchema(BaseModel):
    denomination: int
    orientation: str  # front, back
    inference_time_ms: int

class FeatureDetailSchema(BaseModel):
    feature_name: str
    is_authentic: bool
    confidence: float
    crop_image_url: str
    roi_coordinates: Dict[str, int]

class ImageLinksSchema(BaseModel):
    raw_image_url: str
    grad_cam_url: Optional[str] = None

class VerificationResponseDataSchema(BaseModel):
    verification_id: UUID
    status: str
    verdict: Optional[VerificationVerdictSchema] = None
    base_prediction: Optional[BasePredictionSchema] = None
    feature_details: List[FeatureDetailSchema] = []
    images: Optional[ImageLinksSchema] = None
    report_url: Optional[str] = None
    created_at: datetime

class VerificationResponseSchema(BaseModel):
    success: bool = True
    data: VerificationResponseDataSchema
    meta: dict

class VerificationHistoryItemSchema(BaseModel):
    verification_id: UUID
    denomination: int
    system_verdict: str
    confidence_score: float
    created_at: datetime

class VerificationHistoryResponseSchema(BaseModel):
    success: bool = True
    data: List[VerificationHistoryItemSchema]
    meta: dict
