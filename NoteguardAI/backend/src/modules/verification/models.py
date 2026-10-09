from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, Numeric, BIGINT, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from src.core.database.connection import Base
from src.core.database.base_model import AuditModel
from src.modules.auth.models import User

class CurrencyVerification(AuditModel):
    """
    Currency Note Scan verification transaction record.
    """
    __tablename__ = "currency_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed

    # Relationships
    user = relationship("User")
    image = relationship("UploadedImage", back_populates="verification", uselist=False, cascade="all, delete-orphan")
    result = relationship("VerificationResult", back_populates="verification", uselist=False, cascade="all, delete-orphan")
    report = relationship("VerificationReport", back_populates="verification", uselist=False, cascade="all, delete-orphan")

class UploadedImage(AuditModel):
    """
    Metadata of uploaded raw currency images stored in S3/MinIO.
    """
    __tablename__ = "uploaded_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("currency_verifications.id", ondelete="CASCADE"), nullable=False)
    storage_url = Column(String(512), nullable=False)
    file_size_bytes = Column(BIGINT, nullable=False)
    sha256_checksum = Column(String(64), nullable=False)
    resolution_width = Column(Integer, nullable=False)
    resolution_height = Column(Integer, nullable=False)
    mime_type = Column(String(50), nullable=False)

    # Relationships
    verification = relationship("CurrencyVerification", back_populates="image")

class VerificationResult(AuditModel):
    """
    Validation decision and aggregated metrics for a scan.
    """
    __tablename__ = "verification_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("currency_verifications.id", ondelete="CASCADE"), nullable=False)
    is_authentic = Column(Boolean, nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=False)
    system_verdict = Column(String(20), nullable=False)  # authentic, counterfeit, suspicious
    verdict_reason = Column(String(255), nullable=True)

    # Relationships
    verification = relationship("CurrencyVerification", back_populates="result")
    prediction = relationship("AIPrediction", back_populates="result", uselist=False, cascade="all, delete-orphan")
    features = relationship("FeatureValidation", back_populates="result", cascade="all, delete-orphan")

class AIPrediction(Base):
    """
    Saves CNN base model prediction values.
    """
    __tablename__ = "ai_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_result_id = Column(UUID(as_uuid=True), ForeignKey("verification_results.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(UUID(as_uuid=True), nullable=True)  # References model registry if populated
    predicted_denomination = Column(Integer, nullable=False)
    predicted_orientation = Column(String(10), nullable=False)  # front, back
    confidence_score = Column(Numeric(5, 4), nullable=False)
    inference_time_ms = Column(Integer, nullable=False)

    # Relationships
    result = relationship("VerificationResult", back_populates="prediction")

class FeatureValidation(Base):
    """
    Individual security feature results checks performed by verification plugins.
    """
    __tablename__ = "feature_validations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_result_id = Column(UUID(as_uuid=True), ForeignKey("verification_results.id", ondelete="CASCADE"), nullable=False)
    feature_name = Column(String(50), nullable=False)  # watermark, security_thread, ashoka_pillar, microtext
    is_authentic = Column(Boolean, nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=False)
    crop_image_url = Column(String(512), nullable=False)
    roi_coordinates = Column(JSONB, nullable=False)
    plugin_metadata = Column(JSONB, nullable=False)

    # Relationships
    result = relationship("VerificationResult", back_populates="features")

class VerificationReport(AuditModel):
    """
    Aggregated PDF report compilation files.
    """
    __tablename__ = "verification_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("currency_verifications.id", ondelete="CASCADE"), nullable=False)
    storage_url = Column(String(512), nullable=True)
    report_status = Column(String(20), nullable=False, default="pending")  # pending, completed, failed

    # Relationships
    verification = relationship("CurrencyVerification", back_populates="report")
