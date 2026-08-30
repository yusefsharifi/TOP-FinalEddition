"""Tests for Quality module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_inspections(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/quality/inspections", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_create_inspection(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/quality/inspections", json={
        "title": "بازرسی تست",
        "inspection_type": "incoming",
        "status": "pending",
        "scheduled_date": "2025-06-01",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_inspection(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/quality/inspections/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_update_inspection(client: AsyncClient, auth_headers: dict):
    resp = await client.patch("/api/v1/quality/inspections/1", json={
        "status": "in_progress",
    }, headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_complete_inspection(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/quality/inspections/1/complete", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_inspection_defects(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/quality/inspections/1/defects", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_create_defect(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/quality/defects", json={
        "inspection_id": 1,
        "title": "نقص تست",
        "severity": "medium",
        "description": "توضیحات نقص",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_resolve_defect(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/quality/defects/1/resolve", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_quality_dashboard(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/quality/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
