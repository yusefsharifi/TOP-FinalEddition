"""
API Dependencies — RBAC Permission Enforcement
TOP WorX ERP System

FIX: Added require_permission dependency for RBAC enforcement
"""
from typing import Annotated, Optional, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from jose import jwt, JWTError

from app.db.session import get_db
from app.core.config import settings
from app.models.auth_enhanced import User, UserRole, RolePermission, Permission, UserPermissionOverride

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Validate JWT and return current user (async)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
        
        if payload.get("type") != "access":
            raise credentials_exception
            
    except (JWTError, ValueError):
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


# ============================================
# NEW: RBAC Permission Dependency
# ============================================

class PermissionDenied(HTTPException):
    def __init__(self, permission: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {permission} required",
        )


def require_permission(
    permission_code: str,
    data_scope: Optional[str] = None
) -> Callable:
    """
    FastAPI dependency factory for RBAC permission checking.
    
    Usage:
        @router.post("/payroll/approve")
        async def approve_payroll(
            db: DBDep,
            user: User = Depends(require_permission("hr:approve:payroll"))
        ):
            ...
    
    Args:
        permission_code: Permission code like "hr:approve:payroll", "inventory:delete", etc.
        data_scope: Optional data scope override ("own", "department", "all", etc.)
    
    Returns:
        Dependency function that returns User if authorized, raises 403 if not.
    """
    async def permission_checker(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        
        # Check for direct permission override (deny takes precedence)
        override_result = await check_permission_override(db, current_user.id, permission_code)
        if override_result == "deny":
            raise PermissionDenied(permission_code)
        if override_result == "grant":
            return current_user
        
        # Check role-based permissions
        has_perm = await user_has_permission(db, current_user.id, permission_code)
        
        if not has_perm:
            raise PermissionDenied(permission_code)
        
        # TODO: Check data scope if needed (e.g., user can only view own records)
        # if data_scope and not await check_data_scope(db, current_user, data_scope):
        #     raise PermissionDenied(f"{permission_code} with scope {data_scope}")
        
        return current_user
    
    return permission_checker


async def check_permission_override(
    db: AsyncSession,
    user_id: int,
    permission_code: str
) -> Optional[str]:
    """
    Check for direct user permission overrides (grant or deny).
    Returns: "grant", "deny", or None
    """
    # Get permission ID first
    perm_result = await db.execute(
        select(Permission.id).where(Permission.code == permission_code)
    )
    perm_id = perm_result.scalar_one_or_none()
    
    if not perm_id:
        return None
    
    # Check for override
    override_result = await db.execute(
        select(UserPermissionOverride).where(
            and_(
                UserPermissionOverride.user_id == user_id,
                UserPermissionOverride.permission_id == perm_id
            )
        )
    )
    override = override_result.scalar_one_or_none()
    
    if override:
        return override.override_type  # "grant" or "deny"
    return None


async def user_has_permission(db: AsyncSession, user_id: int, permission_code: str) -> bool:
    """
    Check if user has permission through their roles.
    """
    # Get permission ID
    perm_result = await db.execute(
        select(Permission.id).where(
            and_(
                Permission.code == permission_code,
                Permission.is_active == True
            )
        )
    )
    perm_id = perm_result.scalar_one_or_none()
    
    if not perm_id:
        return False  # Permission doesn't exist
    
    # Check if user has this permission through any of their roles
    # Join: User -> UserRole -> Role -> RolePermission -> Permission
    result = await db.execute(
        select(RolePermission).join(
            UserRole, 
            RolePermission.role_id == UserRole.role_id
        ).where(
            and_(
                UserRole.user_id == user_id,
                RolePermission.permission_id == perm_id,
                UserRole.expires_at.is_(None)  # Not expired
            )
        )
    )
    
    return result.scalar_one_or_none() is not None


async def require_role(
    required_roles: List[str]
) -> Callable:
    """
    Check if user has ANY of the required roles (simpler than permission-based).
    
    Usage:
        @router.delete("/items/{id}")
        async def delete_item(
            user: User = Depends(require_role(["admin", "manager"]))
        ):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        # Get user's role names
        user_roles = []
        if hasattr(current_user, 'user_roles'):
            for ur in current_user.user_roles:
                if ur.role:
                    role_name = getattr(ur.role, 'code', None) or getattr(ur.role, 'name', None)
                    if role_name:
                        user_roles.append(role_name.lower())
        
        # Check if any required role matches
        required_lower = [r.lower() for r in required_roles]
        if not any(role in required_lower for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: one of {required_roles}"
            )
        
        return current_user
    
    return role_checker


# ============================================
# Convenience Aliases
# ============================================

DBDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]

# Common permission shortcuts
RequireAdmin = Depends(require_permission("admin:full"))
RequireManager = Depends(require_permission("inventory:manage"))
RequireHRManager = Depends(require_permission("hr:manage"))
RequireFinanceManager = Depends(require_permission("finance:manage"))