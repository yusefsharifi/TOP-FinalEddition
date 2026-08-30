"""Tests for Pricing module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_pricing_rule(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/pricing/pricing-rules/", json={
        "name": "تخفیف ویژه",
        "type": "percentage",
        "value": 10,
        "min_quantity": 5,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_pricing_rule(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/pricing/pricing-rules/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_create_price_adjustment(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/pricing/price-adjustments/", json={
        "product_id": 1,
        "adjustment_type": "percentage",
        "value": 5,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_calculate_price(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/pricing/calculate-price/?product_id=1&quantity=10", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_active_discounts(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/pricing/active-discounts/", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_volume_discount(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/pricing/volume-discounts/", json={
        "product_id": 1,
        "min_quantity": 10,
        "discount_percentage": 15,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_dynamic_pricing(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/pricing/dynamic-pricing/", json={
        "product_id": 1,
        "base_price": 100000,
        "demand_factor": 1.2,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)
