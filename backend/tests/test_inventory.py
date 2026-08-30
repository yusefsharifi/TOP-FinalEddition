"""Tests for Inventory module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_inventory_category(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/inventory/categories", json={
        "name": "مواد اولیه",
        "description": "مواد اولیه تولید",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_inventory_categories(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/inventory/categories", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_create_supplier(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/inventory/suppliers", json={
        "name": "تأمین‌کننده تست",
        "contact_person": "رضا",
        "email": "reza@supplier.com",
        "phone": "09121234567",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_suppliers(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/inventory/suppliers", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_inventory_item(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/inventory/items", json={
        "name": "پیچ M8",
        "sku": "SCR-M8-001",
        "unit": "kg",
        "minimum_stock": 100,
        "reorder_point": 150,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_inventory_items(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/inventory/items", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_stock_levels(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/inventory/stock", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_stock_adjust(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/inventory/stock/adjust", json={
        "item_id": 1,
        "quantity": 50,
        "type": "in",
        "notes": "ورودی انبار",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_movements(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/inventory/movements", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_location(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/inventory/locations", json={
        "name": "انبار مرکزی",
        "code": "WH-01",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)
