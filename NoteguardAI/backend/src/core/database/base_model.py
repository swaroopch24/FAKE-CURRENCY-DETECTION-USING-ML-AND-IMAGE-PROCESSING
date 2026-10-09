from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from src.core.database.connection import Base

class AuditModel(Base):
    """
    Abstract base model mapping auditing columns to database tables.
    """
    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
