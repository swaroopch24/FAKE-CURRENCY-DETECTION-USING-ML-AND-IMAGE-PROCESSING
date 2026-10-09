from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
import uuid
import time
import structlog
from sqlalchemy.orm import Session
from src.core.database.connection import get_db
from src.modules.verification.models import CurrencyVerification, VerificationResult, AIPrediction
from src.modules.auth.router import get_current_user, get_optional_current_user
from src.modules.auth.models import User
from src.modules.ai_engine.pipeline import AIInferencePipeline
from src.modules.ai_engine.exceptions import (
    AIException,
    InvalidImageException,
    UnsupportedFormatException,
    ImageTooLargeException,
    ImageUnreadableException,
    ImageTooSmallException,
    ExtremeAspectRatioException,
    ModelLoadException,
    InferenceException
)
from src.modules.ai_engine.schemas import (
    VerificationResponse,
    DecisionState,
    VerificationAction,
    VerificationMeta,
    VerificationHistoryItem,
    VerificationHistoryResponse,
    Authenticity,
    CirculationStatus
)
from src.modules.ai_engine.training.config import training_config
from src.modules.ai_engine.loaders import ModelLoader

logger = structlog.get_logger()
router = APIRouter()

# Instantiate the pipeline
pipeline = AIInferencePipeline()
model_loader = ModelLoader()

def build_error_response(request_id: str, error_status: DecisionState, message: str, processing_time_ms: int, http_code: int = 400) -> JSONResponse:
    """Builds a deterministic error response based on the Inference Contract."""
    response = VerificationResponse(
        request_id=request_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        status=error_status,
        result=None,
        action=VerificationAction(
            requires_retake=True,
            requires_manual_review=False if error_status in [DecisionState.INVALID_IMAGE, DecisionState.UNSUPPORTED_IMAGE] else True,
            decision_reason=message
        ),
        meta=VerificationMeta(
            processing_time_ms=processing_time_ms,
            model_version=training_config.MODEL_VERSION,
            policy_threshold=training_config.CONFIDENCE_THRESHOLD
        )
    )
    return JSONResponse(status_code=http_code, content=response.model_dump())

from src.core.security.rate_limit import verify_rate_limiter

