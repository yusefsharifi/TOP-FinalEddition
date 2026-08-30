"""
User Schemas — Pydantic v2 compatible
TOP WorX ERP System

FIX: Rewrote UserPublic to use @model_validator instead of from_orm,
so it works with both model_validate() and from_attributes=True.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import datetime


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserUpdate(UserBase):
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


# ============================================
# UserPublic — login response user object
# ============================================

class UserPublic(BaseModel):
    """
    Public user profile — sent in login response.

    Expected by frontend authService.ts:
    {
      id: string,
      name: string,
      email: string,
      role: string
    }

    FIX: Uses @model_validator to handle both ORM objects and dicts.
    Works with Pydantic v2 model_validate() and from_attributes=True.
    """
    id: str = ""                # String to match frontend expectation
    email: str = ""
    name: str = ""              # Computed from first_name + last_name
    role: str = "staff"         # Primary role name
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    roles: List[str] = []       # All roles if multiple

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def extract_from_orm(cls, data):
        """
        Handle ORM objects by extracting fields before validation.
        This makes UserPublic work with both:
          - UserPublic.model_validate(orm_user)
          - UserPublic.from_orm(orm_user)
        """
        if hasattr(data, '__dict__') and not isinstance(data, dict):
            # It's an ORM object — extract what we need
            obj = data
            result = {}

            # ID — always convert to string for frontend
            result['id'] = str(getattr(obj, 'id', 0))
            result['email'] = getattr(obj, 'email', '')

            # Name computation
            first_name = getattr(obj, 'first_name', None)
            last_name = getattr(obj, 'last_name', None)
            full_name_prop = getattr(obj, 'full_name', None)

            # full_name is a property on auth_enhanced.User
            if callable(getattr(type(obj), 'full_name', None)):
                try:
                    full_name_prop = obj.full_name
                except Exception:
                    full_name_prop = None

            if full_name_prop:
                result['name'] = full_name_prop
            elif first_name or last_name:
                result['name'] = f"{first_name or ''} {last_name or ''}".strip()
            else:
                result['name'] = getattr(obj, 'username', '') or result['email']

            result['first_name'] = first_name
            result['last_name'] = last_name
            result['full_name'] = full_name_prop or result['name']
            result['username'] = getattr(obj, 'username', None)

            # is_active — handle as property on auth_enhanced.User
            if callable(getattr(type(obj), 'is_active', None)):
                try:
                    result['is_active'] = obj.is_active
                except Exception:
                    result['is_active'] = True
            else:
                result['is_active'] = getattr(obj, 'is_active', True)

            # Roles — extract from user_roles relationship
            roles = []
            role = 'staff'

            user_roles = getattr(obj, 'user_roles', None)
            if user_roles:
                for ur in user_roles:
                    role_obj = getattr(ur, 'role', None)
                    if role_obj:
                        role_name = getattr(role_obj, 'name', None) or getattr(role_obj, 'code', None)
                        if role_name:
                            roles.append(role_name)
                role = roles[0] if roles else 'staff'

            # Fallback: simple role field
            if not roles and hasattr(obj, 'role'):
                role_val = obj.role
                if hasattr(role_val, 'value'):
                    role = role_val.value
                else:
                    role = str(role_val)
                roles = [role] if role else []

            result['role'] = role or 'staff'
            result['roles'] = roles

            return result

        return data
