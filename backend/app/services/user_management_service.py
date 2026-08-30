"""
RBAC Module — User Management Service + FastAPI Dependencies
TOP WorX ERP System

UserManagementService: full user lifecycle (create, invite, suspend, etc.)
Permission dependencies: require_permission(), require_role() for FastAPI
"""
from __future__ import annotations

import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_enhanced import (
    AuditAction, AuditStatus, DataScope, PasswordHistory, Role,
    User, UserInvitation, UserRole, UserSession, UserStatus,
)
from app.services.permission_engine import audit_service, password_policy, permission_engine


class UserManagementError(Exception):
    pass


class UserManagementService:

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

    def _check_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def _generate_temp_password(self, length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        # Ensure policy compliance
        pwd = (
            secrets.choice(string.ascii_uppercase) +
            secrets.choice(string.ascii_lowercase) +
            secrets.choice(string.digits) +
            secrets.choice("!@#$%^&*") +
            "".join(secrets.choice(alphabet) for _ in range(length - 4))
        )
        chars = list(pwd)
        secrets.SystemRandom().shuffle(chars)
        return "".join(chars)

    async def create_user(
        self,
        db: AsyncSession,
        *,
        email: str,
        first_name: str,
        last_name: str,
        role_id: int,
        created_by: User,
        password: Optional[str] = None,
        first_name_fa: Optional[str] = None,
        last_name_fa: Optional[str] = None,
        phone: Optional[str] = None,
        employee_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> tuple[User, str]:
        """
        Create a new user with a role.
        Returns (user, plain_text_password) — password must be delivered to user.
        """
        # Check uniqueness
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise UserManagementError(f"Email '{email}' is already registered")

        # Validate role exists + creator can assign it
        role_r = await db.execute(select(Role).where(Role.id == role_id, Role.is_active.is_(True)))
        role = role_r.scalar_one_or_none()
        if not role:
            raise UserManagementError(f"Role {role_id} not found")

        # Level check: cannot assign role with level lower (more powerful) than creator's
        creator_role = await self._get_primary_role(db, created_by)
        if creator_role and role.level < creator_role.level:
            raise UserManagementError(
                f"Cannot assign role '{role.name}' (level {role.level}) — "
                f"your role level is {creator_role.level}"
            )

        # Generate / validate password
        plain_password = password or self._generate_temp_password()
        is_valid, errors = password_policy.validate_strength(plain_password)
        if not is_valid:
            raise UserManagementError(f"Password policy violation: {'; '.join(errors)}")

        hashed = self._hash_password(plain_password)
        user = User(
            email=email,
            hashed_password=hashed,
            first_name=first_name,
            last_name=last_name,
            first_name_fa=first_name_fa,
            last_name_fa=last_name_fa,
            phone=phone,
            employee_id=employee_id,
            status=UserStatus.ACTIVE,
            email_verified=False,
            password_changed_at=datetime.utcnow(),
            password_expires_at=password_policy.should_expire_at(),
            force_password_change=password is None,  # temp password → must change
            created_by_id=created_by.id,
        )
        db.add(user)
        await db.flush()

        # Assign role
        user_role = UserRole(
            user_id=user.id,
            role_id=role_id,
            assigned_by_id=created_by.id,
            is_primary=True,
        )
        db.add(user_role)

        # Record password history
        await password_policy.record_history(db, user)

        await audit_service.log(
            db, user=created_by, action=AuditAction.CREATE,
            module="admin", resource_type="user", resource_id=user.id,
            resource_description=email, ip_address=ip_address,
            new_values={"email": email, "role": role.code},
        )
        await db.flush()
        return user, plain_password

    async def invite_user(
        self,
        db: AsyncSession,
        *,
        email: str,
        role_id: int,
        invited_by: User,
        department_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> UserInvitation:
        """Send invitation link (valid 48 hours)."""
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise UserManagementError(f"Email '{email}' is already registered")

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        invitation = UserInvitation(
            email=email,
            role_id=role_id,
            invited_by_id=invited_by.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=48),
            department_id=department_id,
            first_name=first_name,
            last_name=last_name,
        )
        db.add(invitation)
        await db.flush()

        # TODO: send invitation email with link:
        # /auth/accept-invitation?token={token}
        # DECISION POINT ⚙️: Integrate with email service

        await audit_service.log(
            db, user=invited_by, action=AuditAction.CREATE,
            module="admin", resource_type="invitation", resource_description=email,
        )
        return invitation

    async def accept_invitation(
        self,
        db: AsyncSession,
        token: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        inv_r = await db.execute(
            select(UserInvitation).where(
                UserInvitation.token_hash == token_hash,
                UserInvitation.is_used.is_(False),
                UserInvitation.expires_at > datetime.utcnow(),
            )
        )
        inv = inv_r.scalar_one_or_none()
        if not inv:
            raise UserManagementError("Invitation token is invalid or expired")

        is_valid, errors = password_policy.validate_strength(password)
        if not is_valid:
            raise UserManagementError(f"Password policy: {'; '.join(errors)}")

        hashed = self._hash_password(password)
        invited_by_r = await db.execute(select(User).where(User.id == inv.invited_by_id))
        invited_by = invited_by_r.scalar_one_or_none()

        user = User(
            email=inv.email,
            hashed_password=hashed,
            first_name=first_name or inv.first_name or "",
            last_name=last_name or inv.last_name or "",
            status=UserStatus.ACTIVE,
            email_verified=True,
            password_changed_at=datetime.utcnow(),
            password_expires_at=password_policy.should_expire_at(),
            created_by_id=inv.invited_by_id,
        )
        db.add(user)
        await db.flush()

        user_role = UserRole(
            user_id=user.id, role_id=inv.role_id,
            department_id=inv.department_id,
            assigned_by_id=inv.invited_by_id, is_primary=True,
        )
        db.add(user_role)
        await password_policy.record_history(db, user)

        inv.is_used = True
        inv.accepted_at = datetime.utcnow()
        await db.flush()
        return user

    async def authenticate(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_type: str = "desktop",
    ) -> User:
        """Authenticate and return user. Raises on failure."""
        user_r = await db.execute(select(User).where(User.email == email))
        user = user_r.scalar_one_or_none()

        if not user:
            # Log failed attempt without exposing user existence
            await audit_service.log(
                db, action=AuditAction.LOGIN_FAILED, module="auth",
                resource_description=email, ip_address=ip_address,
                status=AuditStatus.FAILURE, error_message="User not found",
            )
            raise UserManagementError("Invalid email or password")

        if user.deleted_at:
            raise UserManagementError("Account has been deactivated")

        # Check lockout
        if user.locked_until and datetime.utcnow() < user.locked_until.replace(tzinfo=None):
            remaining = int((user.locked_until.replace(tzinfo=None) - datetime.utcnow()).total_seconds() / 60)
            raise UserManagementError(f"Account locked. Try again in {remaining} minutes")

        if user.status == UserStatus.SUSPENDED:
            raise UserManagementError("Account is suspended. Contact administrator.")

        # Verify password
        if not self._check_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= password_policy.max_failed_attempts:
                user.locked_until = datetime.utcnow() + timedelta(minutes=password_policy.lockout_minutes)
            await db.flush()
            await audit_service.log(
                db, user=user, action=AuditAction.LOGIN_FAILED, module="auth",
                ip_address=ip_address, status=AuditStatus.FAILURE,
                error_message=f"Attempt {user.failed_login_attempts}/{password_policy.max_failed_attempts}",
            )
            raise UserManagementError("Invalid email or password")

        # Success — reset counter
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = ip_address
        await db.flush()
        return user

    async def create_session(
        self,
        db: AsyncSession,
        user: User,
        jti: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_type: str = "desktop",
    ) -> UserSession:
        session = UserSession(
            user_id=user.id,
            token_jti=jti,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )
        db.add(session)
        await db.flush()

        await audit_service.log(
            db, user=user, action=AuditAction.LOGIN, module="auth",
            ip_address=ip_address, session_id=jti,
        )
        return session

    async def revoke_session(
        self, db: AsyncSession, session: UserSession, reason: str, revoked_by: Optional[User] = None
    ) -> None:
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        session.revoke_reason = reason
        await db.flush()

    async def revoke_all_sessions(
        self, db: AsyncSession, user: User, reason: str, revoked_by: Optional[User] = None
    ) -> int:
        sessions_r = await db.execute(
            select(UserSession).where(UserSession.user_id == user.id, UserSession.is_active.is_(True))
        )
        sessions = sessions_r.scalars().all()
        for session in sessions:
            session.is_active = False
            session.revoked_at = datetime.utcnow()
            session.revoke_reason = reason
        await db.flush()
        await audit_service.log(
            db, user=revoked_by or user, action=AuditAction.SESSION_REVOKE, module="admin",
            resource_type="user", resource_id=user.id,
            resource_description=f"All sessions revoked: {reason}",
        )
        return len(sessions)

    async def is_session_valid(self, db: AsyncSession, jti: str) -> bool:
        r = await db.execute(
            select(UserSession).where(
                UserSession.token_jti == jti,
                UserSession.is_active.is_(True),
                UserSession.expires_at > datetime.utcnow(),
            )
        )
        return r.scalar_one_or_none() is not None

    async def suspend_user(
        self, db: AsyncSession, user_id: int, reason: str, suspended_by: User
    ) -> User:
        user_r = await db.execute(select(User).where(User.id == user_id))
        user = user_r.scalar_one_or_none()
        if not user:
            raise UserManagementError(f"User {user_id} not found")
        if user.id == suspended_by.id:
            raise UserManagementError("Cannot suspend yourself")

        user.status = UserStatus.SUSPENDED
        await self.revoke_all_sessions(db, user, f"Account suspended: {reason}", suspended_by)
        await audit_service.log(
            db, user=suspended_by, action=AuditAction.SUSPEND, module="admin",
            resource_type="user", resource_id=user.id,
            new_values={"status": "suspended", "reason": reason},
        )
        await db.flush()
        return user

    async def activate_user(self, db: AsyncSession, user_id: int, activated_by: User) -> User:
        user_r = await db.execute(select(User).where(User.id == user_id))
        user = user_r.scalar_one_or_none()
        if not user:
            raise UserManagementError(f"User {user_id} not found")
        user.status = UserStatus.ACTIVE
        await audit_service.log(
            db, user=activated_by, action=AuditAction.ACTIVATE, module="admin",
            resource_type="user", resource_id=user.id,
        )
        await db.flush()
        return user

    async def change_password(
        self,
        db: AsyncSession,
        user: User,
        new_password: str,
        changed_by: Optional[User] = None,
        require_old: bool = False,
        old_password: Optional[str] = None,
    ) -> None:
        if require_old and old_password:
            if not self._check_password(old_password, user.hashed_password):
                raise UserManagementError("Incorrect current password")

        is_valid, errors = password_policy.validate_strength(new_password)
        if not is_valid:
            raise UserManagementError(f"Password policy: {'; '.join(errors)}")

        reuse_ok, reuse_err = await password_policy.check_history(db, user.id, new_password)
        if not reuse_ok:
            raise UserManagementError(reuse_err)

        await password_policy.record_history(db, user)
        user.hashed_password = self._hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        user.password_expires_at = password_policy.should_expire_at()
        user.force_password_change = False
        user.failed_login_attempts = 0

        await audit_service.log(
            db, user=changed_by or user, action=AuditAction.PASSWORD_CHANGE, module="auth",
            resource_type="user", resource_id=user.id,
            is_sensitive=True,
        )
        await db.flush()

    async def change_role(
        self,
        db: AsyncSession,
        user_id: int,
        new_role_id: int,
        changed_by: User,
    ) -> User:
        user_r = await db.execute(select(User).where(User.id == user_id))
        user = user_r.scalar_one_or_none()
        if not user:
            raise UserManagementError(f"User {user_id} not found")

        new_role_r = await db.execute(select(Role).where(Role.id == new_role_id))
        new_role = new_role_r.scalar_one_or_none()
        if not new_role:
            raise UserManagementError(f"Role {new_role_id} not found")

        changer_role = await self._get_primary_role(db, changed_by)
        if changer_role and new_role.level < changer_role.level:
            raise UserManagementError("Cannot assign a role more powerful than your own")

        # Get old role for audit
        old_role = await self._get_primary_role(db, user)

        # Remove existing primary roles
        primary_r = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.is_primary.is_(True))
        )
        for ur in primary_r.scalars().all():
            await db.delete(ur)

        # Assign new role
        user_role = UserRole(user_id=user_id, role_id=new_role_id, assigned_by_id=changed_by.id, is_primary=True)
        db.add(user_role)

        # Revoke sessions when permissions reduced
        await self.revoke_all_sessions(db, user, "Role changed — re-login required", changed_by)

        await audit_service.log(
            db, user=changed_by, action=AuditAction.PERMISSION_CHANGE, module="admin",
            resource_type="user", resource_id=user_id,
            changes={"role": {"old": old_role.code if old_role else None, "new": new_role.code}},
        )
        await db.flush()
        return user

    async def soft_delete(self, db: AsyncSession, user_id: int, deleted_by: User) -> User:
        user_r = await db.execute(select(User).where(User.id == user_id))
        user = user_r.scalar_one_or_none()
        if not user:
            raise UserManagementError(f"User {user_id} not found")
        if user.id == deleted_by.id:
            raise UserManagementError("Cannot delete yourself")

        user.deleted_at = datetime.utcnow()
        user.deleted_by_id = deleted_by.id
        user.status = UserStatus.INACTIVE
        await self.revoke_all_sessions(db, user, "Account deleted", deleted_by)
        await audit_service.log(
            db, user=deleted_by, action=AuditAction.DELETE, module="admin",
            resource_type="user", resource_id=user_id,
        )
        await db.flush()
        return user

    async def _get_primary_role(self, db: AsyncSession, user: User) -> Optional[Role]:
        r = await db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id, UserRole.is_primary.is_(True))
            .limit(1)
        )
        return r.scalar_one_or_none()


