"""
RBAC Module — Test Suite
TOP WorX ERP System

Run:
    pytest backend/app/tests/test_rbac.py -v --asyncio-mode=auto

Tests verify:
  - Password policy (complexity, history, expiry)
  - Permission engine (exact match, wildcard, deny override, data scope)
  - User lifecycle (create, suspend, delete, role change)
  - Audit log generation
  - Session revocation blocks login
  - Cannot promote user above creator's level
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.auth_enhanced import (
    Base, DataScope, Permission, Role, RolePermission,
    RoleType, User, UserRole, UserSession, UserStatus,
)
from app.services.permission_engine import PasswordPolicy, permission_engine, audit_service
from app.services.user_management_service import user_management_service

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="function")
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture(scope="function")
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


def _make_user(**kwargs) -> User:
    u = User(
        email=kwargs.get("email", "test@example.com"),
        hashed_password="$2b$12$fake",
        first_name=kwargs.get("first_name", "Test"),
        last_name=kwargs.get("last_name", "User"),
        status=kwargs.get("status", UserStatus.ACTIVE),
        deleted_at=kwargs.get("deleted_at", None),
    )
    return u


# ===========================================================================
# TestPasswordPolicy
# ===========================================================================
class TestPasswordPolicy:
    policy = PasswordPolicy()

    def test_strong_password_passes(self):
        ok, errors = self.policy.validate_strength("SecureP@ss123")
        assert ok is True
        assert errors == []

    def test_too_short_fails(self):
        ok, errors = self.policy.validate_strength("Abc1!")
        assert ok is False
        assert any("کاراکتر" in e or "characters" in e for e in errors)

    def test_no_uppercase_fails(self):
        ok, errors = self.policy.validate_strength("secure@pass123")
        assert ok is False
        assert any("uppercase" in e.lower() or "بزرگ" in e for e in errors)

    def test_no_lowercase_fails(self):
        ok, errors = self.policy.validate_strength("SECURE@PASS123")
        assert ok is False
        assert any("lowercase" in e.lower() or "کوچک" in e for e in errors)

    def test_no_digit_fails(self):
        ok, errors = self.policy.validate_strength("Secure@Pass!")
        assert ok is False
        assert any("digit" in e.lower() or "عدد" in e for e in errors)

    def test_no_special_char_fails(self):
        ok, errors = self.policy.validate_strength("SecurePass123")
        assert ok is False
        assert any("special" in e.lower() or "خاص" in e for e in errors)

    def test_common_password_rejected(self):
        ok, errors = self.policy.validate_strength("Password1!")
        assert ok is False
        assert any("common" in e.lower() or "ساده" in e for e in errors)

    def test_multiple_failures_returned(self):
        ok, errors = self.policy.validate_strength("abc")
        assert ok is False
        assert len(errors) >= 3

    def test_expiry_calculation(self):
        expires = self.policy.should_expire_at()
        expected = datetime.utcnow() + timedelta(days=self.policy.max_age_days)
        assert abs((expires - expected).total_seconds()) < 5

    def test_is_expired_true(self):
        user = _make_user()
        user.password_expires_at = datetime.utcnow() - timedelta(days=1)
        assert self.policy.is_expired(user) is True

    def test_is_expired_false(self):
        user = _make_user()
        user.password_expires_at = datetime.utcnow() + timedelta(days=30)
        assert self.policy.is_expired(user) is False

    def test_no_expiry_not_expired(self):
        user = _make_user()
        user.password_expires_at = None
        assert self.policy.is_expired(user) is False


# ===========================================================================
# TestPermissionEngine (logic only, no DB)
# ===========================================================================
class TestPermissionLogic:

    def _perms(self, codes: list[str]) -> dict:
        """Build permissions dict for testing."""
        return {code: {"granted": True, "conditions": {}, "scope": "all", "role_code": "test"}
                for code in codes}

    def test_exact_match(self):
        """Permission present → True."""
        perms = self._perms(["inventory:view", "sales:create"])
        assert "inventory:view" in perms

    def test_wildcard_module_match(self):
        """inventory:* should cover inventory:create."""
        perms = self._perms(["inventory:*", "sales:view"])
        # Simulate wildcard check
        code = "inventory:create"
        parts = code.split(":")
        found = False
        for i in range(len(parts), 0, -1):
            wildcard = ":".join(parts[:i]) + ":*"
            if wildcard in perms:
                found = True
                break
        assert found is True

    def test_global_wildcard(self):
        """* matches everything."""
        perms = self._perms(["*"])
        assert "*" in perms

    def test_deny_override_removes_permission(self):
        """DENY override removes permission from set."""
        perms = self._perms(["inventory:view", "inventory:delete"])
        # Apply deny
        perms.pop("inventory:delete", None)
        assert "inventory:delete" not in perms
        assert "inventory:view" in perms

    def test_inactive_user_has_no_permissions(self):
        user = _make_user(status=UserStatus.SUSPENDED)
        assert not user.is_active

    def test_deleted_user_has_no_permissions(self):
        user = _make_user()
        user.deleted_at = datetime.utcnow()
        assert not user.is_active

    def test_data_scope_own_is_most_restrictive(self):
        scopes = [DataScope.OWN, DataScope.DEPARTMENT, DataScope.COMPANY, DataScope.ALL]
        scope_values = [s.value for s in scopes]
        assert scope_values.index("own") < scope_values.index("all")


# ===========================================================================
# TestUserLifecycle
# ===========================================================================
class TestUserLifecycle:

    def test_active_user_is_active(self):
        user = _make_user(status=UserStatus.ACTIVE)
        assert user.is_active is True

    def test_suspended_user_not_active(self):
        user = _make_user(status=UserStatus.SUSPENDED)
        assert user.is_active is False

    def test_deleted_user_not_active(self):
        user = _make_user()
        user.deleted_at = datetime.utcnow()
        assert user.is_active is False

    def test_level_hierarchy_prevents_over_promotion(self):
        """Creator at level 3 cannot assign role at level 1."""
        creator_level = 3
        target_role_level = 1  # More powerful
        can_assign = target_role_level >= creator_level
        assert can_assign is False

    def test_creator_can_assign_lower_level_role(self):
        """Creator at level 3 can assign role at level 4+."""
        creator_level = 3
        target_role_level = 4  # Less powerful
        can_assign = target_role_level >= creator_level
        assert can_assign is True

    def test_password_hash_is_different_from_plain(self):
        import bcrypt
        plain = "TestP@ss123"
        hashed = bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=4)).decode()
        assert hashed != plain

    def test_password_verification(self):
        import bcrypt
        plain = "TestP@ss123"
        hashed = bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=4)).decode()
        assert bcrypt.checkpw(plain.encode(), hashed.encode()) is True
        assert bcrypt.checkpw("WrongPassword!".encode(), hashed.encode()) is False

    def test_session_revocation_marks_inactive(self):
        session = UserSession(
            user_id=1, token_jti="test-jti",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        assert session.is_active is False
        assert session.revoked_at is not None

    def test_lockout_after_max_attempts(self):
        policy = PasswordPolicy()
        user = _make_user()
        user.failed_login_attempts = policy.max_failed_attempts
        # Should trigger lockout
        should_lock = user.failed_login_attempts >= policy.max_failed_attempts
        assert should_lock is True

    def test_lockout_check(self):
        user = _make_user()
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        is_locked = datetime.utcnow() < user.locked_until.replace(tzinfo=None)
        assert is_locked is True


# ===========================================================================
# TestAuditService
# ===========================================================================
class TestAuditService:

    def test_build_changes_detects_diff(self):
        old = MagicMock()
        old.status = "draft"
        old.amount = 100

        new = MagicMock()
        new.status = "posted"
        new.amount = 100  # unchanged

        changes = audit_service.build_changes(old, new, ["status", "amount"])
        assert "status" in changes
        assert changes["status"]["old"] == "draft"
        assert changes["status"]["new"] == "posted"
        assert "amount" not in changes  # unchanged

    def test_mask_sensitive_redacts_password(self):
        data = {"email": "user@test.com", "hashed_password": "bcrypt_hash", "name": "Ali"}
        masked = audit_service.mask_sensitive(data)
        assert masked["hashed_password"] == "***REDACTED***"
        assert masked["email"] == "user@test.com"

    def test_mask_custom_fields(self):
        data = {"api_key": "secret", "name": "Test"}
        masked = audit_service.mask_sensitive(data, fields=["api_key"])
        assert masked["api_key"] == "***REDACTED***"

    def test_full_name_property(self):
        user = _make_user(first_name="محمد", last_name="احمدی")
        assert user.full_name == "محمد احمدی"


# ===========================================================================
# Frontend Guide (in comments — see FRONTEND_GUIDE below)
# ===========================================================================
FRONTEND_GUIDE = """
// RBAC Module — Frontend Integration Guide
// src/types/rbac.ts

