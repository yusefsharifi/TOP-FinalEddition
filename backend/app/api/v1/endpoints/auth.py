"""Auth Module — FastAPI Router (Async)"""
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import DBDep
from app.core.config import settings
from app.models.auth_enhanced import User
from app.schemas.token import Token, TokenRefreshResponse, RefreshTokenRequest
from app.schemas.user import UserPublic
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    username: str,
    password: str,
    db: DBDep,
) -> Token:
    """
    Authenticate user and return tokens with user profile.
    
    FIX: Now returns full Token schema with refresh_token and user.
    """
    # Authenticate
    user = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # FIX: Pass user object to create_access_token (from HIGH-7 fix)
    access_token = create_access_token(
        user=user,
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(user.id)
    
    # FIX: Return complete Token with user profile
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserPublic.model_validate(user),
    )


@router.post("/logout")
async def logout():
    """Logout endpoint — stateless JWT, client discards token."""
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: DBDep,
):
    """
    Refresh access token using valid refresh token.
    """
    user_id = verify_token(request.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    new_access_token = create_access_token(
        user=user,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    new_refresh_token = create_refresh_token(user.id)
    
    return TokenRefreshResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )