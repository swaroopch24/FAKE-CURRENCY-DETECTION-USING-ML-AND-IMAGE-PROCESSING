import re
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from src.modules.auth.repositories import UserRepository
from src.modules.auth.schemas import UserLoginSchema, UserRegisterSchema
from src.core.security.password import PasswordHelper
from src.core.security.token import TokenHelper
from src.modules.auth.models import User, UserRefreshToken
from src.config import settings
from typing import Optional

class InvalidCredentialsException(Exception):
    """Raised when authentication credentials matching fails."""
    pass

class DuplicateEmailException(Exception):
    """Raised when email is already registered."""
    pass

class PasswordValidationException(Exception):
    """Raised when password policy is violated."""
    pass

class AuthenticationService:
    """
    Orchestrates user validations, password hash matching, and JWT session generation.
    """
    def __init__(self):
        self.user_repo = UserRepository()

    def authenticate_user(self, db: Session, login_data: UserLoginSchema) -> User:
        """
        Validates email and checks password. Raises InvalidCredentialsException on failures.
        """
        user = self.user_repo.get_by_email(db, login_data.email)
        if not user:
            raise InvalidCredentialsException("Invalid email or password.")
            
        if user.status != "active":
            raise InvalidCredentialsException(f"User account is {user.status}.")

        if not PasswordHelper.verify_password(login_data.password, user.password_hash):
            raise InvalidCredentialsException("Invalid email or password.")

        return user

    def register_user(self, db: Session, register_data: UserRegisterSchema) -> User:
        """
        Registers a new user, enforcing email uniqueness, password strength policies,
        and mapping default system Teller roles.
        """
        # 1. Duplicate check (case-insensitive)
        existing_user = self.user_repo.get_by_email(db, register_data.email)
        if existing_user:
            raise DuplicateEmailException("Email already registered.")

        # 2. Password policy (8-chars, upper, lower, number)
        password = register_data.password
        if len(password) < 8:
            raise PasswordValidationException("Password must be at least 8 characters long.")
        if not re.search(r"[a-z]", password):
            raise PasswordValidationException("Password must contain at least one lowercase letter.")
        if not re.search(r"[A-Z]", password):
            raise PasswordValidationException("Password must contain at least one uppercase letter.")
        if not re.search(r"\d", password):
            raise PasswordValidationException("Password must contain at least one number.")

        # 3. Default role query ("ROLE_TELLER")
        role = self.user_repo.get_role_by_key(db, "ROLE_TELLER")
        if not role:
            # Fallback fail-safe if db wasn't seeded correctly yet
            from src.modules.auth.models import Role
            role = Role(
                name="Bank Teller",
                key="ROLE_TELLER",
                description="Teller officer processing scan audits"
            )
            db.add(role)
            db.flush()

        # 4. Hash password
        hashed_pwd = PasswordHelper.hash_password(password)

        # 5. Store user
        user = User(
            email=register_data.email,
            full_name=register_data.full_name,
            password_hash=hashed_pwd,
            role_id=role.id,
            status="active"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def generate_login_session(self, user: User, db: Session) -> dict:
        """
        Generates access token and refresh token payloads matching standard success responses.
        """
        role = self.user_repo.get_role_by_id(db, user.role_id)
        role_key = role.key if role else "ROLE_USER"

        # Sign JWT access token
        access_token_data = {
            "sub": str(user.id),
            "full_name": user.full_name or "",
            "role": role_key
        }
        
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = TokenHelper.create_access_token(
            data=access_token_data,
            expires_delta=expires_delta
        )

        # Sign JWT refresh token
        refresh_token_data = {
            "sub": str(user.id)
        }
        refresh_token = TokenHelper.create_refresh_token(
            data=refresh_token_data
        )

        # Persist refresh token in PostgreSQL for revocation validation
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_ref_token = UserRefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            is_revoked=False
        )
        db.add(db_ref_token)
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "full_name": user.full_name or "",
                "email": user.email,
                "role": role_key
            }
        }

