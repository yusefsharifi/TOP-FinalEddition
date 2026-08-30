"""Tests for Auth module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", data={
        "username": "admin@topworx.com",
        "password": "admin123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data.get("token_type") == "bearer"
    # Verify user object structure
    user = data["user"]
    assert "id" in user
    assert "email" in user
    assert "name" in user
    assert "role" in user


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", data={
        "username": "admin@topworx.com",
        "password": "wrongpassword",
    })
    assert resp.status_code in (400, 401, 422)


@pytest.mark.asyncio
async def test_login_missing_fields(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", data={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/auth/logout", headers=auth_headers)
    assert resp.status_code in (200, 204)


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/auth/refresh", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_refresh_token_no_header(client: AsyncClient):
    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code in (401, 403)
