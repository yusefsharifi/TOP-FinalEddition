# backend/app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh", "password_reset"]

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_token(
    subject: str,
    token_type: TokenType,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta is None:
        if token_type == "access":
            expires_delta = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        elif token_type == "refresh":
            expires_delta = timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        else:
            expires_delta = timedelta(
                hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
            )

    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": token_type,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    """
    raises JWTError اگر توکن نامعتبر یا منقضی باشد
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
