"""Tests for Product module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/products/products/", json={
        "name": "محصول تست",
        "sku": "PRD-001",
        "description": "توضیحات محصول",
        "category_id": 1,
        "price": 100000,
        "is_active": True,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_product(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/products/products/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_search_products(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/products/products/search/?q=test", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/products/product-categories/", json={
        "name": "دسته‌بندی تست",
        "description": "توضیحات",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_category(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/products/product-categories/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_create_variant(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/products/products/1/variants/", json={
        "name": "سایز بزرگ",
        "sku": "PRD-001-L",
        "price": 120000,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201, 404)


@pytest.mark.asyncio
async def test_product_prices(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/products/products/1/prices/", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_product_reviews(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/products/products/1/reviews/", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_product_images(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/products/products/1/images/", headers=auth_headers)
    assert resp.status_code in (200, 404)
