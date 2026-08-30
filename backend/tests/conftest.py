"""
Shared test fixtures for TOP WorX ERP endpoint tests.

Provides:
  - Async SQLite engine + session for DB tests
  - Mock current user dependency
  - FastAPI TestClient with dependency overrides
"""
from __future__ import annotations

from typing import AsyncGenerator
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base_class import Base
from app.main import app

# Import all new models so Base.metadata sees their tables
import app.models.hse          # noqa: F401
import app.models.tasks        # noqa: F401
import app.models.contracts    # noqa: F401
import app.models.messages     # noqa: F401
import app.models.settings     # noqa: F401
import app.models.auth_enhanced  # noqa: F401

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


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client with DB and auth dependencies overridden."""

    async def _override_db():
        yield db

    def _override_user():
        user = MagicMock()
        user.id = 1
        user.email = "test@topworx.com"
        user.is_active = True
        return user

    from app.api.deps import get_db, get_current_active_user
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_active_user] = _override_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers() -> dict:
    """Fake Authorization header for authenticated endpoints."""
    return {"Authorization": "Bearer fake-test-token"}