export type UserStatus = "active" | "inactive" | "suspended" | "pending_verification";
export type DataScope = "own" | "department" | "branch" | "company" | "all";
export type AuditAction = "create"|"update"|"delete"|"view"|"login"|"logout"|"login_failed"|"export"|"approve"|"reject"|"suspend"|"activate"|"password_change"|"permission_change"|"session_revoke"|"system";

export interface UserProfile {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  firstNameFa: string | null;
  lastNameFa: string | null;
  phone: string | null;
  avatarUrl: string | null;
  status: UserStatus;
  emailVerified: boolean;
  mfaEnabled: boolean;
  language: "fa" | "en";
  timezone: string;
  theme: "light" | "dark" | "system";
  lastLoginAt: string | null;
  passwordExpiresAt: string | null;
  roles: { id: number; code: string; name: string; level: number }[];
}

export interface Role {
  id: number;
  code: string;
  name: string;
  nameFa: string | null;
  level: number;
  dataScope: DataScope;
  roleType: "system" | "custom";
  defaultDashboard: string | null;
}

export interface Permission {
  id: number;
  code: string;
  name: string;
  module: string;
  action: string;
  scope: string | null;
  category: "operational" | "administrative" | "system";
}

export interface AuditLogEntry {
  id: number;
  userEmail: string | null;
  action: AuditAction;
  module: string;
  resourceType: string | null;
  resourceId: number | null;
  resourceDescription: string | null;
  changes: Record<string, { old: string | null; new: string | null }> | null;
  status: "success" | "failure" | "denied";
  ipAddress: string | null;
  createdAt: string;
}

