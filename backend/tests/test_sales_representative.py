"""Tests for Sales Representative module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_sales_rep(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/sales-reps/sales-representatives/", json={
        "name": "نماینده تست",
        "email": "rep@test.com",
        "phone": "09121234567",
        "region_id": 1,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_sales_rep(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales-reps/sales-representatives/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_create_region(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/sales-reps/sales-regions/", json={
        "name": "منطقه تست",
        "description": "توضیحات",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_visits(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales-reps/sales-visits/", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_visit(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/sales-reps/sales-visits/", json={
        "sales_rep_id": 1,
        "customer_id": 1,
        "visit_date": "2025-06-01",
        "purpose": "مشاوره فروش",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_team_performance(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/sales-reps/team-performance/1", headers=auth_headers)
    assert resp.status_code in (200, 404)
