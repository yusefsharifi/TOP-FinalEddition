"""Tests for AI Workflow Automation endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_workflow_handlers(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/workflows/handlers", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 8


@pytest.mark.asyncio
async def test_run_all_handlers(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/workflows/run-all", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data


@pytest.mark.asyncio
async def test_scan_status(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/workflows/scan-status", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scan_inventory(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/workflows/scan/inventory", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scan_finance(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/workflows/scan/finance", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scan_crm(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/workflows/scan/crm", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scan_hr(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/workflows/scan/hr", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scan_projects(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/workflows/scan/projects", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scan_quality(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/workflows/scan/quality", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_run_specific_handler(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/workflows/run/low_stock_auto_po", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "handler" in data or "result" in data