user_management_service = UserManagementService()


# ===========================================================================
# FastAPI Dependencies
# ===========================================================================
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
import jwt
import os

bearer_scheme = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> User:
    """
    Base dependency: validate JWT, check session is active, return User.
    INTEGRATION POINT: Replace with your existing get_current_user or merge logic.
    """
    if not credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub", 0))
        jti: str = payload.get("jti", "")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    # INTEGRATION POINT: Import your actual DB session and User model
    # This is a placeholder — replace with real DB lookup
    # async with get_db() as db:
    #     user = await db.get(User, user_id)
    #     if not user or not user.is_active:
    #         raise HTTPException(401, "User not found or inactive")
    #     if not await user_management_service.is_session_valid(db, jti):
    #         raise HTTPException(401, "Session expired or revoked")
    #     return user
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Wire up DB session")


def require_permission(permission_code: str):
    """
    FastAPI dependency factory for permission checking.

    Usage:
        @router.post("/inventory/items")
        async def create_item(
            ...,
            current_user: User = Depends(require_permission("inventory:create"))
        ):
    """
    async def _checker(
        current_user: User = Depends(get_current_user),
        # INTEGRATION POINT: inject db session here
    ) -> User:
        # async with get_db() as db:
        #     if not await permission_engine.has_permission(db, current_user, permission_code):
        #         await audit_service.log(
        #             db, user=current_user, action=AuditAction.VIEW, module=permission_code.split(":")[0],
        #             status=AuditStatus.DENIED, error_message=f"Missing: {permission_code}",
        #         )
        #         raise HTTPException(403, f"Permission denied: {permission_code}")
        # return current_user
        return current_user  # Stub
    return _checker


def require_role(*role_codes: str):
    """Require user to have one of the specified roles."""
    async def _checker(current_user: User = Depends(get_current_user)) -> User:
        # user_role_codes = {ur.role.code for ur in current_user.user_roles}
        # if not any(code in user_role_codes for code in role_codes):
        #     raise HTTPException(403, f"Required roles: {role_codes}")
        return current_user
    return _checker


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is not active")
    if current_user.force_password_change:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Password change required before proceeding")
    return current_user
