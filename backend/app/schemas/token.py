from typing import Optional
from pydantic import BaseModel

# Import UserPublic — adjust import path as needed
from app.schemas.user import UserPublic


class Token(BaseModel):
    """
    Login response schema.
    
    FIX: Added refresh_token and user fields to match frontend expectations.
    Frontend expects: { access_token, refresh_token, token_type, user: {...} }
    """
    access_token: str
    refresh_token: str           # ← ADDED: Frontend expects this
    token_type: str = "bearer"
    user: UserPublic             # ← ADDED: Frontend expects user object


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: Optional[str] = None     # user_id as string (for int: convert in code)
    type: Optional[str] = "access"  # "access" or "refresh"
    jti: Optional[str] = None     # JWT ID for revocation


class RefreshTokenRequest(BaseModel):
    """Request body for token refresh endpoint."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Response from token refresh endpoint."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    """Response from logout endpoint."""
    message: str = "Successfully logged out"