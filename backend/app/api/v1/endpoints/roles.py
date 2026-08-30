"""
RBAC Role Checking Helper
TOP WorX ERP System

Provides a simple role-checking function for endpoint decorators.
"""
from __future__ import annotations

from typing import List

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_active_user
from app.models.auth_enhanced import User


async def check_role(
    current_user: User,
    required_roles: List[str],
) -> User:
    """
    Check if current user has any of the required roles.
    
    Usage in endpoint:
        @router.post("/items")
        async def create_item(
            data: ItemCreate,
            db: DBDep,
            current_user: CurrentUser = Depends(lambda: check_roleDepends(check_role, ["admin", "manager"])),
        ):
            ...
    
    Or use the convenience function:
        @router.post("/items")
        async def create_item(
            data: ItemCreate,
            db: DBDep,
            current_user: CurrentUser,
            _: User = Depends(require_roles(["admin", "manager"])),
        ):
            ...
    """
    user_roles = []
    if hasattr(current_user, 'user_roles'):
        for ur in current_user.user_roles:
            if ur.role:
                role_name = getattr(ur.role, 'code', None) or getattr(ur.role, 'name', None)
                if role_name:
                    user_roles.append(role_name.lower())
    
    required_lower = [r.lower() for r in required_roles]
    if not any(role in required_lower for role in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role required: one of {required_roles}"
        )
    
    return current_user


def require_roles(roles: List[str]):
    """
    Dependency factory that checks if user has any of the specified roles.
    
    Usage:
        @router.delete("/items/{id}")
        async def delete_item(
            item_id: int,
            db: DBDep,
            current_user: CurrentUser,
            _: User = Depends(require_roles(["admin", "manager"])),
        ):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        return await check_role(current_user, roles)
    
    return role_checker
