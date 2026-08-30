"""
Users endpoints — TOP WorX ERP
Provides /users/me and other user-related routes.

FIX: Added to match frontend authService.getCurrentUser() which calls GET /users/me
"""
from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserPublic

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: CurrentUser) -> UserPublic:
    """
    Return current authenticated user profile.

    Called by frontend authService.getCurrentUser() after login
    or on page refresh to restore user state.

    FIX: Added missing endpoint — frontend calls GET /users/me.
    """
    return UserPublic.model_validate(current_user)