@router.post("/verify", response_model=VerificationResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(verify_rate_limiter)])
async def verify_image(
    request: Request,
    image_front: UploadFile | None = File(None),
    file: UploadFile | None = File(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user)
):
    """
    Currency verification endpoint. Validates, predicts, and routes through the Decision Engine.
    Persists valid verification attempts locally.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    upload_file = image_front or file or image
    if upload_file is None or not upload_file.filename:
        return build_error_response(
            request_id=request_id,
            error_status=DecisionState.INVALID_IMAGE,
            message="No banknote image file provided. Please select or capture an image of an Indian currency note.",
            processing_time_ms=0,
            http_code=400
        )
    
    logger.info("Received verification request.", request_id=request_id)

    try:
        image_bytes = await upload_file.read()
        
        # Pipeline handles validation -> preprocessing -> inference -> decision engine
        decision_dict = pipeline.process_inference(image_bytes)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        status_state = decision_dict["status"]
        result = decision_dict.get("result")
        
        response = VerificationResponse(
            request_id=request_id,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            status=status_state,
            result=result,
            action=decision_dict["action"],
            meta=VerificationMeta(
                processing_time_ms=processing_time,
                model_version=training_config.MODEL_VERSION,
                policy_threshold=training_config.CONFIDENCE_THRESHOLD
            )
        )
        
        # Safe persistence block
        if status_state in [DecisionState.ACCEPTED, DecisionState.UNABLE_TO_DETERMINE]:
            try:
                from src.modules.verification.models import AIPrediction
                db_verif = CurrencyVerification(
                    id=uuid.UUID(request_id),
                    status=status_state.value,
                    user_id=current_user.id if current_user else None
                )
                db.add(db_verif)
                if result:
                    db_res = VerificationResult(
                        verification_id=db_verif.id,
                        is_authentic=(result.authenticity == "AUTHENTIC"),
                        confidence_score=result.authenticity_confidence,
                        system_verdict=result.authenticity.value,
                        verdict_reason=decision_dict["action"].decision_reason
                    )
                    db.add(db_res)
                    db.flush()
                    
                    db_pred = AIPrediction(
                        verification_result_id=db_res.id,
                        predicted_denomination=result.denomination,
                        predicted_orientation="front", # Dummy value for now as we don't return orientation in VerificationResult schema
                        confidence_score=result.denomination_confidence,
                        inference_time_ms=processing_time
                    )
                    db.add(db_pred)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error("Database persistence failed for verification.", request_id=request_id, error=str(e))
        
        logger.info("Verification complete.", request_id=request_id, status=status_state.value, processing_time_ms=processing_time)
        return response

    except UnsupportedFormatException as e:
        logger.error("Validation failed.", request_id=request_id, error="UNSUPPORTED_FORMAT")
        return build_error_response(request_id, DecisionState.UNSUPPORTED_IMAGE, str(e), int((time.time() - start_time) * 1000), 415)
        
    except ImageTooLargeException as e:
        logger.error("Validation failed.", request_id=request_id, error="IMAGE_TOO_LARGE")
        return build_error_response(request_id, DecisionState.INVALID_IMAGE, str(e), int((time.time() - start_time) * 1000), 413)

    except (InvalidImageException, ImageUnreadableException, ImageTooSmallException, ExtremeAspectRatioException) as e:
        logger.error("Validation failed.", request_id=request_id, error="INVALID_IMAGE")
        return build_error_response(request_id, DecisionState.INVALID_IMAGE, str(e), int((time.time() - start_time) * 1000), 400)

    except (ModelLoadException, InferenceException) as e:
        logger.error("Inference execution failed.", request_id=request_id, error="INFERENCE_ERROR")
        return build_error_response(request_id, DecisionState.PROCESSING_ERROR, "An internal inference error occurred. Our team has been notified.", int((time.time() - start_time) * 1000), 500)
        
    except Exception as e:
        logger.error("Unexpected execution failure.", request_id=request_id, error=str(e))
        return build_error_response(request_id, DecisionState.PROCESSING_ERROR, "An internal server error occurred. Our team has been notified.", int((time.time() - start_time) * 1000), 500)

@router.get("/admin/models", status_code=status.HTTP_200_OK)
def get_model_metadata():
    """
    Returns metadata about active registered CNN weights.
    """
    metadata = model_loader.get_metadata()
    return {
        "success": True,
        "data": {
            "model_metadata": metadata
        },
        "meta": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    }

@router.get("/history", response_model=VerificationHistoryResponse, status_code=status.HTTP_200_OK)
def get_verification_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the most recent 50 verification records, ordered by created_at DESC.
    ROLE_ADMIN sees global history. ROLE_TELLER sees only their own history.
    """
    try:
        query = db.query(CurrencyVerification)
        
        # Enforce Role-Based Access Control
        if current_user.role.key != "ROLE_ADMIN":
            query = query.filter(CurrencyVerification.user_id == current_user.id)
            
        verifications = query.order_by(CurrencyVerification.created_at.desc()).limit(50).all()
        
        history_items = []
        for v in verifications:
            item = VerificationHistoryItem(
                verification_id=str(v.id),
                status=DecisionState(v.status),
                timestamp=v.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if v.created_at else ""
            )
            
            if v.result:
                # The verdict reason contains circulation status if applicable
                item.authenticity = Authenticity.AUTHENTIC if v.result.is_authentic else Authenticity.COUNTERFEIT
                item.confidence = float(v.result.confidence_score)
                if v.result.verdict_reason and "withdrawn" in v.result.verdict_reason.lower():
                    item.circulation_status = CirculationStatus.WITHDRAWN_FROM_CIRCULATION
                else:
                    item.circulation_status = CirculationStatus.ACTIVE
                
                if v.result.prediction:
                    item.denomination = v.result.prediction.predicted_denomination
            
            history_items.append(item)
            
        return VerificationHistoryResponse(
            success=True,
            data=history_items
        )
    except Exception as e:
        logger.error("Failed to retrieve verification history.", error=str(e))
        raise HTTPException(status_code=500, detail="Could not retrieve history")
