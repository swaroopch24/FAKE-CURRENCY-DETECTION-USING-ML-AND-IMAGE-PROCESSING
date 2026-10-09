from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import jwt, JWTError
from src.config import settings

class TokenHelper:
    """
    Signs and decodes JWT access tokens and maps session states.
    """
    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates signed JWT access payload.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates signed JWT refresh payload with long-term validation.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """
        Decodes and verifies a JWT token. Returns payload dict on success, None on error.
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None