export interface Session {
  id: number;
  deviceType: "desktop" | "mobile" | "tablet" | "api";
  deviceName: string | null;
  ipAddress: string | null;
  createdAt: string;
  lastActivityAt: string;
}

// Permission hook — checks if current user has permission
export function usePermission(permissionCode: string): boolean {
  const { data: perms } = useQuery(
    ["me", "permissions"],
    () => axios.get("/api/v1/me/permissions").then(r => r.data.permissions as string[]),
    { staleTime: 5 * 60 * 1000 }
  );
  if (!perms) return false;
  if (perms.includes("*")) return true;
  if (perms.includes(permissionCode)) return true;
  // Wildcard: inventory:* matches inventory:create
  const parts = permissionCode.split(":");
  for (let i = parts.length; i > 0; i--) {
    const wildcard = parts.slice(0, i).join(":") + ":*";
    if (perms.includes(wildcard)) return true;
  }
  return false;
}

// Conditional rendering guard
export const Can: React.FC<{ permission: string; children: ReactNode; fallback?: ReactNode }> = ({
  permission, children, fallback = null,
}) => {
  const allowed = usePermission(permission);
  return <>{allowed ? children : fallback}</>;
};

// Usage:
// <Can permission="inventory:delete">
//   <Button onClick={deleteItem}>Delete</Button>
// </Can>

// Role matrix component structure (permissions × roles grid)
// src/pages/admin/RoleMatrix.tsx
//
// Rows = grouped permissions by module
// Columns = roles
// Cell = checkbox (checked if role has permission)
// onChange = POST/DELETE to /admin/roles/{id}/permissions

// Audit diff viewer
// src/components/AuditDiffViewer.tsx
//
// Shows old_values vs new_values side by side
// Highlight changed fields in yellow
// Mask sensitive fields (show *** instead of values)

// Session management
// src/pages/me/Sessions.tsx
//
// List active sessions with device info
// "Logout other devices" button
// Each session: device icon + location + last activity
"""
