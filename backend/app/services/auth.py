from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.auth_enhanced import User
from app.core.config import settings
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token with user.id in 'sub' claim.
    
    Args:
        user: Authenticated user object
        expires_delta: Optional custom expiration time
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # FIX: Store user.id (as string) in 'sub' claim — NOT username or email
    to_encode = {
        "sub": str(user.id),           # ← CHANGED: was username/email from data dict, now user.id
        "type": "access",
        "email": user.email,            # Keep email for reference (optional)
        "jti": str(uuid.uuid4()),       # Unique token ID for revocation
        "iat": datetime.utcnow().timestamp(),
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: int) -> str:
    """
    Create JWT refresh token with user_id in 'sub' claim.
    Note: This is kept for backward compatibility, but internally uses user_id consistently.
    """
    expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expires,
        "sub": str(user_id),           # Already correct: stores user_id as string
        "type": "refresh",
        "jti": str(uuid.uuid4())       # Add JTI for consistency
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[int]:
    """
    Verify JWT token and return user_id (as integer) from 'sub' claim.
    
    Returns:
        user_id as integer, or None if token is invalid
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Verify token type is access token (or allow refresh for internal use)
        token_type = decoded_token.get("type", "access")
        if token_type not in ["access", "refresh"]:
            return None
            
        # FIX: Extract user_id from 'sub' and convert to int
        sub_value = decoded_token.get("sub")
        if sub_value is None:
            return None
            
        # Convert string back to integer
        try:
            user_id = int(sub_value)
            return user_id
        except ValueError:
            # If 'sub' contains old username/email format, return None to force re-login
            return None
            
    except JWTError:
        return None

async def get_current_user(db: AsyncSession, token: str) -> Optional[User]:
    """
    Get user from token by looking up user_id.
    """
    user_id = verify_token(token)
    if user_id is None:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def update_last_login(db: AsyncSession, user: User) -> None:
    user.last_login_at = datetime.utcnow()
    await db.commit()

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    Authenticate user by email (username parameter kept for API compatibility).
    """
    result = await db.execute(select(User).where(User.email == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token for the given email.
    The token expires in EMAIL_RESET_TOKEN_EXPIRE_HOURS hours.
    """
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    encoded_jwt = jwt.encode(
        {
            "exp": expires,
            "nbf": now,
            "sub": email,               # Password reset keeps email in sub (different use case)
            "type": "password_reset"
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the email if valid.
    Returns None if the token is invalid or expired.
    """
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if decoded_token.get("type") != "password_reset":
            return None
        return decoded_token.get("sub")  # Returns email for password reset
    except JWTError:
        return None