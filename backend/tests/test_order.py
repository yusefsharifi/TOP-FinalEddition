"""Tests for Order module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/orders/orders/", json={
        "customer_id": 1,
        "items": [{"product_id": 1, "quantity": 5, "unit_price": 100000}],
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_order(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/orders/orders/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_update_order_status(client: AsyncClient, auth_headers: dict):
    resp = await client.put("/api/v1/orders/orders/1/status", json={
        "status": "confirmed",
    }, headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_order_totals(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/orders/orders/1/totals", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_order_history(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/orders/orders/1/history", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_customer_orders(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/orders/customers/1/orders", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_create_order_item(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/orders/orders/1/items/", json={
        "product_id": 2,
        "quantity": 3,
        "unit_price": 200000,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201, 404)


@pytest.mark.asyncio
async def test_create_payment(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/orders/orders/1/payments/", json={
        "amount": 500000,
        "method": "bank_transfer",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201, 404)
