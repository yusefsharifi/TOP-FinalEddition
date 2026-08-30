"""Tests for Sales module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_opportunity(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/sales/opportunities", json={
        "name": "فرصت فروش تست",
        "customer_id": 1,
        "amount": 50000000,
        "stage": "prospecting",
        "expected_close_date": "2025-06-30",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_opportunities(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales/opportunities", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_quote(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/sales/quotes", json={
        "customer_id": 1,
        "items": [{"product_name": "محصول A", "quantity": 10, "unit_price": 500000}],
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_quotes(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales/quotes", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_invoice(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/sales/invoices", json={
        "customer_id": 1,
        "items": [{"product_name": "محصول A", "quantity": 10, "unit_price": 500000}],
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_invoices(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales/invoices", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_pipeline(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales/pipeline", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sales_forecast(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales/forecast", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sales_dashboard(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales/dashboard", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_leads(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales/leads", headers=auth_headers)
    assert resp.status_code == 200
