from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.core.database.connection import get_db
from src.modules.auth.services import (
    AuthenticationService, InvalidCredentialsException, 
    DuplicateEmailException, PasswordValidationException
)
from src.modules.auth.schemas import (
    UserLoginSchema, UserRegisterSchema, LoginResponseSchema, 
    UserProfileResponseSchema
)
from src.modules.auth.repositories import UserRepository
from src.modules.auth.models import UserRefreshToken
from src.core.security.token import TokenHelper
from src.config import settings
import time
import structlog

logger = structlog.get_logger()
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependency checking JWT token authenticity.
    Returns User DB object or raises HTTP 401.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials token."
        )

    payload = TokenHelper.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token."
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token context."
        )

    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user profile not found."
        )
        
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is suspended/inactive."
        )

    return user

def get_optional_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependency checking JWT token authenticity if present.
    Returns User DB object or None if no token is provided.
    Raises HTTP 401 only if the token is present but invalid/expired.
    """
    if not token:
        return None

    payload = TokenHelper.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token."
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token context."
        )

    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user profile not found."
        )
        
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is suspended/inactive."
        )

    return user

from src.core.security.rate_limit import auth_rate_limiter

@router.post("/auth/register", response_model=UserProfileResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth_rate_limiter)])
def register(
    register_data: UserRegisterSchema,
    db: Session = Depends(get_db)
):
    """
    Registers a new note verification user.
    """
    auth_service = AuthenticationService()
    try:
        user = auth_service.register_user(db, register_data)
        
        # Load user role mapping key
        role = UserRepository.get_role_by_id(db, user.role_id)
        role_key = role.key if role else "ROLE_USER"

        return {
            "success": True,
            "data": {
                "id": user.id,
                "full_name": user.full_name or "",
                "email": user.email,
                "role": role_key,
                "status": user.status,
                "created_at": user.created_at
            },
            "meta": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        }
    except DuplicateEmailException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "DUPLICATE_EMAIL",
                    "message": str(e),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            }
        )
    except PasswordValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "error": {
                    "code": "PASSWORD_POLICY_VIOLATED",
                    "message": str(e),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            }
        )
    except Exception as e:
        logger.error("User registration failed.", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal authentication error during user registration.",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            }
        )

@router.post("/auth/login", response_model=LoginResponseSchema, dependencies=[Depends(auth_rate_limiter)])
def login(
    login_data: UserLoginSchema,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Session login endpoint. Checks credentials and returns JWT access & refresh tokens.
    """
    auth_service = AuthenticationService()
    try:
        user = auth_service.authenticate_user(db, login_data)
        session_data = auth_service.generate_login_session(user, db)
        
        return {
            "success": True,
            "data": session_data,
            "meta": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        }
    except InvalidCredentialsException as e:
        logger.warn("User login failed.", email=login_data.email, reason=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": str(e),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            }
        )

@router.post("/auth/logout")
def logout(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revokes and terminates all active refresh token sessions for the logged-in user.
    """
    db.query(UserRefreshToken).filter(
        UserRefreshToken.user_id == current_user.id
    ).update({UserRefreshToken.is_revoked: True})
    db.commit()
    
    return {
        "success": True,
        "detail": "Logged out successfully."
    }

@router.post("/auth/refresh")
def refresh_token(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Validates a refresh token and generates a new access/refresh token pair.
    """
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing refresh token."
        )

    # Decode and check signature
    token_payload = TokenHelper.decode_token(refresh_token)
    if not token_payload or token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    # Query refresh token state in database
    db_token = db.query(UserRefreshToken).filter(
        UserRefreshToken.token == refresh_token,
        UserRefreshToken.is_revoked == False
    ).first()
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or expired."
        )

    user = UserRepository.get_by_id(db, db_token.user_id)
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive."
        )

    # Generate new session credentials
    auth_service = AuthenticationService()
    session_data = auth_service.generate_login_session(user, db)

    # Revoke old refresh token (secure rotation)
    db_token.is_revoked = True
    db.commit()

    return {
        "success": True,
        "data": session_data,
        "meta": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    }


@router.get("/users/me", response_model=UserProfileResponseSchema)
def get_me(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves current user details.
    """
    role = UserRepository.get_role_by_id(db, current_user.role_id)
    role_key = role.key if role else "ROLE_USER"

    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "full_name": current_user.full_name or "",
            "email": current_user.email,
            "role": role_key,
            "status": current_user.status,
            "created_at": current_user.created_at
        },
        "meta": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    }
