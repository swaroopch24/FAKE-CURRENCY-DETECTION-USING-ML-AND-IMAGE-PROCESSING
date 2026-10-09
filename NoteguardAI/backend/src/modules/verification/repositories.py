from sqlalchemy.orm import Session, joinedload
from src.modules.verification.models import CurrencyVerification, VerificationResult
from uuid import UUID
from typing import Optional, List, Tuple

class VerificationRepository:
    """
    Handles read/write database actions for scan files, results, and history pages.
    """
    @staticmethod
    def save_verification(db: Session, verification: CurrencyVerification) -> CurrencyVerification:
        db.add(verification)
        db.commit()
        db.refresh(verification)
        return verification

    @staticmethod
    def get_by_id(db: Session, verification_id: UUID) -> Optional[CurrencyVerification]:
        """
        Retrieves a verification record with joined tables loaded to prevent N+1 queries.
        """
        return db.query(CurrencyVerification).options(
            joinedload(CurrencyVerification.image),
            joinedload(CurrencyVerification.result).joinedload(VerificationResult.prediction),
            joinedload(CurrencyVerification.result).joinedload(VerificationResult.features),
            joinedload(CurrencyVerification.report)
        ).filter(CurrencyVerification.id == verification_id).first()

    @staticmethod
    def list_history(
        db: Session,
        user_id: Optional[UUID] = None,
        role: str = "ROLE_ADMIN",
        page: int = 1,
        limit: int = 20,
        denomination: Optional[int] = None,
        verdict: Optional[str] = None
    ) -> Tuple[List[CurrencyVerification], int]:
        """
        Returns a paginated list of scans.
        Enforces tenant isolation: ROLE_USER can only load their own scans.
        """
        query = db.query(CurrencyVerification).options(
            joinedload(CurrencyVerification.result)
        )

        # Enforce user boundary restrictions
        if role == "ROLE_USER":
            query = query.filter(CurrencyVerification.user_id == user_id)

        # Apply optional filters
        if denomination is not None or verdict is not None:
            # Join results table
            query = query.join(CurrencyVerification.result)
            if denomination is not None:
                query = query.filter(CurrencyVerification.result.has(
                    VerificationResult.prediction.has(predicted_denomination=denomination)
                ))
            if verdict is not None:
                query = query.filter(VerificationResult.system_verdict == verdict)

        # Get total matching count
        total_count = query.count()

        # Apply sorting, offset and limit
        offset = (page - 1) * limit
        results = query.order_by(CurrencyVerification.created_at.desc()).offset(offset).limit(limit).all()

        return results, total_count
