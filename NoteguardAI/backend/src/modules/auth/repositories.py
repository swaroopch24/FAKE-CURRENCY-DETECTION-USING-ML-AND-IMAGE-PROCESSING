from sqlalchemy.orm import Session
from src.modules.auth.models import User, Role
from uuid import UUID
from typing import Optional

class UserRepository:
    """
    Handles direct relational queries on the User and Role database layers.
    """
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email.ilike(email)).first()

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_role_by_key(db: Session, role_key: str) -> Optional[Role]:
        return db.query(Role).filter(Role.key == role_key).first()

    @staticmethod
    def get_role_by_id(db: Session, role_id: UUID) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()
