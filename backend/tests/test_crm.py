"""Tests for CRM module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_customer_360(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/crm/customers/360/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_customer_segments(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/crm/customers/segments", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_tag(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/crm/tags", json={
        "name": "VIP",
        "color": "#ff0000",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_tags(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/crm/tags", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_customer_interactions(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/crm/customers/1/interactions", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_refresh_scores(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/crm/customers/1/refresh-scores", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_social_accounts(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/crm/social/accounts", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sms_templates(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/crm/sms/templates", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_social_account(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/crm/social/accounts", json={
        "platform": "telegram",
        "account_name": "topworx_bot",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_social_messages(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/crm/social/messages", headers=auth_headers)
    assert resp.status_code == 200
