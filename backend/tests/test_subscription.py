"""Tests for Subscription module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_subscription(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/subscriptions/subscriptions/", json={
        "customer_id": 1,
        "plan": "monthly",
        "start_date": "2025-01-01",
        "amount": 500000,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_subscription(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/subscriptions/subscriptions/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_upcoming_deliveries(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/subscriptions/subscriptions/upcoming-deliveries", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_subscription_totals(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/subscriptions/subscriptions/1/totals", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_subscription_history(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/subscriptions/subscriptions/1/history", headers=auth_headers)
    assert resp.status_code in (200, 404)
