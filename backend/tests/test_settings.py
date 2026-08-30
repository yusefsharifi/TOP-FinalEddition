"""
Settings & Administration Module — Test Suite
TOP WorX ERP System

Tests:
  - System settings CRUD
  - Role management
  - Audit log
  - System notifications
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


# ── System Settings ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_setting(client: AsyncClient):
    resp = await client.post("/api/v1/settings/system", json={
        "key": "company_name",
        "value": "TOP WorX",
        "category": "general",
        "description": "Company display name",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["key"] == "company_name"
    assert data["value"] == "TOP WorX"


@pytest.mark.asyncio
async def test_create_duplicate_setting(client: AsyncClient):
    await client.post("/api/v1/settings/system", json={
        "key": "theme", "value": "dark", "category": "ui",
    })
    resp = await client.post("/api/v1/settings/system", json={
        "key": "theme", "value": "light", "category": "ui",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_setting(client: AsyncClient):
    await client.post("/api/v1/settings/system", json={
        "key": "max_upload_mb", "value": "50", "category": "general",
    })
    resp = await client.get("/api/v1/settings/system/max_upload_mb")
    assert resp.status_code == 200
    assert resp.json()["value"] == "50"


@pytest.mark.asyncio
async def test_get_setting_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/settings/system/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_setting(client: AsyncClient):
    await client.post("/api/v1/settings/system", json={
        "key": "language", "value": "fa", "category": "ui",
    })
    resp = await client.put("/api/v1/settings/system/language", json={
        "key": "language", "value": "en", "category": "ui",
    })
    assert resp.status_code == 200
    assert resp.json()["value"] == "en"


@pytest.mark.asyncio
async def test_list_settings(client: AsyncClient):
    await client.post("/api/v1/settings/system", json={
        "key": "a", "value": "1", "category": "general",
    })
    await client.post("/api/v1/settings/system", json={
        "key": "b", "value": "2", "category": "security",
    })

    resp = await client.get("/api/v1/settings/system")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_list_settings_filter_by_category(client: AsyncClient):
    await client.post("/api/v1/settings/system", json={
        "key": "x", "value": "1", "category": "general",
    })
    await client.post("/api/v1/settings/system", json={
        "key": "y", "value": "2", "category": "security",
    })

    resp = await client.get("/api/v1/settings/system?category=security")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["category"] == "security"


# ── System Notifications ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_system_notification(client: AsyncClient):
    resp = await client.post("/api/v1/settings/notifications", json={
        "title": "System Maintenance",
        "message": "Scheduled maintenance on Saturday.",
        "severity": "warning",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "System Maintenance"
    assert data["severity"] == "warning"
    assert data["created_by_id"] == 1


@pytest.mark.asyncio
async def test_list_system_notifications(client: AsyncClient):
    await client.post("/api/v1/settings/notifications", json={
        "title": "Notice 1", "message": "Msg", "severity": "info",
    })
    await client.post("/api/v1/settings/notifications", json={
        "title": "Notice 2", "message": "Msg", "severity": "error",
    })

    resp = await client.get("/api/v1/settings/notifications")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ── Audit Log ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_log_records_creates(client: AsyncClient):
    # Create a setting (should generate audit log)
    await client.post("/api/v1/settings/system", json={
        "key": "audit_test", "value": "yes", "category": "general",
    })

    resp = await client.get("/api/v1/settings/audit-log")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["action"] == "create"
    assert data[0]["module"] == "settings"


@pytest.mark.asyncio
async def test_audit_log_filter_by_module(client: AsyncClient):
    await client.post("/api/v1/settings/system", json={
        "key": "test", "value": "1", "category": "general",
    })

    resp = await client.get("/api/v1/settings/audit-log?module=settings")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
