"""Tests for Customer module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_customer(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/customers/customers/", json={
        "name": "شرکت تست",
        "type": "company",
        "email": "test@company.com",
        "phone": "02112345678",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_customer(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/customers/customers/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_search_customers(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/customers/customers/search/?q=test", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_customer_contact(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/customers/customers/1/contacts/", json={
        "name": "مدیر فروش",
        "email": "sales@company.com",
        "phone": "09121234567",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201, 404)


@pytest.mark.asyncio
async def test_customer_notes(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/customers/customers/1/notes/", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_customer_activities(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/customers/customers/1/activities/", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_customer_segments(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/customers/customer-segments/", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_segment(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/customers/customer-segments/", json={
        "name": "مشتریان ویژه",
        "description": "مشتریان با خرید بالا",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)
