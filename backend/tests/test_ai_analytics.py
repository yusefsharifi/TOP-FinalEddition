"""Tests for AI Analytics endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_dashboard(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/analytics/dashboard", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analytics_inventory(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/analytics/inventory", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analytics_finance(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/analytics/finance", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analytics_hr(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/analytics/hr", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analytics_sales(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/analytics/sales", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analytics_crm(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/analytics/crm", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_predict_inventory(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/analytics/predict", json={
        "module": "inventory",
        "metric": "demand",
    }, headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_detect_anomalies(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/anomalies?module=sales", headers=auth_headers)
    assert resp.status_code == 200
